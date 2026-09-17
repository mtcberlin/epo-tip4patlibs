# TIP4PATLIBS

Course material for PATLIB staff across Europe, for getting real work out of the **EPO
Technology Intelligence Platform (TIP)**. Every notebook runs top-to-bottom inside TIP's own
JupyterLab, with a sensible default so it works before you change anything.

> **You do not have to learn SQL. You have to install something that writes it — and then
> decide what to ask.**

## Start here — one command

Open a terminal in TIP and paste:

```bash
curl -fsSL https://raw.githubusercontent.com/mtcberlin/epo-tip4patlibs/main/install.sh | bash
```

That installs an AI coding assistant that **survives a TIP restart**, configures it for this
environment, and clones this repository into `~/epo-tip4patlibs`. Run it again any time —
after TIP rebuilds your machine it repairs the setup and updates the material.

Prefer to read before running? Same thing in three steps:

```bash
curl -fsSL https://raw.githubusercontent.com/mtcberlin/epo-tip4patlibs/main/install.sh -o install.sh
less install.sh
bash install.sh
```

Then open any module folder below and run its notebooks in order. Modules 5 and 6 show
their finished report at the end with one click.

## The modules

Rising ambition from top to bottom: three worked examples, then two full use cases.

| | Module | What it answers |
|---|---|---|
| **2** | [`2_querylib/`](2_querylib/) | *"Who in Europe is working on solid-state batteries?"* — a ready query you adapt, and what it costs in time |
| **3** | [`3_patstat_explorer/`](3_patstat_explorer/) | *"How big is Siemens Healthineers' portfolio?"* — a name search returns 200 rows; which one is the answer? Then the same search as an app |
| **4** | [`4_lead_generation/`](4_lead_generation/) | *"Which companies in your region should you be talking to?"* — a named shortlist for your region, and what it leaves out |
| **5** | [`5_patentreports/`](5_patentreports/) | *"What is happening in antibiotic resistance?"* — a publishable landscape report, and the search strategy behind its corpus *(Riccardo Priore)* |
| **6** | [`6_ipscore/`](6_ipscore/) | *"What is this patent worth?"* — the EPO IPScore model end to end, and how much of the number is evidence rather than judgement |

Each module folder is **self-contained**: its notebooks, its data, its slide deck and its own
copy of `tip_tools.py`. Nothing reaches across folders, so you can open one and work in it.

Numbering starts at 2 because the old module 1 — *setting up TIP* — is now `install.sh`. Its
notebooks are kept in `9_misc/legacy/startwithtip/` if you want to see what the script does
and why.

## How to run them

Connect to PATSTAT the same way everywhere — PATSTAT Global, Autumn 2025:

```python
from epo.tipdata.patstat import PatstatClient
patstat = PatstatClient(env='PROD')
```

**Modules 2–4 ship with cleared outputs** — you run them yourself. **Modules 5 and 6 ship
pre-executed** and are read as finished reports; their stored outputs *are* the deliverable,
so please do not re-run the cells to tidy them.

## Also in the repository

| Path | What it is |
|---|---|
| `1_handouts/` | The full 45-minute written version of every module, as A4 PDFs, plus the sources they are built from |
| `TIP4PATLIBS_1_Workshop_v4.pdf` | The workshop deck |
| `9_misc/plan/` | Planning documents and session notes |
| `9_misc/legacy/` | Earlier worked examples, and the original TIP-setup notebooks |
| `9_misc/ipscore/` | Riccardo Priore's original IPScore HTML tools — and the EPO workbook module 6 reads its model from |
| `9_misc/lead-generation-research/` | DPMA interface specs and implementation notes behind module 4 |

## License

EPO Internal Use · Author: Arne Krüger (mtc.berlin / depa.tech) ·
Modules 5 and 6 after material by Riccardo Priore (Centro PATLIB, AREA Science Park)
