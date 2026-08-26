"""Map a German 5-digit postcode (PLZ) to a NUTS3 region + Bundesland.

This is the piece PATSTAT cannot give you for national-only DE filings: NUTS is
assigned on the EP/PCT route only, so the ~70 % of DE families that stay national
carry no NUTS. The DPMA register *does* have the applicant's PLZ (see
:mod:`register_parser`); this module turns that PLZ into the same NUTS3 code
PATSTAT uses for EP/PCT applicants, so the two populations become comparable.

Crosswalk: Eurostat GISCO "postal codes ↔ NUTS" correspondence table
(``pc2025_DE_NUTS-2024_v1.0.csv``, NUTS 2024, CC-BY-SA-4.0), bundled under
``data/``. Each of the 8 333 German PLZ maps to exactly one NUTS3 (Landkreis /
kreisfreie Stadt). The Bundesland (NUTS1) is the first three characters of the
NUTS3 code — resolved via :data:`BUNDESLAND_BY_NUTS1` below.
"""

from __future__ import annotations

import csv
from functools import lru_cache
from pathlib import Path
from typing import Optional

__all__ = ["BUNDESLAND_BY_NUTS1", "load_crosswalk", "map_plz", "enrich_rows"]

_DATA = Path(__file__).with_name("data") / "pc2025_DE_NUTS-2024_v1.0.csv"

# NUTS1 (first 3 chars of the NUTS3 code) -> German federal state.
BUNDESLAND_BY_NUTS1 = {
    "DE1": "Baden-Württemberg",
    "DE2": "Bayern",
    "DE3": "Berlin",
    "DE4": "Brandenburg",
    "DE5": "Bremen",
    "DE6": "Hamburg",
    "DE7": "Hessen",
    "DE8": "Mecklenburg-Vorpommern",
    "DE9": "Niedersachsen",
    "DEA": "Nordrhein-Westfalen",
    "DEB": "Rheinland-Pfalz",
    "DEC": "Saarland",
    "DED": "Sachsen",
    "DEE": "Sachsen-Anhalt",
    "DEF": "Schleswig-Holstein",
    "DEG": "Thüringen",
}


@lru_cache(maxsize=None)
def load_crosswalk(path: Optional[str] = None) -> dict[str, str]:
    """Load the PLZ→NUTS3 crosswalk as ``{plz: nuts3}`` (cached).

    The Eurostat CSV is ``NUTS3;CODE`` with single-quoted, semicolon-separated
    values and a UTF-8 BOM.
    """
    p = Path(path) if path else _DATA
    mapping: dict[str, str] = {}
    with open(p, encoding="utf-8-sig", newline="") as fh:
        reader = csv.reader(fh, delimiter=";")
        next(reader, None)  # header: NUTS3;CODE
        for row in reader:
            if len(row) < 2:
                continue
            nuts3 = row[0].strip().strip("'")
            plz = row[1].strip().strip("'")
            if plz:
                mapping[plz] = nuts3
    return mapping


def map_plz(plz: Optional[str], path: Optional[str] = None) -> Optional[dict]:
    """Map a 5-digit PLZ to ``{plz, nuts3, nuts1, bundesland}`` or ``None``.

    Returns ``None`` for a missing/foreign PLZ (no German NUTS assignment).
    """
    if not plz:
        return None
    nuts3 = load_crosswalk(path).get(str(plz).strip())
    if not nuts3:
        return None
    nuts1 = nuts3[:3]
    return {
        "plz": str(plz).strip(),
        "nuts3": nuts3,
        "nuts1": nuts1,
        "bundesland": BUNDESLAND_BY_NUTS1.get(nuts1),
    }


def enrich_rows(rows: list[dict], plz_key: str = "plz", path: Optional[str] = None) -> list[dict]:
    """Add ``nuts3`` / ``nuts1`` / ``bundesland`` to applicant-row dicts in place.

    Rows without a mappable PLZ (foreign applicants) get ``None`` for all three,
    so a DataFrame stays rectangular. Returns the same list for convenience.
    """
    for row in rows:
        hit = map_plz(row.get(plz_key), path)
        row["nuts3"] = hit["nuts3"] if hit else None
        row["nuts1"] = hit["nuts1"] if hit else None
        row["bundesland"] = hit["bundesland"] if hit else None
    return rows
