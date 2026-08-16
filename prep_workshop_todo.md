# Workshop Preparation — open work

Working notes for the **PATLIB Warsaw workshop, 18 September 2026**. Goal: five topics, seven
modules, one consistent course. Modules 6 and 7 are Riccardo Priore's contributions, reworked here;
his repository (`rickypriore/patlib-sessions`) stays the upstream source.

---

## DONE · Module 6 file reorganisation (executed 2026-07-23, variant B)

Executed as decided: variant B, `0_inputs/`, MODERNIZED dropped, reorg first. One output
folder per notebook, prefix stripped. All 39 code-path references rewritten across the three
notebooks and verified — **0 old paths remain in code or markdown**; every read/link path
(10/10) resolves to a file on disk. `IPC_Rankings.xlsx` was never committed (write-only nb2
output) — its code path now points at `2_technology_network_output/` and it is created on the
next run. Notebooks stay valid and pre-executed (outputs preserved).

✅ **Resolved — the TIP re-run happened** (commit `47d30da`, *"Module 6: ship the assembled
report from a clean 1→2→3 run"*). Re-verified 2026-08-15: **zero** old path literals in the
three notebooks or in `report/antibiotic_resistance_report.html`, all 7 relative links in the
report resolve to files on disk, and no `/home/jovyan/` strings remain. Nothing stale here any
more.

<details><summary>The original warning (kept for the record)</summary>

⚠️ **Still requires a TIP re-run of 1→2→3.** Stored `print()` outputs and the links baked into
the already-generated `report/antibiotic_resistance_report.html` still show the *old* paths —
they only refresh when the chain is re-run on TIP. Until then the code is correct but those
committed artefacts are stale.

</details>

<details><summary>Original plan (for reference)</summary>

## PLAN · Module 6 file reorganisation (proposed — awaiting go)

**Problem.** The `output_*` folders are named after Riccardo's *old flat notebooks*
(`Patent_Analysis_CLEAN`, `Network_Analysis`, `Triadic_Families`, `tSNE_Analysis_NEW`), which no
longer map to our 1-2-3 chain. Worse, **notebook 3 writes into folders "belonging to" notebooks
1 and 2**, so folder ≠ notebook and nobody can tell which file comes from where. Every filename
also carries a redundant `Antibiotic_Resistance_` prefix inside a folder already called
`1_antibiotic_resistance/`.

**Goal.** One output folder per notebook, named exactly like the notebook, so a notebook and its
outputs sit adjacent when sorted. Strip the redundant prefix. Separate external inputs and the
final deliverable.

### Producer map (verified)

| Notebook | writes | reads (prerequisites) |
|---|---|---|
| `1_dataset_and_search_strategy` | `dataset.xlsx` (the seed), `dataset_highlighted.html`, `ipc_analysis.html`, `statistics.html` | — (queries PATSTAT) |
| `2_technology_network` | `ipc_cooccurrence.xlsx`, `ipc_rankings.xlsx`, `technology_legend.xlsx`, `technology_network.html` | nb1 `dataset.xlsx` |
| `3_additional_analyses_and_report` | 13 files: triadic (4), authority (3), cooccurrence-derived (3), cluster (3) | nb1 `dataset.xlsx`; nb2 `technology_legend.xlsx` + `ipc_cooccurrence.xlsx`; external `Antibiotic_Report_FINAL.html` |

### Target layout

```
6_patentreports/1_antibiotic_resistance/
├── 1_dataset_and_search_strategy.ipynb
├── 1_dataset_and_search_strategy_output/
│     dataset.xlsx  dataset_highlighted.html  ipc_analysis.html  statistics.html
├── 2_technology_network.ipynb
├── 2_technology_network_output/
│     ipc_cooccurrence.xlsx  ipc_rankings.xlsx  technology_legend.xlsx  technology_network.html
├── 3_additional_analyses_and_report.ipynb
├── 3_additional_analyses_and_report_output/
│     triadic_families_applicants.xlsx  triadic_applicant_ranking.xlsx
│     triadic_applicant_ranking_table.html  triadic_families_map.html
│     authority_breakdown.xlsx  intl_authority_totals.html  intl_authority_trend.html
│     raw_cooccurrence_with_year.parquet  temporal_pair_evolution.xlsx
│     relationship_change_heatmap.html
│     cluster_families.json  cluster_data.json  cluster_explorer.html
├── _inputs/                          # external — no notebook here regenerates these
│     Antibiotic_Report_FINAL.html    # 50 MB; nb3 Step 4 reads it
│     interactive_scatter.html        # from the un-imported t-SNE notebook; the report links it
│     cluster_dashboard.html          # same
│     patent_landscape_MODERNIZED.html # Riccardo's 13-analysis reference; the report links it
├── report/
│     antibiotic_resistance_report.html   # OUR assembled deliverable (Step 7)
└── PROVENANCE.md
```

### What it costs (why this needs a coordinated edit, not just `git mv`)

1. **Path rewrites in all three notebooks.** The 4 old folder names appear as literals ~31×
   total (CLEAN 11, Network 10, Triadic 5, tSNE 5) plus 3 folder constants (`CLEAN`, `NETWORK`,
   `TSNE`) in nb3's Step 7. Every read/write path must point at the new folder (and new filename
   if we strip the prefix). Scripted find-replace, then verify no old path remains.
2. **Cross-notebook reads must be repointed:** nb2→nb1, nb3→nb1+nb2.
3. **Re-run required on TIP afterwards.** The notebooks ship pre-executed; renaming on disk +
   in code leaves the *stored* outputs (print statements, and the links baked into the already
   generated `report.html`) pointing at old paths. They are only refreshed by re-running 1→2→3
   on TIP. Until then: code is correct for a fresh run, but committed HTML links are stale.
4. **`git mv`** for every file so history is preserved.

### Two variants

- **A — folders only (low risk):** move files into the three `_output/` folders + `_inputs/` +
  `report/`, keep filenames unchanged. Rewrite only the 4 folder names (~31 literals + 3
  constants). Smallest surface.
- **B — folders + strip `Antibiotic_Resistance_` prefix (tidier, recommended):** as A, plus
  lowercase/de-prefix filenames per the tree above. Roughly doubles the rewrite surface but
  gives the clean result the tree shows.

**Recommendation: B**, executed as one scripted pass with a full old→new map, then a single
verification (`grep` for any surviving `output_Antibiotic_Resistance_*` or `Antibiotic_Resistance_`
path in code), then re-run on TIP.

### Open questions before executing
- [ ] Variant A or B?
- [ ] `_inputs/` vs `0_inputs/` (leading `_` sorts *after* the numbered folders; `0_` forces it
      first) — cosmetic, your call.
- [ ] Is `MODERNIZED.html` a kept reference, or does our own `report.html` fully replace it? (It
      is currently *linked from* our report, so it stays until Step 7 stops referencing it.)
- [ ] Do this **before** the templating rebuild (§1) or after? Doing it first means the rebuild
      writes into the clean layout from the start — I'd recommend first.


</details>

---

## DONE · Module 7 preparation (executed 2026-07-24)

Module 7 is **demo-ready**. It is the one module that needs no PATSTAT, no database and no
internet: five self-contained HTML tools (an Excel model turned into a web page), launched
inside TIP through `open_html()` / jupyter-server-proxy. Verified on TIP that day:
`build/verify_against_excel.py` passes — all 3 Excel test patents (329,059.4284 / 4,361.2849 /
−4,686.3598) plus the planner demo (1,225,801.6019), exact to 4 decimals.

What was done:

- **Launcher outputs cleared.** A test run had baked a session-bound URL
  (`/user/<hub-id>/proxy/<port>/…`) into both code cells — dead for anyone else, and it carried
  the hub session id. The two launcher cells are the one place where "guest modules ship
  pre-executed" does not apply: their output is only valid inside the session that produced it.
- **Notebook text corrected.** It told the reader to press a *Fill demo* button that **does not
  exist**. Actual behaviour: `IPscore_EN_Demo.html` fills itself on load (`fillDemo()` in
  `DOMContentLoaded`) and lands on the results page; `NPV_Target_Planner_EN.html` starts empty
  and has a *"▶ Load worked example (NovaMed Diagnostics Ltd.)"* button on its Setup page.
  Both are now described as they behave. Also: the two conflicting CSP explanations merged, the
  dead `Session_Menu.ipynb` reference dropped, the verification claim made honest.
- **Tidied.** `build/dist/` untracked (byte-identical to the live files, `render.py` recreates
  it) and re-excluded in `.gitignore` after the `!7_ipscore/build/**` negation;
  `Dennemeyer_HTML_Tools_Builder.ipynb` → `build_html_tools.ipynb` with its
  `/home/jovyan/Dennemeyer` assert message fixed and two empty trailing cells dropped;
  `BUILD_LOG.md` scope-noted and its file inventory corrected to what this repo actually holds;
  `PROVENANCE.md` records every formal change. **No tool content was altered** and no cell of
  his was re-run.

⚠️ **Deliberately not done** — both change Riccardo's content, and he is being asked first:
neutralising the named commercial vendors, and rendering a blank English form. See §5.

---

## Guiding decision: show the whole chain, not just the last step

Riccardo's own framing is that only the **final step** — the finished report — needs
explaining. **We disagree, deliberately.** For a PATLIB audience the interesting question is
*"how do I get to a report like this for my own topic?"*, and the answer lives in the steps he
treats as prerequisites: **the search strategy is the actual professional skill**, and it was
the one thing invisible in the imported material.

Hence module 6 is now a three-part chain, each part feeding the next:

| Notebook | Answers | Produces |
|---|---|---|
| `1_dataset_and_search_strategy.ipynb` | *How is the corpus defined?* Keywords **AND** classifications; ambiguous acronyms (MRSA/VRE/ESBL) deliberately excluded; one representative publication per family (EP > WO > US) | `Antibiotic_Resistance_Dataset.xlsx` (3,974 families) |
| `2_technology_network.ipynb` | *Which technology fields co-occur?* | `Technology_Legend.xlsx`, `IPC_Cooccurrence.xlsx`, `IPC_Rankings.xlsx` |
| `3_additional_analyses_and_report.ipynb` | Triadic families, filing authorities, cluster explorer, IPC evolution — **and** the report assembly (Step 7) | the assembled report + `output_*` artifacts |

**Done:** notebooks 1 and 2 imported from upstream, TIP absolute paths
(`/home/jovyan/training/Patlib Sessions/…`) rewritten to relative, branded headers added,
all three numbered. *(Remaining `/home/jovyan` strings sit only in stored `print()` outputs
and disappear on the next run.)*

---

## TODO

### 1. Templating / report assembly — rebuild it ourselves

> **Decision: we do not ask Riccardo.** The templating script stays unavailable; we
> reconstruct the assembly from what is already in the repo. Everything needed is there.

**Status (2026-07-24): route B taken, and the work has moved.** This section is no longer the
live plan — module 6's rebuild is now tracked in
[`6_patentreports/2_antibiotic_resistance_rebuild/REBUILD_PLAN.md`](6_patentreports/2_antibiotic_resistance_rebuild/REBUILD_PLAN.md),
which carries the session log and the locked decisions D1–D8. Where the two disagree, that
file wins.

Three folders now sit side by side in `6_patentreports/`:

| Folder | What it is |
|---|---|
| `1_antibiotic_resistance/` | the imported version, formally reworked — reference, kept untouched |
| `2_antibiotic_resistance_mvp/` | **frozen** minimal pipeline (4 notebooks, 5 charts, assembled report) — the guaranteed-to-run walkthrough. Do not extend |
| `2_antibiotic_resistance_rebuild/` | the full clean build: `report_kit.py` contract, Phase 2 done (13-chart report, paged ⇄ one-page toggle). Phase 3 = the remaining advanced analyses |

The analysis that led there is kept below for reference.

<details><summary>Original route analysis (superseded by REBUILD_PLAN.md)</summary>

#### What the target actually contains

`…_MODERNIZED.html` (2.4 MB) is **13 analyses**. Notably it has **20 live plotly charts and
zero base64 images** — Riccardo re-generated the charts as real plotly for this version,
unlike `Antibiotic_Report_FINAL.html` (50 MB, ~199 static PNGs). That is why it is 20× smaller,
and it means the modern report is **chart data, not screenshots** — worth preserving.

| # | Analysis | Source available to us? |
|---|---|---|
| 1 | Core patent dataset identification | ✅ notebook 1 |
| 2 | Geographic filing patterns | ❌ no notebook |
| 3 | International filing strategies | ✅ notebook 3, Step 3 |
| 4 | Patent family size & global reach | ❌ no notebook |
| 5 | Institutional sector (basic) | ❌ no notebook |
| 6 | Institutional sector (enhanced) | ❌ no notebook |
| 7 | Patent grant rates | ❌ no notebook |
| 8 | IPC/technology co-occurrence network | ✅ notebook 2 |
| 9 | Temporal co-occurrence patterns | ✅ notebook 3, Step 6 |
| 10 | Technology clustering (t-SNE) | ⚠️ upstream `…_tSNE_Analysis_NEW.ipynb`, not imported |
| 11 | UN SDG mapping | ⚠️ upstream `…_SDG_Analysis.ipynb`, not imported |
| 12 | Forward citation network | ❌ no notebook |
| 13 | Most influential organizations | ❌ no notebook |

**Seven analyses have no notebook anywhere** — not in his repo either. They came from the
master notebook behind `Antibiotic_Report_FINAL.html`, which was `nbconvert`-exported and never
committed. This is the same gap as the Virology report upstream.

#### Two routes — recommendation: mostly B

**A · Extract the rendered content** from `Antibiotic_Report_FINAL.html`, the way notebook 3's
Step 4 already extracts cluster assignments from an embedded chart. Mechanical, exact, no
re-computation — but it inherits the static PNGs and produces a report we cannot regenerate
from data.

**B · Recompute the missing seven as notebook code.** They are all standard patent analytics,
and **we already have the recipes documented at code level** from his Fuel Cells suite in
`_docu/02_analysis_recipes.md` (branch `herrkrueger`, upstream repo):

| Missing analysis | Documented recipe |
|---|---|
| Grant rates (7) | Recipe 2 — `granted == 'Y'` per applicant, stacked bar |
| Family size / reach (4) | Recipe 7 — `docdb_family_size` mean by country/year |
| Institutional sector (5, 6) | Recipe 3 + the `psn_sector` priority logic from `Genome-ranking_titolari` |
| Forward citations (12) | Recipe 10 — the ORM-select / BigQuery-join hybrid |
| Most influential orgs (13) | Recipe 3 — `func.count(func.distinct(docdb_family_id))` |
| Geographic patterns (2) | Recipe 1 — `groupby(appln_auth, year)`, choropleth |

Route B makes module 6 **fully reproducible from a PATSTAT query**, which is the entire point of
showing the chain. It is more work, but it is exactly the work that turns the module from a
display piece into a teaching artifact.

- [x] Decide the split: recompute the seven (B), and keep A only where re-computation is
      disproportionate.
- [x] Extend Step 7 into the real assembler — **assembly stays in the notebook**, not in an
      external script. That was the original defect; do not reproduce it.
- [x] Keep charts as live plotly (as `…_MODERNIZED.html` does), not static images.
- [ ] End state: notebooks 1–3 produce the complete report with **no hidden step**.

</details>

### 2. Simplify and clarify
- [ ] Review the three notebooks end to end for redundancy — they were written independently
      and repeat setup/query boilerplate.
- [ ] Make the numbering visible *inside* each notebook (which part, what it needs, what it
      hands on) so the chain is obvious when opened standalone.
- [ ] Consider whether the two legacy artifacts (`Antibiotic_Report_FINAL.html` 50 MB,
      `…_MODERNIZED.html` 2.4 MB) should stay once our own assembled report is complete.
      `Antibiotic_Report_FINAL.html` is still **required** — notebook 3 Step 4 reads the cluster
      assignments out of its embedded chart.

### 3. Display convention — results inside TIP, no downloads
The point of the rework: Riccardo's model writes standalone HTML you must download.
**Ours should show results in TIP.** Four tiers, in order of preference:

| Tier | For | Mechanism | Status |
|---|---|---|---|
| 1 | Plotly charts | `fig.show()` inline | ⬜ 4 charts in notebook 3 still write-only |
| 2 | Tables | `itables` inline instead of hand-built DataTables HTML | ⬜ blocked: is `itables` on TIP? |
| 3 | Finished HTML tools | serve via `jupyter-server-proxy` (`tip_tools`) | ✅ done in module 7 |
| 4 | Real apps | launcher pattern (PATSTAT Explorer) | ✅ established |

**Key constraint (verified on TIP):** an `IFrame` cannot work. JupyterLab resolves relative
`src` against the page URL, and Jupyter Server serves `/files/` with a **CSP sandbox that
disables JavaScript**. That is exactly why Riccardo links everything with `?download=1`.
The proxy route is the only way to get interactivity inside TIP.

- [ ] Verify `itables` availability on TIP → decides tier 2.
- [ ] Add `fig.show()` to the charts in notebook 3, re-run on TIP so outputs are stored.
- [ ] Once settled, write the convention into `CLAUDE.md` so all 7 modules stay consistent.

### 4. Optional — complete the picture
Two further upstream notebooks feed the *original* 13-analysis report but are not imported:
`Antibiotic_Resistance_tSNE_Analysis_NEW.ipynb` (the clustering) and
`Antibiotic_Resistance_SDG_Analysis.ipynb` (SDG mapping).

- [ ] Decide whether the t-SNE notebook should join the chain — notebook 3 currently reads the
      cluster assignments out of the published report instead of computing them, which is a
      deliberate correctness choice (the separate t-SNE run yields *different* clusters:
      3,840 vs 3,585 families). Importing it would need that discrepancy explained, not hidden.

### 5. Module 7 — open points, and what to ask Riccardo

**Direction, if module 7 gets the same MVP → Rebuild treatment as module 6:** the story stays
**patent valuation as content** — what a patent is worth, where it is weak, which action moves
the NPV. The Excel → web-tool build path stays a side note, closer to his original intent.
(The alternative — teaching the conversion recipe itself — was considered and set aside.)

#### ANSWERED · Riccardo, 2026-08-15 — all five, and four resolve to *no work*

Arne put the five questions to him. Net effect: **module 7 stays exactly as it is**, and the
two decisions this section had pre-recorded are **reversed** (no neutralisation, no blank EN
form). Only the attribution wording still needs a sentence when module 8 ships.

- [x] **What does he want to show on stage?** → **Antibiotics (module 6) and IPScore (module 7)**
      — his two inputs. Arne's rebuilds exist so they match the rest of the material in look,
      feel and structure; the content stays his. Both keep their slot.
- [x] **Are the named commercial vendors deliberate?** → **Yes, they stay.** Verified
      2026-08-15: EN names Dennemeyer 3×, CPA Global / Anaqua / IAM Market 1× each; IT adds
      LOT Network and IPH. ⚠️ **This reverses the earlier decision** ("neutralise EN and IT and
      re-render") — **do not touch the vendor names.** If it is ever reopened, the source is
      `7_ipscore/build/data/ipscore_questions_{en,it}.json` → `render.py --promote`, never the
      generated HTML.
- [x] **Is a rebuild acceptable, and how is attribution worded?** → **Yes, explicitly welcome**
      — he values the support. **Wording settled 2026-08-15:** *"created by Arne Krüger · model:
      EPO IPScore 3.01 · scenario analysis after Riccardo Priore's NPV Target Planner"*, in all
      four module-8 headers and the report footer. It names the EPO as the model's owner, keeps
      *created by Riccardo Priore* for modules 6 and 7 only, and credits by name the one idea
      module 8 did take from him. Full reasoning in `8_ipscore_rebuild/PROVENANCE.md`.
- [x] **Should there be a blank English form?** → **No — pre-filled is preferred**, by both
      Arne and Riccardo: you cannot ask a workshop audience for their company's turnover, cost
      and depreciation figures on the spot, so the tool has to arrive with a worked example.
      ⚠️ **This reverses the earlier decision** ("yes, plus a third launcher cell") — that cell
      is not built. *Applies to module 8 too: its deliverable ships pre-filled.*
- [x] **Does he want the IT versions maintained?** → **No.** English only for the course
      (confirms V6). His IT files are his own working copies and stay untouched in the repo.

#### Technical, independent of his answer

- [ ] **`build/smoke_test.js` is vacuous for the IPscore family** (verified 2026-07-24). All
      three IPscore files return `{"total":"0/200","vanTotal":"0 €"}` for the live *and* the
      regenerated file, because the DOM stub's `querySelector` always returns `checked:false`,
      so `updateResults()` reads zeros — "MATCH" compares 0 with 0. The NPV Planner test is
      real (€1,225,802). `verify_against_excel.py` is the binding check. Fix: make the stub
      remember radio state.
- [ ] Consider whether `build_html_tools.ipynb` belongs next to the course notebook at all, or
      should move into `build/` (needs its `Path.cwd()/"build"` assumption adjusted).

### 6. Before the release
- [ ] Dry-run all five topics against the clock (~8 min each). Module 7 has no query latency —
      it is the safe slot if the schedule slips.
- [ ] Re-sync with upstream (`git fetch` in `rickypriore/patlib-sessions`) — he commits actively.
- [ ] Release `develop` → `main`, then send Riccardo the link to both reworked modules,
      together with the questions in §5.

---

---

## Warnings — read before touching modules 6 and 7

Things that will bite silently if forgotten. Each was verified, not assumed.

1. **Do not "fix" notebook 3 Step 4 to compute clusters itself.** It deliberately reads the
   cluster assignments out of the published chart, because the separate t-SNE run yields
   **different clusters** — 3,840 vs 3,585 families (470/681/396/819/353/332/534). Recomputing
   would silently desynchronise the Cluster Explorer from the diagram it belongs to. Riccardo
   hit this as a real bug on 2026-07-17. If the t-SNE notebook is ever imported, that
   discrepancy must be *explained*, not hidden.
2. **`Antibiotic_Report_FINAL.html` (50 MB) cannot be deleted** while Step 4 exists — it is the
   source that step reads from.
3. **An `IFrame` can never display these HTML artifacts inside TIP.** Verified: JupyterLab
   resolves relative `src` against the page URL, and Jupyter Server serves `/files/` with a CSP
   sandbox that disables JavaScript. Riccardo's `?download=1` links are a workaround for the
   same constraint, not a stylistic choice. Use the proxy launcher (`tip_tools`).
4. **Guest modules ship pre-executed** — the stored outputs *are* the deliverable. Never
   "tidy" them by clearing or re-running without a working TIP session, or the module goes
   silently blank.
5. **`.gitignore` has a generic `build/` rule** that already swallowed Riccardo's entire
   IPScore pipeline once. A negated rule (`!7_ipscore/build/`) restores it — check any new
   folder with a conventional name against `git check-ignore` before assuming it was committed.
   Since 2026-07-24 a third rule re-excludes `7_ipscore/build/dist/` (regenerated output,
   byte-identical to the live files). Order matters: it must stay *after* the negation.
6. **Notebook 3's outputs are `print()` text only** — 17 stream outputs, zero rendered charts,
   because all four charts go to `write_html()`. "Pre-executed" therefore currently shows a
   reader almost nothing. This is the concrete reason for the display convention above.
7. **Leftover `/home/jovyan/…` strings** in notebooks 1 and 2 sit only in stored print output,
   not in code. They clear on the next TIP run — do not hand-edit them out of the JSON.
8. **Riccardo commits actively** (three substantive commits in two days). Re-sync before any
   large rework, and never edit his upstream files in place — his repo stays canonical.
9. **Module 7: never commit the launcher cells with outputs.** `open_html()` emits a URL
   containing the hub session id and an ephemeral port — valid only inside the session that
   produced it, dead for everyone else. Rule 4 (guest modules ship pre-executed) does *not*
   extend to launcher cells. Clear those two outputs before committing
   `7_ipscore/1_ipscore-and-npv.ipynb`.
10. **Module 7: the generated HTML is never hand-edited.** Change `build/data/*.json` or the
   `.j2` template and re-render via `render.py --promote`, then re-run
   `build/verify_against_excel.py` — an Italian apostrophe in a single-quoted JS string once
   killed an entire page silently, which is why the pipeline exists at all.

## Reference

- Full analysis of Riccardo's repository: `_docu/` on branch `herrkrueger` in
  `rickypriore/patlib-sessions` (local only — the remote branch was deleted).
- Attribution: IPScore is an **EPO tool**, ASP adaptation. Modules 6 & 7 credit
  *created by Riccardo Priore*.
- Guest-module conventions (pre-executed outputs, authorship in header): see `CLAUDE.md`.
