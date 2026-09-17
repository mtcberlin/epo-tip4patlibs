# TIP4PATLIBS

Course material for PATLIB staff across Europe, for getting real work out of the **EPO
Technology Intelligence Platform (TIP)**. Every notebook is meant to be opened and run
top-to-bottom inside TIP's own JupyterLab — no installation, and a sensible default so it
works before you change anything.

> **You do not have to learn SQL. You have to install something that writes it — and then
> decide what to ask.**

## Start here

**`1_startwithtip/1_getting-started-with-tip.ipynb`** — it sets up an AI assistant that is
still there after TIP rebuilds your machine. Everything else assumes you have done that.

## The six modules

Read left to right: one claim, three examples of rising ambition, two full use cases.

### The claim

| | Module | What it answers |
|---|---|---|
| **1** | [`1_startwithtip/`](1_startwithtip/) | You have a login to a machine you do not own, rebuilt without warning. How do you get an assistant onto it that is still there next session? |

### Three examples

| | Module | What it answers |
|---|---|---|
| **2** | [`2_querylib/`](2_querylib/) | *"Who in Europe is working on solid-state batteries?"* — a ready query you adapt, and what it costs in time |
| **3** | [`3_patstat_explorer/`](3_patstat_explorer/) | *"How big is Siemens Healthineers' portfolio?"* — a name search returns 200 rows; which one is the answer? Then the same search as an app |
| **4** | [`4_lead_generation/`](4_lead_generation/) | *"Which companies in your region should you be talking to?"* — a named shortlist for your own region, and what it leaves out |

### Two use cases

| | Module | What it answers |
|---|---|---|
| **5** | [`5_patentreports/`](5_patentreports/) | *"What is happening in antibiotic resistance?"* — a publishable landscape report, and the search strategy that defined its corpus *(Riccardo Priore)* |
| **6** | [`6_ipscore_rebuild/`](6_ipscore_rebuild/) | *"What is this patent worth?"* — the EPO IPScore model end to end, and how much of the number is evidence rather than judgement |

## How to run them

Connect to PATSTAT the same way everywhere — PATSTAT Global, Autumn 2025:

```python
from epo.tipdata.patstat import PatstatClient
patstat = PatstatClient(env='PROD')
```

**Modules 1–4 ship with cleared outputs** — you run them yourself. **Modules 5 and 6 ship
pre-executed**, and are read as finished reports. Their stored outputs *are* the
deliverable, so please do not re-run the cells to tidy them.

## Handouts and slides

`9_documentation/course/` holds the full 45-minute written version of every module as an A4
PDF, the workshop deck, and `TIP4PATLIBS_LiveDemo_Menu.ipynb` — a launcher that opens every
notebook, report and deck from one page.

## Not course material

Kept for reference, not part of the six modules:

| Path | What it is |
|---|---|
| `9_documentation/` | Plans, session notes and the course sources |
| `9_documentation/ipscore/` | Riccardo Priore's original IPScore HTML tools — and the EPO workbook module 6 reads its model from |
| `9_documentation/legacy/` | Earlier worked examples (Airbus, TU Dortmund, Belgium) |
| `9_documentation/lead-generation-research/` | DPMA interface specs and implementation notes behind module 4 |

## License

EPO Internal Use · Author: Arne Krüger (mtc.berlin / depa.tech) ·
Modules 5 and 6 after material by Riccardo Priore (Centro PATLIB, AREA Science Park)
