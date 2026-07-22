# Workshop Preparation — open work

Working notes for the **PATLIB Warsaw 2026** workshop. Goal: five topics, seven modules,
one consistent course. Modules 6 and 7 are Riccardo Priore's contributions, reworked here;
his repository (`rickypriore/patlib-sessions`) stays the upstream source.

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

**Status:** partly solved. Step 7 in notebook 3 assembles a one-file report
(`Antibiotic_Resistance_Report.html`, 5.6 MB) — but it currently carries only the triadic
ranking, not the full picture.

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

- [ ] Decide the split: recompute the seven (B), and keep A only where re-computation is
      disproportionate.
- [ ] Extend Step 7 into the real assembler — **assembly stays in the notebook**, not in an
      external script. That was the original defect; do not reproduce it.
- [ ] Keep charts as live plotly (as `…_MODERNIZED.html` does), not static images.
- [ ] End state: notebooks 1–3 produce the complete report with **no hidden step**.

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

### 5. Before the release
- [ ] Dry-run all five topics against the clock (~8 min each).
- [ ] Re-sync with upstream (`git fetch` in `rickypriore/patlib-sessions`) — he commits actively.
- [ ] Release `develop` → `main`, then send Riccardo the link to both reworked modules.

---

---

## Warnings — read before touching module 6

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
6. **Notebook 3's outputs are `print()` text only** — 17 stream outputs, zero rendered charts,
   because all four charts go to `write_html()`. "Pre-executed" therefore currently shows a
   reader almost nothing. This is the concrete reason for the display convention above.
7. **Leftover `/home/jovyan/…` strings** in notebooks 1 and 2 sit only in stored print output,
   not in code. They clear on the next TIP run — do not hand-edit them out of the JSON.
8. **Riccardo commits actively** (three substantive commits in two days). Re-sync before any
   large rework, and never edit his upstream files in place — his repo stays canonical.

## Reference

- Full analysis of Riccardo's repository: `_docu/` on branch `herrkrueger` in
  `rickypriore/patlib-sessions` (local only — the remote branch was deleted).
- Attribution: IPScore is an **EPO tool**, ASP adaptation. Modules 6 & 7 credit
  *created by Riccardo Priore*.
- Guest-module conventions (pre-executed outputs, authorship in header): see `CLAUDE.md`.
