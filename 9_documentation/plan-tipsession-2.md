# TIP session 2 — run the evidence layer

**One task.** `8_ipscore_rebuild/2_evidence_from_patstat.ipynb` is written, stub-verified and
committed **without outputs**. It is the only notebook in the module that needs TIP. Running it
is the last step of Phase 3.

| | |
|---|---|
| **Where** | EPO TIP JupyterLab, `PatstatClient(env='PROD')`, working dir `8_ipscore_rebuild/` |
| **Time** | ~20 minutes, most of it query latency |
| **Input** | `worked_example.json` — EP3074539B1, Q-Linea AB, family `53398085` |
| **Deadline** | Workshop **18 September 2026** |

## Do this

```bash
cd 8_ipscore_rebuild
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

## Before committing

- **Clear cell 19 of `4_assemble_tool.ipynb`** (the `open_html()` launcher). Run on TIP it bakes
  in the hub session id and an ephemeral port. Warning 9 in `prep_workshop_todo.md`.
- Commit `2_evidence_from_patstat.ipynb` **with** its outputs — unlike before, its stored output
  is now the deliverable — plus `2_evidence_from_patstat_output/`, the re-run 3 and 4, and
  `4_tool/`.
- Ticket `#PIP-127`, branch `develop`.

## If the SQL breaks

The queries are drafts. Fixes belong in the notebook, and anything schema-level worth
remembering belongs in `results-tipsession.md` next to the five corrections already recorded
there. Known traps, already handled: `granted` is `'Y'`/`'N'`; claim counts are on
`tls211_pat_publn`, not `tls201_appln`; `tls803.event_impact` is NULL for every code; the lapsed
state is in `tls231.lapse_country`, not `event_text`.

## Still open, and not TIP work

- **Attribution wording for module 8** — our implementation of the **EPO** model; modules 6 and 7
  keep *created by Riccardo Priore*.
- **O3 — what does a PATLIB actually get asked?** A conversation with Riccardo. Note that the
  `PGFP` renewal evidence now makes *"should I renew this?"* answerable from data.
