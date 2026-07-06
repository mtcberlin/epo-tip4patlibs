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
| `setup/` | Install helpers (e.g. Claude Code) |
| `harmonization/`, `ipc-extension/`, `context/`, `docs/` | Supporting analyses & material |
| `_bmad*`, `.claude/`, `.agent/`, `.gemini/` | Agent tooling (BMAD workflows) — not course content |

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

## Conventions
- Notebooks open with the branded red **TIP4PATLIBS** header (see
  `5_lead_generation/epo_training_regional-leads.ipynb`) plus a short table of
  contents. Keep new notebooks visually consistent.
- Ship a sensible default so a notebook runs out of the box (e.g. Alsace `FR42`
  in lead generation), with user-editable parameters near the top.
- Inside TIP, prefer PATSTAT (`env='PROD'`). The `*_bq.ipynb` variants are
  BigQuery ports and need separate credentials — not needed on TIP.
- Git: SSH remotes, do work on `develop`, open PRs into `main`.
