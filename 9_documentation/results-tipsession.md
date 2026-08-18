# TIP session results — module 8 Phase 3 unblocked

**Session run 2026-08-15** against the plan in [`plan-tipsession-1-recon.md`](plan-tipsession-1-recon.md).
EPO TIP JupyterLab, base conda env, `PatstatClient(env='PROD')`, PATSTAT Global Autumn 2025.

**All five tasks are done. Phase 3 is unblocked** — `2_evidence_from_patstat.ipynb` can now be
written offline. Pre-flight passed both lines: `ipscore_kit.py` → 3 PASS, *"All three EPO test
patents reproduced"*; `extract_spec_from_excel.py --check` → *"spec is up to date"*.

| Task | Result |
|---|---|
| **1 · O1** legal status | **Best case.** Legal events present *and* populated — A1, A3 and A7 all become `measured` |
| **2 · O2** claim counts | **`nb_claims` does not exist** — but `tls211_pat_publn.publn_claims` is 100 % populated for EP B1, so A4 survives |
| **3 · V5** worked example | **Family `53398085` — Q-Linea AB, `EP3074539B1`** |
| **4** notebook 1 charts | Rendered and reviewed. Cell 9 is fine; **cell 21 has two real problems** |
| **5** `open_html()` | **Proven.** The proxy branch executes and serves the report |

The O1, O2 and V5 answers are also written into `8_ipscore_rebuild/REBUILD_PLAN.md` under
*Open questions*, which is where notebook 2 should read them from. This file is the fuller record.

---

## O1 — TIP's PATSTAT carries legal-status data, and plenty of it

Both candidate tables exist **and are populated**. This is the first of the plan's three
outcomes — the best one. **A1, A3 and A7 all become `measured`**, and A7 does *not* drop out of
the evidence layer.

`tls231_inpadoc_legal_event`, top authorities:

| `event_auth` | events | applications |
|---|---:|---:|
| EP | 141,172,811 | 5,496,545 |
| US | 85,150,448 | 11,732,998 |
| DE | 22,214,516 | 10,252,613 |
| WO | 21,282,950 | 5,277,526 |
| FR | 5,180,259 | 2,433,829 |
| GB | 4,476,383 | 3,427,080 |

Events are current to **2026-02-13** for EP, DE, FR, ES, US and WO (GB 2026-02-11). IT is stale —
last event 2021-12-29 — which matters if an example is ever validated there.

### A7 — opposition is answerable outright

The `26N`/`26` pair gives both halves of the fraction, so opposition *frequency* is computable,
not just presence:

| code | meaning | applications |
|---|---|---:|
| `PLBE` / `26N` | no opposition filed | 2,303,917 / 2,280,532 |
| `PLBI` / `26` | **opposition filed** | 106,871 / 106,591 |
| `PLBN` / `27O` | opposition rejected — patent survives | 22,814 / 22,714 |
| `PUAH` / `27A` | maintained in amended form | 32,530 / 32,434 |
| `RDAG` / `27W` | **patent revoked** | 36,586 / 36,454 |
| `PLBP` | opposition withdrawn | 9,719 |
| `APB*` | appeal recorded / closed | ~30,000 |

That yields an EP opposition rate of **≈ 4.5 %** (106.6 k of 2.39 M), which matches the published
EPO figure — a cheap sanity check that the `tls231 ↔ tls803` join is correct.
**`kit.PATSTAT_CANDIDATES["A7"]["strength"]` can move off `"open"`.**

### A1 / A3 — in force, not merely granted

Category `H` *IP right cessation* is the richest category for EP (56.8 M events over 2.45 M
applications): `PG25` lapsed in a contracting state, `GBPC` ceased for non-payment, `MM4A`
lapsed, `MG4D` invalidated, `27W` revoked. Against that, `PGFP` renewal-fee payments carry
`fee_renewal_year`, so *"renewals paid up to year N"* is a fact. A3 stops being a nominal
filing + 20 upper bound.

### Two traps that would have cost a re-run

- **`event_impact` is `NULL` for all 4,332 codes** in `tls803`. The `+/-` rights indicator is
  unusable — select on `event_category_code` plus explicit code lists instead.
- **`tls231` is far wider than its first columns suggest** (~48 columns). The lapsed state is in
  **`lapse_country` / `lapse_date` / `lapse_text`**, *not* `event_text`, which is empty. Alongside
  it sit `fee_country` / `fee_renewal_year` / `fee_payment_date`, `designated_states`,
  `extension_states`, the `spc_*` block and the `party_*` block. Notebook 2 should read the full
  schema once before writing queries against it.

---

## O2 — the column is gone, the question survives

**`nb_claims` does not exist on `tls201_appln`** in this edition. The table has 27 columns and no
claims field of any name. The plan anticipated the error but not the recovery: the claim count
lives on **`tls211_pat_publn.publn_claims`**.

Coverage by publication kind, filings 2010–2022:

| authority | kind | publications | with claims | coverage | mean claims |
|---|---|---:|---:|---:|---:|
| EP | **`B1`** | 1,094,114 | 1,094,042 | **100.0 %** | **11.5** |
| EP | `B2` | 6,691 | 6,690 | 100.0 % | 10.9 |
| EP | `A1` | 1,819,655 | 928,112 | 51.0 % | 13.7 |
| US | all B | 9,192,003 | 3,994,525 | 43.5 % | 15.4 |
| **WO** | all | 3,174,379 | 0 | **0.0 %** | — |
| DE / GB / FR / IT | all | — | 0 | 0.0 % | — |

EP `B1` coverage is **100 % in every single filing year 2010–2022** — no decay at the recent end.

**So A4 keeps its labelled weak proxy** for the granted-EP case module 8 actually works on, and it
gains a benchmark to quote against: *this patent has N claims, a typical granted EP has 11.5*.
Two rules for notebook 2:

- Take the count from the **`B1`**, never the `A1` — the A-publication is only 51 % covered and is
  the as-filed claim set, not the granted one. Those are different claims.
- **WO has nothing.** Any WO-only family gets no A4 evidence at all. Say so rather than silently
  showing a blank.

---

## V5 — the worked example: Q-Linea AB, `EP3074539B1`

Searched the module 6 corpus (4,172 families) for granted EP B1 documents in families of ≥ 5,
filed 2012–2018, with a `psn_sector = 'COMPANY'` applicant: **135 candidate publications, 95 with
a company applicant.** The 4,172-id list was fine as `UNNEST([...])` — no chunking needed.

**Picked: `docdb_family_id` `53398085`.**

| | |
|---|---|
| Applicant | **Q-Linea AB**, Dag Hammarskjölds väg 52A, 752 37 Uppsala (SE), NUTS `SE121`, `COMPANY` |
| Title | *Method for detecting and characterising a microorganism* — US: *…the identity and antimicrobial susceptibility of a microorganism* |
| EP patent | **`EP3074539B1`**, granted 2018-01-10, **19 claims** |
| Divisional | `EP3351642B1`, granted 2019-09-11, 21 claims — mention it, value the parent |
| Earliest filing | 2014-06-13 → nominal expiry **2034-06-13** |
| Family | 10 members; granted in **EP, US, JP, CN, KR, AU, CA**; 30 citing families |
| Legal events | 219 events across all 10 members, 2016-01-27 → 2025-07-30 |

### Why this one

It meets every criterion in the plan — granted EP, 10-member family across 8 authorities, a
company rather than a university, filed 2014 (≈ 8 years of term left), and a mid-size specialist
(2 families in the corpus, against Merck's 6 and Venatorx's 6) rather than a giant. Two things
make it better than merely eligible:

**1 · It is the patent the module already describes.** `worked_example.json` invented *"a rapid
point-of-care test for antibiotic resistance markers"* from *"a mid-size European diagnostics
company"*. Q-Linea is a Swedish in-vitro diagnostics firm doing exactly that. The narrative
survives the swap from invented to real — only the numbers change.

**2 · Its legal history teaches the point of the evidence layer.** The patent was designated in
**38 EPC states** at grant:

```
AL AT BE BG CH CY CZ DE DK EE ES FI FR GB GR HR HU IE IS IT
LI LT LU LV MC MK MT NL NO PL PT RO RS SE SI SK SM TR
```

It then lapsed in roughly two dozen of them — ES, EE, PL, CZ, LT, DK, AT, MT, MC, RO, NL, RS, AL,
SK, MK, FI, NO, BG, GR, IS, PT mostly for *"failure to submit a translation of the description or
to pay the fee"*, then IE, LU and BE for non-payment, and CH dropped after year 9 in 2024.

Renewal fees at **year 11 were paid in June 2025 in exactly four states: DE, SE, GB, FR.**

So the patent is granted, **unopposed** (`26N`, effective 2018-10-11) — and **in force in four
states out of thirty-eight**. "Granted" and "in force" are not the same answer, and the gap
between A1 and A5 is precisely where IPScore asks you to notice that. An invented example cannot
teach this; this one does it with real dates.

### Not yet applied

`worked_example.json` is **deliberately unchanged**. Swapping it rewrites the forty scores and
therefore notebooks 3 and 4 and the committed report — that is Phase 3 work, per the plan's
*"notebook 2 writes the rest"*. The financial figures stay invented in any case: turnover, cost
structure and depreciation are not in PATSTAT.

---

## Task 4 — notebook 1's charts, seen for the first time

Rendered from the **committed** notebook output — read the stored plotly JSON out of the `.ipynb`
and drew it to PNG — so this is what ships today, and no re-run was needed to look at it.

I first suspected the committed output was stale and checked: recomputing all seven traces from
notebook 1's own answer set reproduces the committed values **exactly**. The chart is faithful.
The problems are in the example it was given.

### Cell 9 — the 40-question grid: fine

Legible, no overlapping labels, legend clear of the plot, CVD-safe palette, and the eight
highlighted questions are the right ones (B5, C2, C3, C6, D1–D4). One cosmetic nit: noticeable
dead space below row E, with the y-axis line running down through it.

### Cell 21 — the cash-flow bars: two real problems

Both trace to notebook 1's own money scores, which differ from `worked_example.json`'s:

**1 · Two of the six components are structurally zero.** Notebook 1 answers **D3 = 3** and
**D4 = 3**, which map to `production_cost_index = 1.0` and `investment_index = 1.0`. Efficiency
scales with `(1 − production_cost_index)` and investment reduction with `(1 − investment_index)`,
so both are **0.00 in all ten years** — yet both still occupy legend slots. The legend promises
six components; the chart draws four. Investments is non-zero in exactly one year (a 0.54 sliver),
so it really reads as three.

**2 · Years 7–10 are empty.** **C3 = 4** gives a 4-year life expectancy and **B5 = 2** a 2-year
run-up, so the technology is on the market in years 3–6 only. Four of ten year slots are blank and
the liquidity line sits flat on zero — which reads as *"the value collapsed"* rather than *"the
horizon outlives the technology"*.

### Both fixes are the same edit, and it is offline work

`worked_example.json` already uses **D3 = 4, D4 = 4, C3 = 5, B5 = 3** →
`production_cost_index 0.85`, `investment_index 0.7`, life expectancy 8 years, market entry in
year 2. Recomputed against notebook 1's company figures, that gives:

| year | revenue | regained | efficiency | inv. red. | costs | investments | liquidity |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.00 | 0.00 | 0.00 | 0.00 | 3.20 | 0.00 | −3.20 |
| 2 | 2.02 | 8.75 | **5.25** | **2.94** | 1.28 | 0.62 | 17.05 |
| 3 | 2.35 | 9.45 | **5.67** | 0.00 | 1.50 | 0.00 | 15.97 |
| … | … | … | … | … | … | … | … |
| 9 | 5.92 | 14.99 | **9.00** | 0.00 | 3.77 | 0.00 | 26.13 |

All six components non-zero, years 2–9 filled. So **aligning notebook 1's teaching answer set
with the module's actual worked example fixes both problems at once** — and removes the oddity
that notebook 1's chart and notebook 4's report currently describe differently-shaped patents.

That re-run is the same one already needed for the three hand-written `measured` stamps. Do them
together — and note that O1/V5 now supply *real* evidence strings for exactly those three:

- **A1** — "granted 2018-01-10, no opposition filed (`26N`, effective 2018-10-11)"
- **A3** — "renewals paid to year 11 in June 2025; nominal expiry 2034-06-13"
- **A5** — "in force in DE, SE, GB, FR of 38 designated states"

The hand-written strings can become *true* rather than being deleted.

---

## Task 5 — `open_html()` is proven, and so is the warning

Run from `8_ipscore_rebuild/` on TIP:

```
repo_root()   → /home/jovyan/epo-tip4patlibs        (walks up for CLAUDE.md, as designed)
server_base() → /user/ASfgQo6rDwkhmZZcdZkvtH/proxy/44705/
GET …/8_ipscore_rebuild/4_tool/ipscore_valuation.html → HTTP 200, 4,928,944 bytes, valid HTML
```

The proxy branch **executes** — `jupyter_server_proxy` 4.4.0 is present in the base env — so the
red **▶ Open** button renders rather than the download fallback. The `/files/` fallback URL also
resolves correctly through the `/home/jovyan` symlink:
`/user/…/files/epo-tip4patlibs/8_ipscore_rebuild/4_tool/ipscore_valuation.html?download=1`.

**The committed report needed no regeneration.** It already has **8 sections and 5 charts**,
because notebook 3's `_report_parts` are committed. Section titles match the plan exactly: the
verdict · the patent and the company · the profile · how much of this valuation can data reach ·
the eight answers that carry money · the ten-year cash flow · which lever actually moves the
number · all forty answers. Charts are `fig_profile`, `fig_reach`, `fig_cashflow`, `fig_tornado`,
`fig_steps` — a 6th `Plotly.newPlot` in the file is inside plotly.js's own bundled documentation
string, not an orphan chart.

**Warning 9 is confirmed concretely.** That URL bakes in the hub session id
`ASfgQo6rDwkhmZZcdZkvtH` *and* the ephemeral port `44705`. Both are dead for everyone else.

---

## Where the plan's SQL needed correcting

Worth carrying into notebook 2, since the same assumptions recur:

- **`tls201_appln.granted` is `'Y'`/`'N'`**, not a boolean — `CAST(granted AS INT64)` fails.
- **`nb_claims` is not on `tls201_appln`** at all; claim counts live on `tls211_pat_publn`.
- **`event_impact` is `NULL`** for every one of the 4,332 codes in `tls803`.
- **The lapsed state is in `tls231.lapse_country`**, not `event_text`, which is empty.
- A failing query may report only *"BigQuery Standard SQL dialect is currently selected"* with no
  column name. That generic message usually means **a column does not exist** — dump
  `SELECT * … LIMIT 1` and read the real schema rather than trusting the error.
- The 4,172-id `IN` list was fine as `UNNEST([...])`; the plan's chunking worry was unfounded.

**Added by session 2** (2026-08-15, running notebook 2 — see below):

- **There is no `event_date` on `tls231`.** It has *ten* date columns —
  `event_filing_date`, `event_publn_date`, `event_effective_date`, `ref_doc_date`,
  `fee_payment_date`, `lapse_date`, `reinstate_date` and three `spc_*` ones — and the obvious
  name is not among them. For "when did this event take legal effect", use
  **`event_effective_date`**, but guard the sentinel: it holds `9999-12-31` where the date does
  not apply, so fall back to `event_publn_date`. The pattern that works:
  ```sql
  MIN(CASE WHEN event_effective_date < DATE '9999-01-01'
           THEN event_effective_date ELSE event_publn_date END)
  ```
  On `26N` for the worked example that yields 2018-10-11 — the date `known_facts` records —
  where `event_publn_date` alone would have said 2018-12-19.
- **`event_filing_date` is the sentinel on opposition rows**, so it is not a substitute.

---

## Session 2 — running the evidence layer

`2_evidence_from_patstat.ipynb` was executed on TIP against PATSTAT PROD. **All eleven reachable
answers now resolve; no query fails.** The chain `2 → 3 → 4` re-ran with zero cell errors, and
`ipscore_kit.py` still reproduces its three EPO test patents.

**One query had to be fixed.** A1 — the flagship, *"is it granted and was it opposed"* — died on
`MIN(event_date)`, a column that does not exist, and reported only the generic dialect message.
It was the one trap the previous session had not hit. With `event_effective_date` (sentinel
guarded) it returns:

> A1 · 4 → 5 · `measured` — granted, and the opposition period expired with no opposition filed
> (`26N`, effective 2018-10-11)

**What the record did to the adviser's first pass** — eleven answers checked, five moved:

| Q | | guessed | record | provenance | evidence |
|---|---|---:|---:|---|---|
| A1 | patent status | 4 | **5** ↑ | `measured` | granted, `26N` effective 2018-10-11 |
| A3 | term remaining | 4 | **3** ↓ | `measured` | expiry 2034-06-13 = 7.8 years; renewals to year 11 in DE, FR, GB, SE |
| A4 | breadth of claim | 3 | **4** ↑ | `informed` | 19 claims in the B1 vs a mean of 11.5 |
| A5 | geographical coverage | 3 | 3 | `informed` | designated 38, lapsed 34, in force DE/FR/GB/SE + 6 national grants = 10 territories |
| A7 | legal proceedings | 3 | 3 | `informed` | 22,141 of 330,611 in C12M/C12P/C12Q/G01N/G06T opposed = 6.7 % vs the 4.5 % EP baseline |
| E1 | securing existing markets | 4 | **5** ↑ | `informed` | 7 of 8 jurisdictions already familiar to Q-Linea |
| E2 | winning new markets | 3 | **2** ↓ | `informed` | only JP is new |
| E7 | core technology | 4 | 4 | `informed` | 12 of the 19 IPC-classified families share the subclass = 63 % |
| B1 · B2 · C4 | — | — | unchanged | `judgement` | citation and neighbourhood counts attached as *context only* |

A5 is worth noting as a cross-check: notebook 2 derived "designated 38, in force in DE/FR/GB/SE"
independently of session 1, by a different route, and got the same answer.

**And the number did not move.** `1,248,870 EUR → 1,248,870 EUR`, difference `+0`, with the
`NPV effect (EUR)` column zero on every row — exactly as the plan said to check. The profile
moved (138 → 139 points), the provenance panel moved, the valuation did not. That is the
module's argument, now demonstrated rather than asserted.

**The report** went from 8 sections to **9** (the new *"What the record actually says"* at order
450) and from 5 charts to **6** (`fig_evidence`). Its front panel now reads
**`2 measured · 6 informed · 32 judgement`** where it used to read `0 · 0 · 40`, and names the
answer set: *"measured against PATSTAT for EP3074539B1 by 2_evidence_from_patstat.ipynb"*.

**One wording fix.** The E-block printed *"portfolio: 25 families"* and then scored E7 against
*"Q-LINEA's 19 families"* — two different numbers for the same portfolio, because only 19 of the
25 carry an IPC symbol. The computation was right (you cannot classify what has no
classification); the sentence was not. Both lines now say which population they mean.

---

## What changed in the repo

Only documentation. **No notebook was re-run and no notebook output was touched**, so
`1_the_model.ipynb`, `4_assemble_tool.ipynb` and `4_tool/` are byte-identical to before the
session — and cell 19 carries no baked URL, so nothing needed clearing. `ipscore_kit.py` still
passes its three EPO test patents after the session.

| File | Change |
|---|---|
| `8_ipscore_rebuild/REBUILD_PLAN.md` | O1, O2, V5 answered under *Open questions*; V5 section added |
| `9_documentation/plan-tipsession-1-recon.md` | Ticked off, pointing here |
| `9_documentation/results-tipsession.md` | This file |

---

## What is still open

- **O3 — what does a PATLIB actually get asked?** Needs a conversation with Riccardo, not a query
  (`prep_workshop_todo.md` §5). Note that O1's renewal-fee evidence (`PGFP`, `fee_renewal_year`)
  now makes *"should I renew this?"* answerable from data if that turns out to be the real
  question.
- **Notebook 1's `measured` stamps + the cell-21 fix** — one re-run, bundled, as above.
- **Attribution wording for module 8** — module 8 is our implementation of the **EPO** model and
  must say so, while modules 6 and 7 keep *created by Riccardo Priore*.
- **Applying V5** to `worked_example.json` — Phase 3 work, after notebook 2 exists.

## What this unblocks

`2_evidence_from_patstat.ipynb` can now be written **offline**: the three *strong* questions first
(A1, A3, A5), the three *good* ones next (E1, E2, E7), the proxies last and labelled as proxies.
`kit.PATSTAT_CANDIDATES` already names what each one sources — and A7 is no longer `"open"`.

Only its **execution** needs TIP. Then the provenance panel on the report stops reading
`0 measured · 0 informed · 40 judgement`, which is the whole point of module 8.
