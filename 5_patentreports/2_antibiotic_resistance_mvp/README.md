# Antibiotic Resistance — MVP snapshot (frozen)

A **frozen snapshot** of the clean rebuild at its minimal, working milestone: a four-step
pipeline with **three analysis notebooks (five charts) + an assembled report**. Preserved
as a small, guaranteed-to-run walkthrough for the workshop — enough to show *how* you get
from a search strategy to a finished landscape report, without the weight of the full set.

> **Do not extend this folder.** The full build (~17 analyses + the paged/one-page report
> toggle) continues in the sibling **`../2_antibiotic_resistance_rebuild/`**. This copy stays
> as-is, so there is always a simple version that works.

## Run order (all on EPO TIP — each queries PATSTAT PROD)

| # | Notebook | Produces |
|---|----------|----------|
| 1 | `1_dataset_and_search_strategy.ipynb` | the shared corpus `…_output/dataset.xlsx` + 2 charts |
| 2 | `2_core_landscape_analyses.ipynb` | filing-authority charts (totals, WO-vs-EP trend) |
| 3 | `3_advanced_analyses.ipynb` | the IPC technology co-occurrence network |
| 4 | `4_assemble_report.ipynb` | `4_report/antibiotic_resistance_report.html` + `…_report_data.xlsx` |

Run 1 → 2 → 3 → 4 in order: each writes what the next reads, and notebook 4 assembles
everything. The folder ships **pre-executed** — the report opens without a re-run, so it can
be demonstrated offline.

## How it fits together

Every analysis follows one shape: **a question (markdown) → one code cell that reads
`dataset.xlsx`, queries PATSTAT, builds one Plotly figure → `report_kit.record(...)`**, which
shows the figure inline and saves both the figure (as an inline HTML fragment) and the data
behind it. Notebook 4 collects all contributions from every `…_output/_report_parts/manifest.json`,
orders them, and stitches them into **one self-contained HTML report** (a single embedded
plotly.js, no iframes — so it renders inside TIP) plus **one data workbook** (one sheet per
chart). The report is opened with the shared `open_html()` button (`1_startwithtip/tip_tools.py`).

The small contract lives in [`report_kit.py`](report_kit.py).
