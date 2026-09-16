# Plan · Simplify the repository for PATLIB beginners

**Branch:** `cleanup/simplify-for-patlib-beginners` · **Status:** draft, awaiting decisions
**Spec:** `9_documentation/course/TIP4PATLIBS_1_Workshop_v3.pdf` — 18 slides, six modules

> **Intent.** A PATLIB colleague who has never used TIP opens this repository and has to
> see, immediately, which six things they are meant to run and in what order. Today they
> meet **265 files and 36 notebooks** and have no way to tell the course from the workshop
> logistics, the current version from the superseded one, or a notebook they should run
> from a script that built something once.
>
> **Scope: structure only.** Which files exist, what they are called, which folder they sit
> in. **No notebook content is rewritten** — not a cell, not a chart, not a word of
> explanation. That is a separate job.

---

## 1 · The spec: what the deck says the course is

The v3 deck is the authority. Six modules, each with a folder printed in the slide corner:

| # | Module | Folder in the deck | Who |
|---|--------|--------------------|-----|
| 1 | Install the assistant, persistently | `1_startwithtip/` | Arne |
| 2 | The Query Library | `2_querylib/` | Arne |
| 3 | PATSTAT Explorer | `3_patstat_explorer/` | Arne |
| 4 | Regional Lead Generation | `4_lead_generation/` | Arne |
| 5 | Patent landscape reports | `5_patentreports/` | Riccardo |
| 6 | What is this patent worth? | `6_ipscore_rebuild/` | Riccardo |

Plus `9_documentation/course/` for the seven handouts (slide 18).

**Every folder the deck names already exists under that name.** The renumbering of
26 August did its job. The problem is not the six folders — it is everything else sitting
beside and inside them.

**Working rule for this plan:** *if no slide points at it, it is not course material.*
That does not mean delete — it means it does not belong in a course module folder.

---

## 2 · The decision that shapes everything else

**Slide 16 names folder `6_ipscore_rebuild/` and promises "the questionnaire and the NPV
for one granted European patent."**

`6_ipscore_rebuild/` has no questionnaire. `0_questionnaire.ipynb` lives in
`7_ipscore_demo/`, imported this morning — and **no slide mentions `7_ipscore_demo/` at
all.** The deck resolves, in the opposite direction, the question left open a few hours
earlier in `plan-workshop-warsaw.md`.

The analysis is already done and still holds:

- Riccardo's v2 differs from module 6 by **~48 source lines**; notebooks 2, 3 and 4 differ
  only by empty trailing cells.
- The genuinely new files are `0_questionnaire.ipynb`, `0_questionnaire_tool.html` and
  `tools/build_questionnaire_html.py`.
- The `kit.EXAMPLE_PATH` pin in notebook 1 is its **intended companion**, not a workaround:
  it keeps notebook 1 reproducing the shipped case while 2–4 follow the questionnaire.
- The redirect of notebooks 2–4 onto the participant's own patent is **the point of the
  feature**, as `plan-workshop-warsaw.md` says plainly.

**Proposed:** bring the three files plus the `EXAMPLE_PATH` pin into `6_ipscore_rebuild/`,
and retire `7_ipscore_demo/`. Module 6 then matches its slide, and the course has one
IPScore module instead of two nearly identical ones.

**This is question 1 for Arne.** Everything below assumes yes; if the answer is no, the
duplicate stays and the repo keeps two 5-notebook chains that differ by 48 lines.

---

## 3 · What is actually there

265 tracked files, ~127 MB, 36 notebooks. Where the weight is:

| Folder | Files | Size | In the deck? |
|---|---|---|---|
| `1_startwithtip/` | 5 | 92 K | ✅ module 1 |
| `2_querylib/` | 12 | 496 K | ✅ module 2 |
| `3_patstat_explorer/` | 3 | 1.5 M | ✅ module 3 |
| `4_lead_generation/` | 26 | 976 K | ✅ module 4 |
| `5_patentreports/` | 94 | **108 M** | ✅ module 5 — but see below |
| `6_ipscore_rebuild/` | 20 | 5.1 M | ✅ module 6 |
| `7_ipscore_demo/` | 20 | 5.8 M | ❌ no slide |
| `9_documentation/` | 81 | 5.2 M | partly — `course/` only |

### 3.1 Module 5 carries three versions of the same report

| Folder | Size | Notebooks | Referenced by |
|---|---|---|---|
| `1_antibiotic_resistance/` | **95 M** | 3 | handouts (×2) — **not** the deck, not the menu |
| `2_antibiotic_resistance_mvp/` | 5.7 M | 4 | handouts (×1) — not the deck, not the menu |
| `2_antibiotic_resistance_rebuild/` | 6.7 M | 4 | **the deck, the live-demo menu** ✅ |

`1_antibiotic_resistance/` alone is **three quarters of the repository**, including a
single 50 MB HTML file (`0_inputs/Antibiotic_Report_FINAL.html`) and seven more over 4 MB.
It is Riccardo's original import; `PROVENANCE.md` names his repo canonical.

### 3.2 The rest of the noise

| What | Where | Why it is noise |
|---|---|---|
| Belgium notebook | `4_lead_generation/3_belgien.ipynb` | German filename, no slide; the deck's "same run for a German region" is `2_national-coverage.ipynb` (DPMA ×37) |
| DPMA research kit | `4_lead_generation/dpma/` (9 files) | Parser, sample XML, a `.zip`, NUTS CSV — build material, not a course step |
| Interface specs & briefs | `4_lead_generation/docs/` (13 files) | DPMAconnect spec PDF, implementation plans, comparison notes — working papers |
| Unit tests | `2_querylib/tests/` (7 files) | Correct to have, wrong to meet as a beginner |
| Legacy examples | `9_documentation/legacy/` (5 files, 740 K) | Airbus / TU Dortmund; CLAUDE.md already says "not shown in Warsaw" |
| Workshop log | `prep_workshop_todo.md` (410 lines) | Preparation log at the repo root, beside the course |

### 3.3 Naming is inconsistent, and module 2 is the outlier

Every module numbers its notebooks `1_`, `2_`, `3_` — **except module 2**:

```
2_querylib/TIP_for_PATLIBs_QueryLib.ipynb              <- no number
2_querylib/TIP_for_PATLIBs_InteractiveQueryDemo.ipynb  <- no number
2_querylib/TIP_for_PATLIBs_QueryLib_core.py
2_querylib/tip4patlibs_core.py                         <- third spelling of the same name
```

Three spellings of the product name in one folder (`TIP_for_PATLIBs`, `tip4patlibs`,
`TIP4PATLIBS`), and the only two notebooks in the course that do not say what order to
run them in.

Elsewhere: `1_Applicant_consolidation_notebook.ipynb` (says "notebook" in a notebook
name), `3_belgien.ipynb` (German), `1_regional-leads.ipynb` (hyphens) against
`1_the_model.ipynb` (underscores).

### 3.4 The clear-outputs convention is not being followed

CLAUDE.md: modules 1–4 clear outputs so participants run them; guest material ships
pre-executed because *the outputs are the deliverable*.

| Notebook | State | Should be |
|---|---|---|
| `2_querylib/TIP_for_PATLIBs_QueryLib.ipynb` | 2 of 4 cells | clear |
| `2_querylib/…InteractiveQueryDemo.ipynb` | 4 of 6 | clear |
| `3_patstat_explorer/1_Applicant_consolidation…` | 6 of 6 | clear |
| `3_patstat_explorer/2_PATSTAT_Explorer_application` | 1 of 1 | clear |
| `4_lead_generation/2_national-coverage.ipynb` | 8 of 9 | clear |

Modules 5 and 6 are **out of scope** here — guest material ships executed, by rule.

---

## 4 · Proposed changes

### A · Retire the duplicate IPScore module *(depends on question 1)*
Move `0_questionnaire.ipynb`, `0_questionnaire_tool.html`,
`tools/build_questionnaire_html.py` and the `EXAMPLE_PATH` pin into `6_ipscore_rebuild/`.
Delete `7_ipscore_demo/`, recording the upstream commit in module 6's `PROVENANCE.md`.
**−20 files, −5.8 MB, −5 notebooks.**

### B · One report version in module 5 *(depends on question 3)*
Keep `2_antibiotic_resistance_rebuild/` — the one the deck and the menu point at.
Remove `1_antibiotic_resistance/` and `2_antibiotic_resistance_mvp/`.
**−~101 MB, −7 notebooks.** Module 5 becomes a single four-notebook chain.

### C · Move working material out of the course
Not deleted — moved to `9_documentation/`, which is already where non-course material
lives:

- `4_lead_generation/docs/` → `9_documentation/lead-generation-research/`
- `4_lead_generation/dpma/` → `9_documentation/lead-generation-research/dpma/`
- `4_lead_generation/3_belgien.ipynb` → `9_documentation/legacy/`
- `prep_workshop_todo.md` → `9_documentation/`

`2_querylib/tests/` **stays** — tests belong with their code; they are simply not numbered
and not in anyone's way.

### D · One naming scheme, applied everywhere
`N_short-lowercase-name.ipynb`, hyphens, no "notebook" in the name, English only:

| Module | Now | Proposed |
|---|---|---|
| 2 | `TIP_for_PATLIBs_QueryLib.ipynb` | `1_query-library.ipynb` |
| 2 | `TIP_for_PATLIBs_InteractiveQueryDemo.ipynb` | `2_interactive-demo.ipynb` |
| 3 | `1_Applicant_consolidation_notebook.ipynb` | `1_applicant-consolidation.ipynb` |
| 3 | `2_PATSTAT_Explorer_application.ipynb` | `2_explorer-app.ipynb` |
| 6 | `1_the_model.ipynb` … | `1_the-model.ipynb` … |

Module 2's Python files follow: `tip4patlibs_core.py` and
`TIP_for_PATLIBs_QueryLib_core.py` resolve to one spelling.

### E · Clear the five notebooks in §3.4
Outputs only. No cell content touched.

### F · A README that is a front door
Today's README is 43 lines and does not lead with the six modules. Replace with the
deck's own table: six rows, one line each, a "start here" pointer at
`1_startwithtip/1_getting-started-with-tip.ipynb`, and the handouts named.

### Net effect

| | Before | After |
|---|---|---|
| Tracked files | 265 | **195** |
| Notebooks in module folders 1–7 | 29 | **17** |
| Working tree | 127 MB | **~22 MB** |
| Notebooks in module 5 | 11 | 4 |
| IPScore modules | 2 | 1 |
| **What `git clone` downloads** | **344 MiB** | **344 MiB — unchanged** |

That last row is the point of question 2. Deleting 101 MB of HTML changes what a beginner
*sees*; it changes nothing about what they *download*, because the blobs stay in history.

---

## 5 · Constraints and acceptance tests

1. **The live-demo menu must stay at 15/15.** `TIP4PATLIBS_LiveDemo_Menu.ipynb` links into
   `7_ipscore_demo/` and `5_patentreports/2_antibiotic_resistance_rebuild/`. Every rename
   and deletion carries a link fix; the 15/15 resolver check is the test.
2. **The handouts hard-code 14 notebook filenames and every folder name.** Renaming
   invalidates the seven rendered PDFs. They must be rebuilt from
   `9_documentation/course/source/*.md` via `build_handouts.py` — and the source `.md`
   edited first. `3_belgien.ipynb` and `1_antibiotic_resistance/` are both named there.
3. **The deck prints folder paths in the slide corners.** The six module folders therefore
   **must not be renamed** — only files inside them. `slides.yaml` → `build_slides.py`
   would otherwise need a rebuild, and the v3 PDF is already distributed.
4. **`9_documentation/ipscore/` cannot be deleted.** Module 6's
   `tools/extract_spec_from_excel.py` reads `IPscore_3.01 WORKHORSE.xlsx` from it as the
   source of truth for `ipscore_spec.json`.
5. **Guest material is never re-run.** CLAUDE.md is explicit: the outputs are the
   deliverable.
6. **Deleting files does not shrink a clone.** The working tree is 127 MB; the packed
   history is **344 MiB**, and that is what `git clone` transfers. Removing 101 MB of HTML
   makes the repo *readable*, not *smaller* to download — see question 2.

---

## 6 · Questions for Arne

**Q1 · Module 6 and the questionnaire.** The deck says module 6 *is* `6_ipscore_rebuild/`
and promises the questionnaire. Merge Riccardo's three files into module 6 and retire
`7_ipscore_demo/` — or keep both and accept two near-identical modules?

**Q2 · Which problem are we solving?** "Too complex to read" is fixed by deleting and
renaming. "It is too heavy to clone onto a machine that gets rebuilt every week" is
**not**: the working tree is 127 MB but the packed history is **344 MiB**, and that is
what every `git clone` on TIP transfers — before and after this cleanup alike. Only a
history rewrite changes it, and that means re-signing every commit and force-pushing a
`main` that took two merges today. Which of the two is the actual pain? If it is both,
the rewrite is a separate job with its own plan, not a step in this one.

**Q3 · Deleting Riccardo's original.** `5_patentreports/1_antibiotic_resistance/` is 95 MB
and 75 % of the repo. It is *his* import, `PROVENANCE.md` names his repo canonical, and he
presents from module 5 tomorrow. Delete it, or leave module 5 alone until after Warsaw?

**Q4 · Ticket and timing.** Still `#PIP-135`, or a new ticket? And does any of this land
before the workshop, or is the branch parked until after 17 September?

---

## 7 · Explicitly out of scope

- Rewriting notebook content, cells, charts or explanatory text
- Renaming the six module folders (constraint 3)
- Re-running or re-generating modules 5 and 6 (constraint 5)
- Touching `.gitignore`, git signing, or branch protection
- Any history rewrite, unless Q2 says otherwise
