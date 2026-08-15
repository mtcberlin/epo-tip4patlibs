# Module 8 — Clean Rebuild Plan (IPScore: what is this patent worth?)

**Goal.** Not to reimplement Riccardo's HTML tools, but to rebuild **the ideas behind IPScore**
as a teachable four-step chain a workshop audience can follow: *"here is how you get, in four
understandable steps, from a patent number to a defensible number — and here is exactly how
much of that number is evidence and how much is judgement."*

**Direction (Arne's steer, 2026-07-24): patent valuation as content.** The subject is what a
patent is worth, where it is weak, and which action moves the number. How the tool is built
stays a side note.

**Reference hierarchy**, in this order:

1. **`7_ipscore/IPscore_3.01 WORKHORSE.xlsx` — the primary reference.** The EPO model itself:
   questions, OEK tables, the cash-flow chain, and three test patents with Excel's own NPVs.
   When anything disagrees, the Excel wins. It is read **once**, by
   `tools/extract_spec_from_excel.py`, into `ipscore_spec.json`; no notebook opens it.
2. **`7_ipscore/` as it stands today** — Riccardo's working tools plus `build/` and
   `BUILD_LOG.md`. Executable ground truth for *how the model behaves*, and the record of a
   real bug found by checking against the Excel.

Both are reference only. Nothing is imported or patched.

---

## 📍 Where we are — session log

**2026-07-24 — Phase 0.** Folder scaffolded, this plan and `PROVENANCE.md` written. Decisions
V1–V9 proposed. No code yet.

**2026-07-24 — Phase 1 done.** Decisions locked (see the table below; V3 changed, V4 and V5
answered). Built and verified offline:

- `tools/extract_spec_from_excel.py` → `ipscore_spec.json` — 40 questions, 8 OEK value tables,
  risk/opportunity flags, and the 3 test patents with the EPO's own NPVs. Re-runnable
  (`--check` compares against the committed spec); not part of the notebook chain.
- `ipscore_kit.py` — the engine: spec loading, `Answer` with its provenance marker, the score
  profile, the score→parameter bridge, the ten-year cash flow, `npv()`, and the shared chart
  palette. `python ipscore_kit.py` runs the acceptance test.
- `1_the_model.ipynb` — the model explained in seven steps, ending in the acceptance test.
  Runs offline; **ships executed**, because the stored output *is* the proof.

**All three EPO test patents reproduce exactly** (329,059.4284 / 4,361.2849 / −4,686.3598;
largest deviation 6·10⁻¹¹, floating-point noise). The engine is verified.

Committed as `f66c69f` — *Module 8 Phase 1: the engine, verified against the EPO workbook*.

**2026-08-15 — Phase 2 done.** The chain now exists end to end, offline.

- `4_assemble_tool.ipynb` — 21 cells, executed, no errors. Hand-scores one patent, computes the
  profile, the eight economic parameters, the ten-year cash flow and the NPV, and assembles
  **`4_tool/ipscore_valuation.html`** (7 sections, 3 inline charts, 4.9 MB, one embedded
  `plotly.js`, **0 iframes, 0 external requests**) plus **`4_tool/ipscore_valuation_data.xlsx`**
  (5 sheets). Opened with `open_html()`.
- Two additions to `ipscore_kit.py`: **`PATSTAT_CANDIDATES`** — the eleven questions a query can
  speak to, each with a strength (`strong` · `good` · `proxy` · `context` · `open`) and what
  notebook 2 will source — and **`answer_table()`**, the 40-row tidy table the report is built
  around. The acceptance test still passes.
- **Provenance is honest and therefore empty.** All forty answers carry `judgement`; the report
  says `0 measured · 0 informed · 40 judgement` on its front section. Notebook 2 is what changes
  that, and the eleven reachable answers already carry a `-> notebook 2 (strength): …` note in
  their `evidence` field — a promise, never a measurement.
- **The launcher cell ships without output**, the same rule module 7 learned the hard way
  (warning 9 in `prep_workshop_todo.md`): run offline, `open_html()` bakes in the *author's*
  filesystem path and the message "jupyter-server-proxy is unavailable here", both of which are
  wrong on TIP. Clear that one cell before every commit.
- **The report was rendered and looked at**, in Chrome, over a local HTTP server (`file://` is
  blocked by the extension). Three rounds of fixes came out of actually seeing it: the worked
  example's `C3` went 4 → 5 so the cash flow covers years 1–9 instead of dying at year 5;
  `D3`/`D4` went 3 → 4 so all six cash-flow components are alive rather than two sitting dead in
  the legend; the radar's radial axis moved to 36° so its tick labels stop colliding with the
  *A — Legal status* label. This closes the open item below — module 8's charts are no longer
  unseen.

**2026-08-15 — Phase 4 done.** `3_valuation_and_scenarios.ipynb` — 14 cells, executed, offline.

- `kit.sensitivity()` varies each of the eight OEK answers across all five levels, one at a
  time, and returns a `LeverResponse` per lever (swing · upside · downside · step up · step
  down), widest first. Two charts: the **tornado**, and **what a single step is worth** — the
  realistic version, since a client rarely moves an answer all the way to the best one.
- The finding the module was built to show, now computed rather than asserted: **the widest
  lever is not the one to work on.** D3 has the largest swing (1,875,011 €) but only 468,753 €
  left to gain; **C2 has the most room (+562,830 €)**; **C3 is already at the best answer**, so
  its entire swing is downside risk. And the tornado carries a labelled zero-width row for *the
  other 32 answers*, which cannot move the number at all.
- Two structural changes came with it:
  - **`worked_example.json`** — the patent, the seven company figures and the forty scores now
    live in one file that notebooks 3 and 4 both read. They can no longer drift, and **V5**
    (swap in a real family from module 6's corpus) becomes an edit to that file alone.
  - **`kit.record_section()` / `kit.load_sections()`** — the optional half of the report
    contract, added at the moment the plan said to add it: when a second producer actually
    existed. Notebook 3 hands over section **700**; notebook 4 slots it between the cash flow
    (600) and the full questionnaire (900), and adds its rows to the workbook. With no
    contribution present the assembler simply builds one section fewer.
- The assembled report is now **8 sections, 5 inline charts, 6 workbook sheets, 0 iframes**.
  Both new charts were rendered and reviewed in a browser.
- **`3_valuation_and_scenarios_output/_report_parts/` is committed on purpose.** It is an
  intermediate, not a deliverable, but committing it makes the shipped `ipscore_valuation.html`
  reproducible without first re-running notebook 3. Do not "tidy" it away. It also means the
  **run order matters** — `1 → 3 → 4` today, `1 → 2 → 3 → 4` once notebook 2 exists — and both
  notebook 4's header and its contract cell now say so.

---

## ▶️ Resume here — everything the next session needs

*Written 2026-07-24 so work can continue from a cold start. Read this section, run the two
commands, then go to "Phase 2, concretely".*

### 30-second orientation

Module 8 rebuilds the **EPO IPScore** valuation model in this course's shape. The engine is
done and provably correct; three of the four notebooks still have to be written. Module 7 is
Riccardo Priore's working version and stays untouched — it is the workshop-ready one until
module 8 proves itself.

### Check that the ground is still solid

```bash
cd 8_ipscore_rebuild
python ipscore_kit.py                            # → 3 PASS, "All three EPO test patents reproduced."
python tools/extract_spec_from_excel.py --check   # → "spec is up to date"
```

If the first fails, the engine broke — fix that before anything else. If the second fails,
either the workbook moved or the spec was hand-edited (it never should be).

### What exists, file by file

| File | What it is | Touch it? |
|---|---|---|
| `ipscore_spec.json` | The model as data: 40 questions, 5 answer texts each, the 8 OEK tables, risk/opportunity flags, the 3 EPO test patents + their NPVs | **Never by hand** — regenerate with the extractor |
| `ipscore_kit.py` | The only place anything is computed. `load_spec` · `Answer` · `profile` · `oek_from_answers` · `Financials` · `cash_flow` · `npv` · `verify` · `PALETTE` · `CHART_LAYOUT` | yes, this is the engine |
| `tools/extract_spec_from_excel.py` | One-off derivation from `7_ipscore/IPscore_3.01 WORKHORSE.xlsx`. Not part of the course chain | only if the spec must change |
| `1_the_model.ipynb` | Notebook 1, executed, 27 cells. Offline | done; edit only for narrative |

### How the pieces fit (the mental model)

Forty answers go in. Thirty-two of them only shape the **profile** (points per section, average
risk, average opportunity). Eight — B5, C2, C3, C6, D1–D4 — are looked up in their OEK table
and become **economic parameters**, which together with seven figures from the company accounts
drive a ten-year cash flow whose discounted sum is the **NPV**. Module 8's own addition is that
every `Answer` carries a provenance marker (`measured` / `informed` / `judgement`), so the
output can show how much of the number is evidence.

### Conventions already set — follow them

- **Plain-language markdown above every code cell.** This is teaching material for PATLIB staff
  who will not learn Python or SQL; explain the step, not the syntax.
- **Branded red header + a "what this notebook does" box** at the top of every notebook — copy
  the one in `1_the_model.ipynb`.
- **Charts use `kit.PALETTE` and `kit.CHART_LAYOUT`**, shown inline with `fig.show()` (never
  `write_html()` only — a pre-executed notebook that shows a reader nothing is the mistake
  module 6 made). `CHART_LAYOUT` uses magic-underscore title keys, so `fig.update_layout(
  **kit.CHART_LAYOUT, title="…")` works.
- **`git check-ignore` any new folder** before assuming it is committed. `build/`, `dist/` and
  `__pycache__/` are swallowed globally.
- Work on `develop`, PR into `main`, SSH remotes.

### The report contract — settled in Phase 2, and different from module 6's

Module 6 merges a pile of charts by an `order` number, because three notebooks scatter figures
across three folders. A valuation cannot be assembled that way: it has a **required shape** —
you cannot show someone an NPV before you have shown them what was assumed to get there. So:

- **Notebook 4 always builds the spine itself** — verdict · patent and company · profile ·
  data reach · the eight money answers · cash flow · all forty answers. Seven sections, fixed
  order, always present.
- **Notebook 2 hands over a better answer set**, not a section: the same forty answers, with
  `provenance="measured"` and a real PATSTAT fact in `evidence` wherever a query decided the
  score. The report shape does not change; the provenance panel stops reading `0 measured`.
- **Notebook 3 hands over one extra section**, the sensitivity ranking. *That* is the moment to
  add a manifest — not before. Writing merge machinery for producers that do not exist yet was
  the one thing Phase 2 deliberately did not do.

### Phase 3, concretely — the next thing to build

`2_evidence_from_patstat.ipynb`, and it is **TIP-only**. Before it can be written, one short
TIP session has to answer O1 and O2 (below) and settle V5 — which family from module 6's
antibiotic-resistance corpus becomes the worked example. Then: the three *strong* questions
first (A1, A3, A5), the three *good* ones next (E1, E2, E7), the proxies last and labelled as
proxies. `kit.PATSTAT_CANDIDATES` already names what each one sources.

Phase 4 is **done** — notebook 3 was built and executed offline on 2026-08-15, ahead of
Phase 3. Only notebook 2 is left, and only it needs TIP.

### Open items — none of them blocking

- **Notebook 4's three charts have been rendered and reviewed** (2026-08-15, Chrome over a
  local HTTP server — `file://` is blocked by the extension). **Notebook 1's two charts still
  have not been**; they remain verified only structurally. Worth one look in the same TIP
  session as O1/O2.
- **Notebook 1 stamps three answers `measured`** (A1, A3, A5) with hand-written evidence
  strings. Harmless there — it illustrates the dataclass, and that notebook's deliverable is
  the acceptance test — but it is the opposite of the standard notebook 4 now sets. Worth
  reconciling before the release; it needs a re-run of notebook 1, so it is not free.
- **Notebooks 1 and 4 ship executed** — deliberate, see the convention note under the decisions
  table. Reverse if module 8 should be run rather than read.
- **O1–O3** (legal-status tables on TIP, `nb_claims` coverage, what a PATLIB is really asked)
  are still open and gate Phase 3. See the end of this file.

---

## What the model actually is (facts, read out of the Excel and the live tools)

1. **40 questions, five sections** — A Legal (8) · B Technology (9) · C Market (9) · D Finance
   (6) · E Strategy (8) — each scored 1–5, 200 points maximum.
2. **Two independent read-outs from the same answers.** A *qualitative* profile (radar per
   section; each question flagged as a risk driver, an opportunity driver, or both — risk
   contributes `-(5-score)/4`, opportunity `(score-1)/4`), and a *financial* one.
3. **Only 8 of the 40 questions carry money.** B5, C2, C3, C6, D1, D2, D3, D4 — the **OEK**
   questions. Each maps a 1–5 answer onto an economic parameter through a fixed table. The
   other 32 questions never touch the NPV at all. *This is the single most surprising fact in
   the model and the best thing to show a room.*
4. **The NPV is a 10-year discounted cash flow** driven by those 8 parameters plus 7 financial
   inputs (turnover, direct and indirect costs, depreciation and its period, sector share,
   discount rate):
   ```
   Liquidity[y] = Revenue[y] − Costs[y] − Investments[y]
                + Regained[y] + Efficiency[y] + InvReduction[y]
   NPV = Σ Liquidity[y] × BT/100 / (1+r)^y      for y = 1 … 10
   ```
   Two invariants that are easy to get wrong: **Investments and InvestmentReduction are
   one-time events** in the first revenue year, not annual; revenue and the regained/efficiency
   terms use a **fractional-year factor** for partial entry and exit years.
5. **The model is entirely subjective on input.** All 40 answers come from a human. Nothing in
   IPScore checks a single fact about the patent. That is the gap module 8 exists to close.

---

## The one idea this rebuild adds: separate evidence from judgement

Module 7 is an island — the only module in the course that never touches PATSTAT. A PATLIB,
however, *has* PATSTAT, and some of these 40 questions are simply matters of record.

Mapped honestly against the real question set:

| Question | What PATSTAT can contribute | Strength |
|---|---|---|
| **A1** What is the patent status? | `granted` flag + publication kind codes across the family | **strong** — this is a lookup, not an opinion |
| **A3** How long is the patent still valid? | earliest filing date + 20 years → nominal remaining term | **strong as an upper bound**; actual lapses need legal-status data (see open question O1) |
| **A5** Does geographical coverage include the relevant markets? | every family member's filing authority — the actual footprint | **strong** for the coverage half; "relevant markets" stays judgement |
| **E1 / E2** Consolidate existing markets, or enter new ones? | this family's jurisdictions against the applicant's historical footprint | **good** — a genuinely new insight, and cheap |
| **E7** Is the patent in the company's core technology areas? | share of the applicant's own families in the same IPC subclass | **good** |
| **A4** How broad are the claims? | claim count, IPC breadth | **weak proxy** — breadth is not count. Show it, label it |
| **B1 / B2** Unique / technically superior? | forward citations received | **weak proxy** — citations measure attention, not superiority |
| **C4** Competitive or substitute products? | size and composition of the IPC neighbourhood | **context, not an answer** |
| **A7** Are legal disputes frequent in these markets? | opposition frequency in that authority/IPC | **open** — depends on O1 |
| the other ~30 | nothing | **judgement, and we say so** |

**So: roughly six questions become evidence-based, four gain useful context, thirty stay
expert judgement.** That ratio *is* the teaching point. A valuation is not automatable; data
narrows the guesswork on the legal and geographic axes and nowhere else. Any tool that hides
that is lying to its user, so module 8 shows the split in the output — every answer carries a
provenance marker: **measured · informed · judgement**.

---

## Architecture — the same four-step chain as module 6

```
8_ipscore_rebuild/
  ipscore_spec.json                 ← the model as data: 40 questions, 8 OEK tables, 3 test patents
  ipscore_kit.py                    ← the one engine: profile, cash flow, NPV, provenance markers,
                                      the shared chart palette              ✅ built
  tools/
    extract_spec_from_excel.py      ← derives the spec from the EPO workbook — run once, by us,
                                      never by a participant                ✅ built
  1_the_model.ipynb                 ← the model explained + verified against the Excel's 3 test patents
                                                                            ✅ built, executed
  2_evidence_from_patstat.ipynb     ← one real patent: what PATSTAT can and cannot answer
  2_evidence_from_patstat_output/
  3_valuation_and_scenarios.ipynb   ← the valuation + which lever actually moves the NPV
                                                                            ✅ built, executed
  3_valuation_and_scenarios_output/ ← _report_parts/: section 700 for the assembler  ✅ built
  worked_example.json               ← the one worked example both nb3 and nb4 read   ✅ built
  4_assemble_tool.ipynb             ← one self-contained HTML deliverable + one data workbook
                                                                            ✅ built, executed
  4_tool/                                                                   ✅ built
    ipscore_valuation.html          ← opened with open_html(); 7 sections, 0 iframes
    ipscore_valuation_data.xlsx     ← one sheet per step: answers, parameters, cash flow, sensitivity
  PROVENANCE.md  REBUILD_PLAN.md  README.md
```

Notebook 1 writes no output folder: it proves the engine, and nothing downstream reads its
numbers. Notebooks 2 and 3 do feed notebook 4, so they keep the one-folder-per-notebook rule.

Same conventions as module 6: one output folder per notebook, a small kit module holding the
contract, a final notebook that assembles, `open_html()` for the deliverable, and **a short
plain-language markdown cell above every code cell** — it is teaching material.

### Step by step

**1 · The model.** Load the questions and OEK tables, walk through the scoring and the cash
flow with a worked example, and end with the acceptance test: reproduce Excel's three test
patents (329,059.4284 / 4,361.2849 / −4,686.3598). The step is also the honest-verification
lesson module 7 already tells — here it is executable rather than narrated.

**2 · Evidence from PATSTAT.** Take one real patent family, pull what the table above says is
knowable, and pre-fill those answers with the fact behind each one attached. Everything else is
left explicitly blank and marked *judgement*. This is the only notebook that needs TIP.

**3 · Valuation and scenarios.** Complete the questionnaire, compute score, profile and NPV —
then the part Riccardo's planner does in reverse: vary each of the 8 OEK levers across its five
levels and rank them by how much the NPV moves. A one-line answer to *"what should we do about
it?"*, computed rather than asserted, and honest about the fact that only 8 of 40 answers can
move the number at all.

**4 · Assemble.** Narrative + figures + the answer table with provenance markers → one
self-contained HTML file (single embedded plotly.js, no iframes — the constraint module 6
already proved) plus a workbook with one sheet per step.

---

## The engine question — one source of truth (V3, V4 · settled)

Riccardo's tools compute in JavaScript inside the HTML. If module 8 computed in Python *and*
shipped an interactive page, the formulas would exist twice and drift.

**Settled: Python is the only engine.** V4 came back *report first*, so the deliverable is a
computed valuation report — no page-side arithmetic, no second implementation, nothing to keep
in sync. `ipscore_kit.py` is the single authority; `ipscore_spec.json` is the single copy of
the model's data. Interactivity is a later option, and if it ever arrives, the rule is that any
page-side formula must pass the same acceptance test as Python.

**The Excel is a source, not a dependency.** `tools/extract_spec_from_excel.py` reads the
workbook once and writes `ipscore_spec.json`; from then on module 8 stands alone and module 7
could be retired without breaking it. The cost of that independence is that the spec can go
stale silently — so the extractor stays in the repo with a `--check` mode that re-derives and
compares, and the three expected NPVs travel *inside* the spec rather than as hand-typed
constants.

---

## Phasing (so there is always something that runs)

- **Phase 0 — scaffold + plan.** ← *done, 2026-07-24*
- **Phase 1 — the engine and its proof.** ← *done, 2026-07-24.* Spec extracted,
  `ipscore_kit.py` written, notebook 1 executed, all three EPO test patents reproduced.
- **Phase 2 — the deliverable.** ← *done, 2026-08-15.* Notebook 4: one hand-scored patent →
  `4_tool/ipscore_valuation.html` + `ipscore_valuation_data.xlsx`, opened with `open_html()`.
  Built and executed **offline**, and the report was rendered in a browser and reviewed.
- **Phase 3 — the evidence layer.** Notebook 2 against PATSTAT: the six strong questions first,
  the four proxies second, each with its provenance marker. TIP-only.
- **Phase 4 — scenarios.** ← *done, 2026-08-15.* Notebook 3: the sensitivity ranking over the
  8 OEK levers, plus `worked_example.json` and the `record_section` contract. Offline.
- **Phase 5 — polish.** Narrative, branded header, dry-run against the clock, and a side-by-side
  sanity check against Riccardo's tools on the same inputs (they should agree — same model).

After Phase 2 there is a demonstrable artifact; after each later phase there still is.

## Division of labour — better than module 6's

Module 6 could only ever be verified on TIP, because every analysis queries PATSTAT. Here
**three of the four notebooks (1, 3, 4) need no database at all** and can be authored *and
executed* offline. Only notebook 2 is TIP-only. So the loop is: build and verify offline, hand
Arne exactly one notebook to run on TIP, commit outputs.

---

## Decisions — locked 2026-07-24 ✅

| # | Question | Decision |
|---|---|---|
| **V1** | Structure? | ✅ **Four-step chain** mirroring module 6 (model → evidence → scenarios → assemble), one output folder per notebook that produces data, an `ipscore_kit.py` contract. |
| **V2** | What is rebuilt? | ✅ **The EPO model**, re-implemented in Python from the Excel. Riccardo's help text, € benchmarks and demo narratives are **not** copied — module 8 writes its own. |
| **V3** | Where does the engine live? | ✅ **Changed from the original proposal.** The Excel is read **once** by `tools/extract_spec_from_excel.py` into `ipscore_spec.json`; no notebook opens the workbook, and module 8 does not depend on module 7 at runtime. Python is the single engine. |
| **V4** | Interactive tool or computed report? | ✅ **Report first.** One engine, no formulas in two languages. Interactivity only if the workshop turns out to need it. |
| **V5** | Which patent is the worked example? | ✅ **A family from module 6's antibiotic-resistance corpus**, so the course links up: the landscape says where a field stands, module 8 values one patent inside it. Picked in Phase 3, when notebook 2 meets PATSTAT. |
| **V6** | Languages? | ✅ **English only.** The Italian versions stay Riccardo's; we do not take on translations. |
| **V7** | Relationship to module 7? | ✅ **Module 7 stays untouched and workshop-ready.** Module 8 is a sibling, not a replacement. Retirement (or merge) decided only after module 8 proves itself on TIP. |
| **V8** | Scope of the evidence layer? | ✅ **The six strong questions + four labelled proxies**, never more. Every answer in the output carries measured / informed / judgement. |
| **V9** | Numbering — a top-level `8_`? | ✅ As instructed. Marked *under construction* in `README.md` until Phase 2 lands. |

### Two conventions this module sets, worth a second look before the release

- **Notebook 1 ships executed.** Modules 1–5 clear outputs so participants run them; modules 6
  and 7 ship pre-executed because they are read as reports. Notebook 1 is a *proof* — the
  stored output is the evidence that the engine matches the EPO — so it keeps its outputs.
  Reverse this if module 8 is meant to be run rather than read.
- **`tools/` rather than `build/`.** `build/` is ignored globally by `.gitignore`, the same
  trap module 7 had to work around with a negation rule. Any new folder gets a
  `git check-ignore` before it is assumed committed.

## Open questions to resolve before Phase 3

- **O1 — Does TIP's PATSTAT edition carry legal-event / legal-status tables?** Decides how far
  A1, A3 and A7 can go: with them, "still in force" and opposition history become facts; without
  them, A3 is a nominal upper bound and A7 drops out. Check on TIP before building notebook 2.
- **O2 — Is `nb_claims` populated** for the authorities we care about? Decides whether A4 gets
  even a weak proxy.
- **O3 — What does a PATLIB actually get asked?** If the real client question is "should I renew
  this?" rather than "what is it worth?", the renewal-cost side deserves more weight than
  IPScore gives it. Worth one conversation with Riccardo (see `prep_workshop_todo.md` §5).
