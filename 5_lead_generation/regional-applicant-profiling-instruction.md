# Development Brief — Regional Applicant Profiling SQL

*This is the brief we use to **develop and verify the SQL** that powers the workshop
notebook `epo_training_regional-leads.ipynb`, using Claude + the **patstat-mcp** (EPO
PATSTAT Global on BigQuery) against live data.*

> **Read this first, then read the three `docs/`** — they hold the fully worked, live-verified
> method (Alsace/FR42 recipe, the Philippe comparison, and the regional-analysis guide fixes).
> This brief tells you *how to build and re-derive the queries*; the notebook is the
> participant-facing product.

## Two audiences, one method — keep them separate
| Artifact | Audience | Runs on | May use |
|---|---|---|---|
| **this brief + `docs/`** | us (query development) | patstat-mcp / BigQuery | `execute_query` (with `dry_run`), `get_guide`, schema tools |
| **the notebook** | PATLIB staff (workshop) | **EPO TIP only** | `PatstatClient.sql_query` — **no MCP, no BigQuery** |

So: **develop and cost-check every query here via the MCP, then bake the verified SQL into
the notebook.** The notebook must contain only explanations and TIP-runnable SQL. Keep the
SQL to portable standard-SQL constructs (`CASE … WHEN`, `COUNT(DISTINCT …)`, `TRIM`,
`SUBSTR`, `LIKE`) so it runs unchanged through `PatstatClient.sql_query`.

## What the analysis produces
For a **region** (given as NUTS codes), the **EP/PCT-active company applicants based there**
over a recent multi-year window, profiled on two axes and segmented into lead tiers:
1. **Portfolio depth** — patent families per company.
2. **Geographic reach** — which economic zones those families cover.

Segmentation into **neutral tiers** (small/medium/large depth × local/regional/global reach)
tells a PATLIB which regional firms are worth approaching for IP services and training.

## Methodology non-negotiables (verified — see `docs/`)
- **Backbone:** `tls206_person → tls207_pers_appln → tls201_appln`.
- **Applicants only:** `pa.applt_seq_nr > 0` (not inventors).
- **Families, never applications:** `COUNT(DISTINCT a.docdb_family_id)`.
- **Companies only:** `p.psn_sector = 'COMPANY'`.
- **Both geocoding sources:** `p.nuts_level IN (3,4)`.
- **Region across BOTH NUTS vintages** — old level-3 codes (`FR421/FR422`) *and* current
  level-4 REGPAT codes (`FRF11/FRF12`). Never truncate one prefix with `SUBSTR(nuts,1,4)`:
  that silently drops every level-4 record (Alsace: 52/280 → **78/396** once both are included).
- **Genuine patent applications:** `TRIM(appln_kind) = 'A'` — `appln_kind` is space-padded,
  so `= 'A'` matches nothing; and this excludes `T` (EP validations) and `U` (utility models).
- **Reach across all family members:** join back to `tls201_appln` on `docdb_family_id` and
  read `appln_auth` for every member, not just the regional filing.
- **Window:** filing years (e.g. 2017–2022) = *active in window*.

## The one honest caveat (put it in the notebook prominently)
A NUTS filter returns only the **EP/PCT-active subset** of a region's applicants. NUTS is
assigned on the EP/PCT route only; **~70% of national (e.g. DPMA/INPI) patent families never
take that route and carry no NUTS** — typically the smaller, locally-filing firms a PATLIB
most wants. PATSTAT cannot recover them by postcode (`tls226.zip_code` empty; addresses
sparse). Full-population work needs national-office data. Also flag `han_name`
under-consolidation (group/legal-form splits: KUHN SAS + KUHN SA; HAGER ELECTRO + HAGER
CONTROLS) — consolidate via `doc_std_name_id`/`psn_id` before any final ranking.

## Verification workflow
1. `get_guide('regional-analysis')` for the maintained methodology; cross-check with `docs/`.
2. `execute_query(..., dry_run=True)` first to check bytes/cost (the depth/reach queries scan
   ~10–13 GB, ≈ 0.06 EUR each — fine, but always dry-run before a new variant).
3. Anchor every change against the **Alsace reference numbers**:
   - edition self-check `MAX(appln_filing_date)` → **2025-09-23**;
   - both-vintage corpus → **78 companies / 396 families**; leader **HAGER ELECTRO SAS (63)**,
     KUHN SAS (38); depth distribution (1/2/3–4/5–10/10–20/20–50/>50) = **31/15/13/9/5/4/1**;
   - segmentation totals to 78.
4. When you change a query in the notebook, re-run its MCP equivalent and confirm the
   numbers still match before committing.

## Extending to another region
Discover the region's codes across both vintages (level-3 codes carry labels in
`tls904_nuts`; level-4 codes do not — `LEFT JOIN`, never inner-join), then list them all in
the notebook's `NUTS_CODES` parameter. Supported example countries: FR, IT, BE, DE, PL.

## Reference
- `docs/alsace-applicant-screening-methodology.md` — the reproducible recipe (both axes).
- `docs/philippe-vs-patstat-comparison.md` — method/scope/effort vs the INPI address-based approach.
- `docs/regional-analysis-guide-improvements.md` — the correctness fixes behind the non-negotiables.
