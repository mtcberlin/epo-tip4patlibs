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
   When anything disagrees, the Excel wins.
2. **`7_ipscore/` as it stands today** — Riccardo's working tools plus `build/` and
   `BUILD_LOG.md`. Executable ground truth for *how the model behaves*, and the record of a
   real bug found by checking against the Excel.

Both are reference only. Nothing is imported or patched.

---

## 📍 Where we are — session log

**2026-07-24 — Phase 0.** Folder scaffolded, this plan and `PROVENANCE.md` written. Decisions
V1–V9 below are **proposed, not locked** — they need Arne's go, the way D1–D8 were locked for
module 6. No code yet.

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
  ipscore_kit.py                    ← the one engine: questions, OEK tables, cash flow, NPV,
                                      the record() contract, provenance markers
  1_the_model.ipynb                 ← the model explained + verified against the Excel's 3 test patents
  1_the_model_output/
  2_evidence_from_patstat.ipynb     ← one real patent: what PATSTAT can and cannot answer
  2_evidence_from_patstat_output/
  3_valuation_and_scenarios.ipynb   ← the valuation + which lever actually moves the NPV
  3_valuation_and_scenarios_output/
  4_assemble_tool.ipynb             ← one self-contained HTML deliverable + one data workbook
  4_tool/
    ipscore_valuation.html          ← opened with open_html()
    ipscore_valuation_data.xlsx     ← one sheet per step: answers, parameters, cash flow, sensitivity
  PROVENANCE.md  REBUILD_PLAN.md  README.md
```

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

## The engine question — one source of truth (V3)

Riccardo's tools compute in JavaScript inside the HTML. If module 8 computes in Python *and*
ships an interactive page, the formulas exist twice and will drift.

**Proposal.** `ipscore_kit.py` is the single authority. The question texts and all OEK/scoring
tables live in one JSON that the kit emits, so **the data cannot drift** — the page and Python
read the same file. Where the page needs to recompute live in the browser, its formulas are
covered by the same acceptance test as Python: both must reproduce the three Excel patents, and
notebook 4 fails loudly if either does not. Formulas may exist twice; they may never disagree
silently.

If interactivity turns out not to be needed (V4 below), this collapses to Python only — one
engine, no page-side arithmetic — which is materially simpler and is the default until Arne
says otherwise.

---

## Phasing (so there is always something that runs)

- **Phase 0 — scaffold + plan.** ← *done, 2026-07-24*
- **Phase 1 — the engine and its proof.** `ipscore_kit.py` + notebook 1, ending in the Excel
  acceptance test. **Runs offline** — no PATSTAT, so it can be verified here before it ever
  reaches TIP. This is the spine; nothing else is worth building until the three numbers match.
- **Phase 2 — the deliverable.** A minimal notebook 4: one hand-scored patent → the assembled
  HTML + workbook, opened with `open_html()` on TIP. Proves the whole chain end to end while it
  is still small — the same trick that made module 6's MVP useful.
- **Phase 3 — the evidence layer.** Notebook 2 against PATSTAT: the six strong questions first,
  the four proxies second, each with its provenance marker. TIP-only.
- **Phase 4 — scenarios.** Notebook 3: the sensitivity ranking over the 8 OEK levers.
- **Phase 5 — polish.** Narrative, branded header, dry-run against the clock, and a side-by-side
  sanity check against Riccardo's tools on the same inputs (they should agree — same model).

After Phase 2 there is a demonstrable artifact; after each later phase there still is.

## Division of labour — better than module 6's

Module 6 could only ever be verified on TIP, because every analysis queries PATSTAT. Here
**three of the four notebooks (1, 3, 4) need no database at all** and can be authored *and
executed* offline. Only notebook 2 is TIP-only. So the loop is: build and verify offline, hand
Arne exactly one notebook to run on TIP, commit outputs.

---

## Decisions — proposed, awaiting sign-off ⬜

| # | Question | Proposal |
|---|---|---|
| **V1** | Structure? | ⬜ **Four-step chain** mirroring module 6 (model → evidence → scenarios → assemble), one output folder per notebook, a `ipscore_kit.py` contract. |
| **V2** | What is rebuilt? | ⬜ **The EPO model**, re-implemented in Python from the Excel. Riccardo's help text, € benchmarks and demo narratives are **not** copied — module 8 writes its own. |
| **V3** | Where does the engine live? | ⬜ **Python is the single authority**; tables shared as one JSON; any page-side arithmetic must pass the same Excel acceptance test. |
| **V4** | Does the deliverable have to be *interactive*, or is a computed valuation report enough? | ⬜ **Report first** (simpler, one engine). Interactivity added later only if the workshop needs it. **Needs Arne's answer — it changes Phase 2 materially.** |
| **V5** | Which patent is the worked example? | ⬜ **Open.** Proposal: a family from module 6's antibiotic-resistance corpus, so the course links up — the landscape says where a field stands, module 8 then values one patent inside it. Alternative: a patent Arne wants on stage. |
| **V6** | Languages? | ⬜ **English only.** The Italian versions stay Riccardo's; we do not take on translations. |
| **V7** | Relationship to module 7? | ⬜ **Module 7 stays untouched and workshop-ready.** Module 8 is a sibling, not a replacement. Retirement (or merge) decided only after module 8 proves itself on TIP. |
| **V8** | Scope of the evidence layer? | ⬜ **The six strong questions + four labelled proxies**, never more. Every answer in the output carries measured / informed / judgement. |
| **V9** | Numbering — a top-level `8_`? | ⬜ As instructed. Note it makes module 8 look like a finished course module in `README.md`; it is marked *under construction* there until Phase 2 lands. |

## Open questions to resolve before Phase 3

- **O1 — Does TIP's PATSTAT edition carry legal-event / legal-status tables?** Decides how far
  A1, A3 and A7 can go: with them, "still in force" and opposition history become facts; without
  them, A3 is a nominal upper bound and A7 drops out. Check on TIP before building notebook 2.
- **O2 — Is `nb_claims` populated** for the authorities we care about? Decides whether A4 gets
  even a weak proxy.
- **O3 — What does a PATLIB actually get asked?** If the real client question is "should I renew
  this?" rather than "what is it worth?", the renewal-cost side deserves more weight than
  IPScore gives it. Worth one conversation with Riccardo (see `prep_workshop_todo.md` §5).
