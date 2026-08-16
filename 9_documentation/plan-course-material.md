# Plan — course material for modules 1, 3, 4, 5, 6 and 8

**What this is.** A plan for turning six modules of notebooks into teachable course material:
a **45-minute block per module** as a written document, and a **condensed slide version** of the
same substance for the PATLIB Warsaw workshop on **18 September 2026**.

**This run produces the plan only.** The material itself is drafted in run 2 as Markdown; PDFs
and slides are rendered in run 3. Nothing is rendered yet, deliberately — the structure has to be
agreed before six documents are written against it.

> Module numbering follows the folders: **1** `1_startwithtip` · **3** `3_querylib` ·
> **4** `4_patstat_explorer` · **5** `5_lead_generation` · **6** `6_patentreports` ·
> **8** `8_ipscore_rebuild`. Modules 2 (legacy) and 7 (Riccardo's IPScore tools) are out of scope.

---

## 1 · What we are working with — measured, not estimated

Reading time is markdown words ÷ 180 wpm plus ~25 s per code cell to read and run it. It is the
*notebook* content, before any course document is written.

| Module | notebooks | cells | code cells | lines of code | md words | ≈ working time |
|---|---:|---:|---:|---:|---:|---:|
| 1 Start with TIP | 2 | 60 | 25 | 525 | 2,602 | **24 min** |
| 3 Query Library | 2 | 20 | 10 | 477 | 643 | **8 min** |
| 4 PATSTAT Explorer | 2 | 18 | 7 | 112 | 1,300 | **10 min** |
| 5 Lead Generation | 3 | 72 | 31 | 643 | 3,895 | **34 min** |
| 6 Patent Reports | 4 | 66 | 29 | 703 | 2,788 | **27 min** |
| **8 IPScore Rebuild** | 4 | 87 | 38 | **1,130** | **8,272** | **61 min** |
| **total** | **17** | **323** | **140** | **3,590** | **19,500** | **≈ 2 h 45** |

Two things follow immediately, and they drive the rest of this plan:

- **Module 8 is the problem, and by a wider margin than it feels.** Its 8,272 words are *more
  prose than modules 1, 3, 4 and 6 combined* (7,333), and it carries a third of all the code in
  the course. At 61 minutes it does not fit a 45-minute block — not by trimming, only by
  restructuring. Section 5 proposes how.
- **Modules 3 and 4 are the opposite problem.** At 8 and 10 minutes they are too thin to fill a
  block on their own; their documents will have to *add* framing, exercises and context rather
  than summarise.

---

## 2 · What a participant should be able to do afterwards

### The overall goal, across all six modules

> A PATLIB adviser can take a real question from a real client — *"who is active in my region?"*,
> *"what does this technology field look like?"*, *"is this patent worth anything?"* — and answer
> it from PATSTAT on TIP, with a defensible method, a reproducible notebook and an artifact the
> client can keep. And they can say **which parts of that answer are evidence and which are
> judgement.**

That last clause is what separates this course from a tool demonstration, and it is why module 8
sits at the end rather than module 6.

### The chain — what each module assumes and adds

The six modules are not six topics. They are **three skills and three applications**, and the
applications each consume all three skills.

```
   SKILLS                                        APPLICATIONS
   ┌──────────────────────────┐                  ┌──────────────────────────────┐
   │ 1  Work on TIP at all    │───────┐          │ 5  Who is out there?         │
   │    environment, persistence      │          │    region → applicants → leads│
   ├──────────────────────────┤       ├─────────▶├──────────────────────────────┤
   │ 3  Ask PATSTAT a question│───────┤          │ 6  What does a field look like?│
   │    the query library     │       │          │    corpus → analyses → report │
   ├──────────────────────────┤       │          ├──────────────────────────────┤
   │ 4  Find the right people │───────┘          │ 8  What is one patent worth?  │
   │    applicant consolidation│                 │    model → evidence → valuation│
   └──────────────────────────┘                  └──────────────────────────────┘
```

| # | Assumes | Adds | One-sentence goal |
|---|---|---|---|
| **1** | nothing | the working environment | *I can open TIP, connect to PATSTAT, and keep my setup across a restart.* |
| **3** | 1 | the question repertoire | *I can pick a ready-made query, adapt its parameters, and read the result.* |
| **4** | 1, 3 | applicant identity | *I know why "Siemens" is forty different strings, and I can consolidate them.* |
| **5** | 1, 3, 4 | a client-facing output | *I can profile a region's applicants and segment them into lead tiers.* |
| **6** | 1, 3, 4 | a publishable analysis | *I can define a corpus and turn it into a landscape report with a defensible search strategy.* |
| **8** | 1, 3, 4 | the evidence/judgement split | *I can value a patent, and state exactly how much of that number is checkable.* |

**Modules 5, 6 and 8 are parallel, not sequential.** A PATLIB that never does valuations can stop
after 6. Say this in the material: it lowers the barrier and it is true.

---

## 3 · The template for each module document

One Markdown file per module, same structure throughout, sized for **45 minutes**.

**Dual track in one document** (as decided): the running text addresses the **participant**;
trainer material sits in clearly marked boxes so the same file works as a handout *and* as a
script. One file to maintain, and it is what another PATLIB could reuse.

```markdown
# Module N — <title>

## Lernziel            ← one sentence, from the table in §2
## Voraussetzungen     ← which modules, which TIP state
## Teillernziele       ← 3–5, each observable ("kann …", not "versteht …")

## Phase 1 · Einleitung        (≈ 7 min)
   Warum diese Frage?  |  Lehr- und Lernaktivität  |  ⏱ Zeit
   > 🎓 Trainer: opening question for the room, expected wrong answers

## Phase 2 · Erarbeitung       (≈ 28 min)
   step | what the participant does | what they see | ⏱
   > 🎓 Trainer: where this breaks, what to do when a query is slow
   > ⚠️ Stolperstelle: the known traps, from the repo's own warnings

## Phase 3 · Lernergebnis      (≈ 10 min)
   What now exists (artifact) · self-check questions · transfer to own work
   > 🎓 Trainer: how to close, what to assign
```

**Time budget inside 45 minutes:** Einleitung 7 · Erarbeitung 28 · Lernergebnis 10.
Within the 28 minutes of Erarbeitung, roughly **12–15 minutes is reading** (≈ 2,200–2,700 words
of notebook prose) and the rest is running cells and looking at results. **That number is the
constraint module 8 fails**, and the yardstick for every module document.

### Worked pattern — module 3, filled in

> **Stale.** The sketch below predates the *English throughout* decision in §6 and is kept
> only as the reasoning trail. **`course/03_query-library.md` is authoritative** — do not
> regenerate anything from this block.

Module 3 is used as the pattern because it is the smallest, so the structure stays legible.
Note how a thin module is *filled*, not padded: the Einleitung does real work.

| | |
|---|---|
| **Lernziel** | Ich kann aus der Query Library eine passende Abfrage wählen, ihre Parameter anpassen und das Ergebnis lesen. |
| **Voraussetzungen** | Modul 1 (TIP läuft, PATSTAT verbunden) |
| **Teillernziele** | (1) kann die Frage eines Kunden einer Query-Kategorie zuordnen · (2) kann Parameter ändern, ohne SQL zu schreiben · (3) kann erkennen, wann ein Ergebnis *plausibel* ist · (4) weiß, wann eine Abfrage zu teuer wird |

**Phase 1 · Einleitung (7 min).** Open with a real question — *"Ein Kunde fragt: Wer forscht in
Europa an Feststoffbatterien?"* Let the room propose approaches for two minutes; collect them on
the flipchart. **The point being made:** most proposals are keyword searches, and keyword searches
alone give a corpus nobody can defend. That tension is what the Query Library resolves.
*🎓 Trainer: the expected wrong answer is "Google Patents durchsuchen" — take it seriously, then
ask how they would prove the list is complete.*

**Phase 2 · Erarbeitung (28 min).** Run `TIP_for_PATLIBs_QueryLib.ipynb`, pick the applicant
query, change the country and the year window, read the result. Then the interactive demo.
*⚠️ Stolperstelle: PATSTAT PROD is not fast. A query that scans a full year takes a minute — say
so before the room decides it is broken.*

**Phase 3 · Lernergebnis (10 min).** Each participant has one adapted query and one result table.
Self-check: *"Warum liefert dieselbe Frage mit `appln_auth = 'EP'` weniger Treffer als mit
`docdb_family_id`?"* Transfer: which of your own recurring client questions maps onto which query?

---

## 4 · The workshop version — 3 slides per module

The same substance, compressed for projection. **Not a second content stream**: the slides are
generated *from* the module documents, so there is one source of truth.

**Structure:** 6 modules × 3 slides = **18 slides**, in two blocks:

| Block | Modules | Slides | Time | Per module |
|---|---|---:|---:|---:|
| **A — Skills** | 1, 3, 4 | 9 | 45 min | 15 min |
| **B — Applications** | 5, 6, 8 | 9 | 45 min | 15 min |

Each module gets exactly three slides, mirroring the three phases:

1. **Einleitung** — the client question this module answers, and why the obvious approach fails.
2. **Erarbeitung** — *one* screenshot of the notebook doing the work, plus the link to it. Not a
   method walkthrough: one picture and the three steps in the caption.
3. **Ergebnis** — what exists afterwards (the artifact), and the one sentence to remember.

Plus two frame slides: the chain diagram from §2 at the start of block A, and a closing slide.
**20 slides total.**

This is tight — 15 minutes for a module whose material is a 45-minute block. That is the correct
compression for a showcase, and it is why the module documents must be written first: you cannot
condense what has not been articulated.

---

## 5 · Module 8 — the restructuring proposal

### What is actually wrong

Not the length of any one notebook. **Each of the four notebooks re-teaches the module's
premise.** The zero-overlap thesis, the provenance markers, the "IPScore is subjective" framing
and the iframe/CSP constraint are each explained two to four times, because each notebook was
written to stand alone.

| Notebook | md words | re-explains |
|---|---:|---|
| 1 the model | 2,442 | provenance markers · the 8-of-40 surprise |
| 2 evidence from PATSTAT | 2,541 | provenance markers · the 8-of-40 surprise · zero overlap |
| 3 valuation and scenarios | 1,150 | the 8-of-40 surprise |
| 4 assemble the tool | 2,139 | provenance markers · zero overlap · the CSP constraint |

### The proposal

**Move the premise into the module document's Einleitung, once.** The notebooks then refer back
to it instead of rebuilding it. Estimated saving: **1,500–2,000 words** without losing an idea.

**Define a core path and an extension.** A 45-minute block cannot cover four notebooks and
1,130 lines of code. Proposed:

| | Notebooks | Words | Role |
|---|---|---:|---|
| **Core (45 min)** | **1 the model** + a guided read of the **finished report** from 4 | ~2,400 | The model, the 8-of-40 surprise, the acceptance test, and the deliverable as a finished artifact |
| **Extension** | 2 evidence · 3 scenarios · 4 assembly in full | ~5,800 | For PATLIBs that want to run it themselves; a second 45-minute block if there is appetite |

The core keeps the module's two strongest moments — *only 8 of 40 answers touch the money*, and
*the eleven answers data can check are none of those eight* — and drops the implementation walk.
A participant who never opens notebook 2 still leaves with the argument.

**Target: the module 8 core document sized like every other module** — ≈ 2,400 words of notebook
prose in Erarbeitung, down from 8,272.

> **This is a proposal about teaching, not about the code.** Nothing in `8_ipscore_rebuild/` gets
> deleted or rewritten. The core/extension split lives in the course document; the module stays
> complete and the four notebooks stay as they are.

---

## 6 · Decisions

**Taken here — say so, do not re-open:**

- **Module 6 uses `2_antibiotic_resistance_rebuild/`** — the current clean build, four notebooks.
  Not `1_antibiotic_resistance/` (the imported reference) and not the frozen MVP.
- **Module 5 uses `1_regional-leads.ipynb` as the core.** `2_national-coverage` (DPMA route) and
  `3_belgien` become optional extensions — otherwise module 5 is 34 minutes.
- **One Markdown source per module**, dual-track, from which both PDF and slides are rendered.
- **Modules 2 and 7 are out of scope**, as instructed.

**Settled with Arne, 2026-08-16:**

- **Setting:** both audiences in one document — participant text plus marked trainer boxes.
- **Size:** 45-minute block per module for the written material; the workshop gets a compressed
  slide version of the same substance, 3 slides per module, two 45-minute blocks.

**Settled with Arne, 2026-08-16 (second round):**

- **Language: English throughout**, including the trainer boxes. Consistent with the rest of the
  repo and with an audience of PATLIB staff from across Europe.
- **Module 8: the core path only.** `08_ipscore.md` covers notebook 1 plus a guided read of the
  finished report, sized like every other module. The implementation walk (notebooks 2, 3 and 4)
  is **not** written for 18 September; it is deferred to a possible supplementary document,
  `08_ipscore_part2.md`, if a PATLIB wants to run the chain itself. That removes ~5,800 words
  from run 2.

---

## 7 · Run 2 and run 3 — scope, and one constraint worth knowing now

**Run 2 — the drafts. ✅ Done, 2026-08-16.** Seven Markdown documents in
`9_documentation/course/`: one per module against the §3 template, plus `00_overview.md` carrying
§2 (the overall goal and the chain) and the course-level framing. Text only; no rendering, no
screenshots.

| File | Words | Notes |
|---|---:|---|
| `00_overview.md` | 1,426 | goal · chain · how to run it · what ships executed · credits |
| `01_start-with-tip.md` | 1,878 | core path only — Claude Code sections and notebook 2 Part 2 handed over as self-study |
| `03_query-library.md` | 1,526 | the worked pattern |
| `04_patstat-explorer.md` | 2,006 | thin module, filled by the step-2 discussion |
| `05_lead-generation.md` | 2,206 | notebook 1 only; 2 and 3 are extensions |
| `06_patent-reports.md` | 2,082 | credits Riccardo Priore; written against the **rebuild**, not the reference folder |
| `08_ipscore.md` | 2,869 | core path: notebook 1 + guided read of the report |

All seven share the same heading set (Lernziel · Voraussetzungen · Teillernziele · Material ·
Phase 1/2/3 · Where this leads · Notes for the next revision). Each ends with a **"Notes for the
next revision"** section listing the defects found while writing — those are the repo's to-do
list, not the course's, and they are deliberately *not* fixed in this run (see §8: the course
material describes the modules, it does not modify them).

**Run 3 — rendering.** Two targets from the same sources:

- **PDF** — the `mtc-pdf` skill exists and produces branded A4 with title page and running
  header. No new tooling needed.
- **Slides** — **no skill exists for this.** Either `python-pptx` (real `.pptx`, editable in
  PowerPoint) or a self-contained HTML deck (matches the course's existing house style, opens in
  any browser, but is not a `.pptx` anyone can edit). **Decide in run 3, not now.**

### ⚠️ The screenshot constraint

Screenshots come from executed notebook outputs. The modules do not ship the same way:

| Module | executed cells | screenshots available offline? |
|---|---|---|
| 1 Start with TIP | 0 of 25 | ❌ **needs a TIP run** |
| 3 Query Library | 6 of 10 | ⚠️ partial |
| 4 PATSTAT Explorer | 7 of 7 | ✅ |
| 5 Lead Generation | 8 of 31 | ❌ **needs a TIP run** |
| 6 Patent Reports | 29 of 29 | ✅ |
| 8 IPScore Rebuild | 37 of 38 | ✅ |

Modules 1–5 ship with cleared outputs **on purpose** — participants are meant to run them. So the
screenshots for modules 1 and 5 (and part of 3) require someone to run those notebooks on TIP and
capture the output, and that is a **separate TIP session** to schedule before 18 September.
Modules 4, 6 and 8 are free.

The alternative for 1 and 5 is screenshots of the *notebook as it ships* — code and explanation
with empty output cells — which is honest for module 1 (whose subject is the environment) but
weak for module 5, whose whole point is the resulting lead table.

---

## 8 · Files this plan creates

```
9_documentation/
  plan-course-material.md        ← this file
  course/
    00_overview.md               ← §2: overall goal, the chain, how to use the material
    01_start-with-tip.md
    03_query-library.md
    04_patstat-explorer.md
    05_lead-generation.md
    06_patent-reports.md
    08_ipscore.md
    slides/                      ← run 3
```

Nothing under `1_`–`8_` is touched. The course material describes the modules; it does not
modify them.

---

## 9 · Defects found while writing run 2

Writing the course material was also a close read of the modules. These are the concrete problems
it surfaced, collected here so they do not stay buried in seven documents. **None of them was
fixed in run 2** — per §8, the course material describes the modules and does not modify them.

| Module | Finding | Severity |
|---|---|---|
| **1** | `2_getting-started-with-patstat.ipynb` warns that `han_name` shows *"TECHNISCHE UNIVERSITAT MUNCHEN"* for TU Berlin. Verify against Autumn 2025 — a wrong warning teaches badly | check |
| **1** | The same notebook names *2023–2024* as the incomplete years. On Autumn 2025 that is **2024–2025** | text fix |
| **3** | Two leftover developer cells, *"Story 3.2 / 3.3 AC Validation"*, at the end of the interactive demo | remove |
| **4** | Three typos in the Explorer app header: *"Integlligence"*, *"knowlegde"*, and `TIP4PATLIBs` (inconsistent casing) — it is the first slide-worthy screen in the module | text fix |
| **4** | The Explorer app is cloned from GitHub at run time. Confirm reachability from the workshop network before 18 September | logistics |
| **5** | The 70% / 77% NUTS-coverage figures are stated as "measured on the current edition" — confirm on Autumn 2025 or restate with the edition measured | check |
| **4** | `CLAUDE.md` states the convention as *modules 1–5 clear outputs, 6–7 ship pre-executed*. Module 4 actually ships **7 of 7 executed** — the course material reports the measured state, so the convention line needs updating | align |
| **6** | The rebuild's `README.md` says notebook 3 holds the technology network only; the repo `CLAUDE.md` describes module 6 as including t-SNE clusters and triadic families (that is the *reference* folder). Align them so nobody promises a chart the report does not contain | **align** |
| **6** | Notebook 2's forward-citation cell needs BigQuery, not TIP. State it in the notebook header, not only in a cell comment | text fix |
| **8** | `8_ipscore_rebuild/README.md` is stale: it says notebook 2 "does not exist yet" and quotes `0 measured · 0 informed · 40 judgement`. The shipped report reads **`2 measured · 6 informed · 32 judgement`** | **stale** |
| **8** | `1_the_model.ipynb` says "four of them strongly" about the PATSTAT-reachable questions. `PATSTAT_CANDIDATES` holds **3 strong · 4 good · 3 proxy · 1 context**; the report's "three strongly" is the correct one | **wrong** |

Verified figures used throughout `08_ipscore.md`, read out of the shipped report rather than from
any README: NPV **1,248,870 EUR** over ten years at **12%**, **139 / 200** points, **−0.39**
average risk, **+0.63** average opportunity, **2 measured · 6 informed · 32 judgement**. Largest
upside lever **C2 · Market growth rate** (+563k); **C3 · Life expectancy** has an upside of exactly
zero because its answer is already the best on the scale.
