"""Parse DPMAconnect Plus register records (ST.36 XML) into applicant rows.

Workshop helper for module 5 (Lead Generation). It turns the ``getRegisterInfo``
response of the DPMAregister patent/utility-model service into flat, tabular
applicant records — the German national-office address data that PATSTAT is
missing for the ~70 % of DE filings that never take the EP/PCT route (see
``docs/national-coverage-extension-dpmaconnect.md``).

Scope: parsing only. Fetching lives in :mod:`fetch` (optional, credentialed);
PLZ→region mapping lives in :mod:`plz_nuts`.

The register XML (schema ``DE-PATGBM-RegisterExt``) carries a *default*
namespace, so every tag is namespaced. We match with the ``{*}`` wildcard so the
parser keeps working across schema-version bumps.

Confirmed against a 1977 utility model and a 2024 patent (2026-07-02):

* Applicant address block::

      bibliographic-data/parties/applicants/applicant/addressbook
        name       -> applicant name
        text       -> full "Name, PLZ Ort, Land" string
        address/address-1 -> "PLZ Ort"   (postcode + city MERGED; no street!)
        address/country   -> country code

* There is **no** separate street / postcode / city tag — PLZ is the leading
  five digits of ``address-1``; foreign applicants have no PLZ ("Obernai, FR").
* ``inventors`` / ``agents`` / ``correspondence-address`` are *separate* party
  blocks — this parser reads ``applicants`` only.
"""

from __future__ import annotations

import io
import re
import zipfile
from dataclasses import dataclass, field, asdict
from typing import Iterator, Optional
from xml.etree import ElementTree as ET

__all__ = [
    "Applicant",
    "Registration",
    "parse_register_xml",
    "iter_registrations_from_zip",
    "applicant_rows",
    "split_address1",
    "format_ipc",
]

# PLZ = the leading 5 digits of address-1 (rest is the city). DE postcodes only.
_PLZ_CITY = re.compile(r"^\s*(\d{5})\s+(.*\S)\s*$")


def split_address1(address1: Optional[str]) -> tuple[Optional[str], Optional[str]]:
    """Split an ``address-1`` value ("66440 Blieskastel") into (plz, city).

    Returns ``(None, city)`` when there is no leading 5-digit postcode — which is
    the normal case for foreign applicants ("Obernai" for FR, "Emmenbrücke" for
    CH), whose region cannot be mapped via the German PLZ crosswalk.
    """
    if not address1:
        return None, None
    m = _PLZ_CITY.match(address1)
    if m:
        return m.group(1), m.group(2)
    return None, address1.strip() or None


def format_ipc(raw: Optional[str]) -> Optional[str]:
    """Format a compact ST.36 IPC symbol ("A61C0009000000") as "A61C 9/00"."""
    if not raw:
        return None
    s = raw.strip().replace(" ", "")
    if len(s) < 8:
        return raw.strip()
    subclass = s[0:4]          # e.g. A61C
    main = s[4:8].lstrip("0") or "0"   # 0009 -> 9
    subgroup = s[8:14].rstrip("0") or "00"  # 000000 -> 00 ; 530000 -> 53
    if len(subgroup) < 2:
        subgroup = subgroup + "0"  # keep the conventional 2-digit minimum
    return f"{subclass} {main}/{subgroup}"


def _kind_code(kind: Optional[str], type_of_ip_right: Optional[str]) -> Optional[str]:
    """Map to the module's A/U convention (patent vs utility model).

    Prefers the publication ``kind`` (``A1``/``U1``…); falls back to the
    office-specific ``type-of-ip-right`` (``patent`` / ``gebrauchsmuster``).
    """
    if kind:
        first = kind.strip()[:1].upper()
        if first == "A":
            return "A"
        if first == "U":
            return "U"
    if type_of_ip_right:
        t = type_of_ip_right.strip().lower()
        if t.startswith("patent"):
            return "A"
        if t.startswith("gebrauchsmuster"):
            return "U"
    return None


@dataclass
class Applicant:
    """One applicant of one registration."""

    name: Optional[str]
    plz: Optional[str]
    city: Optional[str]
    country: Optional[str]
    address_raw: Optional[str]   # the merged address-1 line, verbatim


@dataclass
class Registration:
    """One DPMA register record (one patent or utility model)."""

    appln_number: Optional[str]      # e.g. "102024206684.2"
    filing_date: Optional[str]       # ISO date "2024-07-16"
    kind: Optional[str]              # A = patent, U = utility model
    ipc: list[str] = field(default_factory=list)
    title: Optional[str] = None
    applicants: list[Applicant] = field(default_factory=list)


def _text(el, path: str) -> Optional[str]:
    node = el.find(path)
    return node.text.strip() if node is not None and node.text else None


def parse_register_xml(data) -> Registration:
    """Parse one ``getRegisterInfo`` ST.36 response into a :class:`Registration`.

    ``data`` may be an XML string, bytes, a file path, or an ``ElementTree``
    root element.
    """
    if isinstance(data, ET.Element):
        root = data
    elif isinstance(data, (bytes, bytearray)):
        root = ET.fromstring(data)
    elif isinstance(data, str) and data.lstrip().startswith("<"):
        root = ET.fromstring(data)
    else:  # treat as a path
        root = ET.parse(data).getroot()

    appln_number = _text(root, ".//{*}application-reference/{*}document-id/{*}doc-number")
    filing_date = (
        _text(root, ".//{*}application-reference/{*}document-id/{*}date")
        or _text(root, ".//{*}office-specific-bib-data/{*}national-filing-data")
    )
    kind = _text(root, ".//{*}publication-reference/{*}document-id/{*}kind")
    type_of_ip = _text(root, ".//{*}office-specific-bib-data/{*}type-of-ip-right")
    title = _text(root, ".//{*}invention-title")

    ipc = [
        format_ipc(node.text)
        for node in root.findall(".//{*}classifications-ipcr/{*}classification-ipcr/{*}text")
        if node.text
    ]

    applicants: list[Applicant] = []
    # Applicants ONLY — deliberately not inventors / agents / correspondence.
    for book in root.findall(".//{*}parties/{*}applicants/{*}applicant/{*}addressbook"):
        address1 = _text(book, "./{*}address/{*}address-1")
        plz, city = split_address1(address1)
        applicants.append(
            Applicant(
                name=_text(book, "./{*}name"),
                plz=plz,
                city=city,
                country=_text(book, "./{*}address/{*}country"),
                address_raw=address1,
            )
        )

    return Registration(
        appln_number=appln_number,
        filing_date=filing_date,
        kind=_kind_code(kind, type_of_ip),
        ipc=[i for i in ipc if i],
        title=title,
        applicants=applicants,
    )


def iter_registrations_from_zip(data) -> Iterator[Registration]:
    """Yield one :class:`Registration` per XML member of a register-extract ZIP.

    ``data`` is the bytes (or a path / open file) of a ``getRegisterabzuege``
    response — a ZIP holding one ST.36 record per registration, named by
    Aktenzeichen (``1020242066842.xml``). Non-XML members (e.g. the
    ``KeinTreffer.txt`` marker returned for an empty period) are skipped, as are
    individual records that fail to parse (logged via the ``errors`` note is out
    of scope here — malformed records are simply skipped).

    This is the **population-scale** route for regional lead generation: pull a
    whole publication period, then filter/aggregate by region — rather than
    searching one applicant name at a time.
    """
    zf = data if isinstance(data, zipfile.ZipFile) else zipfile.ZipFile(
        io.BytesIO(data) if isinstance(data, (bytes, bytearray)) else data
    )
    for name in zf.namelist():
        if not name.lower().endswith(".xml"):
            continue
        try:
            yield parse_register_xml(zf.read(name))
        except ET.ParseError:
            continue


def applicant_rows(reg: Registration) -> list[dict]:
    """Flatten a :class:`Registration` to one dict per applicant.

    Ready for ``pandas.DataFrame(...)``. Registration-level fields (number,
    date, kind, IPC) are repeated on each applicant row.
    """
    ipc_str = "; ".join(reg.ipc)
    rows = []
    for a in reg.applicants:
        row = asdict(a)
        row.update(
            appln_number=reg.appln_number,
            filing_date=reg.filing_date,
            kind=reg.kind,
            ipc=ipc_str,
            title=reg.title,
        )
        rows.append(row)
    return rows
