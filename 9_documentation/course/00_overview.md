# TIP4PATLIBS — Course Overview

*Six modules · six 45-minute blocks · EPO Technology Intelligence Platform*

> **What this document is.** The frame around the six module documents: what a participant can do
> at the end, how the modules depend on each other, how to run the material as a course, and what
> is deliberately not in it.

---

## The overall goal

> **A PATLIB adviser can take a real question from a real client — *"who is active in my region?"*,
> *"what does this technology field look like?"*, *"is this patent worth anything?"* — and answer it
> from PATSTAT on TIP, with a defensible method, a reproducible notebook and an artifact the client
> can keep. And they can say which parts of that answer are evidence and which are judgement.**

That last clause is what separates this course from a tool demonstration. Every module returns to
it, and module 8 makes it the output.

---

## The chain — three skills and three applications

The six modules are not six topics. They are **three skills** and **three applications**, and each
application consumes all three skills.

```
   SKILLS                                       APPLICATIONS
   ┌───────────────────────────┐                ┌────────────────────────────────┐
   │ 1  Work on TIP at all     │──────┐         │ 5  Who is out there?           │
   │    environment, first query│     │         │    region → applicants → leads │
   ├───────────────────────────┤      ├────────▶├────────────────────────────────┤
   │ 3  Ask PATSTAT a question │──────┤         │ 6  What does a field look like?│
   │    the query library      │      │         │    corpus → analyses → report  │
   ├───────────────────────────┤      │         ├────────────────────────────────┤
   │ 4  Find the right people  │──────┘         │ 8  What is one patent worth?   │
   │    applicant consolidation│                │    model → evidence → valuation│
   └───────────────────────────┘                └────────────────────────────────┘
```

| # | Module | Assumes | Adds | One-sentence goal |
|---|---|---|---|---|
| **1** | Start with TIP | — | the working environment | *I can open TIP, connect to PATSTAT, write my first query, and keep my setup across a restart.* |
| **3** | The Query Library | 1 | the question repertoire | *I can pick a ready-made query, adapt its parameters, and read the result.* |
| **4** | PATSTAT Explorer | 1, 3 | applicant identity | *I know why one company is forty different names, and I can consolidate them.* |
| **5** | Regional Lead Generation | 1, 3, 4 | a client-facing output | *I can profile a region's applicants and segment them into lead tiers.* |
| **6** | Patent Landscape Reports | 1, 3, 4 | a publishable analysis | *I can define a corpus with a defensible search strategy and turn it into a report.* |
| **8** | IPScore — what is a patent worth? | 1, 3, 4 | the evidence/judgement split | *I can value a patent, and state exactly how much of that number is checkable.* |

**Modules 5, 6 and 8 are parallel, not sequential.** A PATLIB that never does valuations can stop
after module 6 and has lost nothing. Say this to participants — it lowers the barrier, and it is
true.

> **Why module 8 sits last.** Not because it is hardest, but because it is where the course's
> recurring theme becomes the deliverable. Module 3 says *an analysis you cannot open up is one you
> cannot defend.* Module 4 adds that some of what you open up is a decision you made. Module 5 makes
> you state your coverage limit. Module 6 makes you state your exclusions. Module 8 prints the split
> on the front page of the report.

---

## Skipped module numbers

The numbering follows the repository folders, so two numbers are missing here on purpose:

| | |
|---|---|
| **2** | `2_legacy/` — earlier worked end-to-end examples, superseded by modules 4–6 |
| **7** | `7_ipscore/` — Riccardo Priore's workshop-ready IPScore tools. Not taught as a block here; module 8 is the course's own rebuild of the same model |

---

## How to run the material

### As a course — six 45-minute blocks

Each module document is one block, timed the same way:

| Phase | Time | What happens |
|---|---:|---|
| **Einleitung** | ≈ 7 min | The client question this module answers, and why the obvious approach fails |
| **Erarbeitung** | ≈ 28 min | The notebooks, step by step, with the traps named before they are hit |
| **Lernergebnis** | ≈ 10 min | What now exists, four self-check questions, and a transfer exercise for the participant's own desk |

Roughly 12–15 minutes of the Erarbeitung is reading; the rest is running cells and looking at
results.

**A note on module 8.** Its full material is 8,272 markdown words across four notebooks — more prose
than modules 1, 3, 4 and 6 combined. `08_ipscore.md` therefore covers a **core path**: the model
plus a guided read of the finished report. The implementation chain is a second block,
`08_ipscore_part2.md`. Nothing is missing from the argument; only the code walk is deferred.

### As a workshop — two 45-minute blocks

For a showcase there is a slide version of the same material, three slides per module:

| Block | Modules | Slides | Per module |
|---|---|---:|---:|
| **A — Skills** | 1, 3, 4 | 9 | 15 min |
| **B — Applications** | 5, 6, 8 | 9 | 15 min |

Plus the chain diagram above as an opening slide and one closing slide — **20 slides**. The slides
are generated *from* these documents, so there is one source of truth.

### As a handout

Each document is dual-track: **the running text addresses the participant**, and material for
whoever is running the session sits in boxes marked 🎓. Traps sit in boxes marked ⚠️. One file
serves as handout and as script, which is what makes the material reusable by another PATLIB.

---

## Prerequisites for the whole course

- A **TIP account** with JupyterLab access. Nothing is installed locally.
- **No Python and no SQL** are assumed. Both appear at the level needed and no further.
- Modules 1, 3, 4 and 5 need PATSTAT PROD; one cell in module 6 additionally uses BigQuery and
  ships with its output.

**Data edition throughout: PATSTAT Global, Autumn 2025.** Every number in the material depends on
it — module 5 opens by checking which edition you are actually on, and that habit is worth keeping.

---

## What ships executed, and what does not

This matters for reading ahead, and it is not an accident.

| Module | Executed cells | Why |
|---|---|---|
| 1 Start with TIP | 0 of 25 | You are meant to run it — it configures *your* environment |
| 3 Query Library | 6 of 10 | Partly interactive; the browser has to be run |
| 4 PATSTAT Explorer | 7 of 7 | Read it before you run it |
| 5 Lead Generation | 8 of 31 | You are meant to run it for **your own** region |
| 6 Patent Reports | 29 of 29 | Read as a **finished report** — the outputs *are* the deliverable |
| 8 IPScore Rebuild | 37 of 38 | Read as a finished valuation |

> ⚠️ Modules 6 and 8 must **never** be re-run to "tidy" their outputs. For module 6 in particular
> the committed outputs are contributed material.

---

## Credits

- Modules 1, 3, 4, 5 and 8 — **Arne Krüger**, mtc.berlin / depa.tech.
- Module 6 — landscape analyses after **Riccardo Priore**, Centro PATLIB, AREA Science Park,
  reworked to match this course's look. Module 7, outside this block, is his material as well.
- **IPScore is an EPO tool.** Module 8 is this course's own implementation of the IPScore 3.01
  model, verified against the EPO's own workbook.

License: **EPO Internal Use**.

---

## The six documents

| | |
|---|---|
| `01_start-with-tip.md` | The environment, and your first query written by hand |
| `03_query-library.md` | Choosing from queries somebody already made defensible |
| `04_patstat-explorer.md` | Why one company is forty names, and what to do about it |
| `05_lead-generation.md` | A region's applicants, ranked and segmented into lead tiers |
| `06_patent-reports.md` | A corpus, a battery of analyses, and one self-contained report |
| `08_ipscore.md` | A valuation, and how much of it is evidence |

The planning document behind them — including the module-8 restructuring argument and the
rendering plan — is `../plan-course-material.md`.
