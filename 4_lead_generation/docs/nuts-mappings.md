# NUTS mappings for the DPMA national-coverage extension

Reference for how German applicant postcodes (PLZ) are turned into **NUTS regions**
— the same geocoding PATSTAT uses, but recovered for the national-only DE filings
PATSTAT leaves un-coded. Used by [`dpma/plz_nuts.py`](../dpma/plz_nuts.py); see the
design in [`national-coverage-extension-dpmaconnect.md`](national-coverage-extension-dpmaconnect.md).

## Two mapping layers

1. **PLZ → NUTS3** (Landkreis / kreisfreie Stadt) — data-driven, from the Eurostat
   crosswalk below. NUTS3 is the finest level; it matches PATSTAT's `nuts` at
   `nuts_level = 3`.
2. **NUTS3 → NUTS1** (Bundesland) — structural: the Bundesland is the **first three
   characters** of the NUTS3 code (`DEA11` → `DEA` → Nordrhein-Westfalen). Resolved
   via the fixed 16-row table in the next section.

```
PLZ "40217"  ──crosswalk──▶  NUTS3 "DEA11"  ──prefix[:3]──▶  NUTS1 "DEA" = Nordrhein-Westfalen
```

## NUTS1 → Bundesland (`BUNDESLAND_BY_NUTS1`)

The German NUTS-1 codes are stable across NUTS revisions. Coverage figures are from
the bundled crosswalk (NUTS 2024): number of distinct NUTS3 regions and PLZ per state.

| NUTS1 | Bundesland | NUTS3 regions | PLZ |
|-------|------------|--------------:|----:|
| DE1 | Baden-Württemberg | 44 | 1210 |
| DE2 | Bayern | 96 | 2079 |
| DE3 | Berlin | 1 | 193 |
| DE4 | Brandenburg | 18 | 225 |
| DE5 | Bremen | 2 | 42 |
| DE6 | Hamburg | 1 | 102 |
| DE7 | Hessen | 26 | 551 |
| DE8 | Mecklenburg-Vorpommern | 8 | 194 |
| DE9 | Niedersachsen | 45 | 821 |
| DEA | Nordrhein-Westfalen | 53 | 874 |
| DEB | Rheinland-Pfalz | 36 | 660 |
| DEC | Saarland | 6 | 71 |
| DED | Sachsen | 13 | 406 |
| DEE | Sachsen-Anhalt | 14 | 223 |
| DEF | Schleswig-Holstein | 15 | 453 |
| DEG | Thüringen | 22 | 229 |
| **Total** | **16 states** | **400** | **8333** |

## The PLZ → NUTS3 crosswalk

- **File:** [`../dpma/data/pc2025_DE_NUTS-2024_v1.0.csv`](../dpma/data/pc2025_DE_NUTS-2024_v1.0.csv)
  (single source of truth — the code loads it from there, not from `docs/`).
- **Source:** Eurostat GISCO "postal codes ↔ NUTS" correspondence table (Germany),
  NUTS 2024 vintage. © EuroGeographics / Eurostat, **CC-BY-SA-4.0**.
  Portal: <https://ec.europa.eu/eurostat/web/gisco/geodata/statistical-units/postal-codes>
- **Format:** `NUTS3;CODE`, semicolon-separated, single-quoted values, UTF-8 BOM.
  `CODE` is the 5-digit PLZ; `NUTS3` is its region. Example row: `'DEC05';'66440'`.
- **Shape:** 8 333 German PLZ → **400** NUTS3 regions. Each PLZ maps to **exactly one**
  NUTS3 (no ambiguous postcodes in this table), so the lookup is a plain dict.

## Notes & limits

- **Foreign applicants have no German PLZ** (`Obernai, FR`, `Emmenbrücke, CH`), so they
  get `nuts3 = None` by design — they cannot and should not be regionalised via this
  crosswalk.
- **NUTS3 = code, not name.** This mirrors PATSTAT, which stores the NUTS *code*.
  Landkreis *labels* would need Eurostat's separate NUTS-labels table; not bundled
  because the workshop compares against PATSTAT on codes.
- **Vintage matters.** NUTS 2024 is used here. If you join against a PATSTAT edition
  built on an older NUTS revision (e.g. 2021), a handful of recoded regions can differ;
  align vintages before a strict code-level join.
- **PLZ ≠ Kreis boundaries.** A postcode can physically straddle two Kreise; the Eurostat
  table assigns each PLZ its dominant NUTS3. This is the same pragmatic assumption used
  across postcode-based regionalisation (incl. OECD REGPAT).
