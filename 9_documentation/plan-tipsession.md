# TIP session plan — unblock module 8 Phase 3

**Why this exists.** Module 8's remaining work is one notebook — `2_evidence_from_patstat.ipynb`,
the PATSTAT evidence layer. It cannot be written until four things are established, and all four
need a live TIP session. Everything else in module 8 is done and runs offline.

| | |
|---|---|
| **Where** | EPO TIP JupyterLab, base conda env, `PatstatClient(env='PROD')` |
| **Working dir** | `8_ipscore_rebuild/` unless a task says otherwise |
| **Time** | ~30 minutes, five tasks |
| **Blocks** | Phase 3 (notebook 2). Phases 1, 2 and 4 are finished and committed |
| **Deadline** | Workshop is **18 September 2026** |

> ⚠️ **The SQL below is untested.** It was written offline, against no database. Treat every
> query as a draft to adapt, not as something that will run first time. The *questions* are what
> matter; the syntax is a starting point.

---

## Pre-flight — 30 seconds

Run this first. If either line fails, stop and fix that before anything else: it means the
engine or the spec drifted, and nothing downstream is trustworthy.

```bash
cd 8_ipscore_rebuild
python ipscore_kit.py                             # → 3 PASS, "All three EPO test patents reproduced."
python tools/extract_spec_from_excel.py --check    # → "spec is up to date"
```

---

## Task 1 · O1 — does TIP's PATSTAT carry legal-status data?

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

## Task 2 · O2 — is `nb_claims` populated?

**The decision it makes.** Question **A4** *breadth of claim*. Claim count is a **weak proxy** for
claim breadth and module 8 labels it as one — but a proxy with no data is not even that. If the
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
module 8 cares about, since the worked example is an EP-first family.

**Record:** coverage percentage for EP and WO. Rule of thumb — below ~50 % for EP, A4 is not worth
showing even as a labelled proxy.

---

## Task 3 · V5 — pick the worked example family

**The decision it makes.** Right now `8_ipscore_rebuild/worked_example.json` holds an invented
patent, and its eight money-carrying scores were **chosen so the charts teach well**, not sampled
from reality. Decision **V5** says the real example comes from module 6's antibiotic-resistance
corpus, so the two modules link up: the landscape says where a field stands, module 8 values one
patent inside it.

**The corpus** is `6_patentreports/2_antibiotic_resistance_rebuild/1_dataset_and_search_strategy_output/dataset.xlsx`
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
    "../6_patentreports/2_antibiotic_resistance_rebuild/"
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

## Task 4 · Look at notebook 1's two charts

**Why.** Nobody has ever seen them rendered. They were verified structurally — traces, ranges,
tick labels, a CVD-safe palette — but the build environment had no kaleido and no browser.
Notebook 4's five charts *have* now been rendered and reviewed in a browser, and doing that
turned up three real problems, so this is not a formality.

Open `8_ipscore_rebuild/1_the_model.ipynb` and look at the two figures:

1. **Cell 9** — the 40-question grid, *"Only 8 of the 40 IPScore questions reach the NPV"*
2. **Cell 21** — the ten-year cash-flow bars

**Check for:** overlapping tick labels, a legend covering the plot, bars clipped at the axis,
unreadable text inside the markers. If something is off, note *what* — the fix is offline work
and does not need TIP.

---

## Task 5 · Prove `open_html()` works in notebook 4

**Why.** The last cell of `4_assemble_tool.ipynb` opens the report through jupyter-server-proxy.
It is structurally correct — it walks up for `CLAUDE.md` to find the repo root, which works from
`8_ipscore_rebuild/` — but **the proxy branch has never executed**. Offline there is no
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
> warning 9 in `prep_workshop_todo.md`, the one module 7 learned the hard way.

---

## Afterwards — what to commit

Only these, and only if they changed:

- `8_ipscore_rebuild/1_the_model.ipynb` — **only** if you re-ran it (and then check its three
  `measured` stamps, see below)
- `8_ipscore_rebuild/4_assemble_tool.ipynb` — **with cell 19's output cleared**
- `8_ipscore_rebuild/4_tool/` — if the report was regenerated on TIP
- The answers to O1, O2 and V5 — write them into `REBUILD_PLAN.md` under *Open questions*

Ticket `#PIP-127`. Work on `develop`.

---

## Not part of this session, but decide before 18 September

- **Notebook 1 stamps three answers `measured`** (A1, A3, A5) with hand-written evidence strings.
  Harmless there — it illustrates the dataclass, and that notebook's deliverable is the
  acceptance test — but it is the opposite of the standard notebook 4 now sets, where all forty
  answers are honestly `judgement`. The last inconsistency in the module. Fixing it costs a
  notebook 1 re-run.
- **Attribution wording for module 8.** Riccardo has agreed to the rebuild; the sentence itself
  is still unwritten. Module 8 is our implementation of the **EPO** model and must say so, while
  modules 6 and 7 keep *created by Riccardo Priore*.
- ~~Unsigned commits on `develop`~~ — **done, 2026-08-15.** All four were re-signed and
  force-pushed; `git log --format='%h %G?' f141276..develop` shows `G` on every one. The
  pre-rewrite state is kept locally as `backup/pre-resign-develop`; delete that branch once the
  PR into `main` has landed.

---

## What this unblocks

With O1, O2 and V5 answered, `2_evidence_from_patstat.ipynb` can be written **offline**: the
three *strong* questions first (A1, A3, A5), the three *good* ones next (E1, E2, E7), the proxies
last and labelled as proxies. `kit.PATSTAT_CANDIDATES` already names what each one sources.

Only its **execution** needs TIP. Then the provenance panel on the report stops reading
`0 measured · 0 informed · 40 judgement` — which is the whole point of module 8.
