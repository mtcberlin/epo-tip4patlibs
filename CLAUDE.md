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
| `2_querylib/` | Query Library — ready-to-use PATSTAT queries |
| `3_patstat_explorer/` | Applicant & technology search notebook + app |
| `4_lead_generation/` | Regional lead generation — profile a region's EP/PCT applicants by portfolio depth × geographic reach, segment into lead tiers |
| `5_patentreports/` | Landscape reports (**Riccardo Priore**) — triadic families, filing authorities, t-SNE clusters, interactive explorer. Ships **pre-executed** (see below) |
| `6_ipscore_rebuild/` | ✅ Complete — all four notebooks written and run on TIP; the evidence layer measures 11 of the 40 answers and the report reads `2 measured · 6 informed · 32 judgement`. Our own rebuild of the IPScore ideas as an explained notebook chain, adding a PATSTAT evidence layer. Engine in `ipscore_kit.py`, model data in `ipscore_spec.json`, deliverable in `4_tool/`, phasing in `REBUILD_PLAN.md`; `9_documentation/ipscore/` stays untouched as the working reference |
| `9_documentation/` | Working documents that are not themselves course modules — see below |
| `9_documentation/legacy/` | Earlier worked end-to-end examples (Airbus filing strategy, TU Dortmund portfolio). Not shown in Warsaw |
| `9_documentation/ipscore/` | Patent valuation (**Riccardo Priore**) — EPO IPScore questionnaire → NPV; self-contained interactive HTML tools, opened via `open_html()` (jupyter-server-proxy), **never** via `IFrame`. Not shown in Warsaw; module 5 is the course's own rebuild |

**The folders are numbered in the workshop's running order** (renumbered 2026-08-26): the claim
first, then the three examples of rising ambition, then Riccardo's two use cases. Two folders that
are not shown in Warsaw — the earlier worked examples and Riccardo's imported IPScore tools — moved
under `9_documentation/`. **Module numbers in the teaching material were *not* renumbered**: the
handouts and slides still speak of modules 1, 2, 3, 4, 5 and 6. See `9_documentation/plan-course-material.md`.

### What lives in `9_documentation/`
**TIP sessions**, one brief per session, named for what the session was:
`plan-tipsession-1-recon.md` (✅ 2026-08-15 — what can PATSTAT answer?) ·
`plan-tipsession-2-evidence-run.md` (✅ 2026-08-15 — run notebook 2) ·
`plan-tipsession-3-screenshots.md` (⏳ **open** — the shots that cannot be produced offline, before
17 September), with the findings of the first two in `results-tipsession.md`.
**Workshop:** `plan-workshop-warsaw.md` — the 90-min Warsaw session (17 Sep 2026): the spine, the
running order, what is cut, and how it splits between Arne and Riccardo.
**Teaching material:** `plan-course-material.md` and `course/` — a 45-min block per module with
learning objectives and the three phases Introduction · Working through · Learning outcome, plus a
3-slide workshop version of each. `course/` holds the rendered A4 handouts and three decks:
`TIP4PATLIBS_1_Workshop_v1.pptx` (ours, generated from `slides.yaml`) and Riccardo's two
(`…_AntibioticResistance_LiveDemo_Warsaw2026.pptx`, `…_IPScore_NotebookLogic_Explained_con_note.pptx`).
The Markdown, its YAML sidecars, `build_handouts.py`, `build_slides.py` and `build_shots.py` live in
`course/source/`.

The **course** is modules 1–6. Alongside it sit four working documents that are not course
material: this file, `README.md`, `prep_workshop_todo.md` (the workshop-preparation log) and
`9_documentation/` (plans that need a live TIP session or a decision). Earlier
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
  `4_lead_generation/1_regional-leads.ipynb`) plus a short table of
  contents. Keep new notebooks visually consistent.
- Ship a sensible default so a notebook runs out of the box (e.g. Alsace `FR42`
  in lead generation), with user-editable parameters near the top.
- Inside TIP, prefer PATSTAT (`env='PROD'`). The `*_bq.ipynb` variants are
  BigQuery ports and need separate credentials — not needed on TIP.
- Git: SSH remotes, do work on `develop`, open PRs into `main`.

### Guest material (Riccardo Priore) (Riccardo Priore)
Modules `5_patentreports/` and `9_documentation/ipscore/` are contributed material, reworked to
match this course's look. Two deliberate deviations from the conventions above:
- **They ship pre-executed** (outputs kept) — modules 1–4 clear outputs so
  participants run them; 6–7 are read as finished reports in a 90-min showcase.
- **The header credits `created by Riccardo Priore`**, not the repo author.

Never re-run or re-generate their code cells to "tidy" them — the outputs *are* the
deliverable. Each folder has a `PROVENANCE.md` naming the upstream repo and commit;
his repository stays the canonical source. IPScore is an **EPO tool** in an ASP
adaptation. The IPScore HTML tools are *generated* from JSON + Jinja2 templates —
edit the data or template and re-render, never the generated HTML.
