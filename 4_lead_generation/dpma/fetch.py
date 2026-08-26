"""Minimal DPMAconnect Plus REST client (search + getRegisterInfo).

Shows *how to use the national register*: run an expert-search query, take a
lead ``leading-registered-number`` from the hit list, then pull the full ST.36
register record for parsing (:mod:`register_parser`).

Auth is HTTP Basic via the ``DPMA_USER`` / ``DPMA_PASS`` environment variables —
credentials are **never** hard-coded, logged, or committed. Stdlib only.

Notes / limits (from ``docs/national-coverage-extension-dpmaconnect.md``):

* Applicant/proprietor field is **``INH``** (Inhaber), e.g. ``INH=Hager`` —
  *not* ``pa``/``PA`` (those are rejected by the query grammar).
* ``search`` is capped at **1000 hits** (100 on a test account). For a whole
  Bundesland/year use the bulk routes (``getRegisterabzuege`` /
  ``getPublikationsdaten_XML``), not this client.
* Automated runs need ``dpmaconnect.dpma.de`` on the network egress allowlist.
"""

from __future__ import annotations

import base64
import io
import os
import re
import urllib.parse
import urllib.request
import zipfile
from dataclasses import dataclass
from typing import Optional
from xml.etree import ElementTree as ET

__all__ = ["DpmaClient", "Hit"]

BASE_URL = "https://dpmaconnect.dpma.de/dpmaws/rest-services"
SERVICE = "DPMAregisterPatService"


@dataclass
class Hit:
    """One entry from a ``search`` hit list."""

    leading_registered_number: Optional[str]  # the Aktenzeichen to fetch
    registered_number: Optional[str]
    type: Optional[str]
    application_date: Optional[str]
    applicants: list[str]
    title: Optional[str]


class DpmaClient:
    """Tiny authenticated client for the DPMAregister patent service."""

    def __init__(self, user: Optional[str] = None, password: Optional[str] = None,
                 timeout: int = 60):
        user = user or os.environ.get("DPMA_USER")
        password = password or os.environ.get("DPMA_PASS")
        if not user or not password:
            raise RuntimeError(
                "DPMA credentials missing — set DPMA_USER / DPMA_PASS in the "
                "environment (never hard-code them)."
            )
        token = base64.b64encode(f"{user}:{password}".encode()).decode()
        self._auth = f"Basic {token}"
        self._timeout = timeout

    def _get(self, path: str) -> bytes:
        req = urllib.request.Request(
            f"{BASE_URL}/{SERVICE}/{path}",
            headers={"Authorization": self._auth},
        )
        with urllib.request.urlopen(req, timeout=self._timeout) as resp:
            return resp.read()

    def search_raw(self, expert_query: str) -> bytes:
        """Run an expert query (e.g. ``"INH=Hager"``); return raw hit-list XML."""
        # Encode the whole expert query; '=' becomes %3D as the API expects.
        return self._get(f"search/{urllib.parse.quote(expert_query, safe='')}")

    def search(self, expert_query: str) -> list[Hit]:
        """Run an expert query and parse the hit list.

        Raises ``ValueError`` if the query grammar rejects the input (the API
        answers HTTP 200 with ``HitCount=0`` and an error message, so we surface
        it instead of silently returning nothing).
        """
        root = ET.fromstring(self.search_raw(expert_query))
        msg = root.get("Message_EN") or root.get("Message_DE")
        if msg:
            raise ValueError(f"DPMA rejected query {expert_query!r}: {msg}")
        hits = []
        for rec in root.findall(".//{*}PatentHitListRecord"):
            hits.append(
                Hit(
                    leading_registered_number=_t(rec, "{*}leading-registered-number"),
                    registered_number=_t(rec, "{*}registered-number"),
                    type=_t(rec, "{*}type"),
                    application_date=_t(rec, "{*}applicationDate"),
                    applicants=[a.text.strip() for a in rec.findall(".//{*}applicant") if a.text],
                    title=_t(rec, "{*}invention-title"),
                )
            )
        return hits

    def search_applicant(self, name: str) -> list[Hit]:
        """Convenience: search by applicant/proprietor name (``INH`` field)."""
        return self.search(f"INH={name}")

    def search_aktenzeichen(self, appln_nr: str) -> list[Hit]:
        """Look up a register record by application number (``AKZ`` field).

        Accepts a PATSTAT-style DE application number directly — the 12-digit
        Aktenzeichen base *without* the check digit, e.g. ``102019213199``. The
        single hit carries the applicant name + PLZ (parse with
        :func:`register_parser.parse_hit_applicant`) and the
        ``leading-registered-number`` (base + computed check digit) for an
        optional :meth:`get_register_info`. This is the bridge from PATSTAT
        ``appln_nr`` to the DPMA register — ``getRegisterInfo`` rejects the bare
        12-digit number, but ``AKZ`` search accepts it.
        """
        return self.search(f"AKZ={appln_nr}")

    def get_register_info(self, aktenzeichen: str) -> bytes:
        """Fetch the full ST.36 register record (feed to ``parse_register_xml``)."""
        return self._get(f"getRegisterInfo/{urllib.parse.quote(str(aktenzeichen), safe='')}")

    def get_register_extract(self, date: str, period: str = "weekly") -> bytes:
        """Fetch a bulk register extract (``getRegisterabzuege``) as ZIP bytes.

        This is the **population route** for regional lead generation: it returns
        *all* registrations with register activity in the given period — one
        ST.36 record per file — which you then filter/aggregate by region
        (feed to :func:`register_parser.iter_registrations_from_zip`).

        ``date`` is ``YYYY-MM-DD`` and must match an actual extract date;
        ``period`` is one of ``daily`` / ``weekly`` / ``monthly`` / ``yearly``.
        Raises ``ValueError`` if the account lacks permission, the period is
        empty (a ``KeinTreffer.txt`` marker), or the server returns an error.

        Note: the sibling ``getPublikationsdaten_XML`` route is *not* used here —
        it requires a separate DPMAconnect permission the workshop account may
        not hold.
        """
        if period not in {"daily", "weekly", "monthly", "yearly"}:
            raise ValueError(f"period must be daily/weekly/monthly/yearly, got {period!r}")
        raw = self._get(
            f"getRegisterabzuege/{urllib.parse.quote(date, safe='')}/{period}"
        )
        # An error is returned as an XML <Transaction> instead of a ZIP.
        if not raw[:2] == b"PK":
            msg = raw.decode("utf-8", "replace")
            m = re.search(r"<TransactionErrorText>(.*?)</TransactionErrorText>", msg, re.S)
            raise ValueError(f"getRegisterabzuege failed: {m.group(1) if m else msg[:200]}")
        # A ZIP whose only member is KeinTreffer.txt means "no records this period".
        with zipfile.ZipFile(io.BytesIO(raw)) as zf:
            names = zf.namelist()
            if not any(n.lower().endswith(".xml") for n in names):
                raise ValueError(
                    f"no records for {date}/{period} "
                    f"(extract contained: {', '.join(names) or 'nothing'})"
                )
        return raw


def _t(el, path: str) -> Optional[str]:
    node = el.find(path)
    return node.text.strip() if node is not None and node.text else None
