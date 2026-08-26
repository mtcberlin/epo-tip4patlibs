# TIP session 1 — reconnaissance: what can PATSTAT actually answer?

**What this is.** The briefing for the **first** of the module 6 TIP sessions, handed to whoever
sat in front of TIP. It is a **reconnaissance** session: five open questions that could not be
answered offline, because they are about what the data on TIP *contains*. Nothing was built here
— the point was to find out what could be built.

**What it is not.** It does not run any of module 6's notebooks. That is
[`plan-tipsession-2-evidence-run.md`](plan-tipsession-2-evidence-run.md), an **execution**
session with a single task, run the same day once these answers were in.

**Read it for** the questions that were asked and the SQL as it was *drafted* — including the
five places that draft turned out to be wrong, which is the more useful half. The findings live
in [`results-tipsession.md`](results-tipsession.md).

---

> ✅ **Done, 2026-08-15.** All five tasks ran; results in
> [`results-tipsession.md`](results-tipsession.md). Notebook 2 has since been written against
> those answers — the one run it still needs is in
> [`plan-tipsession-2-evidence-run.md`](plan-tipsession-2-evidence-run.md). ✅ done

> ## ✅ Run on 2026-08-15. All five tasks done — Phase 3 is unblocked.
>
> **The results are in [`results-tipsession.md`](results-tipsession.md).** The answers to O1, O2
> and V5 are also in `6_ipscore_rebuild/REBUILD_PLAN.md` under *Open questions*, which is where
> notebook 2 should read them from.
>
> | Task | | Result |
> |---|---|---|
> | **1 · O1** legal status | ✅ | **Best case** — legal events present *and* populated; A1, A3 and A7 all become `measured` |
> | **2 · O2** claim counts | ✅ | `nb_claims` gone, but `tls211_pat_publn.publn_claims` is 100 % for EP B1 — A4 survives |
> | **3 · V5** worked example | ✅ | Family `53398085` — **Q-Linea AB, `EP3074539B1`** |
> | **4** notebook 1 charts | ✅ | Cell 9 fine; **cell 21 has two real problems**, fixable offline |
> | **5** `open_html()` | ✅ | **Proven** — the proxy branch executes and serves the report |
>
> This file is kept as the record of what was asked and how the plan's SQL had to be corrected.

**Why this exists.** Module 6's remaining work is one notebook — `2_evidence_from_patstat.ipynb`,
the PATSTAT evidence layer. It cannot be written until four things are established, and all four
need a live TIP session. Everything else in module 6 is done and runs offline.

| | |
|---|---|
| **Where** | EPO TIP JupyterLab, base conda env, `PatstatClient(env='PROD')` |
| **Working dir** | `6_ipscore_rebuild/` unless a task says otherwise |
| **Time** | ~30 minutes, five tasks |
| **Blocks** | ~~Phase 3 (notebook 2)~~ — **unblocked 2026-08-15.** Phases 1, 2 and 4 were already finished |
| **Deadline** | Workshop is **17 September 2026** |

> ⚠️ **The SQL below is untested.** It was written offline, against no database. Treat every
> query as a draft to adapt, not as something that will run first time. The *questions* are what
> matter; the syntax is a starting point.
>
> **It needed correcting in five places** — `granted` is `'Y'`/`'N'` not a boolean, `nb_claims`
> is not on `tls201_appln`, `event_impact` is all `NULL`, the lapsed state is in `lapse_country`
> not `event_text`, and the `UNNEST` list needed no chunking. See *Where the plan's SQL needed
> correcting* in the results.

---

## Pre-flight — 30 seconds

Run this first. If either line fails, stop and fix that before anything else: it means the
engine or the spec drifted, and nothing downstream is trustworthy.

```bash
cd 6_ipscore_rebuild
python ipscore_kit.py                             # → 3 PASS, "All three EPO test patents reproduced."
python tools/extract_spec_from_excel.py --check    # → "spec is up to date"
```

---

## Task 1 · O1 — does TIP's PATSTAT carry legal-status data? ✅

> **Yes, and richly.** 141 M EP events over 5.5 M applications, current to 2026-02-13 — the first
> of the three outcomes below. **A1, A3 and A7 all become `measured`**; A7 does not drop out.
> Two traps: `event_impact` is all `NULL`, and the lapsed state is in `lapse_country`, not
> `event_text`. Full detail in [`results-tipsession.md`](results-tipsession.md#o1--tips-patstat-carries-legal-status-data-and-plenty-of-it).

**The decision it makes.** Three questions in the IPScore questionnaire hang on this:

- **A1** *patent status* — with legal events this becomes "still in force", not just "granted"
- **A3** *remaining term* — without events it stays a **nominal upper bound** (filing + 20 years),
  because lapses and renewals are invisible
- **A7** *legal proceedings* — needs opposition history. **Without it, A7 drops out of the
  evidence layer entirely** and stays judgement

`kit.PATSTAT_CANDIDATES["A7"]["strength"]` is currently `"open"` for exactly this reason.

**How to check.** Probe the candidate tables rather than trusting a table list — a table can
exist and be empty.

```python
from epo.tipdata.patstat import PatstatClient
import pandas as pd

patstat = PatstatClient(env='PROD')

CANDIDATES = [
    "tls231_inpadoc_legal_event",   # INPADOC legal events — the one that matters most
    "tls803_legal_event_code",      # the code lookup that goes with it
    "tls222_appln_jp_class",        # sanity check: a table we know PATSTAT Global has
    "tls201_appln",                 # sanity check: must succeed
]

for table in CANDIDATES:
    try:
        df = pd.DataFrame(patstat.sql_query(f"SELECT * FROM {table} LIMIT 3",
                                            use_legacy_sql=False))
        print(f"✅ {table:32} {len(df)} rows, columns: {list(df.columns)[:8]}")
    except Exception as e:
        print(f"❌ {table:32} {type(e).__name__}: {str(e)[:110]}")
```

If the probe route is awkward, the edition's own table list is the fallback:

```python
df = pd.DataFrame(patstat.sql_query(
    "SELECT table_name FROM INFORMATION_SCHEMA.TABLES ORDER BY table_name",
    use_legacy_sql=False))
print(len(df), "tables")
print([t for t in df["table_name"] if t.startswith(("tls23", "tls80"))])
```

**Record the answer as one of these three:**

| Outcome | What notebook 2 does |
|---|---|
| Legal events present **and populated** | A1 → in force / lapsed · A3 → real remaining term · A7 → opposition frequency. All three become `measured` |
| Tables present but thin/empty for our authorities | A1 stays granted-flag only, A3 stays a nominal upper bound, **A7 drops out** |
| Not present at all | Same as above. Say so explicitly in notebook 2 — *"this is what PATSTAT cannot tell you"* is a teaching point, not a failure |

---

## Task 2 · O2 — is `nb_claims` populated? ✅

> **The column does not exist** on `tls201_appln` — but the question survives it.
> `tls211_pat_publn.publn_claims` is **100 % populated for EP `B1`** in every filing year
> 2010–2022 (mean 11.5 claims). WO is 0 %. **A4 keeps its labelled proxy** and gains a benchmark.
> Take the count from the `B1`, never the `A1`.

**The decision it makes.** Question **A4** *breadth of claim*. Claim count is a **weak proxy** for
claim breadth and module 6 labels it as one — but a proxy with no data is not even that. If the
column is empty for EP and WO, A4 drops out and stays pure judgement.

```python
sql = """
SELECT appln_auth,
       COUNT(*)                                            AS applications,
       COUNTIF(nb_claims IS NOT NULL AND nb_claims > 0)     AS with_claims,
       ROUND(AVG(NULLIF(nb_claims, 0)), 1)                  AS mean_claims
FROM tls201_appln
WHERE appln_filing_year BETWEEN 2010 AND 2022
  AND appln_auth IN ('EP', 'WO', 'US', 'DE', 'FR', 'GB', 'IT')
GROUP BY appln_auth
ORDER BY applications DESC
"""
pd.DataFrame(patstat.sql_query(sql, use_legacy_sql=False))
```

If `nb_claims` does not exist on `tls201_appln` in this edition, the query errors on the column
name — that itself is the answer. Note the coverage **per authority**: EP and WO are the ones
module 6 cares about, since the worked example is an EP-first family.

**Record:** coverage percentage for EP and WO. Rule of thumb — below ~50 % for EP, A4 is not worth
showing even as a labelled proxy.

---

## Task 3 · V5 — pick the worked example family ✅

> **Family `53398085` — Q-Linea AB (Uppsala, SE), `EP3074539B1`**, granted 2018-01-10, 19 claims,
> filed 2014-06-13, 10 members granted in EP/US/JP/CN/KR/AU/CA. 135 candidates were found, 95 with
> a company applicant. Picked because Q-Linea is a real in-vitro diagnostics firm doing exactly the
> AMR rapid testing the module already invented — and because the patent is granted, unopposed,
> designated in **38 EPC states** and in force in **four** (DE, SE, GB, FR, renewals paid to year 11
> in June 2025). "Granted" ≠ "in force" is the A1/A5 teaching point, with real dates.
> `worked_example.json` is deliberately **not** yet changed — that is Phase 3 work.

**The decision it makes.** Right now `6_ipscore_rebuild/worked_example.json` holds an invented
patent, and its eight money-carrying scores were **chosen so the charts teach well**, not sampled
from reality. Decision **V5** says the real example comes from module 5's antibiotic-resistance
corpus, so the two modules link up: the landscape says where a field stands, module 6 values one
patent inside it.

**The corpus** is `5_patentreports/2_antibiotic_resistance_rebuild/1_dataset_and_search_strategy_output/dataset.xlsx`
— 4,172 families, columns `docdb_family_id` and `publication_number` (696 EP, 559 WO, 219 US).

**What makes a good example** — it has to exercise the evidence layer, so:

- **EP publication, granted**, so A1 has something to say
- **Family in several jurisdictions** (`docdb_family_size` ≥ 5), so A5 and E1/E2 are interesting
- **A company applicant, not a university** — the IPScore financial model needs turnover, costs
  and depreciation to mean something. `psn_sector = 'COMPANY'`
- **Filed roughly 2012–2018**, so A3 has meaningful term left without being brand new
- **Not a giant.** Merck with 18 triadic families makes a poor stand-in for a PATLIB client; a
  mid-size specialist is the better story. Venatorx or Wockhardt scale is about right

```python
families = pd.read_excel(
    "../5_patentreports/2_antibiotic_resistance_rebuild/"
    "1_dataset_and_search_strategy_output/dataset.xlsx")
ids = tuple(int(x) for x in families["docdb_family_id"].unique())

sql = f"""
SELECT a.docdb_family_id,
       MIN(a.earliest_filing_year)      AS first_filing,
       MAX(a.docdb_family_size)         AS family_size,
       COUNT(DISTINCT a.appln_auth)     AS authorities,
       MAX(CAST(a.granted AS INT64))    AS any_granted,
       ANY_VALUE(p.psn_name)            AS applicant,
       ANY_VALUE(p.psn_sector)          AS sector
FROM tls201_appln a
JOIN tls207_pers_appln pa ON pa.appln_id = a.appln_id AND pa.applt_seq_nr > 0
JOIN tls206_person     p  ON p.person_id  = pa.person_id
WHERE a.docdb_family_id IN {ids[:1000]}
  AND a.earliest_filing_year BETWEEN 2012 AND 2018
GROUP BY a.docdb_family_id
HAVING family_size >= 5 AND any_granted = 1 AND sector = 'COMPANY'
ORDER BY family_size DESC
LIMIT 25
"""
pd.DataFrame(patstat.sql_query(sql, use_legacy_sql=False))
```

*(`IN {ids[:1000]}` is a blunt instrument — 4,172 ids may exceed the query limit. Chunk it, or
join against a temp table, whichever TIP tolerates.)*

**Record:** one `docdb_family_id`, its EP publication number, the applicant name and why you
picked it. Notebook 2 writes the rest.

---

## Task 4 · Look at notebook 1's two charts ✅

> Rendered from the committed output, without re-executing. **Cell 9 is fine** (one cosmetic nit:
> dead space below row E). **Cell 21 has two real problems**: notebook 1 answers D3 = 3 and D4 = 3,
> which zero out **Efficiency and Investment reduction in all ten years** while both keep their
> legend slots; and C3 = 4 leaves **years 7–10 empty** with the liquidity line flat on zero.
> Both are fixed by the same edit — align notebook 1's money scores with `worked_example.json`
> (D3 = 4, D4 = 4, C3 = 5, B5 = 3). Offline work, and the same re-run the `measured` stamps need.

**Why.** Nobody has ever seen them rendered. They were verified structurally — traces, ranges,
tick labels, a CVD-safe palette — but the build environment had no kaleido and no browser.
Notebook 4's five charts *have* now been rendered and reviewed in a browser, and doing that
turned up three real problems, so this is not a formality.

Open `6_ipscore_rebuild/1_the_model.ipynb` and look at the two figures:

1. **Cell 9** — the 40-question grid, *"Only 8 of the 40 IPScore questions reach the NPV"*
2. **Cell 21** — the ten-year cash-flow bars

**Check for:** overlapping tick labels, a legend covering the plot, bars clipped at the axis,
unreadable text inside the markers. If something is off, note *what* — the fix is offline work
and does not need TIP.

---

## Task 5 · Prove `open_html()` works in notebook 4 ✅

> **Proven.** `jupyter_server_proxy` 4.4.0 is present, `server_base()` returned
> `/user/…/proxy/44705/`, and the report came back **HTTP 200, 4,928,944 bytes** of valid HTML —
> so the red **▶ Open** button renders, not the download fallback. `repo_root()` resolved correctly
> from `6_ipscore_rebuild/`, and the `/files/` fallback survives the `/home/jovyan` symlink.
> No regeneration was needed: the committed report already has **8 sections and 5 charts**.
> Warning 9 confirmed — the URL bakes in the hub session id *and* an ephemeral port.

**Why.** The last cell of `4_assemble_tool.ipynb` opens the report through jupyter-server-proxy.
It is structurally correct — it walks up for `CLAUDE.md` to find the repo root, which works from
`6_ipscore_rebuild/` — but **the proxy branch has never executed**. Offline there is no
jupyter-server-proxy, so it printed the download fallback instead. That is an unproven claim, not
a finished one.

**Run order matters** — the report has 8 sections only if notebook 3 has run:

```
1_the_model.ipynb  →  3_valuation_and_scenarios.ipynb  →  4_assemble_tool.ipynb
```

Then check: does the red **▶ Open** button appear, and does clicking it open a report with
**8 sections and 5 working charts** — verdict, patent and company, profile, data reach, the eight
money answers, cash flow, *which lever moves the number*, all forty answers?

> 🚨 **Clear that cell's output before committing.** Run on TIP, `open_html()` bakes a URL
> containing the hub session id and an ephemeral port into the notebook — dead for everyone else.
> Run offline it bakes in the author's filesystem path. Either way it must not ship. This is
> warning 9 in `prep_workshop_todo.md`, the one the IPScore reference learned the hard way.

---

## Afterwards — what to commit ✅

Only these, and only if they changed:

- ~~`6_ipscore_rebuild/1_the_model.ipynb`~~ — **not re-run**, so untouched. The charts were
  reviewed by reading the stored plotly JSON out of the committed notebook and drawing it to PNG
  in a scratch directory, precisely to avoid a re-run.
- ~~`6_ipscore_rebuild/4_assemble_tool.ipynb`~~ — **not re-run**, so cell 19 carries no baked URL
  and nothing needed clearing.
- ~~`6_ipscore_rebuild/4_tool/`~~ — the report was **not** regenerated; it already had its
  8 sections and 5 charts.
- ✅ The answers to O1, O2 and V5 — written into `REBUILD_PLAN.md` under *Open questions*.
- ✅ [`results-tipsession.md`](results-tipsession.md) — the full session record.

**Committed:** documentation only. `1_the_model.ipynb`, `4_assemble_tool.ipynb` and `4_tool/` are
byte-identical to before the session, and `ipscore_kit.py` still passes its three EPO test patents.

Ticket `#PIP-127`. Work on `develop`.

---

## Not part of this session, but decide before 17 September

> ✅ **Settled since.** The notebook 1 re-run happened — the three `measured` stamps are gone and
> the cell-21 scores are corrected (`C3=5`, `D3=4`, `D4=4`). The module 6 attribution wording is
> written. What remains of this list is O3, which is a conversation, not a query.

- ~~**Notebook 1 stamps three answers `measured`**~~ ✅ **done.** (A1, A3, A5) with hand-written evidence strings.
  Harmless there — it illustrates the dataclass, and that notebook's deliverable is the
  acceptance test — but it is the opposite of the standard notebook 4 now sets, where all forty
  answers are honestly `judgement`. The last inconsistency in the module. Fixing it costs a
  notebook 1 re-run.
  **Bundle this with the cell-21 fix from Task 4** — same re-run, and both are edits to the same
  answer set in cell 11. Note that O1/V5 now supply *real* evidence strings for exactly these
  three: A1 "granted 2018-01-10, no opposition (`26N`)", A3 "renewals paid to year 11 in 2025,
  nominal expiry 2034-06-13", A5 "in force in DE, SE, GB, FR of 38 designated states". The
  hand-written strings can become true rather than being deleted.
- ~~**Attribution wording for module 6.**~~ ✅ **done.** Riccardo has agreed to the rebuild; the sentence itself
  is still unwritten. Module 6 is our implementation of the **EPO** model and must say so, while
  module 5 and the IPScore reference keep *created by Riccardo Priore*.
- ~~Unsigned commits on `develop`~~ — **done, 2026-08-15.** All four were re-signed and
  force-pushed; `git log --format='%h %G?' f141276..develop` shows `G` on every one. The
  pre-rewrite state is kept locally as `backup/pre-resign-develop`; delete that branch once the
  PR into `main` has landed.
  ⚠️ **Reopened, narrowly:** the session-results commit of 2026-08-15 went in **unsigned** — the
  1Password agent was not reachable from the TIP session (`SSH_AUTH_SOCK` unset) and the only
  local key is a different one. Re-sign that single commit before the PR into `main`.

---

## What this unblocks

With O1, O2 and V5 answered, `2_evidence_from_patstat.ipynb` can be written **offline**: the
three *strong* questions first (A1, A3, A5), the three *good* ones next (E1, E2, E7), the proxies
last and labelled as proxies. `kit.PATSTAT_CANDIDATES` already names what each one sources.

Only its **execution** needs TIP. Then the provenance panel on the report stops reading
`0 measured · 0 informed · 40 judgement` — which is the whole point of module 6.
