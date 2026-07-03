# Philippe's Alsace Profiling vs. the PATSTAT/MCP Reproduction

*Method, scope, effort — like for like. Figures verified on PATSTAT Autumn 2025.*

## What Philippe built (INPI Strasbourg)
A 2-D segmentation of Alsatian companies — **portfolio depth** (families over 5–6 years, oldest priority) × **geographic reach** (jurisdiction zones) — bundled into an animal taxonomy (Lobster → Lion) for lead qualification: approach the antelopes/hippos/zebras for IP training, invite the lions to speak. Population by applicant ZIP code from INPI data, with SIREN numbers and manual de-duplication. First version: an intern, ~6 months on Espacenet; later improved with Patstat data.

## What PATSTAT/MCP reproduces
**Both axes**, in a handful of parameterised queries: depth (the 78-company list) and reach (families per zone via `appln_auth` across the family members). The reach columns match the schema of Philippe's per-company master table — so the animal grid reads straight off the result.

## Comparison
| Dimension | Philippe | PATSTAT/MCP |
|---|---|---|
| Counting unit | families, oldest priority | families, filing-year-in-window |
| Population | all companies (ZIP) | EP/PCT-active subset (NUTS) |
| Consolidation | SIREN + manual | `han_name` (residual splits) |
| Country breadth | added via Patstat | full from the start |
| Reproducible, any region | no | yes |

## The decisive divergence — population *(verified)*
NUTS geocodes the **EP/PCT route only**. Measured: **~70% of German national patent families** (`TRIM(appln_kind)='A'`, 2017–2022) never take the EP/PCT route, and **~77% of DE company applicant records have no NUTS** (Alsace/FR comparable). So PATSTAT reproduces the **EP-active subset**, not the full population — the national-only filers (Philippe's lobsters) are invisible. The postcode route does **not** recover them inside PATSTAT (`zip_code` empty; addresses sparse). Philippe's INPI ZIP/SIREN coverage was a real, structural advantage; full-population reproduction needs national-office data (INPI/DPMA) or external city→region enrichment.

## Consolidation
SIREN + manual de-dup gave clean entities. `han_name` leaves group/legal-form splits (KUHN SAS + KUHN SA; HAGER ELECTRO + HAGER CONTROLS). Automated **population-scale** consolidation (`doc_std_name_id`/`psn_id`) — not per-named-entity — is the gap.

## On Philippe's two images
Image 1 is the aggregated animal grid (counts only). Image 2 is the **per-company master table** — its columns (`Total INPI/EP`, the continents, `EP_Dir`, `New`, the rolling-window tiers) **are** the geographic-reach axis, i.e. exactly the schema reproduced here, not an unrelated analysis. It is not a clean validation set (mixes regions, oldest-priority counts), so a controlled cross-check means re-running his exact ZIP-based, oldest-priority method.

## Effort — the honest pitch
Building this by hand from Espacenet took an intern ~6 months. The PATSTAT route returns the comparable top tier in a few queries for cents, rerunnable for any region — with the honest caveat that it covers the EP-active subset; the national-only tail is where the address-based method still wins, until national data is added.
