# TIP4PATLIBs

Course material for PATLIB staff in Europe, to get the most out of the **EPO Technology
Intelligence Platform (TIP)** for patent analytics. Every notebook is meant to be opened and run
inside TIP's own JupyterLab.

## Content

| Course | Folder | Description |
|--------|--------|-------------|
| 1 Start with TIP | `1_startwithtip/` | Set up Claude Code persistently on TIP, then get hands-on with your first PATSTAT queries (company & institution search) |
| 2 Legacy | `2_legacy/` | Earlier worked end-to-end analysis notebooks (Airbus filing strategy, TU Dortmund portfolio) |
| 3 Query Library | `3_querylib/` | Learning PATSTAT and patent analytics with ready-to-use queries that answer the questions PATLIB staff and their audience ask |
| 4 PATSTAT Explorer | `4_patstat_explorer/` | Course material and notebook + app for applicant and technology search within PATSTAT |
| 5 Lead Generation | `5_lead_generation/` | Regional lead generation: profiling the EP/PCT-active company applicants of a region by portfolio depth and geographic reach, and segmenting them into lead tiers |
| 6 Patent Reports | `6_patentreports/` | Turning a patent dataset into a publishable landscape report — triadic families, filing authorities, technology clusters, interactive explorer *(by Riccardo Priore)* |
| 7 IPScore | `7_ipscore/` | Patent valuation: the EPO IPScore questionnaire and its Net Present Value model, as interactive tools *(by Riccardo Priore)* |
| 8 IPScore Rebuild | `8_ipscore_rebuild/` | 🚧 *Planning stage.* Rebuilding the ideas behind IPScore as an explained notebook chain — and separating what PATSTAT can prove about a patent from what stays expert judgement |

## Quick Start

1. **Open this repository inside TIP.** Everything is written for TIP's JupyterLab and the
   base conda environment — no extra installation.
2. **Start with `1_startwithtip/1_getting-started-with-tip.ipynb`.** It explains what survives a
   restart on TIP and sets up Claude Code and Git/SSH persistently.
3. **Then `1_startwithtip/2_getting-started-with-patstat.ipynb`** for your first PATSTAT queries.
   Connection is always `PatstatClient(env='PROD')` — PATSTAT Global, Autumn 2025.
4. **Pick a module.** Each folder stands on its own and ships a sensible default (e.g. Alsace
   `FR42` in lead generation), so it runs top-to-bottom before you change anything.

### Two things worth knowing

- **Modules 1–5 ship with cleared outputs** — you run them. **Modules 6 and 7 ship
  pre-executed**: they are guest contributions by Riccardo Priore, read as finished reports in
  a showcase session. The stored outputs *are* the deliverable, so don't re-run them to tidy up.
- **Module 7 needs no PATSTAT, no database and no internet.** The IPScore tools are
  self-contained HTML — a spreadsheet model turned into a web page. Useful when you want to
  demonstrate something without depending on a live connection.

## License

EPO Internal Use
