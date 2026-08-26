# Warsaw, 90 minutes — a briefing

*PATLIB Conference 2026 · Warsaw · 18 September 2026 · Arne Krüger + Riccardo Priore*

> **The message, in one line.**
> **You do not have to learn SQL. You have to install something that writes it — and then decide
> what to ask.**

Everything in the ninety minutes is evidence for that one sentence. Anything that is not, is a
handout.

---

## 1 · The spine, and the ladder

The session is **not** a tour of six modules. It is one claim, demonstrated once and then applied
three times at rising ambition, so that every person in the room can get off the ladder at the rung
that matches their situation.

**The claim (≈15 min).** Install an AI assistant persistently on TIP, so it survives the restart
that wipes the machine. From then on it writes the SQL and the notebooks, and the PATLIB adviser
does the part that was always the professional work: deciding what to ask, and judging whether the
answer holds.

**Then the ladder — three examples, rising:**

| Rung | Example | The claim it demonstrates | Who gets off here |
|---|---|---|---|
| **1** | **Query Library** (`2_querylib/`) | *Someone already asked your question.* Pick a query, change its parameters, read the result | Anyone. Nobody leaves empty-handed |
| **2** | **PATSTAT Explorer** (`3_patstat_explorer/`) | *It does not have to stay a notebook.* The same SQL behind a user interface — something you hand to a colleague who will never open Jupyter | A PATLIB that wants to serve colleagues, not just itself |
| **3** | **Regional Lead Generation** (`4_lead_generation/`) | *Your region, your client list.* Alsace (`FR42`/`FRF1`) live, and the German path through DPMA for national filings | A PATLIB with a service to sell |

The rungs are deliberately unequal in ambition and in risk. Rung 1 is safe and short. Rung 3 is the
one a PATLIB director remembers, because it ends in a list of named companies in their own region.

**Why this order matters more than the content.** Each rung answers "so what?" for a different
person. Said out loud — *"if you stop listening after the next ten minutes, you still have
something you can use on Monday"* — it turns a dense session into a self-service one.

---

## 2 · The running order

| Time | Who | What |
|---|---|---|
| **0–5** | Arne | The message. What TIP and PATSTAT are, for anyone new — one slide |
| **5–20** | Arne | **The claim: install the assistant, persistently.** Why "persistently" is the whole trick — the machine is rebuilt on every start, and the naive install is gone by Monday |
| **20–28** | Arne | **Rung 1 — Query Library.** A ready question, adapted and run |
| **28–38** | Arne | **Rung 2 — PATSTAT Explorer.** The same query, now an app |
| **38–53** | Arne | **Rung 3 — Regional leads, FR and DE.** Alsace live; the German national path named |
| **53–63** | Riccardo | **Use case 1 — the landscape report** (module 6). Three slides |
| **63–73** | Riccardo | **Use case 2 — IPScore valuation** (module 8). Three slides |
| **73–78** | both | What you take home, and where it lives |
| **78–90** | — | **Buffer — 12 minutes, deliberate** |

**On the buffer.** At `2 × 10` for Riccardo the twelve minutes survive. At `2 × 15` they are gone,
and the session has no margin at all — for the speaker who is known to overrun. That is why
`2 × 10` is not a preference but what ninety minutes actually contains.

---

## 3 · The gap this spine opens — and it is not the screenshots

**The centrepiece of the session is the one part the course material deliberately parks.**

The Claude Code installation lives in sections 6–8 of
`1_startwithtip/1_getting-started-with-tip.ipynb`. The course document says of them:

> Sections 6–8 (Claude Code) and Part 2 of notebook 2 are **excellent self-study** and are
> explicitly handed over as such in Phase 3.
> — `9_documentation/course/source/01_start-with-tip.md:45`

That was the right call for a 45-minute teaching block where the first query had to come first. It
is exactly the wrong call for this session, where the install *is* the argument and the queries are
its evidence.

**Consequence:** the most important fifteen minutes of the workshop had no prepared material at
all, while each of the other three rungs has a finished module behind it. Two thirds of that is now
closed — the deck carries the claim as module 1's three slides, and the notebook opens with the
argument instead of with a setup cell. What is still missing is the **screenshot**: there is no
captured image of the assistant writing a query on TIP, and that needs a live session on the
machine. It is the last piece of the session's centrepiece.

**What closing it looks like** is in section 6.

---

## 4 · Riccardo: two use cases, twenty minutes, and a format that holds them

Riccardo brings two use cases he built with AI, and both are already in this repository as reworked
modules: the **antibiotic-resistance landscape report** (module 6) and **IPScore valuation**
(module 8). They are his content and they stay entirely his to present.

**The problem is not his material, it is the format he is presenting it in.** His two decks are
**eleven slides each**. Eleven slides is a twenty-minute talk, twice — which is the whole session.
Asking him to speak faster does not fix that; the slide count will win.

**The fix already exists in this repository and nobody has to build it.** `build_slides.py` renders
**exactly three slides per module** — *intro · working through · outcome* — and modules 6 and 8 are
already written into `slides.yaml` in that shape. Three slides is about ten minutes at a
comfortable pace.

> **This is the help worth offering.** Not "please cut your deck", but: *here are your own two use
> cases, already rendered in the session's format, three slides each.* The time-box then sits in
> the structure rather than in a request, and it is the same structure everyone else on stage is
> using. His eleven-slide decks — the IPScore one carrying his own speaker notes — become the
> follow-up material, shared with participants afterwards exactly as he offered in his mail of
> 25 August.

The two decks are not wasted by this. They are the best thing to hand somebody who wants to go
deeper, and they reach *every* participant rather than only the ones in the room.

---

## 5 · What is not in the room

| Not presented | Why | Where it lives instead |
|---|---|---|
| Module 1's PATSTAT first-query block | Rung 1 does the same job with a better story: a question already written | Handout `01_start-with-tip.pdf`, and the notebook |
| Module 4's applicant-consolidation depth | Rung 2 shows the app; the identity problem is named in one sentence when the numbers appear, not taught | Handout `04_patstat-explorer.pdf` |
| Modules 6 and 8 as *Arne's* material | They are Riccardo's use cases and stay his | Handouts `06_patent-reports.pdf`, `08_ipscore.pdf` |
| The four-notebook live landscape run | Tens of seconds per PATSTAT query, ten queries in one notebook alone, and a conference network nobody controls | Finished outputs, opened from disk |
| Riccardo's two eleven-slide decks | No room for a second pass over the same use case | Shared with participants as follow-up |

**What is cut here is depth, not whole subjects** — all six modules still appear, but a
45-minute block becomes eight to fifteen minutes. Say that out loud: *"you are holding the full
version of everything you just saw"* lands, and it is true. Quietly rushing does not.

---

## 6 · The work between now and 18 September

| # | Work | Why | State |
|---|---|---|---|
| **1** | **This briefing**, rewritten on the real spine | The first version inferred the split from the material instead of from Arne's intent, and had his part backwards | ✅ this document |
| **2** | **`slides.yaml` restructured** — new message, new blocks, module 1 recut around the persistent install, modules 6 and 8 as Riccardo's three-slide pair; deck re-rendered | The current deck compresses a 6 × 45-minute course into 90 minutes. It is the whole course at triple speed | ✅ `6215ebb` |
| **3** | **Notebook introductions** — the message before the first code cell | Measured: **every** workshop notebook opens with "Setup" or "Run this cell first". The branded header names the topic; nothing states why it is worth the next ten minutes | ✅ `c818ebb` |
| **4** | **Material for the install block** — the fifteen minutes that had none | Section 3 | ◐ slides and the notebook opening now cover it; **the screenshot still needs a TIP run** |
| **5** | **The three-slide pair handed to Riccardo** | Section 4 | ⏳ needs his agreement first |
| **6** | Handouts re-rendered, if any course document changes | `source/build_handouts.py` | ⏳ conditional |

> **Guard rail.** The **course** — six 45-minute blocks, seven handouts — stays as it is. The
> workshop is a separate, sharper cut of the same material, not a replacement for it. Nothing in
> this plan edits a course document in order to serve the workshop.

---

## 7 · Open questions

### For Arne

1. **Do all three rungs get stage time, or does the room choose?** "Je nach Interesse" can mean
   *show all three, briefly* (the running order above) or *show one properly and name the other
   two*. The second is stronger if the room is small enough to ask.
2. **Audience and size** — still unrecorded anywhere. It decides whether rung 3 is a demonstration
   or something people follow along on their own machines.
3. **The screenshot session** (`plan-tipsession-3-screenshots.md`, open, dated before 18 September)
   now also has to cover the install block, which has no captured material at all.
4. **Does the questionnaire work from Riccardo's PR land before Warsaw?** It is the difference
   between "run this on your own patent tonight" and "watch me run it on mine".

### For Riccardo

1. **Two slots of ten minutes, three slides each — does that work for you?** The three-slide
   rendering of your own two use cases already exists in the repository; nothing needs rebuilding.
2. **Your two eleven-slide decks as follow-up material for every participant** — that was your own
   offer of 25 August, and it reaches more people than the room does.
3. **Is the new `0_questionnaire` flow tested on TIP**, including the case where the participant
   has not filed anything? Your mail of 25 August says not yet.
4. **Can new work land in `mtcberlin/epo-tip4patlibs`** rather than as a 260-file pull request on
   your side? The questionnaire and the notebook-1 pinning are small and wanted; the rest of PR #3
   is a copy of this repository.

---

## Appendix · Riccardo's PR #3, unchanged from the first assessment

`rickypriore/patlib-sessions` PR #3, opened 25 August 2026, **260 files, +293,297 lines, open**.

Most of it is a **full copy of this repository** nested under `PATLIB_Conference_2026_Warsaw/`.
Genuinely new, and worth taking:

- `0_questionnaire.ipynb` + `0_questionnaire_tool.html` + `tools/build_questionnaire_html.py` — an
  HTML questionnaire for the participant's **own** patent, feeding notebooks 2–4. It answers his own
  objection of 20 August about the Excel → JSON → notebook path.
- The `kit.EXAMPLE_PATH` pinning in `1_the_model` — its correct companion.
- `0_live_demo/Main_menu.ipynb` — a nine-cell launcher; adopt the pattern, review the detail.

Compared cell by cell against `6_ipscore_rebuild/`: v2 notebooks 2, 3 and 4 differ **only by empty
trailing cells**; notebook 1 by the two cells named above. There is no second body of work to merge
— take the three pieces, not the tree.

---

## Sources

`~/Downloads/Mails Riccardo.pdf` (two mails, 20 and 25 August) · the two `.pptx` in `~/Downloads`
including speaker notes and file metadata · `rickypriore/patlib-sessions` PR #3 read via `gh` ·
`prep_workshop_todo.md` · `9_documentation/course/source/` · the notebook folders at commit
`bc7d327`. The session's shape, the division of labour and the `2 × 10` time-box come from Arne
directly, 26 August — not from the mails, which record none of it.
