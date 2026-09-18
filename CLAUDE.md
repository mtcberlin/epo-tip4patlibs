# TIP4PATLIBs — Course Material

Training material for **PATLIB staff across Europe** to get the most out of the
**EPO Technology Intelligence Platform (TIP)** for patent analytics. The
notebooks are meant to be run by course participants top-to-bottom inside TIP's
JupyterLab.

Author: Arne Krüger (mtc.berlin / depa.tech) · License: **EPO Internal Use**.

## Repository layout

Restructured 2026-09-17: **every module folder is self-contained** — its notebooks, its data,
its slide deck and its own copy of `tip_tools.py`. Nothing imports across folders, so a module
can be opened and worked in on its own.

| Path | Module / purpose |
|------|------------------|
| `install.sh` | **Start here.** One command replaces the old setup notebook: npm prefix, Claude Code, TIP context, status line, course dependencies, clone. Idempotent — safe to re-run after a TIP rebuild. Reads `CLAUDE.md.template` and `statusline-command.sh.template` from the repo root |
| `TIP4PATLIBS_1_Workshop_v4.pdf` | The workshop deck |
| `<module>/tip_tools.py` | `open_html()` — serves an HTML artifact through jupyter-server-proxy, **never** via `IFrame`. **Three byte-identical copies** (`4_patentreports/antibiotic_resistance/`, `5_ipscore/`, `9_misc/ipscore/`) so each folder imports it in one line. Change one, change all three — the file header lists them |
| `9_misc/handouts/` | The 45-minute written version of each module as A4 PDFs, plus `source/` (Markdown, YAML sidecars, `build_handouts.py`, `build_slides.py`, `build_shots.py`) |
| `1_querylib/` | Query Library — ready-to-use PATSTAT queries. Two engines, not duplicates: `TIP_for_PATLIBs_QueryLib_core.py` (the query-library UI) and `tip4patlibs_core.py` (analysis and charting) |
| `2_patstat_explorer/` | Applicant & technology search, notebook + app |
| `3_lead_generation/` | Regional lead generation. `dpma/` **must stay inside the module**: `2_national-coverage.ipynb` locates it by walking *up* from the notebook, so it has to be an ancestor |
| `4_patentreports/` | Landscape reports (**Riccardo Priore**) — `antibiotic_resistance/` plus his demo deck. Ships **pre-executed** (see below) |
| `5_ipscore/` | ✅ Complete — the course's own rebuild of the IPScore ideas with a PATSTAT evidence layer measuring 11 of the 40 answers (`2 measured · 6 informed · 32 judgement`). Starts at `0_questionnaire.ipynb`, Riccardo Priore's form (imported from `rickypriore/patlib-sessions@2a434f02`): it writes `0_questionnaire_output/questionnaire.json`, which `load_worked_example()` prefers over `worked_example.json` for notebooks 2–4, so a participant can value their own patent. Notebook 1 pins `kit.EXAMPLE_PATH` so it always reproduces the shipped case. Engine `ipscore_kit.py`, model data `ipscore_spec.json`, deliverable `4_tool/` |
| `9_misc/` | Everything that is not a course module — see below |

**The five modules are numbered 1–5 and the folder names match** (renumbered 2026-09-17). The old
module 1 (*setting up TIP*) became `install.sh` and its notebooks are archived in
`9_misc/legacy/startwithtip/`; the handouts moved to `9_misc/handouts/` because they are not a module.
The handout files are still named `01_`…`06_` internally — their headings carry the current numbers.

### What lives in `9_misc/`
| Path | What |
|---|---|
| `9_misc/plan/` | Session briefs and planning: `plan-tipsession-1-recon.md` (✅) · `plan-tipsession-2-evidence-run.md` (✅) · `plan-tipsession-3-screenshots.md` · `plan-workshop-warsaw.md` · `plan-course-material.md` · `results-tipsession.md` |
| `9_misc/legacy/` | Earlier worked examples (Airbus, TU Dortmund, Belgium) and `startwithtip/` — the original setup notebooks that `install.sh` replaced |
| `9_misc/ipscore/` | Patent valuation (**Riccardo Priore**) — the IPScore/NPV HTML tools, **and** `IPscore_3.01 WORKHORSE.xlsx`, which `5_ipscore/tools/extract_spec_from_excel.py` reads as the source of truth. Its `build/` pipeline is protected by an explicit negation in `.gitignore` — the generic `build/` rule would otherwise silently untrack it, which is exactly what happened during the 2026-09-17 move |
| `9_misc/lead-generation-research/` | DPMAconnect interface specs, NUTS notes and implementation briefs behind module 4 |
| `9_misc/plan/archive/prep_workshop_todo.md`, `9_misc/plan/archive/plan-repo-simplification.md` | Working logs |

Earlier supporting folders (`setup/`, `harmonization/`, `ipc-extension/`, `context/`, `docs/`) and
the BMAD agent tooling (`_bmad*`, `.claude/`, `.agent/`, `.gemini/`) were removed once no module
referenced them; recover with `git checkout fdcf789 -- <path>`.

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
persistent Claude Code + Git/SSH setup — see **`install.sh`**, and
**`9_misc/legacy/startwithtip/1_getting-started-with-tip.ipynb`** for the reasoning behind
each step it performs.

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
  `3_lead_generation/1_regional-leads.ipynb`) plus a short table of
  contents. Keep new notebooks visually consistent.
- Ship a sensible default so a notebook runs out of the box (e.g. Alsace `FR42`
  in lead generation), with user-editable parameters near the top.
- Inside TIP, prefer PATSTAT (`env='PROD'`). The `*_bq.ipynb` variants are
  BigQuery ports and need separate credentials — not needed on TIP.
- Git: SSH remotes, do work on `develop`, open PRs into `main`.

### Guest material (Riccardo Priore)
`4_patentreports/` and `9_misc/ipscore/` are contributed material, reworked to
match this course's look. Two deliberate deviations from the conventions above:
- **Everything ships pre-executed with code folded away** (`metadata.jupyter.source_hidden`),
  so a participant sees explanation and result without running or reading code. Guest material
  additionally must never be re-run — the outputs *are* the deliverable.
- **The header credits `created by Riccardo Priore`**, not the repo author.

Never re-run or re-generate their code cells to "tidy" them — the outputs *are* the
deliverable. Each folder has a `PROVENANCE.md` naming the upstream repo and commit;
his repository stays the canonical source. IPScore is an **EPO tool** in an ASP
adaptation. The IPScore HTML tools are *generated* from JSON + Jinja2 templates —
edit the data or template and re-render, never the generated HTML.
