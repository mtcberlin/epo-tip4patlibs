# National coverage extension — implementation summary

**Ticket:** PIP-127 · **Merged:** PR #16 → `develop` (2026-07-02) · **Status:** ✅ workshop-ready

What was planned and built to recover the national-only German applicant addresses
PATSTAT is missing, and map them to NUTS regions. Design rationale lives in
[`national-coverage-extension-dpmaconnect.md`](national-coverage-extension-dpmaconnect.md);
NUTS mapping detail in [`nuts-mappings.md`](nuts-mappings.md).

## The problem

A NUTS region filter in PATSTAT returns only the **EP/PCT-active subset** of a region's
applicants — NUTS is assigned on the EP/PCT route only. ~70 % of German national patent
families never take that route and carry **no NUTS**, and PATSTAT can't recover them by
postcode (`tls226.zip_code` is empty). Those national-only filers — mostly smaller,
locally-filing SMEs — are exactly the leads a PATLIB most wants, and they're invisible.

## Approach (planned)

Use the **DPMAconnect Plus** register (which *does* carry every national filing's applicant
address incl. PLZ) to recover the missing tail, then map PLZ → NUTS3 so it lines up with
PATSTAT's geocoding. Scope was deliberately kept to a **workshop notebook + a small helper
package** — not a full production pipeline.

## What was built

| Component | File | Notes |
|-----------|------|-------|
| REST client | [`dpma/fetch.py`](../dpma/fetch.py) | `search` + `getRegisterInfo`; Basic auth from `DPMA_USER`/`DPMA_PASS` env vars only |
| ST.36 parser | [`dpma/register_parser.py`](../dpma/register_parser.py) | XML → applicant rows (name, PLZ, city, country, appln no., filing date, IPC, kind A/U) |
| PLZ → region | [`dpma/plz_nuts.py`](../dpma/plz_nuts.py) | PLZ → NUTS3 + Bundesland via bundled Eurostat crosswalk |
| Crosswalk data | [`dpma/data/pc2025_DE_NUTS-2024_v1.0.csv`](../dpma/data/pc2025_DE_NUTS-2024_v1.0.csv) | Eurostat GISCO, NUTS 2024, CC-BY-SA-4.0 |
| Sample fixtures | `dpma/samples/*.xml` | 1977 utility model + 2024 patent; **company applicants only** (inventor personal data removed) |
| Demo | [`../national_coverage_demo.ipynb`](../national_coverage_demo.ipynb) | offline (bundled samples) + optional live fetch + regional roll-up |
| Package + docs | `dpma/__init__.py`, `dpma/README.md` | importable as `from dpma import ...` |

## Key findings (corrected the original plan)

1. **Applicant search field is `INH`** (Inhaber), *not* `pa`/`PA`. The plan's `pa=` recipe was
   rejected by the query grammar (`HitCount=0`, "'pa' not admissible at position 1"). Fixed in
   the plan doc.
2. **The register has no separate street / postcode / city tags.** Even modern 2024 records
   merge PLZ + city into `<address-1>` (e.g. `66440 Blieskastel`) and publish no street. PLZ is
   extracted as the leading 5 digits; the parser targets `<applicants>` only (not
   `<inventors>` / `<agents>`).
3. **PLZ → NUTS3 is clean and unambiguous** — 8 333 PLZ each map to exactly one of 400 NUTS3
   regions; Bundesland is the NUTS1 (first-3-chars) prefix.

## Verification

- All three helpers **live-tested** against `dpmaconnect.dpma.de` (981 hits for `INH=Hager`,
  query-rejection path, fetch → parse round-trip).
- Notebook **executed end-to-end via nbconvert — 0 errors** (offline + live paths).
- **No secrets committed** (`os.environ` only); committed fixtures contain no natural-person data.

## Deliberately out of scope (next steps)

- **PATSTAT join:** DPMA Aktenzeichen ↔ PATSTAT `appln_nr` (`appln_auth='DE'`) after number
  normalisation, plus a per-family `has_EP` flag to tag firms EP/PCT-active vs national-only.
  Number-format normalisation is still open.
- **Bulk routes** for whole regions: `getRegisterabzuege` / `getPublikationsdaten_XML`
  (`search` caps at 1000 hits).
- **Union & re-tiering:** rebuild the regional list as PATSTAT-NUTS ∪ DPMA-national-only, fed
  into the same depth × reach tiering.

## Caveats

- **GDPR:** company addresses are low-risk B2B; natural-person applicant addresses are personal
  data — handle/store/display accordingly.
- **DE only** — the analogous national route for France is INPI.
- This is an **optional extension**; the module-5 PATSTAT notebook stays TIP-only and
  self-contained.
