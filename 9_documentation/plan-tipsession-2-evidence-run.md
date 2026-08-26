# TIP session 2 — execution: run the evidence layer

**What this is.** The briefing for the **second** module 6 TIP session, run the same day as the
first. It is an **execution** session: one notebook, written offline against session 1's answers
and stub-tested, needed the one thing only TIP can give it — a real PATSTAT. No open questions,
no exploration; a checklist and the things to watch while it ran.

**What it is not.** It establishes nothing about the data. The questions were settled in
[`plan-tipsession-1-recon.md`](plan-tipsession-1-recon.md), the reconnaissance session.

**Read it for** the checklist shape — what to verify while a long notebook runs on TIP, and what
to do when the SQL breaks mid-session. Its tail carries the items left for a **later** session,
now collected in [`plan-tipsession-3-screenshots.md`](plan-tipsession-3-screenshots.md).

---

> ## ✅ Run on 2026-08-15. Phase 3 is complete.
>
> Notebook 2 executed on PATSTAT PROD; the chain `2 → 3 → 4` re-ran with **zero cell errors**.
> **All eleven reachable answers resolve — no query fails.**
>
> | Check from *"What to check as it runs"* | Result |
> |---|---|
> | every `measure()` line prints an answer or a reason | ✅ — **one failed and was fixed**: A1 used `MIN(event_date)`, a column `tls231` does not have |
> | Step 9's `NPV effect (EUR)` all zeros | ✅ — `1,248,870 → 1,248,870 EUR`, difference `+0` |
> | Step 10 writes `evidence_answers.json` | ✅ — `kit.load_answers()` reports *"measured against PATSTAT…"* |
> | the report stops saying `0 measured · 0 informed · 40 judgement` | ✅ — now **`2 measured · 6 informed · 32 judgement`** |
>
> Five of the eleven answers moved (A1 ↑, A3 ↓, A4 ↑, E1 ↑, E2 ↓); the profile went 138 → 139
> points and the valuation did not move by a cent. The report grew to **9 sections and 6 charts**.
> Full detail, including the two new schema traps, in
> [`results-tipsession.md`](results-tipsession.md#session-2--running-the-evidence-layer).

**One task.** `6_ipscore_rebuild/2_evidence_from_patstat.ipynb` is written, stub-verified and
committed **without outputs**. It is the only notebook in the module that needs TIP. Running it
is the last step of Phase 3.

| | |
|---|---|
| **Where** | EPO TIP JupyterLab, `PatstatClient(env='PROD')`, working dir `6_ipscore_rebuild/` |
| **Time** | ~20 minutes, most of it query latency |
| **Input** | `worked_example.json` — EP3074539B1, Q-Linea AB, family `53398085` |
| **Deadline** | Workshop **18 September 2026** |

## Do this

```bash
cd 6_ipscore_rebuild
python ipscore_kit.py                             # → 3 PASS
python tools/extract_spec_from_excel.py --check    # → "spec is up to date"
```

Then run, **in order**: `1_the_model` → `2_evidence_from_patstat` → `3_valuation_and_scenarios`
→ `4_assemble_tool`. Only notebook 2 actually needs re-running; 1, 3 and 4 already carry correct
outputs and will simply reproduce them, but 3 and 4 must run *after* 2 to pick up the measured
answers.

## What to check as it runs

- **Every `measure()` line prints either a corrected answer or a reason it failed.** A failure is
  not fatal by design — that answer stays `judgement` and the notebook carries on. But note which
  ones failed: the SQL was written offline against the previous session's schema notes and has
  never touched the database.
- **Step 9's `NPV effect (EUR)` column should be all zeros.** If anything is non-zero, something
  is wrong — none of the eleven reachable questions carries money.
- **Step 10 writes `2_evidence_from_patstat_output/evidence_answers.json`.** After that,
  `kit.load_answers()` reports *"measured against PATSTAT…"* instead of *"the adviser's first
  pass"*, and notebooks 3 and 4 print it.
- **The finished report** should read something other than `0 measured · 0 informed · 40
  judgement` on its front section — that change is the entire point of the module.

## Before committing ✅

- ✅ **Cleared cell 19 of `4_assemble_tool.ipynb`** (the `open_html()` launcher). It had indeed
  baked in the hub session id `ASfgQo6rDwkhmZZcdZkvtH` and port `60981`. A `grep` over every
  notebook and the report confirms no proxy URL survives anywhere.
- ✅ Committed `2_evidence_from_patstat.ipynb` **with** its outputs, plus
  `2_evidence_from_patstat_output/`, the re-run 3 and 4, and `4_tool/`.
- Ticket `#PIP-127`, branch `develop`.

> `1_the_model.ipynb` was **not** re-run: it reads `load_worked_example()` and never
> `load_answers()`, so the evidence layer cannot change it. Leaving it alone keeps the diff to
> what actually moved.

## If the SQL breaks ✅

The queries are drafts. Fixes belong in the notebook, and anything schema-level worth
remembering belongs in `results-tipsession.md` next to the five corrections already recorded
there. Known traps, already handled: `granted` is `'Y'`/`'N'`; claim counts are on
`tls211_pat_publn`, not `tls201_appln`; `tls803.event_impact` is NULL for every code; the lapsed
state is in `tls231.lapse_country`, not `event_text`.

> **It broke once, in A1.** `MIN(event_date)` — `tls231` has ten date columns and no such name,
> and BigQuery reported only the generic *"Standard SQL dialect is currently selected"* without
> naming the column. Fixed in the notebook with `event_effective_date`, guarded against its
> `9999-12-31` sentinel and falling back to `event_publn_date`; recorded in
> `results-tipsession.md`, and the notebook's own trap list now names five instead of four.

## Still open, and not TIP work

- **Attribution wording for module 6** — our implementation of the **EPO** model; module 5 and the IPScore reference
  keep *created by Riccardo Priore*.
- **O3 — what does a PATLIB actually get asked?** A conversation with Riccardo. Note that the
  `PGFP` renewal evidence now makes *"should I renew this?"* answerable from data.

---

## Leftover for whenever a TIP session happens next (not urgent)

> ➡️ **Carried over.** Both items are now task 3 of
> [`plan-tipsession-3-screenshots.md`](plan-tipsession-3-screenshots.md), which is the
> brief for the next session. They are kept here as the record of why they were deferred.

Two one-line changes were made to `4_assemble_tool.ipynb` **without re-running it**, because
regenerating the report on this laptop would swap the embedded `plotly.js` (TIP builds 3.0.1,
local plotly builds a newer one) — a 4.9 MB library churn for a text change. So the committed
`4_tool/ipscore_valuation.html` still shows the *previous* footer.

- **The report footer** now credits Arne Krüger and names Riccardo's NPV Target Planner as the
  source of the scenario analysis. Re-running notebook 4 on TIP picks it up.
- **The data workbook numbers two sheets `6 …`** — `6 evidence` and `6 sensitivity` — because
  notebook 4 prefixes every contributed section with `6`. Cosmetic. If it is worth fixing, number
  them by section order instead.

Neither is a correctness problem, and the notebook headers (which are markdown) are already
correct everywhere.
