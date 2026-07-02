"""DPMAconnect Plus helpers for module 5 (Lead Generation).

Recover the national-only German applicant addresses that PATSTAT is missing
(NUTS is assigned on the EP/PCT route only) from the DPMA patent/utility-model
register, and map them to the same NUTS3 regions PATSTAT uses.

* :mod:`dpma.fetch` — minimal authenticated REST client (search + getRegisterInfo)
* :mod:`dpma.register_parser` — ST.36 XML → applicant rows
* :mod:`dpma.plz_nuts` — PLZ → NUTS3 + Bundesland

See ``../docs/national-coverage-extension-dpmaconnect.md`` for the design.
"""

from . import fetch, plz_nuts, register_parser
from .plz_nuts import enrich_rows, map_plz
from .register_parser import (
    applicant_rows,
    iter_registrations_from_zip,
    parse_register_xml,
)

__all__ = [
    "fetch",
    "plz_nuts",
    "register_parser",
    "parse_register_xml",
    "iter_registrations_from_zip",
    "applicant_rows",
    "map_plz",
    "enrich_rows",
]
