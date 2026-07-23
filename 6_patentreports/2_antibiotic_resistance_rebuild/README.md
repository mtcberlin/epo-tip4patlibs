# Antibiotic Resistance — clean rebuild

A clean, teachable rebuild of the antibiotic-resistance landscape report as a **four-step
pipeline** you can explain live in a workshop. See [`REBUILD_PLAN.md`](REBUILD_PLAN.md) for the
full plan and the locked decisions (D1–D7).

## Run order (all on EPO TIP — each queries PATSTAT PROD)

| # | Notebook | Produces |
|---|----------|----------|
| 1 | `1_dataset_and_search_strategy.ipynb` | the shared corpus `…_output/dataset.xlsx` + 2 charts |
| 2 | `2_core_landscape_analyses.ipynb` | the "who / where / when" battery — 10 charts (authorities, national trends, innovation waves, filing strategy, family size, top applicants, sectors, grant rate, top cited orgs) |
| 3 | `3_advanced_analyses.ipynb` | the IPC technology co-occurrence network |
| 4 | `4_assemble_report.ipynb` | `4_report/antibiotic_resistance_report.html` + `…_report_data.xlsx` |

Run 1 → 2 → 3 → 4 in order: each writes what the next reads, and notebook 4 assembles everything.

## How it fits together

Every analysis follows one shape: **a question (markdown) → one code cell that reads
`dataset.xlsx`, queries PATSTAT, builds one Plotly figure → `report_kit.record(...)`**, which
shows the figure inline and saves both the figure (as an inline HTML fragment) and the data behind
it. Notebook 4 collects all contributions from every `…_output/_report_parts/manifest.json`, orders
them, and stitches them into **one self-contained HTML report** (a single embedded plotly.js, no
iframes — so it renders inside TIP) plus **one data workbook** (one sheet per chart). The report has
**two view modes** switched by a header button: **Paged** (one chart at a time, step bar +
Previous/Next + ←/→ keys) and **One page** (all charts stacked). It is opened with the shared
`open_html()` button (`1_startwithtip/tip_tools.py`).

The small contract lives in [`report_kit.py`](report_kit.py).

## Status

The MVP spine is proven on TIP (dataset + a few charts + dual-mode report). **Phase 2** then filled
notebook 2 into the full core-landscape battery (10 charts). Notebook 3 (advanced) still holds the
technology network only — the remaining advanced analyses (temporal, citations, t-SNE, SDG, triadic)
are the next phase. Further analyses slot in by following the same `record` contract. The sibling
folder `../1_antibiotic_resistance/` is the current working version, kept untouched as the reference
until this rebuild reaches parity on TIP.

Notebooks are authored offline and **executed on TIP** (they cannot run without PATSTAT); outputs
are committed after a TIP run.
