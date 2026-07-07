# Plan — Regional Leads Workshop Notebook & Instructions (epo-tip4patlibs)

## ✅ STATUS: FULLY IMPLEMENTED
All four rounds delivered and merged to `develop` (PRs #11, #12, #13). Notebook tested live
on EPO TIP by the author — works as intended. A copy of this plan lives in the repo at
`5_lead_generation/docs/workshop-notebook-implementation-plan.md`.

## Context
`epo-tip4patlibs` is EPO Academy training material for PATLIB staff. On `origin/develop`,
the user has started a new module `5_lead_generation/` for **regional lead generation**:
profiling the company patent applicants based in a region along two axes — portfolio
**depth** (families) and geographic **reach** (jurisdiction zones) — then segmenting them
into lead-qualification tiers so a PATLIB knows which regional firms to approach.

The module already contains three **live-verified methodology docs** (Alsace/FR42 recipe,
Philippe-vs-PATSTAT comparison, regional-analysis guide fixes) but the two front-door
artifacts are still drafts:
- `regional-applicant-profiling-instruction.md` — still framed as an open task brief.
- `1_regional-leads.ipynb` — a bare skeleton (placeholder sections, one
  "paste SQL here" cell, empty scratch cells, a title typo).

Goal: (1) rework the instruction md, and (2) turn the notebook into a **self-contained
workshop training manual** — explanations + TIP-runnable SQL only (no BigQuery cells, no
MCP calls inside the notebook). We use the patstat-mcp *now, during authoring*, to design
and verify every query against live PATSTAT; the notebook ships only the verified SQL.

## Branch
Work on `claude/epo4patlibs-workshop-notebook-60r9u3`, based on latest `origin/develop`
(which holds the user's started files). Rebase/reset the working branch onto
`origin/develop` before editing so we build on their latest changes.

### Decisions (from user)
- **Instruction MD = development brief.** Its job is to let us *develop and verify the SQL*
  with Claude + patstat-mcp — the "how the workshop queries were built / how to re-derive
  and extend them" doc. Agent/dev-oriented, not a participant handout.
- **Notebook = participant-facing.** Shows PATLIB staff the *possibilities to find the EP
  applicants in their region*. Worked on Elsass/FR42 but **parameterized by NUTS code**:
  enter a different code → get that region's applicants.
- **Full 7-step methodology.** **Neutral tier labels** (no animal taxonomy).

## Deliverables
### A. `regional-applicant-profiling-instruction.md` (rewrite → development brief)
Reframe as the brief we use to build/verify the notebook SQL with Claude + patstat-mcp.
Cover: objective (produce the workshop's regional-applicant queries), the methodology
non-negotiables (family-based `COUNT(DISTINCT docdb_family_id)`, `applt_seq_nr>0`,
`psn_sector='COMPANY'`, NUTS across **both vintages**, `nuts_level IN (3,4)`,
`TRIM(appln_kind)='A'`), the two-axis + tiering approach, the coverage-reality caveat
(NUTS = EP/PCT-active subset only), how to verify against live data (dry-run cost, expected
Alsace numbers 78/396), and pointers to the three `docs/`. Keep it concise.

### B. `1_regional-leads.ipynb` (rebuild → participant manual)
Follow the repo's proven manual pattern (`1_startwithtip/2_getting-started-with-patstat.ipynb`).
Top of notebook: a `# --- CHANGE THIS ---` **NUTS_CODES** parameter block (default = the
four Alsace vintage codes) so a participant swaps in their own region. Structure:
1. Title/purpose header (fix "Integlligence" typo; audience = PATLIB staff, platform=TIP,
   example = Elsass/FR42, one-line framing "find the EP applicants in your region").
2. Setup cell (keep existing `PatstatClient` + `run_query`).
3. Edition self-check — `MAX(appln_filing_date)` (confirm Autumn 2025 / 2025-09-23).
4. NUTS-vintage discovery — why `SUBSTR(nuts,1,4)` drops level-4 records; how to find your
   region's codes across **both** vintages (Alsace: FR421/FR422 + FRF11/FRF12). Feeds the
   NUTS_CODES parameter.
5. Corpus + **Axis 1 (depth)** — ranked company applicant list with family counts
   (Alsace: 78 companies / 396 families; leader HAGER ELECTRO 63).
6. **Axis 2 (reach)** — families per jurisdiction zone per company across all family members.
7. **Segmentation** — depth × reach into **neutral tiers** (small/medium/large × local/
   regional/global), with a short note that this maps to lead-qualification priority.
8. **Coverage-reality** markdown box — NUTS = EP/PCT-active subset; ~70% national-only
   families invisible; postcode can't recover them; consolidation caveat (`han_name` splits).
9. "Try it yourself" — how to change NUTS_CODES / window for FR/IT/BE/DE/PL + region.

Each analytical step = markdown (**Why**) + parameterized SQL cell + **How to read this**.
All SQL verified live via patstat-mcp; adapt any BigQuery-only idiom for TIP if needed.

## Critical files
- `5_lead_generation/regional-applicant-profiling-instruction.md`
- `5_lead_generation/1_regional-leads.ipynb`
- Reference (read-only): `5_lead_generation/docs/*.md`, `1_startwithtip/2_getting-started-with-patstat.ipynb`

## Verification
- Run each SQL via `mcp__PATSTAT_MCP__execute_query` (dry-run first for cost) during
  authoring; confirm numbers match the docs (78 companies / 396 families for Alsace).
- `python3 -c "import json,nbformat"` load check on the notebook; ensure valid nbformat 4.
- Notebook contains no BigQuery client / no MCP calls — only `run_query(...)` on TIP SQL.

## Resolved (round 1)
1. Instruction-md → development brief (build/verify SQL with Claude+MCP).
2. Region → Elsass/FR42, parameterized by NUTS code.
3. Depth → full 7-step methodology.
4. Tiers → neutral labels.

## Round 1 status: DONE (committed 0dd0b2f, pushed to working branch)
Notebook + instruction reworked, all SQL live-verified, on
`claude/epo4patlibs-workshop-notebook-60r9u3`.

## Round 2 — follow-up from user review
User feedback: (1) add a **German Bundesländer** example list; (2) tables suffice — no
charts; (3) keep explanations *before* each cell (already the case — he will demo the
notebook, then send it + the docs to participants); (4) **open a PR to `develop` when done**.

### Verified (live, this round)
- German NUTS-1 prefixes `DE1`…`DEG` appear at **both** nuts_level 3 and 4 under the *same*
  prefix → a Bundesland is a **single prefix** `DEx%`, no dual-vintage needed (unlike FR
  where `FR42`→`FRF1`). Nice teaching contrast.
- Sachsen (`DED`) runs end-to-end through the corpus query → NOVALED GMBH (155), HELIATEK,
  INFINEON TECH DRESDEN, etc. Sensible.

### Changes to `1_regional-leads.ipynb`
- In **Step 2** (NUTS discovery) and/or **Step 3** (params): add a one-line note that some
  countries need both vintages (FR) while others need only one prefix per region (DE) — the
  discovery query is how you find out.
- Expand the **"Try it yourself"** section with two concrete starter blocks:
  - FR/Alsace (both vintages): `NUTS_CODES = ['FR421','FR422','FRF11','FRF12']`
  - **DE Bundesländer (single prefix each)** — full 16-row table of NUTS-1 codes:
    DE1 Baden-Württemberg, DE2 Bayern, DE3 Berlin, DE4 Brandenburg, DE5 Bremen,
    DE6 Hamburg, DE7 Hessen, DE8 Mecklenburg-Vorpommern, DE9 Niedersachsen,
    DEA Nordrhein-Westfalen, DEB Rheinland-Pfalz, DEC Saarland, DED Sachsen,
    DEE Sachsen-Anhalt, DEF Schleswig-Holstein, DEG Thüringen. e.g. `NUTS_CODES = ['DED']`.
- Regenerate via the scratchpad builder; keep nbformat validation + the offline
  no-BigQuery/no-MCP guard.

### Ship
- Commit to the working branch, push.
- Open a **PR → `develop`** (check for a PR template first; fill it in). Report the PR URL.

## Round 2 status: DONE — PR #11 merged into develop.

## Round 3 — pre-TIP-test hardening (proposed)
User is about to test on EPO TIP and asked for a confidence re-check. Re-verified: run_query
pattern, SQL dialect, and named-column access all match the repo's working TIP notebooks
(airbus). Only gaps below.

### Changes
1. **`1_regional-leads.ipynb`, segmentation cell (18):** replace the fragile
   `df_segments.pivot(...).reindex(...).fillna(0).astype(int)` with
   `pd.pivot_table(df_segments, index='depth_tier', columns='reach_tier', values='companies',
   aggfunc='sum', fill_value=0)` then `.reindex(index=[small,medium,large],
   columns=[local,regional,global], fill_value=0)`. Bulletproof across pandas versions and
   handles missing tier combos / empty regions gracefully. `.pivot` is the only Python
   construct not proven by an existing TIP notebook.
2. **`1_regional-leads.ipynb`:** add a one-line performance note near Step 3 —
   default Alsace is fast and free on TIP; a whole large Bundesland scans much more and may
   take longer.
3. **`regional-applicant-profiling-instruction.md`:** soften the `TRIM(appln_kind)='A'`
   "non-negotiable" wording — clarify it applies to the national-only *coverage* counting,
   not the regional applicant corpus (which matches the verified 78/396 without it).

### Ship (note: PR #11 is merged)
Per merged-PR policy, treat as a fresh change: `git fetch origin develop &&
git checkout -B claude/epo4patlibs-workshop-notebook-60r9u3 origin/develop`, apply the edits,
regenerate + validate the notebook, commit, push, open a **new PR → develop**.

### Cannot verify from here (no TIP access)
Exact pandas version; whether `sql_query` caps rows / times out on very large scans. Default
Alsace path is unaffected.

## Round 3 status: DONE — PR #12 merged into develop.
User tested the notebook live on EPO TIP: works perfectly.

## Round 4 — pre-workshop polish (approved; all four items, English kept)
Base on latest `origin/develop` (PR #12 merged → fresh branch per policy). Make **targeted
JSON edits** to the committed notebook (preserve existing cell ids → clean diff), not a full
builder regeneration.

### Verified live (this round)
- Named-leads per-company query (tier labels + reach cols) works; SPURGIN LEONHART = the
  single large×local firm (matches the grid). 
- Saxony `DED` 2017–2022 anchor: **287 companies / 920 families**, leader NOVALED GMBH (155).

### Changes
1. **Named-leads table (notebook, after Step 6 grid):** insert a markdown + code cell that
   runs the verified per-company query into `df_leads` (applicant, families, depth_tier,
   reach_tier, fam_north_america, fam_asia, fam_oceania), sorted by families desc; show
   `.head(20)` and a one-liner filter example (`df_leads[df_leads.depth_tier.eq('large') &
   df_leads.reach_tier.eq('global')]`). Update the segmentation "How to read this" cell to
   point at `df_leads` instead of "combine Step 4 and 5 manually".
2. **README:** fix the module-5 row description (currently copy-pasted from module 4) →
   regional lead generation (depth × reach → lead tiers).
3. **DE anchor (notebook, Try-it-yourself → Germany):** add expected Saxony numbers
   (287 companies / 920 families, NOVALED 155) as a known-good check for a live DE demo.
4. **Light language/clarity polish:** a few targeted markdown tweaks only — no full rewrite,
   English retained.

### Files
- `5_lead_generation/1_regional-leads.ipynb` (targeted JSON edits)
- `README.md`

### Verification & ship
- `nbformat.validate`; guard: no BigQuery/MCP in code cells; `df_leads` SQL == verified.
- Restart branch from `origin/develop`, commit, push, open **new PR → develop**.

## Round 4 status: DONE — PR #13 open, pushed. User approved merging it.
### Merge step (approved)
Merge **PR #13 → develop** via GitHub (merge_pull_request). Confirm develop tip then
advances past `d37f44d` to include the round-4 commit `5dbbe75`.
