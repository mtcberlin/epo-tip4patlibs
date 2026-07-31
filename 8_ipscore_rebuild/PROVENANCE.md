# Provenance — Module 8 (IPScore rebuild)

**Status: Phase 1 complete** — the engine and notebook 1 exist and are verified. The plan lives
in [`REBUILD_PLAN.md`](REBUILD_PLAN.md); this file records where the ideas come from and who
owns what, so attribution stays clean.

## What this module is

A **clean rebuild of the ideas behind IPScore** — a structured questionnaire that turns
judgement about a patent into a score, a bridge from that score to economic parameters, and a
discounted cash-flow that ends in a Net Present Value. Rebuilt in this course's own shape
(explained notebooks → one self-contained deliverable opened with `open_html()`), the way
module 6's rebuild was done for landscape reports.

It is **not** a translation of Riccardo's HTML tools into Python, and not a fork of them.

## What it is *not* allowed to touch

`7_ipscore/` stays exactly as it is — Riccardo Priore's imported material, workshop-ready,
the **working reference**. Same rule as module 6: the rebuild lives beside the original, the
original keeps running, and whether module 7 is ever retired is a separate decision taken
after module 8 has proven itself on TIP.

## Lineage of the ideas

| What | Where it comes from | Status here |
|---|---|---|
| The 40 questions, 5 sections, 1–5 scoring | **EPO IPScore 3.01** (`7_ipscore/IPscore_3.01 WORKHORSE.xlsx`) | the model we rebuild — EPO's, not ours |
| The 8 OEK score→value tables (B5, C2, C3, C6, D1–D4) | same Excel, *Adapted questions and answers* sheet | reused verbatim; they encode domain judgement, not arithmetic |
| The 10-year cash-flow and NPV formula chain | same Excel, *Financial calculations* sheet | re-derived and re-implemented in Python |
| The 3 built-in test patents and their Excel-computed NPVs | same Excel, *Financial results* sheet | **the acceptance test** — see below |
| Risk / opportunity flags per question | same Excel | reused |
| The idea of working *backwards* from an NPV target | **Riccardo Priore's** NPV Target Planner (`7_ipscore/NPV_Target_Planner_EN.html`) | his contribution, rebuilt as a sensitivity analysis |
| Plain-language help text, € benchmarks, demo narratives | **Riccardo Priore**, authored directly in his HTML | **not copied.** Module 8 writes its own |
| The build pipeline (JSON + Jinja2 → single-file HTML), the Node syntax check, the Excel cross-check | **Riccardo Priore** (`7_ipscore/build/`) | the *method* is adopted; the code is re-authored |

## Attribution, once this ships

- **IPScore is an EPO tool.** Any header, report or generated page must say so.
- Module 8 is **our implementation of the EPO model**, authored in this repository. It does not
  carry *created by Riccardo Priore* — that credit belongs to modules 6 and 7, to his material.
- Riccardo is credited as the source of the **interactive adaptation and the verification
  method** this rebuild learned from. He should see the plan before module 8 is published; the
  questions to put to him are collected in `prep_workshop_todo.md` §5.

## The one hard acceptance test

The Excel carries three test patents with its own computed NPVs. Riccardo's engine reproduces
them exactly, and getting there caught a real off-by-one bug (`avgRev`, see
`7_ipscore/BUILD_LOG.md`). **Module 8's engine must reproduce the same three numbers before it
is allowed to compute anything else:**

| Test patent | Expected NPV |
|---|---|
| Patent 1 | 329,059.4284 |
| Patent 2 | 4,361.2849 |
| Patent 3 | −4,686.3598 |

Verified independently on TIP on 2026-07-24 via `7_ipscore/build/verify_against_excel.py`.
That script reads the Excel directly and is the pattern to copy — not the numbers, the
*habit* of checking against the source of truth rather than against your own previous output.

## Data

The Excel workbook stays where it is (`7_ipscore/IPscore_3.01 WORKHORSE.xlsx`) and module 8
keeps no second copy of it. It is read **once**, by `tools/extract_spec_from_excel.py`, into
`ipscore_spec.json`; the notebooks then run against that file alone. So the *content* of the
questionnaire and the OEK tables remains EPO's, extracted rather than retyped, and the module
still stands on its own if module 7 is ever retired. Re-derive and compare at any time with
`python tools/extract_spec_from_excel.py --check`.

PATSTAT access is the standard course route (`PatstatClient(env='PROD')`, PATSTAT Global
Autumn 2025).

## What was built, and how it was checked (2026-07-24)

`ipscore_kit.py` re-implements the workbook's 'Financial calculations' chain in Python: the
fractional entry/exit year, the six liquidity components, the one-time investment effects in
the launch year, and the ten-year discount. It reproduces all three EPO test patents to within
floating-point noise. Risk and opportunity follow the workbook's own 'RiskOpportunity
Calculation' sheet — `(5 − score) × −0.25` and `(score − 1) × 0.25`, averaged over the flagged
questions only.

Riccardo's `verify_against_excel.py` was read as prior art for *which* cells in the workbook
matter; the formula chain here was re-derived from the sheet itself, and the two agree.
