# National coverage extension — implementation summary

**Ticket:** PIP-127 · **Merged:** PR #16 → `develop` (2026-07-02) · **Updated:** 2026-07-07 · **Status:** ✅ workshop-ready

> **Note (2026-07-07):** the notebook has since moved to a **PATSTAT-anchored** route — it
> starts from the PATSTAT applicant population and resolves only the national-only firms by
> Aktenzeichen, then **unions** them with the PATSTAT-geolocated firms. The two items this doc
> originally listed as "next steps" (PATSTAT join, union & re-tiering) are therefore **done**.
> See *Update (2026-07-07)* at the bottom; sections below are kept as history.

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
| REST client | [`dpma/fetch.py`](../dpma/fetch.py) | **`getRegisterabzuege`** (bulk period extract — population route), `getRegisterInfo` (single record), `search` (`INH=`); Basic auth from `DPMA_USER`/`DPMA_PASS` env only |
| ST.36 parser | [`dpma/register_parser.py`](../dpma/register_parser.py) | XML → applicant rows (name, PLZ, city, country, appln no., filing date, IPC, kind A/U); `iter_registrations_from_zip` streams a whole extract |
| PLZ → region | [`dpma/plz_nuts.py`](../dpma/plz_nuts.py) | PLZ → NUTS3 + Bundesland via bundled Eurostat crosswalk |
| Crosswalk data | [`dpma/data/pc2025_DE_NUTS-2024_v1.0.csv`](../dpma/data/pc2025_DE_NUTS-2024_v1.0.csv) | Eurostat GISCO, NUTS 2024, CC-BY-SA-4.0 |
| Sample fixtures | `dpma/samples/` | single records (1977 U + 2024 A) + a 27-record mini-extract ZIP; **company applicants only** (inventor personal data removed) |
| Demo | [`../2_national-coverage.ipynb`](../2_national-coverage.ipynb) | **region-based lead gen**, now **PATSTAT-anchored**: pull the DE company applicant population from PATSTAT → split already-geolocated vs national-only → resolve national-only addresses by **AKZ lookup** (`search_aktenzeichen`, one per firm) → PLZ→NUTS → **union with the PATSTAT-geolocated firms** → tier by region (see *Update 2026-07-07*) |
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

- Helpers **live-tested** against `dpmaconnect.dpma.de`: `INH=Hager` search (981 hits) +
  query-rejection path, single-record round-trip, and the **bulk extract** for the 2026-06-20
  week (6 760 records → 1 953 DE applicants region-mapped, e.g. Bayern top leads BMW 47 /
  Schaeffler 33 filings).
- Notebook **executed end-to-end via nbconvert — 0 errors** (offline mini-extract + live pull +
  quarter loop) — *this was the bulk-extract version; for the current AKZ route see
  Update (2026-07-07) below.*
- **No secrets committed** (`os.environ` only); committed fixtures contain no natural-person data.

## Design correction (2026-07-02)

The first cut searched by applicant *name* (`INH=`) — backwards for lead generation, which
needs **region → applicants**. Reworked to the population route: pick a period →
`getRegisterabzuege` → parse all → PLZ→NUTS → filter/aggregate by region. `getPublikationsdaten_XML`
was found **permission-denied** for the account, so `getRegisterabzuege` is the route used.
→ *Superseded 2026-07-07 by the PATSTAT-anchored route — see below. `getRegisterabzuege` and the
parser remain in the package for bulk work, but the notebook no longer drives the population
from a period extract.*

## Status of the original "next steps"

- ✅ **PATSTAT join — done.** The notebook now *starts* from PATSTAT (the DE company applicant
  population, patents + utility models) and resolves only the national-only firms (no NUTS) via
  a per-firm Aktenzeichen lookup, so DPMA ↔ PATSTAT are joined by construction. A `has_ep` flag
  tags EP/PCT-active vs national-only firms. `search_aktenzeichen` accepts the raw PATSTAT
  `appln_nr` (`search/AKZ=<appln_nr>`), so no separate number-format normalisation was needed
  for this route.
- ✅ **Union & re-tiering — done.** The regional list is now PATSTAT-NUTS ∪ DPMA-national-only,
  ranked together (notebook Step 5), with a Step-6 payoff quantifying what the PATSTAT-only view
  misses.
- ⬜ **Applicant-name harmonisation** for tighter dedupe across spelling variants — still open.
- ⬜ **Country-wide cached mapping** as a PATSTAT-MCP extension table (`de_applicant_nuts`) so any
  query can join it — still the production next step; design in
  [`patstat-mcp-de-nuts-extension-brief.md`](patstat-mcp-de-nuts-extension-brief.md).

## Update (2026-07-07)

**What changed.** The notebook was reworked from the *period-extract population* route
(`getRegisterabzuege` over a week/quarter, then filter by region) to a **PATSTAT-anchored**
route:

1. PATSTAT gives the DE **company** applicant population for a filing year
   (`appln_auth='DE'`, `TRIM(appln_kind) IN ('A','U')`, `psn_sector='COMPANY'`,
   `person_ctry_code='DE'`), per harmonised applicant `psn_id`, with a `has_nuts` flag and one
   representative `appln_nr`.
2. Firms **with** a German NUTS are kept as-is (region from PATSTAT); firms **without** are the
   national-only tail.
3. Each national-only firm is resolved by **one** `search_aktenzeichen(appln_nr)` call
   (capped at `MAX_RESOLVE`, default 200, for interactivity), reading its PLZ from the hit.
4. `map_plz` → NUTS3 + Bundesland, then **union** with the PATSTAT-geolocated firms and tier by
   region (default `REGION = "Bayern"`, year 2023).

This is why the two original "next steps" are now done. The bulk `getRegisterabzuege` +
`iter_registrations_from_zip` path still ships in `dpma/` (and its fixtures) for population-scale
work, but the workshop notebook no longer uses it.

**Credentials.** `DPMA_USER`/`DPMA_PASS` are still read from the environment only (no secrets in
the repo). On TIP they now come from `~/.secrets/patlibs.env`, loaded into every kernel by an
IPython startup hook (`~/.ipython/profile_default/startup/10-load-env.py`) — this replaced a
per-folder `.env`. The notebook's credential cell falls back to reading that file (or a local
`.env`) if the hook isn't present, so it stays portable.

**Re-verified 2026-07-07 (current AKZ route):** imports + `PatstatClient(env='PROD')` connect,
credential loading via the new mechanism (`DPMA_USER`/`DPMA_PASS` set), and a **live single
`search_aktenzeichen` lookup** returning a parsed applicant (name/PLZ/city). The full
`MAX_RESOLVE`-lookup pass was **not** re-run end-to-end to avoid the DPMA API rate limit.

## Caveats

- **GDPR:** company addresses are low-risk B2B; natural-person applicant addresses are personal
  data — handle/store/display accordingly.
- **DE only** — the analogous national route for France is INPI.
- This is an **optional extension**; the module-5 PATSTAT notebook stays TIP-only and
  self-contained.
