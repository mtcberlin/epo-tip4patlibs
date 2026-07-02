# `dpma/` — National coverage extension (DPMAconnect Plus)

Helpers that recover the **national-only German applicant addresses PATSTAT is
missing** (NUTS is assigned on the EP/PCT route only) and map them to the same
NUTS3 regions PATSTAT uses. Background & design:
[`../docs/national-coverage-extension-dpmaconnect.md`](../docs/national-coverage-extension-dpmaconnect.md).

Demo: [`../national_coverage_demo.ipynb`](../national_coverage_demo.ipynb).

## Modules

| module | purpose |
|---|---|
| `fetch.py` | Minimal authenticated REST client for `DPMAregisterPatService`: **`getRegisterabzuege`** (bulk period extract — the population route), `getRegisterInfo` (single record), `search` (`INH=` applicant field). Credentials from `DPMA_USER` / `DPMA_PASS`. |
| `register_parser.py` | ST.36 register XML → per-applicant rows (name, PLZ, city, country, application number, filing date, IPC, kind A/U). Applicants only — not inventors/agents. `iter_registrations_from_zip` streams a whole extract ZIP. |
| `plz_nuts.py` | 5-digit PLZ → NUTS3 code + Bundesland, using the bundled Eurostat crosswalk. |

## Quick start — regional leads (population route)

Pick a period, pull *all* filings, map to regions, aggregate — the entry point is a
**period, not a name**:

```python
from dpma import fetch, iter_registrations_from_zip, applicant_rows, enrich_rows
import pandas as pd

client = fetch.DpmaClient()                             # reads DPMA_USER / DPMA_PASS
zip_bytes = client.get_register_extract("2026-06-20", "weekly")   # getRegisterabzuege
rows = []
for reg in iter_registrations_from_zip(zip_bytes):
    rows += applicant_rows(reg)
enrich_rows(rows)                                       # adds nuts3 / bundesland
df = pd.DataFrame(rows)
leads = df[(df.country == "DE") & (df.bundesland == "Bayern")]   # regional lead list
```

Single applicant lookup (secondary): `client.search_applicant("Hager")` →
`client.get_register_info(az)` → `parse_register_xml(...)`.

Offline (no credentials): iterate the bundled mini-extract
`samples/registerabzug_sample_2026-06-20_weekly.zip`, or parse the single-record
samples under `samples/`. The full demo is
[`../national_coverage_demo.ipynb`](../national_coverage_demo.ipynb).

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
- **Route choice:** `search` caps at **1000 hits** — fine for one applicant, useless
  for a region. Use **`getRegisterabzuege`** (bulk period extract) for population-scale
  regional work. The sibling `getPublikationsdaten_XML` is **not** used: it needs a
  separate DPMAconnect permission the workshop account may lack.
- **Extract semantics:** a `getRegisterabzuege` period is the register-*change* stream
  (records with activity that period, incl. foreign applicants and EP validations), not
  only new filings. Keep the DE subset for regional leads.
- DE only (the FR analogue is INPI).
