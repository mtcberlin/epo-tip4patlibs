# Regional Lead Generation — brief for working with an AI

*Module 5 of TIP4PATLIBS. This document is for **workshop participants**: paste it into an
AI assistant (Claude, ChatGPT, …) together with the notebook you are looking at, and the AI
has enough context to explain, adapt, or extend what the two notebooks do. It is a
**map of the method**, not a step list — the notebooks themselves are the runnable product.*

> Written in English because the workshop serves PATLIB staff across Europe. Everything here
> describes code you can read: the two notebooks in this folder and the `dpma/` helper package.

## What the module produces

For a **region**, the **company patent applicants based there**, profiled and segmented into
lead tiers a PATLIB can act on. Two notebooks, because a region's applicants come in two
populations that live in different data:

| Notebook | Population it finds | Data source | Runs on |
|---|---|---|---|
| **`1_regional-leads.ipynb`** | the **EP/PCT-active** companies of a region (they carry a NUTS code) | PATSTAT (TIP) | TIP only — no extra credentials |
| **`2_national-coverage.ipynb`** | the **national-only tail** (DE companies that never took the EP/PCT route, so PATSTAT has no NUTS for them) | PATSTAT **+** DPMAconnect Plus register | TIP + DPMA credentials |

**Why two.** A NUTS region filter in PATSTAT returns *only the EP/PCT-active subset* of a
region — NUTS is attached on the European/PCT route only. Roughly **70 % of German national
patent families never take that route** and carry no NUTS; about **77 % of company applicant
records have no NUTS at all**. Those are typically the smaller, locally-filing SMEs a PATLIB
most wants. Notebook 1 finds the internationally-minded filers; Notebook 2 recovers the
national-only tail and **unions the two into one regional lead list**.

## Where things run (important for an AI helping you)

- **Inside EPO TIP**, PATSTAT is reached with the TIP data library — no BigQuery, no MCP:
  ```python
  from epo.tipdata.patstat import PatstatClient
  patstat = PatstatClient(env='PROD')                 # PROD = full production DB
  df = pd.DataFrame(patstat.sql_query(sql, use_legacy_sql=False))   # standard SQL
  ```
  Keep SQL to portable standard-SQL constructs (`CASE … WHEN`, `COUNT(DISTINCT …)`, `TRIM`,
  `SUBSTR`, `LIKE`) so it runs unchanged through `sql_query`. Data edition: **PATSTAT Global,
  Autumn 2025** (latest filing date ≈ **2025-09-23**).
- **DPMA** (Notebook 2 only) is reached through the local `dpma/` helper package. It needs a
  **DPMAconnect Plus** account. Credentials are read from the environment (`DPMA_USER` /
  `DPMA_PASS`) — on TIP put them once in `~/.secrets/patlibs.env`, which is loaded into every
  kernel automatically (see the note at the top of Notebook 2). Never commit credentials.

---

## Notebook 1 — EP/PCT-active regional leads (PATSTAT)

Two axes, then a grid.

1. **Portfolio depth** — patent *families* per company (how much it files).
2. **Geographic reach** — which economic zones those families cover (how far it protects).

Segmented into **neutral tiers** — depth (small/medium/large) × reach (local/regional/global) —
so a PATLIB sees which regional firms are worth approaching, and how.

### Method non-negotiables (get these wrong and the numbers are wrong)

- **Backbone join:** `tls206_person → tls207_pers_appln → tls201_appln`.
- **Applicants only:** `pa.applt_seq_nr > 0` (not inventors).
- **Families, never applications:** `COUNT(DISTINCT a.docdb_family_id)` — one invention filed
  in ten countries counts once.
- **Companies only:** `p.psn_sector = 'COMPANY'` (excludes universities/individuals; also the
  GDPR-safe choice).
- **Region across BOTH NUTS vintages.** PATSTAT stores two vintages side by side, and a region
  has a *different code in each*: older **level-3** codes (labelled, e.g. Alsace `FR421`/`FR422`)
  **and** current **level-4** REGPAT codes (unlabelled, `FRF11`/`FRF12`). Match every code with
  `nuts LIKE '<code>%'` and select `p.nuts_level IN (3,4)`. **Never** truncate one prefix with
  `SUBSTR(nuts,1,4)` — that silently drops every level-4 record (Alsace: 52/280 → **78/396**
  once both vintages are in). Level-3 codes carry labels in `tls904_nuts`; level-4 do not, so
  **`LEFT JOIN`** that table, never inner-join.
- **`appln_kind` is space-padded — always `TRIM` it** (`appln_kind = 'A'` matches nothing).
  The **regional corpus deliberately does *not* filter `appln_kind`** — family-level
  `COUNT(DISTINCT docdb_family_id)` already collapses each company's filings to families, and
  the verified 78/396 reference is counted without a kind filter.
- **Reach across all family members:** join back to `tls201_appln` on `docdb_family_id` and
  read `appln_auth` for **every** member, not just the regional filing. Zones: North America
  (US, CA), Asia (CN, JP, KR, IN, TW, SG, IL), Oceania (AU, NZ). EP/WO is the route almost
  everyone here uses, so the signal is whether a portfolio also reaches *beyond* Europe.
- **Window:** filing years (default 2017–2022) = *active in window*.

### Reference numbers to anchor a rebuild
Default example **Alsace (FR42), 2017–2022** reproduces:
- edition self-check `MAX(appln_filing_date)` → **2025-09-23**;
- both-vintage corpus → **78 companies / 396 families**; leaders **HAGER ELECTRO SAS (63)**,
  **KUHN SAS (38)**; depth distribution (1 / 2 / 3–4 / 5–10 / 11–20 / 21–50 / >50) =
  **31 / 15 / 13 / 9 / 5 / 4 / 1**; the segmentation grid totals back to **78**.
- Region-swap check: **Saxony (`DED`), 2017–2022 → 287 companies / 920 families**, led by
  NOVALED GMBH (155). German codes are stable across vintages, so a whole Bundesland is a
  *single* prefix; France needs all four codes.

---

## Notebook 2 — the national-only tail (PATSTAT + DPMA register), Germany

Notebook 1's honest caveat — "we can't see the national-only filers" — is exactly what this
notebook fixes for Germany. The address is a **company** attribute, so it's **one register
lookup per firm**, not per application.

### The pipeline
1. **Population from PATSTAT** (one query, per harmonised applicant `psn_id`): DE **company**
   applicants for a filing year, patents **and** utility models — `appln_auth='DE'`,
   `TRIM(appln_kind) IN ('A','U')`, `psn_sector='COMPANY'`, `person_ctry_code='DE'`. For each
   firm it records filing count, an EP/PCT-family flag (`has_ep`), whether PATSTAT already has a
   German NUTS (`has_nuts`, from `nuts LIKE 'DE%' AND nuts_level>=3`), and one representative
   application number to resolve.
2. **Split:** `has_nuts = 1` → already geolocated (free, region from their PATSTAT NUTS);
   `has_nuts = 0` → **national-only**, needs the register.
3. **Resolve national-only via DPMA:** for each firm, one Aktenzeichen lookup by its
   representative `appln_nr`, read the applicant's **PLZ** straight from the hit. Capped at
   `MAX_RESOLVE` (default 200) so the workshop stays interactive; a small fraction won't resolve
   (city-only hits, ownership changes) and are skipped.
4. **PLZ → NUTS3 + Bundesland** via the bundled Eurostat crosswalk.
5. **Union & tier:** concatenate PATSTAT-geolocated firms (region from their NUTS3) with the
   DPMA-resolved national-only firms, filter to one Bundesland (`REGION`), rank — the same
   depth-oriented lead list as Notebook 1, now including the previously-invisible tail.
6. **The payoff:** it reports how many of a region's leads are national-only, i.e. what the
   PATSTAT-only view *misses*.

### The `dpma/` helper package (what the AI should know exists)
Importable as `from dpma import ...`. Ground truth is the code, not older design docs.

| Piece | What it gives you |
|---|---|
| `fetch.DpmaClient()` | authenticated REST client (Basic auth from `DPMA_USER`/`DPMA_PASS`). Key methods: `search_aktenzeichen(appln_nr)` → `list[Hit]` (the route the notebook uses); also `search(expert_query)`, `search_applicant(name)` (expert field is **`INH`**=Inhaber, *not* `pa`), `get_register_info`, `get_register_extract(date, period)` (bulk period extract). |
| `register_parser` | ST.36 XML → applicant rows. `parse_hit_applicant(text)` → `{name, plz, city, country}`; `parse_register_xml`, `iter_registrations_from_zip`, `applicant_rows` for bulk extracts. Targets `<applicants>` only (not inventors/agents); PLZ is the leading 5 digits of `<address-1>` (register merges PLZ+city, publishes no street). |
| `plz_nuts` | `map_plz(plz)` → `{nuts3, bundesland, …}`; `BUNDESLAND_BY_NUTS1` maps a NUTS1 (first-3-chars) prefix to a Bundesland name; `enrich_rows` batches it. 8 333 PLZ each map to exactly one of ~400 NUTS3 regions. |
| `dpma/data/…csv` | Eurostat GISCO PLZ→NUTS-2024 crosswalk (CC-BY-SA-4.0). |
| `dpma/samples/` | offline fixtures (single records + a mini-extract ZIP), company applicants only, for running without live access. |

### Reference numbers
Default **2023, Germany, patents + utility models**: ≈ **2,600** German company applicants,
≈ **2,100** already geolocated in PATSTAT, ≈ **500** national-only to resolve. Default
`REGION = "Bayern"`.

---

## Extending it (what participants typically ask the AI for)

- **Another region (NB 1):** in Step 2 set `COUNTRY` + broad `PREFIXES`, read off *all* NUTS
  codes it returns (both vintages), paste them into `NUTS_CODES` in Step 3, re-run. Example
  countries that work the same way: FR, IT, BE, DE, PL.
- **Another window:** change `YEAR_START` / `YEAR_END` (5–6 years works well).
- **Another country's national tail (NB 2):** the DPMA route is **DE only**. The analogous
  national office for France is **INPI**; the pattern (population → resolve address → PLZ/postcode
  → region → union) carries over, the client does not.
- **Tighter lead lists:** consolidate `han_name` splits (e.g. `HAGER ELECTRO` vs `HAGER
  CONTROLS`; `KUHN SAS` vs `KUHN SA`) via `doc_std_name_id` / `psn_id` before publishing a
  ranking — see the harmonisation material.
- **Scale beyond the workshop:** the full, country-wide cached PLZ→NUTS mapping belongs in a
  PATSTAT-MCP extension table (`de_applicant_nuts`) so any query can join it — design in
  `docs/patstat-mcp-de-nuts-extension-brief.md`.

## Honest caveats (keep these visible)
- **NB 1 sees only the EP/PCT-active subset** of a region — great for internationally-minded
  filers, blind to the national-only tail. That is *why* NB 2 exists.
- **GDPR:** companies only (`psn_sector='COMPANY'` / `<applicants>` only). Natural-person
  applicant addresses are personal data — do not store/display them.
- **NUTS vintage:** PATSTAT NUTS vs the Eurostat 2024 crosswalk can differ for a few recoded
  regions; align vintages before a strict code-level comparison.
- **DPMA register quirks:** no separate street/PLZ/city tags (merged in `<address-1>`); some
  firms won't resolve; `getPublikationsdaten_XML` is permission-denied for the workshop account,
  so the bulk route is `getRegisterabzuege`.

## Reference material in this folder
**Notebook 1 (PATSTAT method):**
- `docs/alsace-applicant-screening-methodology.md` — the reproducible recipe (both axes).
- `docs/philippe-vs-patstat-comparison.md` — method/scope vs the INPI address-based approach.
- `docs/regional-analysis-guide-improvements.md` — the correctness fixes behind the non-negotiables.

**Notebook 2 (national coverage / DPMA):**
- `docs/national-coverage-extension-dpmaconnect.md` — design rationale.
- `docs/national-coverage-dpma-implementation-summary.md` — what was built (note: the current
  notebook already implements the PATSTAT-join + union that this summary lists as "next steps").
- `docs/nuts-mappings.md` — PLZ→NUTS mapping detail.
- `docs/patstat-mcp-de-nuts-extension-brief.md` — the production hand-off (cached extension table).
- `dpma/README.md` — the helper package itself.

*For maintainers developing/verifying the SQL against live data via the patstat-mcp
(`execute_query` with `dry_run`, `get_guide('regional-analysis')`), the anchor numbers above
are the regression targets — re-run the MCP equivalent and confirm they still match after any
query change.*
