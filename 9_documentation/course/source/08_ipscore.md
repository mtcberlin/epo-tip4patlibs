# Module 8 — What is this patent worth?

*45-minute block · TIP4PATLIBS course material* · **core path**

> **Scope.** This block covers `1_the_model.ipynb` and a guided read of the finished valuation
> report. The implementation chain — measuring answers against PATSTAT, the scenario analysis, and
> assembling the tool — is a second block, deferred to `08_ipscore_part2.md`. You leave this block
> with the argument, not with the code.

> **How to read this document.** The running text addresses **you, the participant**.
> Boxes marked 🎓 are for whoever is **running the session**; boxes marked ⚠️ are traps that
> have caught people before.

> **IPScore is an EPO tool.** This module is the course's own implementation of the IPScore 3.01
> model, verified against the EPO's workbook. Module 7 is Riccardo Priore's adaptation of the same
> tool and carries his credit.

---

## Learning objective

**I can explain how a patent valuation is produced, run one, and say for every part of the number
whether it is evidence or judgement.**

## Prerequisites

- **Module 1** — TIP is running. (Notebook 1 itself runs anywhere; it needs no database.)
- **Module 4** — you are used to marking which part of an answer was a decision you made.
- Helpful, not required: **module 6**, whose antibiotic-resistance corpus this patent came from.

## Sub-objectives

By the end you can:

1. **Describe the model in one sentence**: 40 questions on a 1–5 scale → a profile and a ten-year
   discounted cash flow → a Net Present Value.
2. **Name the eight questions that carry money**, and explain why the other 32 cannot move the
   number by a cent.
3. **Read the risk/opportunity profile** and say what it does and does not tell a client.
4. **Explain the three provenance markers** — `measured`, `informed`, `judgement` — and state what
   the shipped valuation's split actually is.
5. **State the acceptance-test rule**: check against the source of truth, not against your own
   previous output.

## Material

| | |
|---|---|
| Folder | `6_ipscore_rebuild/` |
| This block | `1_the_model.ipynb` (seven steps, runs offline) · `4_tool/ipscore_valuation.html` (the finished report) |
| Second block | `2_evidence_from_patstat` · `3_valuation_and_scenarios` · `4_assemble_tool` — see `08_ipscore_part2.md` |
| The engine | `ipscore_kit.py` · the model as data in `ipscore_spec.json` · the worked patent in `worked_example.json` |
| Ships | pre-executed |

---

## Phase 1 · Introduction (≈ 7 min)

### The question this module answers

> *A client puts a granted European patent on the table and asks: "what is it worth?"*

Let the room answer for two minutes. You will get renewal costs, you will get comparable licence
rates, you will get "it depends", and you will get someone saying the question is unanswerable.

Then give the model's answer, because it is a good one:

> **A patent is not worth anything by itself. It is worth what it lets a company earn — or stop
> losing — over the years it is still in force.**

**IPScore**, developed by the EPO, turns that sentence into a procedure. Answer 40 structured
questions about the patent on a 1–5 scale, add seven figures from the company's accounts, and the
model returns two things: a **profile** — where this patent is strong and where it is exposed —
and a **number**, the Net Present Value of the technology it protects.

This block opens that machine and shows every wheel. And it ends somewhere uncomfortable, which is
the reason the module sits at the end of the course rather than module 6:

> **The engine is exact. Its inputs are opinions.** All 40 answers come from a person. Nothing in
> IPScore checks a single fact about the patent — not whether it is granted, not how long it runs,
> not where it is in force. An exact machine fed opinions produces a very confident-looking
> opinion.

A PATLIB, however, has PATSTAT. That is where the module goes.

| | Teaching and learning activity | ⏱ |
|---|---|---|
| Opening | Trainer poses the valuation question; room proposes methods | 2 min |
| Tension | Trainer states the model's premise — worth = what it lets a company earn — and that this is answerable | 2 min |
| Framing | Trainer names the discomfort up front: the number is exact and its inputs are opinions. That is what the module is about | 3 min |

> 🎓 **Trainer.** Do not oversell the model and do not undersell it. It is a good structured
> procedure for a hard question, and every valuation produced with it anywhere in the world rests
> entirely on judgement. Both halves have to be said in the same breath, or the module lands as
> either a sales pitch or a debunking. It is neither.

---

## Phase 2 · Working through (≈ 28 min)

### Part A — The model (19 min) · `1_the_model.ipynb`

Seven steps. It runs offline — no PATSTAT, no credentials.

**Step 1 · The questionnaire (3 min).** 40 questions in five sections, each on a 1–5 scale, so
40 × 5 = **200 points** maximum.

| | Section | Asks about |
|---|---|---|
| **A** | Legal status | Is it granted, how long does it run, how broad, where does it apply |
| **B** | Technology | Is it new, is it better, can it be worked, how does it fit the company |
| **C** | Market conditions | Is there a market, is it growing, who else is in it |
| **D** | Finance | What does it cost to develop, produce, and equip |
| **E** | Strategy | Does this patent serve what the company is actually trying to do |

Each question ships with its **five answer options**, so that two people scoring the same patent
mean the same thing by "4".

**Step 2 · The surprise (5 min).** This is the single most important thing in the module, and the
least obvious.

> **Of the 40 questions, exactly 8 feed the financial model.** The EPO workbook marks them *OEK* —
> economic-model questions — and each maps a 1–5 answer onto a concrete economic quantity. A "3"
> on market growth does not mean three points; it means **5% growth per year**.
>
> **The other 32 questions never touch the Net Present Value at all.** You can change all 32 from
> 1 to 5 and the number at the bottom does not move by a cent.

The eight are **B5** (years to market), **C2** (market growth), **C3** (life expectancy of the
technology), **C6** (extra turnover), and **D1–D4** (the four finance questions).

> 🎓 **Trainer.** Spend the time here. This is the fact that changes how a PATLIB runs a valuation
> meeting: it tells you exactly where a discussion about the number can be productive and where it
> cannot. A client arguing about question E4 is arguing about the profile, not about the money —
> and they deserve to be told that.

**Step 3 · The profile and the provenance markers (4 min).** The notebook now scores a **real
patent**: `EP3074539B1`, *"Method for detecting and characterising a microorganism"*, held by
**Q-Linea AB** of Uppsala — rapid identification and antibiotic-susceptibility testing of bacteria,
picked out of **module 6's corpus**. The two modules describe the same field: module 6 maps where
antimicrobial-resistance research stands, module 8 values one patent inside it.

The 40 answers shipped here are **an adviser's first pass** — what a person writes down in a first
session with a client, before checking anything.

Each answer carries a **provenance marker**. This is the course's one addition to the EPO model:

| Marker | Means |
|---|---|
| `measured` | a PATSTAT query decided this — nobody's opinion is involved |
| `informed` | data narrowed the choice, but a person still picked the level |
| `judgement` | expert opinion, and nothing else |

> IPScore as the EPO ships it has no such marker, because it does not need one: **all forty answers
> are always judgement.** That is the honest description of every IPScore valuation in existence.

The profile itself is points per section plus two averages — **risk** (how much worse than perfect
each flagged aspect is) and **opportunity** (how much upside it offers). The notebook shows the
arithmetic; what matters in the room is that both are averages over *flagged* questions only, so
they describe the patent's shape and never the money.

**Step 4–5 · The accounts and the cash flow (5 min).** The score alone cannot produce a Euro amount
— it has no idea how big the company is. So the financial half adds **seven figures from the annual
accounts** (turnover, costs, depreciation, the share of the business affected, the discount rate).

Note what is *not* among them: **nothing about the patent**. The accounts describe the company; the
eight OEK answers describe what the patent changes about it.

The cash flow then asks, for each of ten years: *how much more liquidity does this company have
because it holds this patent?* Four components add, two subtract, and each year is discounted back
and summed. Read the chart rather than the table, and watch three things:

- **Years 1 and 2 are pure cost.** The technology is not on the market yet, but development is
  being paid for.
- **The equipment investment lands once**, in the year of market entry, and never again.
- **The whole thing stops when the technology's life expectancy runs out** — whether or not the
  patent is still in force. A patent with twelve years of term left may protect a technology the
  model expects to be commercially irrelevant long before that.

> ⚠️ **The two implementation traps**, if you ever rebuild this: **entry and exit years are
> fractional** (treat them as whole years and every number comes out too high), and **investments
> happen once, not every year** (spreading them across ten years turns a positive valuation into a
> negative one).

**Step 7 · The acceptance test (2 min).** The EPO workbook ships **three test patents** with its
own computed NPVs. Our engine reproduces all three to the cent — `329,059.4284`, `4,361.2849`,
`−4,686.3598` — before it is allowed to compute anything else. Two of the three are deliberately
awkward: one lands just above zero, one below it.

> **This is the transferable lesson of the module, and it has nothing to do with patents: check
> against the source of truth, not against your own previous output.** Applied to the engine in
> module 7, this exact check once caught a real off-by-one bug that two demo cases had happily
> hidden.

### Part B — Read the finished report (9 min) · `4_tool/ipscore_valuation.html`

Open the shipped report. It is one self-contained HTML file — nine sections, six inline charts, one
embedded copy of `plotly.js`, no iframes, no internet.

> ⚠️ Open it with the course's `open_html()` helper, **never with `IFrame`**. TIP's content-security
> policy sandboxes iframes and disables their JavaScript, so an interactive report renders as a dead
> box.

Walk four of its nine sections, in this order:

**1 · The verdict.** The number, in large type:

> **1,248,870 EUR** — Net Present Value over ten years, discounted at 12%.
> **139 / 200** IPScore points · **−0.39** average risk · **+0.63** average opportunity.

**2 · How much of this number is evidence?** Directly underneath, in the same size:

> **2 measured · 6 informed · 32 judgement**

Eleven of the forty questions are reachable by a PATSTAT query — **three of them strongly**. But
here is the finding the module was built to deliver:

> ⚠️ **None of the eleven checkable questions is one of the eight that carry money.** The two sets
> are disjoint. Measuring them sharpens the picture of the patent — its legal status, its remaining
> term, where it is actually in force — **without moving the valuation by a cent.**

That is not a defect in the tool and it is not a defect in PATSTAT. It is the honest shape of the
problem: **what a database can check and what a valuation depends on barely overlap.**

**3 · What the record actually says.** The section that lists the eleven reachable questions, each
with the query behind it and how strongly the data speaks — `strong`, `good`, `proxy`, `context`.
This is the section a PATLIB can genuinely add to a valuation conversation.

**4 · Which lever actually moves the number?** The tornado chart: each of the eight money questions
varied one at a time, everything else held still. The other 32 have a swing of exactly zero. Two
readings worth pointing out:

- The largest **upside** is **C2 · Market growth rate** (+563k) — the answer most worth improving.
- **C3 · Life expectancy** has an upside of **exactly zero**, because its answer is already the best
  on the scale. Its downside is over a million. It is a wide lever you cannot pull — only lose.

> 🎓 **Trainer.** That last distinction is the one clients remember: *a lever being wide does not
> make it worth working on.* It is worth a minute even if you skip a section elsewhere.

| Part | What you do | What you see | ⏱ |
|---|---|---|---|
| A | Run `1_the_model.ipynb` | The model, the 8-of-40 surprise, and an engine verified against the EPO's own numbers | 19 min |
| B | Read the finished report | A real valuation, with every answer marked evidence or judgement | 9 min |

---

## Phase 3 · Learning outcome (≈ 10 min)

### What now exists

- A **verified** implementation of the EPO IPScore model that you have seen from the inside.
- One completed valuation of a real patent, with a Net Present Value and a profile.
- **A statement of how much of that number is evidence** — the thing no other IPScore output in
  existence carries.

### The one sentence to take away

> **A valuation whose answers are judgement is a structured opinion, not a measurement — and the
> honest thing is to say so on the front page, not in a footnote.**

### Self-check

1. **A client disputes your score on question B2.** How much can the NPV change? *(Not at all. B2
   is not one of the eight. Say so — it saves the meeting.)*
2. **You measure five more answers against PATSTAT. Does the valuation improve?** *(The *picture*
   improves; the *number* does not move, because none of the reachable questions carries money.)*
3. **Why does the cash flow end after four years on the market when the patent has twelve years of
   term left?** *(Because C3 — the technology's life expectancy — governs the cash flow, not the
   legal term. The patent outlives the technology's commercial relevance.)*
4. **Your re-implementation gives a plausible number on the EPO's easy test patent and the wrong
   sign on the hard one. Ship it?** *(No. Two of the three test cases are deliberately near zero
   precisely to catch that.)*

### Transfer to your own work

Take a patent you have actually been asked about. **Do not score it.** Instead, do just two things:

1. Write down which of the **eight money questions** you could answer today, and what you would
   need for the rest.
2. Write down which of them you would mark `judgement` in front of the client.

That list is the honest scoping document for a valuation engagement, and it takes fifteen minutes.

> 🎓 **Trainer.** Close by naming what was deliberately left out. The chain that *measures* answers
> against PATSTAT, runs the scenarios and assembles the report is a second 45-minute block
> (`08_ipscore_part2.md`) for PATLIBs that want to run it themselves. Nothing in this block is
> incomplete without it — a participant who never opens notebook 2 still leaves with the argument.

---

## Where this leads

| Next | Why |
|---|---|
| **Module 7** — IPScore (Riccardo Priore) | The workshop-ready valuation tools, and the module to use for a live client session. |
| **`08_ipscore_part2.md`** | The implementation: measuring answers against PATSTAT, sensitivity, and building the report. |

---

## Notes for the next revision

- **`6_ipscore_rebuild/README.md` is stale.** It states that notebook 2 "does not exist yet" and
  that the report reads `0 measured · 0 informed · 40 judgement`. The shipped report reads
  **`2 measured · 6 informed · 32 judgement`**. Update the README — the course document deliberately
  does not touch module code.
- **`1_the_model.ipynb` says "four of them strongly"** about the PATSTAT-reachable questions.
  `PATSTAT_CANDIDATES` actually holds **3 strong, 4 good, 3 proxy, 1 context**. The report says
  "three strongly" and is correct. Fix the notebook.
- Module 8's full material is 8,272 markdown words — more prose than modules 1, 3, 4 and 6
  combined. The core/extension split above is what makes it teachable; **do not quietly re-expand
  this document** to cover notebooks 2–4.
