# IPScore rebuild — what is this patent worth?

> 🚧 **Under construction — notebook 1 of 4 is ready.** The workshop-ready valuation module is
> **[`7_ipscore/`](../7_ipscore/)**; use that one for the session. This folder is where its
> ideas get rebuilt in the course's own shape.

A clean rebuild of the **ideas behind the EPO IPScore model**: a structured questionnaire that
turns judgement about a patent into a score, a bridge from that score to economic parameters,
and a ten-year discounted cash flow that ends in a Net Present Value.

## Why rebuild something that already works

Module 7 is Riccardo Priore's adaptation and it works well — but it is the one module in this
course that never touches PATSTAT, and the model underneath it is **entirely subjective**: all
40 answers come from a human, and nothing checks a single fact about the patent.

A PATLIB has PATSTAT. Roughly **six of the 40 questions are matters of record** (patent status,
remaining term, geographic coverage, whether this filing consolidates or opens markets, whether
it sits in the applicant's core technology), and about four more can be given honest context.
The other thirty stay expert judgement — and the rebuild says so, on every answer, in the
output. That split is the point of the module.

## Planned shape

| # | Notebook | Answers | Needs | State |
|---|----------|---------|-------|-------|
| 1 | `1_the_model.ipynb` | What the model is, and does our engine reproduce the EPO Excel exactly? | nothing — runs offline | ✅ ready |
| 2 | `2_evidence_from_patstat.ipynb` | For one real patent: what can PATSTAT actually answer? | **TIP / PATSTAT** | planned |
| 3 | `3_valuation_and_scenarios.ipynb` | What is it worth, and which lever moves that number most? | nothing | planned |
| 4 | `4_assemble_tool.ipynb` | One self-contained HTML valuation + one data workbook | nothing | planned |

Two files carry the module: **`ipscore_spec.json`** — the model as data (40 questions, the 8
score→value tables, the EPO's three test patents) — and **`ipscore_kit.py`**, the only place
anything is computed. Run `python ipscore_kit.py` for the acceptance test on its own.
`tools/extract_spec_from_excel.py` re-derives the spec from the EPO workbook; it is a
maintenance script, not part of the course chain.

The full reasoning, the honest question-by-question mapping against PATSTAT, the phasing and
the open decisions are in **[`REBUILD_PLAN.md`](REBUILD_PLAN.md)**. Where the ideas come from
and how attribution works is in **[`PROVENANCE.md`](PROVENANCE.md)**.

## The rule this module is built on

The Excel workbook carries three test patents with its own computed NPVs. The engine has to
reproduce all three — 329,059.4284 / 4,361.2849 / −4,686.3598 — before it is allowed to compute
anything else. That check, applied to Riccardo's engine, once caught a genuine off-by-one bug
that two demo cases had hidden. Checking against the source of truth rather than against your
own previous output is the transferable lesson here.

**IPScore is an EPO tool.** This module is our own implementation of that model; modules 6 and
7 are Riccardo Priore's material and carry his credit.
