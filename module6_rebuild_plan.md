# Module 6 — Clean Rebuild Plan (Antibiotic Resistance landscape report)

**Goal (Arne's steer):** *not* to fix Riccardo's complicated steps, but to build a **clean,
teachable pipeline** that a workshop audience can follow — "here is how you get, in four
understandable steps, from a search strategy to the finished landscape report."

Riccardo's delivered notebooks (in `~/Downloads/TIP notebooks/`) are the **reference for the
analysis logic** — what each analysis computes, which table, which chart, which metric — **not
code we import or patch**.

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
   TIP** (Jupyter's `/files/` CSP sandbox disables JavaScript). Our assembler must **inline** the
   figures, matching the actual structure of the `MODERNIZED.html` we already have (inline plotly
   divs, self-contained).
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

```
6_patentreports/1_antibiotic_resistance/
  1_dataset_and_search_strategy.ipynb   ← the corpus (exists; the CLEAN logic, already reworked)
  2_core_landscape_analyses.ipynb       ← NEW: the "who / where / when" battery
  3_advanced_analyses.ipynb             ← NEW: networks, clustering, citations, SDG
  4_assemble_report.ipynb               ← NEW: narrative + inline figures → one self-contained HTML
  1_.../ 2_.../ 3_.../ 4_..._output/    ← one output folder per notebook (existing convention)
  report/antibiotic_resistance_report.html
```

Every analysis unit follows the **same teachable shape** so the workshop can explain it once:

> a markdown cell stating **the question** → one code cell that **reads `dataset.xlsx` → queries
> PATSTAT → builds one Plotly figure** → `fig.show()` inline → saves the figure as an **inline
> HTML fragment** (`fig.to_html(full_html=False, include_plotlyjs=False)`) into the step's output
> folder for Step 4 to stitch.

Step 4 concatenates the narrative + all fragments with a **single** plotly.js include → one
self-contained, TIP-renderable report. This is the modern structure done cleanly (no IFrame, no
timestamped filenames, no `nbconvert` post-step).

### The 13 report analyses → step assignment

| # | Analysis | Step | Reference notebook | Data access |
|---|---|---|---|---|
| 1 | Core dataset + IPC/stats | **1** | Patent_Analysis_CLEAN | builds corpus (ORM) |
| 2 | Geographic filing (national trends, innovation waves) | **2** | ⚠️ **no producer — rebuild** | dataset → ORM |
| 3 | International filing strategies | **2** | Filing_Strategy | dataset → ORM |
| 4 | Family size & global reach | **2** | Family_Dimension | dataset → ORM |
| 5 | Institutional sector (basic) | **2** | Sectors_Basic | dataset → ORM |
| 6 | Institutional sector (enhanced) | **2** | Sectors_Enhanced (`psn_sector`) | dataset → ORM |
| 7 | Grant rates | **2** | Grant_Rate | dataset → ORM |
| 13 | Most influential organisations | **2** | Top_Cited_Applicants | dataset → **BigQuery SQL** |
| 8 | IPC co-occurrence network | **3** | our current nb2 / Network_Analysis | dataset → ORM |
| 9 | Temporal co-occurrence | **3** | Temporal_Network | dataset → ORM |
| 10 | t-SNE clustering | **3** | tSNE_Analysis_NEW | dataset → ORM + sklearn |
| 11 | UN SDG mapping | **3** | SDG_Analysis | dataset → ORM |
| 12 | Forward citation network | **3** | FWD_Network | dataset → **BigQuery SQL** |

Note: our current notebook 3 also computes **triadic families** and an **authority breakdown** —
neither is one of the 13. Decision **D3** below: keep as a bonus or drop for a report-faithful set.

---

## What we already have vs. build fresh

- **Have (reusable, already clean):** Step 1 dataset; the co-occurrence logic (current nb2); the
  temporal logic and cluster-explorer (current nb3). These get *moved* into the new step
  structure, not rebuilt.
- **Build fresh (clean, from the referenced logic):** geographic (incl. the 2 missing charts),
  family size, sectors (basic+enhanced), grant rate, top organisations, SDG, forward citations,
  t-SNE, and **the Step-4 inline assembler**.
- **Two analyses use raw BigQuery SQL** (forward citations, top organisations) — the citation
  self-joins. Keep that; it is the honest tool for those. Everything else is ORM.

---

## Phasing (so there is always a working artifact)

1. **Phase 1 — prove the spine.** Finish Step 1, write the Step-4 inline assembler, and wire up
   the 2–3 analyses we already have (co-occurrence, temporal). End-to-end: dataset → a few
   figures → one self-contained report that renders in TIP. This validates the whole approach
   before mass-building.
2. **Phase 2 — Step 2 (core landscape):** geographic, family size, sectors, grant rate, top orgs.
3. **Phase 3 — Step 3 (advanced):** t-SNE, SDG, forward citations (+ co-occurrence/temporal moved
   in).
4. **Phase 4 — narrative & polish:** port Riccardo's PURPOSE / KEY RESULTS / KEY FINDING narrative
   (compute the numbers instead of hardcoding where cheap), consistent headers, dry-run on TIP.

An **MVP for the workshop** need not be all 13 — a strong subset (dataset + geographic + grant
rate + sectors + one advanced + assembled report) already tells the full story. Target the 13 as
the finished state.

---

## Division of labour

- **I author the notebooks clean and offline** (code, structure, narrative, the assembler).
- **They can only be executed/verified on TIP** — every analysis re-queries PATSTAT PROD; none is
  an offline replay. So Arne runs each phase on TIP; outputs are committed pre-executed.
- Reference notebooks stay in `~/Downloads/TIP notebooks/` (not shipped into the clean module).

---

## Open decisions

| # | Question | Recommendation |
|---|---|---|
| **D1** | Four-step chain (this plan) vs. Arne's "0_ foundation set" (Option 1)? | **Four-step** — the inventory shows the foundation is just the dataset; a 0_ set adds nothing |
| **D2** | Full 13 analyses now, or MVP subset first? | **MVP spine first (Phase 1)**, then fill to 13 |
| **D3** | Keep triadic families + authority breakdown (not in the 13)? | Keep **authority** (it is the geographic story); make **triadic** an optional bonus or drop |
| **D4** | Narrative: recompute the numbers, or reuse his text verbatim? | **Recompute where cheap**; reuse his prose for interpretation. Avoids stale/"fake" figures |
| **D5** | Do the file-reorg-style rename now, or build new notebooks alongside then retire the old 3? | **Build 2/3/4 fresh, then retire current nb3**; keep nb1 |
