# IPScore rebuild — what is this patent worth?

> 🚧 **All four notebooks exist.** Notebooks 1, 3 and 4 run anywhere and ship executed;
> **notebook 2 needs one run on EPO TIP** and ships without outputs until then. The chain
> runs end to end:
> a scored patent comes out as one self-contained HTML valuation plus a data workbook. The
> workshop-ready valuation module is still **[`9_documentation/ipscore/`](../9_documentation/ipscore/)**; use that one for
> the session. This folder is where its ideas get rebuilt in the course's own shape.

A clean rebuild of the **ideas behind the EPO IPScore model**: a structured questionnaire that
turns judgement about a patent into a score, a bridge from that score to economic parameters,
and a ten-year discounted cash flow that ends in a Net Present Value.

## Why rebuild something that already works

The IPScore reference (`9_documentation/ipscore/`) is Riccardo Priore's adaptation and it works well — but it was the one part of this
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
| 2 | `2_evidence_from_patstat.ipynb` | For one real patent: what can PATSTAT actually answer? | **TIP / PATSTAT** | ✅ ready — run on TIP, all 11 reachable answers resolve |
| 3 | `3_valuation_and_scenarios.ipynb` | What is it worth, and which lever moves that number most? | nothing | ✅ ready |
| 4 | `4_assemble_tool.ipynb` | One self-contained HTML valuation + one data workbook | nothing | ✅ ready |

Run notebook 4 and you get `4_tool/ipscore_valuation.html` — **nine sections, six inline
charts**, one embedded copy of `plotly.js`, no iframes and no internet — plus
`4_tool/ipscore_valuation_data.xlsx`, one sheet per step. It opens inside TIP through the
course's shared `open_html()` helper.

**Run order is `1 → 2 → 3 → 4`.** Notebook 2 writes the measured answer set that 3 and 4 read;
without it they fall back to the adviser's first pass and say so in the report.

Because notebook 2 does not exist yet, that report scores its patent **entirely by hand** and
says so in large type: `0 measured · 0 informed · 40 judgement`. Eleven answers are marked as
reachable by a PATSTAT query — three of them strongly — and notebook 2 is what replaces exactly
those with facts. The gap is the point, not an oversight.

Run notebook 3 first and the report gains a **sensitivity section**: the tornado over the eight
levers, and what exactly one better answer is worth. Its finding is the kind a client can act
on — in the shipped example the *widest* lever is not the one worth working on, because its
answer is already the best one on the scale.

Three files carry the module: **`worked_example.json`** — the one patent, forty scores and seven
company figures that notebooks 3 and 4 both read, so swapping in a real family is a single edit;
**`ipscore_spec.json`** — the model as data (40 questions, the 8
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
