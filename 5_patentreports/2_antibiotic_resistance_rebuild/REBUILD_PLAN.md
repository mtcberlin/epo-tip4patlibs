# Module 6 — Clean Rebuild Plan (Antibiotic Resistance landscape report)

**Goal (Arne's steer):** *not* to fix Riccardo's complicated steps, but to build a **clean,
teachable pipeline** that a workshop audience can follow — "here is how you get, in four
understandable steps, from a search strategy to the finished landscape report."

**Reference hierarchy (important).** The rebuild has two references, in this order:

1. **The current module `5_patentreports/1_antibiotic_resistance/` — the primary reference.** Its
   three notebooks **run successfully on TIP today**, end to end. However badly implemented or
   convoluted a given step may be, *it works* — it is executable ground truth for queries, data
   shapes and results. When in doubt, what the current module computes wins.
2. **Riccardo's delivered notebooks** (in `~/Downloads/TIP notebooks/`) — the secondary reference,
   for the analyses the current module does **not** contain (filing strategy, family size, sectors,
   grant rates, top orgs, SDG, forward citations, t-SNE).

Both are **reference only** — not code we import or patch.

> **Decisions locked (D1–D7, see table at the end).** D1 four-step chain · D2 MVP spine first but
> built to full-course quality from the start · D3 **keep every analysis** (nothing dropped) ·
> D4 **recompute all numbers** (we run on TIP — no query cost) · D5 **clean rebuild of all four
> notebooks** (his code is too dirty to carry over) · D6 exactly **four notebooks → one
> `report.html` + one `report_data.xlsx`**; his 50 MB `FINAL.html` is neither input nor deliverable
> of the rebuild, **QC/quality benchmarking only** · D7 the rebuild lives in the **sibling folder
> `2_antibiotic_resistance_rebuild/`** — the current module stays untouched as working reference.

> **Workshop constraint (from D2).** This is teaching material: **every code cell gets a short,
> plain-language markdown explanation directly above it** — what it does and why — so the room can
> follow live. Clean and teachable beats clever. This applies to all four notebooks.

---

## 📍 Where we are — session log (last updated 2026-07-23, end of day)

**Done and verified on TIP ✅**
- **MVP spine** — nb1 dataset (search strategy preserved, corpus identical) + 2 charts; nb3 the IPC
  co-occurrence network; nb4 the inline assembler → one self-contained `4_report/…report.html` +
  `…report_data.xlsx`, opened via the shared `open_html()` proxy button. Ran flawlessly on TIP.
- **E1 / D8 dual-mode report** — nb4 emits Paged (default) ⇄ One-page, header toggle remembered in
  `localStorage`, pure inline sections (no iframes). Verified on TIP.
- **Phase 2 — nb2 core landscape (10 charts, orders 210–290)** — authority totals/trend + national
  trends + innovation waves + national-vs-international + family size + top applicants + sectors
  (`psn_sector`) + grant rate + most-influential-orgs (BigQuery `tls228` forward citations). **Ran
  perfectly on TIP** (incl. the BigQuery cell). A NULL-`psn_sector` crash was caught offline and
  fixed before TIP.

**Folder layout now**
- `2_antibiotic_resistance_mvp/` — **frozen snapshot** of the proven 5-chart demo (Arne). Do not
  develop here; it is the safe fallback for the workshop.
- `2_antibiotic_resistance_rebuild/` — **the active rebuild** (this plan lives here). nb1 ✅, nb2 ✅
  (10 charts), nb3 = co-occurrence only (Phase 3 pending), nb4 ✅ dual-mode.

**Next up — Phase 3 (nb3 advanced), rows 11–17.** Not yet built:
- Temporal co-occurrence evolution (ref: current `1_antibiotic_resistance/` nb3)
- Backward citation network + temporal citation patterns (his report text-only → **add charts**; BigQuery)
- Forward citation network (ref: `FWD_Network`; BigQuery)
- t-SNE clustering (ref: `tSNE_Analysis_NEW`; ORM + sklearn)
- UN SDG mapping (ref: `SDG_Analysis`; ORM)
- Triadic families (ref: current nb3)
- Suggested report orders: continue the 300s (network already 310) → 320, 330, … Keep gaps.
- After nb3: re-run nb4 on TIP; both report modes should pick the new charts up automatically.

**How to resume (the working loop)**
1. `git pull` first — Arne runs notebooks on TIP and commits executed outputs; build on his real state.
2. Offline agent authors notebooks clean; **execution is TIP-only** (every analysis queries PATSTAT
   PROD). Author output-free, Arne runs each phase on TIP and commits outputs.
3. Extract reference logic with sub-agents (as in Phases 1–2) before authoring — faithful tables/
   columns/filters so numbers match. Reference notebooks: primary = `../1_antibiotic_resistance/`
   (runs on TIP); secondary = `~/Downloads/TIP notebooks/` (Riccardo's delivered originals).
4. **Never read raw `.ipynb`** — use `…/rickypriore/patlib-sessions/_docu/tools/nbsrc.py`.
5. Each analysis follows the `report_kit.record(order, slug, title, fig, data, output_dir, note)`
   contract; nb4 (`load_contributions`) stitches by `order`. Smoke-test pandas transforms offline
   before TIP. Branch `develop`; commit small; push when Arne needs it on TIP.

---

## What the inventory established (facts, verified)

1. **One shared corpus.** A single file `Antibiotic_Resistance_Dataset.xlsx` is built by the
   `Patent_Analysis_CLEAN` notebook (keyword AND IPC/CPC search). **Every other analysis reads
   that one file**, pulls `docdb_family_id` into a list, and re-queries PATSTAT for its own
   detail. → The pipeline chains cleanly from one foundation. (This is already our current
   notebook 1, `1_dataset_and_search_strategy`.)
2. **His report is pure layout.** Both the `ILLUSTRATED_Report` and the 53 MB `FINAL_Report`
   notebooks contain **zero computation** — every code cell is `IFrame('chart.html')` /
   `Image('x.png')`, then `nbconvert --to html --no-input`. His report-generator does not create
   information; it arranges pre-made chart files.
3. **`IFrame` is the fatal flaw.** That is exactly the approach we verified does **not render in
   TIP** (Jupyter's `/files/` CSP sandbox disables JavaScript). Our assembler must **inline** every
   figure (inline plotly divs, one plotly.js, self-contained) — **no iframe pages at all**. The
   current nb3 assembler still wraps its "doc"/"file" pages in iframes; those are precisely the ones
   that stay blank in TIP, and the clean rebuild removes them.
   - **Opening the finished report is already solved.** The self-contained HTML is opened with the
     shared helper **`open_html()` in `1_startwithtip/tip_tools.py`** (used today at the end of nb3):
     it serves the file through **jupyter-server-proxy** and shows a **red "Open" button** (+ a
     download fallback). That button is the *only* place a proxy is involved — it opens a finished
     file, it is not an iframe. **Step 4 must reuse `open_html`, not reinvent it.**
4. **Two charts have no producer** anywhere in his set: the *national-applications-trends bar*
   and the *innovation-waves* chart (report Analysis 2, Geographic). We rebuild those from
   scratch — standard analytics.
5. **`_executed` twins are code-identical** to their base notebooks (only stored outputs differ).
   We only need the base notebooks as reference.
6. The empty `Analisi_..._FINALE.ipynb` (0 bytes) — the report generator he made for us — **saved
   empty**. Nothing to recover there.

---

## Architecture — a clean four-step chain

Chosen over Arne's "Option 1 (a 0_ foundation set)" because the inventory proves the foundation
is simply **Step 1 (the dataset)** — there is no separate shared "set" beyond that one file, so a
straight 1→2→3→4 chain is both simpler and more teachable.

**The rebuild lives in a sibling folder** — the current, working module stays untouched as the
running reference until the rebuild reaches parity:

```
5_patentreports/
  1_antibiotic_resistance/                ← today's WORKING version — untouched, the reference
  2_antibiotic_resistance_rebuild/        ← the clean rebuild (this plan)
    1_dataset_and_search_strategy.ipynb   ← the corpus (same search strategy, re-authored clean)
    2_core_landscape_analyses.ipynb       ← NEW: the "who / where / when" battery
    3_advanced_analyses.ipynb             ← NEW: networks, clustering, citations, SDG
    4_assemble_report.ipynb               ← NEW: narrative + inline figures → one self-contained HTML
    1_.../ 2_.../ 3_.._output/            ← one output folder per notebook (same convention)
    4_report/
      antibiotic_resistance_report.html      ← the clean, self-contained landscape report (paged + one-page)
      antibiotic_resistance_report_data.xlsx ← consolidated data workbook, one sheet per chart
```

**How today's notebooks map into the new cut** (the new 2/3 are *not* today's 2/3):

| Today (works on TIP) | In the rebuild |
|---|---|
| 1 dataset & search strategy | new **1** (re-authored, same corpus) |
| 2 technology network | analysis row 10 in new **3** (IPC co-occurrence network) |
| 3 additional analyses + report | analyses → new **2**/**3** (triadic, authority, temporal, clusters); the assembler → new **4** |

**No `0_inputs/` in the rebuild (D6).** We regenerate everything ourselves — the dataset, every
chart, the clusters. Riccardo's prebuilt artifacts (`Antibiotic_Report_FINAL.html` 50 MB,
`interactive_scatter.html`, `cluster_dashboard.html`) stay where they are in `1_antibiotic_resistance/`
as part of the reference; the rebuild neither reads nor links them. His original report is a
**quality yardstick** only. Whether/when `1_antibiotic_resistance/` is retired is a separate
decision once the rebuild has proven itself on TIP.

Every analysis unit follows the **same teachable shape** so the workshop can explain it once:

> a markdown cell stating **the question** → one code cell that **reads `dataset.xlsx` → queries
> PATSTAT → builds one Plotly figure from a tidy dataframe** → `fig.show()` inline → saves **two
> things** into the step's output folder: the figure as an **inline HTML fragment**
> (`fig.to_html(full_html=False, include_plotlyjs=False)`), and **the exact dataframe behind the
> chart** (a small parquet/csv).

Step 4 then emits **two deliverables from the same per-analysis contributions**:

1. **`report/antibiotic_resistance_report.html`** — narrative + all figure fragments stitched with
   a **single** plotly.js include → one self-contained, TIP-renderable report (the modern
   structure done cleanly: no IFrame, no timestamped filenames, no `nbconvert` post-step).
2. **`report/antibiotic_resistance_report_data.xlsx`** — **one consolidated workbook, one sheet per
   analysis**, holding the exact data that each chart visualises.

This symmetry is a feature: **every chart in the report has a matching sheet in the workbook**.
It gives PATLIB staff the "show me the numbers" companion (which matches Riccardo's own
Excel-verification habit), makes the report auditable, and lets a client re-use the data without
touching TIP.

> **Clarification on the deliverables (D6).** The rebuild produces exactly two files: the lean
> `antibiotic_resistance_report.html` and the `..._report_data.xlsx`. Riccardo's 50 MB
> `FINAL.html` is **not** an input and **not** a deliverable of the rebuild — our t-SNE step
> recomputes its own cluster data from `dataset.xlsx`, so there is nothing to read out of his
> file. It stays in the reference module (and in his repo) purely as a **quality yardstick** we
> review against.

### ⚠️ There is no fixed "13-analysis spec" — his reports disagree

Reviewing against the delivered generator changed this materially. The `MODERNIZED.html` we had
(now deleted) and the `ILLUSTRATED_Report_CLEAN.ipynb` Riccardo delivered are **different report
generations**: MODERNIZED's Analysis 8/9 were *IPC co-occurrence* + *temporal co-occurrence*;
ILLUSTRATED's Analysis 8/9 are *backward citation network* + *temporal citation patterns*, and
**co-occurrence is not in ILLUSTRATED at all.** So there is no single report to reproduce.

**Conclusion (and it is exactly Arne's steer): we define our own coherent analysis set** — the
analyses that (a) have a real producer we can rebuild cleanly and (b) earn a chart — rather than
copy a drifting variant. We are **not** reproducing MODERNIZED byte-for-byte (it is deleted; no
match is expected).

His ILLUSTRATED report is also **chart-light**: of its 13 sections, only **9 embed a chart**;
four (family size, sector-basic, backward-citations, temporal-citations) are **text only**.

### The full set — keep everything (D3)

Arne's call: **keep every analysis that appears anywhere in his set**, and where his report was
text-only, **we add a chart + a data sheet** so the course is consistent. Nothing is dropped. This
is the target (full-course) state; the MVP in Phase 1 is a subset of exactly these.

| # | Analysis | Step | His report | Reference logic | Data access |
|---|---|---|---|---|---|
| 1 | Core dataset + IPC / statistics | **1** | ✅ | Patent_Analysis_CLEAN | builds corpus (ORM) |
| 2 | Geographic filing (trends + innovation waves) | **2** | ✅ but ⚠️ **no producer — rebuild** | — | dataset → ORM |
| 3 | International filing strategies | **2** | ✅ | Filing_Strategy | dataset → ORM |
| 4 | Family size & global reach | **2** | ✖ text-only → **add chart** | Family_Dimension | dataset → ORM |
| 5 | Institutional sector — basic | **2** | ✖ text-only → **add chart** | Sectors_Basic | dataset → ORM |
| 6 | Institutional sector — enhanced | **2** | ✅ | Sectors_Enhanced (`psn_sector`) | dataset → ORM |
| 7 | Grant rates | **2** | ✅ | Grant_Rate | dataset → ORM |
| 8 | Authority breakdown (intl. totals + trend) | **2** | ✅ | CLEAN authority tables | dataset → ORM |
| 9 | Most influential organisations | **2** | ✅ | Top_Cited_Applicants | dataset → **BigQuery** |
| 10 | IPC co-occurrence network | **3** | (MODERNIZED) | current nb2 logic | dataset → ORM |
| 11 | Temporal co-occurrence evolution | **3** | (MODERNIZED) | current nb3 logic | dataset → ORM |
| 12 | Backward citation network | **3** | ✖ text-only → **add chart** | — / BigQuery | dataset → **BigQuery** |
| 13 | Temporal citation patterns | **3** | ✖ text-only → **add chart** | — | dataset → ORM/BQ |
| 14 | Forward citation network | **3** | ✅ | FWD_Network | dataset → **BigQuery** |
| 15 | t-SNE clustering | **3** | ✅ | tSNE_Analysis_NEW | dataset → ORM + sklearn |
| 16 | UN SDG mapping | **3** | ✅ | SDG_Analysis | dataset → ORM |
| 17 | Triadic families | **3** | (nb3) | current nb3 logic | dataset → ORM |

Every row produces **one Plotly figure + one data sheet** (networks yield **two** sheets — nodes and
edges — see the workbook note). The four "add chart" rows are where we *improve* on his report rather
than copy it. Step assignment: Step 2 = the "who/where/when" battery (rows 2–9), Step 3 = the
advanced layer (rows 10–17).

---

## Build approach — all four notebooks fresh (D5)

His code is too dirty to carry over, so **everything is authored clean**, not moved. The reference
notebooks (his delivered set + our current imported nb2/nb3) tell us *what each analysis computes*;
we re-express each one in the single teachable shape, with an explanation cell above every code
cell.

- **Step 1** keeps the **same search strategy** (keyword AND IPC/CPC) so the corpus is identical —
  but is re-authored clean and fully explained. It is the one place we deliberately preserve logic
  (a different corpus would invalidate every downstream number).
- **Steps 2–4 are new.** Rows 2–9 → notebook 2; rows 10–17 → notebook 3; the inline assembler →
  notebook 4.
- **Four analyses use raw BigQuery SQL** (forward + backward citations, top organisations, temporal
  citations) — the citation self-joins. That is the honest tool for those; everything else is ORM.
- **The two missing-producer charts** (geographic trends + innovation waves) are built from scratch
  with standard analytics.

---

## Phasing (so there is always a working artifact)

0. **Step 0 — scaffold.** Create `5_patentreports/2_antibiotic_resistance_rebuild/` and move this
   plan into it. **Nothing is deleted** — `1_antibiotic_resistance/` keeps working untouched as the
   reference; its retirement is decided later, after the rebuild has proven itself on TIP.
1. **Phase 1 — prove the spine.** Re-author Step 1 clean, write the Step-4 inline assembler, and
   wire up 2–3 analyses end-to-end: dataset → a few figures → one self-contained report **that
   renders in TIP** + the matching `report_data.xlsx`. Validates the whole approach — including the
   teaching-cell shape — before mass-building.
2. **Phase 2 — Step 2 (core landscape):** geographic, filing strategy, family size, sectors
   (basic + enhanced), grant rate, authority, top orgs (rows 2–9).
   **Status: built offline ✅ (2026-07-23), pending TIP verification.** nb2 now holds 10 charts
   (orders 210–290): authority totals/trend (already verified), national filing trends + innovation
   waves (built from scratch — no producer), national-vs-international filing strategy, family-size
   distribution, top applicants by families, applicants by institutional sector (`psn_sector`),
   grant rate by top applicants, and most influential organisations (BigQuery forward citations —
   the reference's broken "missing country" filter dropped per D4). Reference logic extracted from
   the delivered notebooks; pandas transforms smoke-tested locally (a NULL-`psn_sector` crash fixed
   pre-TIP). **Next: Arne runs `2_core_landscape_analyses` on TIP; report the first failing cell if any.**
3. **Phase 3 — Step 3 (advanced):** co-occurrence, temporal co-occurrence, backward/forward/temporal
   citations, t-SNE, SDG, triadic (rows 10–17).
4. **Phase 4 — narrative & polish:** rewrite the PURPOSE / KEY RESULTS / KEY FINDING narrative with
   **recomputed** numbers (D4), consistent headers, embed plotly.js (offline-safe), dry-run on TIP,
   and the side-by-side quality check against his `FINAL.html`.

An **MVP for the workshop** need not be all 17 — a strong subset (dataset + geographic + grant
rate + sectors + one advanced + assembled report) already tells the full story. But every MVP cell
is authored to final quality (D2), so the MVP is a real slice of the finished course, not a throwaway.

---

## Division of labour

- **I author the notebooks clean and offline** (code, structure, narrative, the assembler).
- **They can only be executed/verified on TIP** — every analysis re-queries PATSTAT PROD; none is
  an offline replay. So Arne runs each phase on TIP; outputs are committed pre-executed.
- Reference notebooks stay in `~/Downloads/TIP notebooks/` (not shipped into the clean module).

---

## Decisions — locked ✅ (Arne, 2026-07-23)

| # | Question | Decision |
|---|---|---|
| **D1** | Four-step chain vs. a "0_ foundation set"? | ✅ **Four-step chain** (1→2→3→4). |
| **D2** | Full set now, or MVP subset first? | ✅ **MVP spine first**, but built to full-course quality — **every code cell gets a short plain-language explanation above it** (it's a workshop). |
| **D3** | Which analyses to keep? | ✅ **Keep everything.** Nothing dropped; text-only analyses get a chart + data sheet added. Target = the full 17-row set. |
| **D4** | Recompute numbers or reuse his text? | ✅ **Recompute all numbers** — we run on TIP, no query cost. His prose reused only for interpretation. |
| **D5** | Rename in place, or rebuild fresh? | ✅ **Clean rebuild of all four notebooks** (his code is too dirty). nb1 preserves only the search strategy so the corpus is identical. |
| **D6** | One report, or also a FINAL-style page? | ✅ **Four notebooks → one `report.html` + one `report_data.xlsx`.** His 50 MB `FINAL.html` is neither input nor deliverable of the rebuild — it is used **only for QC/quality benchmarking**. |
| **D7** | Where does the rebuild live? | ✅ **Sibling folder `2_antibiotic_resistance_rebuild/`** (Arne, 2026-07-23). The current `1_antibiotic_resistance/` stays untouched as the **working reference** — its three notebooks run on TIP today and are the primary reference (executable ground truth), Riccardo's delivered notebooks the secondary one. Retirement of the old module is decided after the rebuild proves itself on TIP. |
| **D8** | Report navigation for the growing chart set? | ✅ **Dual-mode report — Paged ⇄ One page, toggled in the header** (Arne, 2026-07-23). Default **Paged** (what worked in the demo). Built next by the offline agent, then handed to the TIP agent to verify both modes render. |

---

## Post-MVP enhancements

### E1 — Paged / One-page toggle in the assembler (D8)

**Why.** The MVP report is a one-pager: all chart sections stacked, scroll. Good for
scanning/export, but with the full ~17 charts a live workshop wants **one chart per view**
with Previous/Next — the model Arne liked in the old module. Build **both** into the one
self-contained report, switched by a header control; no second file.

**Reuse, don't reinvent.** The paging shell is already written and proven in the *old*
module: `1_antibiotic_resistance/3_additional_analyses_and_report.ipynb`, the Step-7
assembler cell. Lift its JavaScript/CSS. It already provides, verified on TIP:

- `show(i)` that hides all sections and reveals one (`section.hidden = …`)
- a **step bar** of buttons — here make each button carry the **chart title** (hover/tooltip
  or short label), not just a number, since 17 numbered buttons are unusable
- **Previous / Next** buttons and **←/→ arrow-key** navigation
- **lazy `Plotly.Plots.resize`** on reveal (a plotly div laid out while hidden has no size —
  this is essential, charts render blank without it)
- hash deep-linking (`#3`) so a page is shareable

**What changes vs. the old shell.** The rebuild report is **pure inline plotly divs** —
no iframes. Drop the old shell's `srcdoc`/`data-doc` iframe handling entirely; every page
is a local `<section>`. Add the **mode toggle**:

- **Paged** (default): wrap each contribution in `<section hidden>`; `show(0)` on load.
- **One page**: reveal every section (`hidden=false`), hide the Prev/Next + step bar, let
  the body scroll. A single header button flips between the two and remembers the choice
  (e.g. `localStorage`).

**Where it lives.** The assembler template in `4_assemble_report.ipynb` (Step that builds
`html` from `load_contributions()` entries). `report_kit.py` is unaffected — fragments and
manifest already carry `title`/`order`, which the step bar consumes directly.

**Testing handoff.** Offline agent edits the assembler; Arne re-runs `4_assemble_report`
on TIP (fast — the five fragments already exist, no PATSTAT queries); the finished report
comes back to the TIP agent to confirm **both** modes render inside TIP (paged switching,
one-page scroll, no blank charts, the `open_html` button still opens it). Validate on the
5-chart spine **before** the full set, so the navigation is proven small.

**Status: built offline ✅ (2026-07-23), pending TIP verification.** `4_assemble_report.ipynb`
Step 2 now emits the dual-mode report: paged default (numbered step bar with per-chart title
tooltips, Previous/Next, ←/→ keys, `Plotly.Plots.resize` on reveal, `#n` hash deep-links) plus a
header **Paged ⇄ One-page** toggle remembered in `localStorage`; pure inline sections, no iframes.
Validated offline against the real 5-chart fragments: structure correct (5 sections, one plotly.js,
5 plot divs, no iframes, default paged) and the embedded JS passes a Node syntax check. **Next: Arne
re-runs `4_assemble_report` on TIP and confirms both modes render.**
