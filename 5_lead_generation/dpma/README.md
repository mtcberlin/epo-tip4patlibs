# `dpma/` — National coverage extension (DPMAconnect Plus)

Helpers that recover the **national-only German applicant addresses PATSTAT is
missing** (NUTS is assigned on the EP/PCT route only) and map them to the same
NUTS3 regions PATSTAT uses. Background & design:
[`../docs/national-coverage-extension-dpmaconnect.md`](../docs/national-coverage-extension-dpmaconnect.md).

Demo: [`../national_coverage_demo.ipynb`](../national_coverage_demo.ipynb).

## Modules

| module | purpose |
|---|---|
| `fetch.py` | Minimal authenticated REST client for `DPMAregisterPatService` (`search` + `getRegisterInfo`). Applicant field is **`INH`**. Credentials from `DPMA_USER` / `DPMA_PASS`. |
| `register_parser.py` | ST.36 register XML → per-applicant rows (name, PLZ, city, country, application number, filing date, IPC, kind A/U). Applicants only — not inventors/agents. |
| `plz_nuts.py` | 5-digit PLZ → NUTS3 code + Bundesland, using the bundled Eurostat crosswalk. |

## Quick start

```python
from dpma import fetch, parse_register_xml, applicant_rows, enrich_rows

client = fetch.DpmaClient()                       # reads DPMA_USER / DPMA_PASS
hits = client.search_applicant("Hager")           # INH=Hager
reg = parse_register_xml(client.get_register_info(hits[0].leading_registered_number))
rows = enrich_rows(applicant_rows(reg))           # rows now carry nuts3 / bundesland
```

Offline (no credentials): parse the bundled records under `samples/`.

## Data

`data/pc2025_DE_NUTS-2024_v1.0.csv` — Eurostat GISCO postal-code ↔ NUTS
correspondence table (Germany, NUTS 2024). © EuroGeographics / Eurostat,
licensed **CC-BY-SA-4.0**. Each of the 8 333 German PLZ maps to exactly one
NUTS3 region; the Bundesland (NUTS1) is the first three characters of the code.

## Scope & caveats

- Recovers the **national-only tail**; the complete regional list is the union
  of the PATSTAT NUTS list (EP/PCT-active) and these DPMA firms. Linking a firm
  to its PATSTAT families (Aktenzeichen ↔ `appln_nr`, `has_EP` flag) is a later
  step — number normalisation is still open.
- **GDPR:** company addresses are low-risk B2B; natural-person applicant
  addresses are personal data — the bundled samples have inventor data removed.
- `search` caps at **1000 hits**; for a whole Bundesland/year use the bulk
  routes (`getRegisterabzuege` / `getPublikationsdaten_XML`).
- DE only (the FR analogue is INPI).
