# TIP4PATLIBs — Course Material

Training material for **PATLIB staff across Europe** to get the most out of the
**EPO Technology Intelligence Platform (TIP)** for patent analytics. The
notebooks are meant to be run by course participants top-to-bottom inside TIP's
JupyterLab.

Author: Arne Krüger (mtc.berlin / depa.tech) · License: **EPO Internal Use**.

## Repository layout
| Path | Module / purpose |
|------|------------------|
| `1_startwithtip/` | **Start here.** Set up Claude Code persistently (`1_getting-started-with-tip.ipynb`), then run your first PATSTAT queries (`2_getting-started-with-patstat.ipynb`) |
| `2_legacy/` | Earlier worked end-to-end examples (Airbus filing strategy, TU Dortmund portfolio) |
| `3_querylib/` | Query Library — ready-to-use PATSTAT queries |
| `4_patstat_explorer/` | Applicant & technology search notebook + app |
| `5_lead_generation/` | Regional lead generation — profile a region's EP/PCT applicants by portfolio depth × geographic reach, segment into lead tiers |
| `6_patentreports/` | Landscape reports (**Riccardo Priore**) — triadic families, filing authorities, t-SNE clusters, interactive explorer. Ships **pre-executed** (see below) |
| `7_ipscore/` | Patent valuation (**Riccardo Priore**) — EPO IPScore questionnaire → NPV; self-contained interactive HTML tools, opened via `open_html()` (jupyter-server-proxy), **never** via `IFrame` |
| `8_ipscore_rebuild/` | 🚧 Under construction (notebooks 1, 3 and 4 of 4 — only the PATSTAT evidence layer is left) — our own rebuild of the IPScore ideas as an explained notebook chain, adding a PATSTAT evidence layer. Engine in `ipscore_kit.py`, model data in `ipscore_spec.json`, deliverable in `4_tool/`, phasing in `REBUILD_PLAN.md`; module 7 stays untouched as the working reference |

The course is **modules 1–8 plus this file and `README.md`** — nothing else. Earlier
supporting folders (`setup/`, `harmonization/`, `ipc-extension/`, `context/`, `docs/`)
and the BMAD agent tooling (`_bmad*`, `.claude/`, `.agent/`, `.gemini/`) were removed
once no module referenced them any more; recover any of them from history with
`git checkout fdcf789 -- <path>`. Environment setup now lives entirely in
`1_startwithtip/1_getting-started-with-tip.ipynb`.

## Running notebooks on TIP
Connect to PATSTAT with the TIP data library (available in the base conda env):
```python
from epo.tipdata.patstat import PatstatClient
import pandas as pd
patstat = PatstatClient(env='PROD')                 # PROD = full production DB
df = pd.DataFrame(patstat.sql_query(sql, use_legacy_sql=False))
```
Data edition: **PATSTAT Global, Autumn 2025**. For the full TIP environment model
— what persists across restarts, the `epo.tipdata` venv gotcha, and the
persistent Claude Code + Git/SSH setup — see **`1_startwithtip/1_getting-started-with-tip.ipynb`**.

### The home directory is `/home/jovyan` — via a symlink
TIP uses `jovyan` as the base user; `/home/<your-username>` is a **symlink** to
`/home/jovyan`. Both paths are the same directory, but they are *different strings*, and
that breaks path arithmetic: `Path.home()` returns the unresolved `/home/<username>`
while `Path.cwd()` returns the resolved `/home/jovyan/...`, so
`Path.cwd().relative_to(Path.home())` raises `ValueError`. Use `Path.home().resolve()`,
or the `JUPYTER_SERVER_ROOT` env var (`/home/jovyan`) when you need a path relative to
Jupyter's root — e.g. to build a `/files/` URL.

## Conventions
- Notebooks open with the branded red **TIP4PATLIBS** header (see
  `5_lead_generation/1_regional-leads.ipynb`) plus a short table of
  contents. Keep new notebooks visually consistent.
- Ship a sensible default so a notebook runs out of the box (e.g. Alsace `FR42`
  in lead generation), with user-editable parameters near the top.
- Inside TIP, prefer PATSTAT (`env='PROD'`). The `*_bq.ipynb` variants are
  BigQuery ports and need separate credentials — not needed on TIP.
- Git: SSH remotes, do work on `develop`, open PRs into `main`.

### Guest modules 6 & 7 (Riccardo Priore)
Modules `6_patentreports/` and `7_ipscore/` are contributed material, reworked to
match this course's look. Two deliberate deviations from the conventions above:
- **They ship pre-executed** (outputs kept) — modules 1–5 clear outputs so
  participants run them; 6–7 are read as finished reports in a 90-min showcase.
- **The header credits `created by Riccardo Priore`**, not the repo author.

Never re-run or re-generate their code cells to "tidy" them — the outputs *are* the
deliverable. Each folder has a `PROVENANCE.md` naming the upstream repo and commit;
his repository stays the canonical source. IPScore is an **EPO tool** in an ASP
adaptation. The IPScore HTML tools are *generated* from JSON + Jinja2 templates —
edit the data or template and re-render, never the generated HTML.
