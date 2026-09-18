# Provenance

Imported 2026-07-21 from `rickypriore/patlib-sessions`, commit `cd5a818`
("Add IPScore/NPV Planner material for Arne"). Author: Riccardo Priore (AREA Science Park).
Contains the post-`avgRev`-fix engine (verified against the IPScore 3.01 Excel test patents).
Basis for the PATLIB Warsaw 2026 workshop (ipscore topic); rework happens here.

Note: questionnaire texts and OEK value tables originate from the EPO IPScore tool —
EPO-coordinated PATLIB context, clarified by Arne 2026-07-21.

## Changes made on import (formal only — no tool content altered)

- `Dennemeyer_HTML_Tools_Builder.ipynb` → **`build_html_tools.ipynb`**; its title, the
  `/home/jovyan/Dennemeyer` assert message and two empty trailing cells were adjusted.
  Stored outputs untouched, no cell re-run.
- `BUILD_LOG.md`: scope note added, file inventory corrected to what this repo actually
  holds, stale pre-`avgRev`-fix NPV figures marked. His narrative is otherwise unchanged.
- `build/dist/` is no longer tracked in git — byte-identical to the promoted live files and
  recreated by `render.py`.
- `1_ipscore-and-npv.ipynb` is ours, not his: a course wrapper around his tools.

The five HTML tools, the Excel workbook, `build/data/`, `build/templates/` and all build
scripts are **unmodified** apart from two path comments. `verify_against_excel.py` passes
(all 3 Excel test patents + the planner demo, verified 2026-07-24).
