# Open items

What is still outstanding in this repository, and what is deliberately not.
Last reviewed **25 September 2026**. The five modules themselves are complete and
were delivered in Warsaw on 16–17 September 2026.

---

## 1 · Needs a decision from Arne

### 1.1 A regression guard for the module code

Two defects were found on 20 September, both introduced by the restructuring of
17 September, and both invisible until someone re-ran a cell:

| What broke | Since | How it showed |
|---|---|---|
| All three copies of `tip_tools.py` were **unimportable** — the module docstring lost its closing `"""`, so the parser read the next docstring's em dash as code | `7255c84` | `SyntaxError: invalid character '—'` in module 4, pointing at a line that had not been touched |
| `ipscore_kit.save_questionnaire` was **missing** — merging Riccardo's questionnaire notebook into `5_ipscore/` took the caller and left the callee in `7_ipscore_demo/` | the same merge | `AttributeError` after a participant answered all forty questions |

Neither was caught by anything, and neither could be: **the notebooks ship
pre-executed**, so their stored output came from a run that predated the break.
That is a deliberate property of the course — and it means the shipped output is
not evidence that the code still runs.

Two checks would have caught both on the day they were introduced:

1. Import every module's own `.py` and resolve every attribute its notebooks
   reference — `getattr`, not a regex. This is what found `save_questionnaire`.
2. Assert the three `tip_tools.py` copies are byte-identical and all compile.

Proposed home: `1_querylib/tests/`, beside the query-library tests that already
exist. **Not yet written — awaiting a yes.**

### 1.2 The four commercial decisions

Unchanged since 17 September, in
[`offering-tip-presentation-and-workshop.md`](offering-tip-presentation-and-workshop.md) §5:
pricing above 3 participants · remote or on site · language · whether the free
presentation needs a booking form. The site agent cannot publish offerings 4 and 5
without them.

---

## 2 · Can only be checked on TIP

The attribute sweep of 20 September cleared **15 of 17** notebooks. The two it
could not reach need `epo.tipdata`, which exists only inside TIP:

- `1_querylib/1_query-library.ipynb` → `TIP_for_PATLIBs_QueryLib_core.py`
- `1_querylib/2_interactive-demo.ipynb` → `tip4patlibs_core.py`

Also untested since the restructure: `3_lead_generation/2_national-coverage.ipynb`,
which needs `DPMA_USER` / `DPMA_PASS` in the environment. Module 3's main notebook
runs on PATSTAT alone, so this blocks nothing for a workshop.

---

## 3 · Deliberate, not outstanding

Listed so nobody "fixes" them:

- **`3_lead_generation/1_regional-leads.ipynb` ships with no output.** Its point is
  that the participant enters their own region. Documented in the repository `README.md`.
- **The deck keeps its Warsaw wording** on slides 1 and 3 — decided 20 September.
  It reads as a record of where the material was delivered.
- **The planning documents keep their old module numbers.** They were written under
  the 2–6 numbering; each carries a note at the top mapping old to new instead.
- **Modules 4 and 5 are never re-run.** Guest material from Riccardo Priore: the
  stored outputs *are* the deliverable. See `CLAUDE.md`.

---

## 4 · Cosmetic

- `TIP4PATLIBS_1_Workshop_v4.pdf` in the repository root has white margins from the
  PowerPoint export — a paper-size setting, not a content problem. Re-export at slide
  size when the deck is next touched.
- [`plan-tipsession-3-screenshots.md`](plan-tipsession-3-screenshots.md) lists shots the
  deck never received. Low priority: the course is now shown as executed notebooks
  rather than slide images.

---

## Closed since the workshop

| | Closed |
|---|---|
| `install.sh`, one command, replacing the setup notebook | 18 September |
| `tip.depa.tech/install` — short URL, nginx redirect on Coolify, Let's Encrypt to 17 December 2026 | 18 September |
| npm prefix bug: Claude Code landed outside `~/.npm-global` when a foreign `.npmrc` was present | 19 September, tested in five scenarios |
| The two defects in §1.1 | 20 September, `cc67755` and `eef4957` |
| Eight stale module numbers across `README.md`, `CLAUDE.md`, the engine and the DPMA helpers | 20 September |
| A participant's own answers can no longer be committed by accident | 20 September |
