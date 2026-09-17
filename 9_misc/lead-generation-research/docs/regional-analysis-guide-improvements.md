# Regional-analysis Guide — Change Proposals

*All figures verified against PATSTAT Global Autumn 2025 (latest filing date 2025-09-23) via the depa.tech MCP. The guide's core mechanics are sound; below are correctness fixes (1–4), the key honest caveat (5), and robustness notes (6–8).*

### 1. Region filter must span both NUTS vintages — *correctness*
§3.4/§3.5 filter with `SUBSTR(p.nuts,1,4)='FR42'`. But level-3 records carry the **old** codes (`FR421/FR422`) and level-4 (REGPAT) records carry the **current** codes (`FRF11/FRF12`) — so the prefix drops every level-4 record even though the query asked for `nuts_level IN (3,4)`.
*Evidence:* Alsace companies 2017–2022 — old filter **52 firms / 280 families**, vintage-complete filter **78 / 396** (KUHN 38 not 7; LIEBHERR COMPONENTS COLMAR, 15 families, missing under the old filter).
*Fix:* enumerate the region's codes across both vintages; never truncate one prefix.
```sql
AND (p.nuts LIKE 'FR421%' OR p.nuts LIKE 'FR422%'
  OR p.nuts LIKE 'FRF11%' OR p.nuts LIKE 'FRF12%')
```

### 2. Don't inner-join `tls904_nuts` to resolve a region — *correctness*
The label table holds one vintage only (`FR42/FR421/FR422`; `FRF*` absent), so `JOIN tls904_nuts ON n.nuts = SUBSTR(...)` silently drops current-vintage records.
*Fix:* `LEFT JOIN`; treat an unmatched code as "resolve", not "discard".

### 3. `appln_kind` is space-padded — TRIM it — *correctness*
Values are length-2 (`'A '`, `'U '`, `'T '`), so `appln_kind='A'` matches nothing and returns an empty result.
*Fix:* always `TRIM(appln_kind)='A'`.

### 4. Counting "national-only" filings: exclude `T` and `U`
`appln_auth='DE'` families include `T` (national validations of granted EP patents — they always carry an EP member) and `U` (utility models — no EP route exists). Both distort EP-coverage shares in opposite directions.
*Fix:* restrict to `TRIM(appln_kind)='A'` for genuine national patent applications.

### 5. Add a "coverage reality" box — what a NUTS screen can and cannot see — *the key caveat*
NUTS geocoding is assigned only on the **EP/PCT route** (EPO at level 3, OECD REGPAT/PCT at level 4); purely national filings carry no NUTS. A NUTS region filter therefore returns the **EP/PCT-active subset** of a region, not its full applicant population.
*Evidence (Autumn 2025):* genuine German patent families (`TRIM(appln_kind)='A'`, 2017–2022) = **315,422**; only **21% have an EP member** → **78.6% no EP, 69.6% no EP/PCT, 42.7% purely domestic**. At applicant level **~77% of DE company applicant records have no NUTS** (≈78% FR, ≈81% GB; US has no NUTS at all). The postcode fallback does **not** recover them: `tls226.zip_code` is empty for FR and DE; an address is present for only ~3–7% of the no-NUTS records; at best a `city` string for ~25%. (UK postcodes are alphanumeric, so a numeric-postcode regex returns nothing.)
*Suggested box near §3.1:*
> A NUTS region filter returns the **EP/PCT-active subset** of a region's applicants. Roughly 70% of national (e.g. DPMA) patent families never take the EP/PCT route and carry no NUTS — typically the smaller, locally-filing companies a PATLIB most wants to reach. PATSTAT cannot recover them by postcode (the structured field is empty; addresses are sparse). For the full regional population, add national-office data (DPMA/DEPATISnet, INPI) or external city→region enrichment.

### 6. Flag `han_name` splits at the profiling hand-off
At population scale `han_name` leaves group/legal-form splits (KUHN SAS + KUHN SA; HAGER ELECTRO + HAGER CONTROLS; three LIEBHERR entities) that distort ranking and tiering. Consolidate via `doc_std_name_id`/`psn_id` before tiering; cross-reference the harmonisation guide.

### 7. Distinguish window semantics
`appln_filing_year BETWEEN …` = *active in window*. For families *originating* in the window (a priority cohort), anchor on the earliest `appln_filing_date` per `docdb_family_id`.

### 8. Refresh the edition footer + add a self-check
Footer says "Spring 2025"; live data is Autumn 2025. Add: `SELECT MAX(appln_filing_date) FROM tls201_appln WHERE appln_filing_year BETWEEN 2024 AND 2026;` → `2025-09-23`.
