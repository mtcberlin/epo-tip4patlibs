# IPScore rebuild — what is this patent worth?

> 🚧 **All four notebooks exist.** Notebooks 1, 3 and 4 run anywhere and ship executed;
> **notebook 2 needs one run on EPO TIP** and ships without outputs until then. The chain
> runs end to end:
> a scored patent comes out as one self-contained HTML valuation plus a data workbook. The
> workshop-ready valuation module is still **[`7_ipscore/`](../7_ipscore/)**; use that one for
> the session. This folder is where its ideas get rebuilt in the course's own shape.

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
| 0 | `0_questionnaire.ipynb` | Enter your own patent, company figures and 40 answers | nothing — a clickable form or plain editable cells | ✅ ready, optional |
| 1 | `1_the_model.ipynb` | What the model is, and does our engine reproduce the EPO Excel exactly? | nothing — runs offline | ✅ ready |
| 2 | `2_evidence_from_patstat.ipynb` | For one real patent: what can PATSTAT actually answer? | **TIP / PATSTAT** | ✅ ready — run on TIP, all 11 reachable answers resolve |
| 3 | `3_valuation_and_scenarios.ipynb` | What is it worth, and which lever moves that number most? | nothing | ✅ ready |
| 4 | `4_assemble_tool.ipynb` | One self-contained HTML valuation + one data workbook | nothing | ✅ ready |

### Notebook 0 — the front door (optional, two ways in)

`0_questionnaire.ipynb` gets the patent, the seven company figures, and the 40 IPScore answers
into the module, offering two independent ways in — use one, not both, then run its shared
save step:

* **Option A — the clickable questionnaire.** `0_questionnaire_tool.html` (built by
  `tools/build_questionnaire_html.py`, same generated-not-hand-edited pattern as the Dennemeyer
  / module 7 tools) is a standalone, paginated HTML form — patent, company figures, then the 40
  questions section by section. It never talks to a kernel while you fill it in: clicking and
  typing there is plain browser JavaScript. Its last page downloads a `questionnaire.json` file;
  drop that into `0_questionnaire_upload/` (JupyterLab's file browser, drag-and-drop or Upload)
  and notebook 0's loader cell picks up whatever is in that folder, no renaming or path needed.
  This is the one to hand to someone else, or just to fill in as a form.
* **Option B — plain editable cells.** The patent, financials and scores as literal Python
  dicts, the same style as notebook 1's own worked example — edit the values directly in the
  cell text and run it.

Both designs exist because two more interactive designs were tried *inside the notebook* first,
and both failed on this platform in a way that matters: an `ipywidgets` form rendered fine but
never synced an edit back to the kernel, and sequential `input()` prompts rendered a real text
box but the reply never reached the kernel either — the cell just hung, whether you typed
something or accepted the default. Option A moves data entry outside the kernel entirely (a
plain file hand-off instead of a live connection); Option B has no round trip to fail at all.

Whichever option you use, the last cell saves everything to
`0_questionnaire_output/questionnaire.json` and prints a table of exactly what changed from the
previous save — a row marked "—" is the untouched previous value, not something you deliberately
confirmed.

Skip it entirely and notebooks 1–4 behave exactly as shipped. **Notebook 1 always reproduces
the shipped EP3074539B1 example** regardless of what notebook 0 has saved — it pins to
`ipscore_kit.EXAMPLE_PATH` explicitly, so its own acceptance test and worked walkthrough never
break. **Notebooks 2, 3 and 4 need no edit at all**: `ipscore_kit.load_worked_example()` prefers
`0_questionnaire_output/questionnaire.json` over `worked_example.json` the moment it exists, and
all three already call it with no argument. One safety check comes with this: `load_answers()`
only trusts a previously-saved `evidence_answers.json` if its patent's `docdb_family_id` matches
what notebook 0 currently holds — switch to a different patent and it correctly falls back to
your first-pass answers rather than silently keeping the old patent's measured ones, and says so
in the label.

Run notebook 4 and you get `4_tool/ipscore_valuation.html` — **nine sections, six inline
charts**, one embedded copy of `plotly.js`, no iframes and no internet — plus
`4_tool/ipscore_valuation_data.xlsx`, one sheet per step. It opens inside TIP through the
course's shared `open_html()` helper.

**Run order is `(0) → 1 → 2 → 3 → 4`**, notebook 0 optional. Notebook 2 writes the measured
answer set that 3 and 4 read; without it they fall back to the adviser's first pass and say so
in the report.

Because notebook 2 does not exist yet, that report scores its patent **entirely by hand** and
says so in large type: `0 measured · 0 informed · 40 judgement`. Eleven answers are marked as
reachable by a PATSTAT query — three of them strongly — and notebook 2 is what replaces exactly
those with facts. The gap is the point, not an oversight.

Run notebook 3 first and the report gains a **sensitivity section**: the tornado over the eight
levers, and what exactly one better answer is worth. Its finding is the kind a client can act
on — in the shipped example the *widest* lever is not the one worth working on, because its
answer is already the best one on the scale.

Four files carry the module: **`worked_example.json`** — the shipped patent, forty scores and
seven company figures, always what notebook 1 reproduces;
**`0_questionnaire_output/questionnaire.json`** — the same shape, written by notebook 0, and
what notebooks 2, 3 and 4 read instead the moment it exists;
**`ipscore_spec.json`** — the model as data (40 questions, the 8 score→value tables, the EPO's
three test patents) — and **`ipscore_kit.py`**, the only place anything is computed. Run
`python ipscore_kit.py` for the acceptance test on its own. `tools/extract_spec_from_excel.py`
re-derives the spec from the EPO workbook; it is a maintenance script, not part of the course
chain.

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
