# Workshop Notebook — Implementation Plan & Log

**Status: ✅ fully implemented** (merged to `develop` via PRs #11, #12, #13). Jira: PIP-127.

*Record of how the `5_lead_generation` workshop notebook and its instruction brief were
built. The methodology itself lives in the sibling docs; this file is the build log.*

## Context
`epo-tip4patlibs` is EPO Academy training material for PATLIB staff. Module
`5_lead_generation/` teaches **regional lead generation**: profiling the company patent
applicants based in a region along two axes — portfolio **depth** (families) and geographic
**reach** (jurisdiction zones) — then segmenting them into lead-qualification tiers so a
PATLIB knows which regional firms to approach.

Two front-door artifacts were still drafts and needed reworking:
- `regional-applicant-profiling-instruction.md` — an open task brief.
- `epo_training_regional-leads.ipynb` — a bare skeleton (placeholders, one "paste SQL here"
  cell, a title typo).

**Goal:** rework the instruction into a development brief, and turn the notebook into a
self-contained **workshop training manual** — explanations + TIP-runnable SQL only (no
BigQuery cells, no MCP calls inside the notebook). The patstat-mcp was used *during
authoring* to design and verify every query against live PATSTAT; the notebook ships only
the verified SQL.

### Decisions (from the author)
- **Instruction MD = development brief** (agent/dev-oriented: how the SQL was built/verified).
- **Notebook = participant-facing**, worked on Alsace/FR42 but **parameterized by NUTS code**.
- **Full 7-step methodology**, **neutral tier labels** (no animal taxonomy), tables not charts,
  explanations *before* each cell, English throughout.

## Delivered artifacts
### `regional-applicant-profiling-instruction.md` (development brief)
The brief for building/verifying the notebook SQL with Claude + patstat-mcp: methodology
non-negotiables, the two-axis + tiering approach, the coverage-reality caveat, the
verification workflow with Alsace anchor numbers, and pointers to the three `docs/`.

### `epo_training_regional-leads.ipynb` (participant manual)
Follows the repo's proven manual pattern (`1_startwithtip/2_getting-started-with-patstat.ipynb`): title
header → `PatstatClient` setup → then per step, markdown (**Why**) + parameterized SQL cell
+ **How to read this**. A single `# --- CHANGE THIS ---` `NUTS_CODES` block (default = the
four Alsace vintage codes) lets a participant swap in their own region.

Steps: (1) edition self-check, (2) NUTS both-vintage discovery, (3) region + window params,
(4) Axis 1 depth (ranked company list + SME-pyramid distribution), (5) Axis 2 reach across
all family members, (6) neutral depth × reach segmentation grid **+ the named-leads
shortlist** (`df_leads`), (7) coverage-reality box. Plus a "Try it yourself" with FR (both
vintages) and a 16-row German Bundesländer table (single prefix each).

## Verified live against PATSTAT Global Autumn 2025
- Edition `MAX(appln_filing_date)` = **2025-09-23**.
- Alsace corpus (both vintages) = **78 companies / 396 families**; single-prefix vs
  both-vintage contrast 52/280 → 78/396; leader HAGER ELECTRO SAS (63), KUHN SAS (38);
  depth distribution 31/15/13/9/5/4/1; segmentation totals 78.
- German NUTS-1 prefixes `DE1`…`DEG` present at nuts_level 3 **and** 4 under the same prefix
  → a Bundesland is a single prefix (no dual vintage, unlike FR).
- Saxony (`DED`, 2017–2022) anchor = **287 companies / 920 families**, led by NOVALED GMBH (155).
- Notebook validated with `nbformat`; a guard confirms **no BigQuery/MCP calls in any code
  cell** — it runs purely through `PatstatClient.sql_query` on TIP.

## Build log
| Round | Scope | Ship |
|---|---|---|
| 1 | Rework instruction brief + rebuild notebook (7 steps, neutral tiers) | PR #11 ✅ merged |
| 2 | German Bundesländer example + NUTS-vintage note | PR #11 ✅ merged |
| 3 | Pre-TIP hardening: `pivot_table`, speed note, `appln_kind` wording | PR #12 ✅ merged |
| 4 | Named-leads shortlist (`df_leads`), Saxony anchor, reach-tier wording, README fix | PR #13 ✅ merged |

**Author tested the notebook live on EPO TIP after rounds 3 and 4 — works as intended.**

## Known limitations (carried into the notebook's Step 7)
- A NUTS filter returns only the **EP/PCT-active subset** of a region (~70% of national-only
  families carry no NUTS; postcode cannot recover them). Full population needs national-office
  data (INPI/DPMA) or city→region enrichment.
- `han_name` under-consolidates (group/legal-form splits); consolidate via
  `doc_std_name_id`/`psn_id` before a published ranking.

## Possible follow-ups (not yet done)
Second worked region as contrast; automated `han_name` consolidation; a screencast script.
