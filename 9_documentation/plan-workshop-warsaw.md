# Warsaw, 90 minutes — a briefing

*PATLIB Conference 2026 · Warsaw · 18 September 2026 · Arne Krüger + Riccardo Priore*

> **The problem, in one line.** Nothing in the material is bad. There is roughly **three times too
> much of it** for 90 minutes, and two people have to hand over to each other inside that. This
> document proposes what to keep, what to shorten, and — the part that actually buys the time —
> what to leave out entirely.

---

## 1 · The arithmetic that proves "too much"

Three finished decks exist for one 90-minute slot:

| Deck | Slides | Covers | Source |
|---|---|---|---|
| `TIP4PATLIBS_workshop.pptx` | **20** | all six course modules, 3 slides each | built from `course/source/slides.yaml` |
| `TIP4PATLIBS_AntibioticResistance_LiveDemo_Warsaw2026.pptx` | **11** | module 6, four notebooks, run **live** | `~/Downloads`, via Riccardo |
| `TIP4PATLIBS_IPScore_NotebookLogic_Explained_con_note.pptx` | **11** | module 8, notebooks 1→4 in depth | `~/Downloads`, via Riccardo |
| | **42** | | |

Forty-two slides in ninety minutes is **just over two minutes per slide with no time for anything
else** — no live run, no questions, no handover between two speakers, no room recovering from a
demo that stalls.

And the material does not intend to be static. The Antibiotic deck's slide 10 ("WHAT HAPPENS
NEXT · Live in TIP") commits to running all four notebooks end to end in front of the room. The
repository's own course text says why that cannot fit:

> **PATSTAT PROD is not fast.** A query scanning a full year of filings takes tens of seconds.
> — `9_documentation/course/source/03_query-library.md:110`

Notebook 2 of the landscape chain re-queries the corpus **ten times**, once per chart. Notebook 1
builds a corpus of 3,974 families. A full live 1→2→3→4 run is a large fraction of the whole slot,
and it is the part most likely to fail in a conference room.

**The root cause is structural, not editorial.** `slides.yaml` was written for `2 × 45 minutes`
covering all six modules — but those six modules are the *course*, and the course is
**6 × 45 minutes = 4.5 hours**. The deck is the whole course compressed by a factor of three. It
feels like too much because it is.

---

## 2 · What the mails actually say

Source: `~/Downloads/Mails Riccardo.pdf` — one page, two mails from Riccardo, 20.08. and 25.08.2026.

| Fact | Detail | Source |
|---|---|---|
| Format still **undecided** | Live TIP demo vs. classical PowerPoint vs. a mix — "I have not yet decided" | mail 20.08. |
| A planning meeting is **proposed, not held** | Riccardo back in the office in the week of 31.08.; wants a short online meeting to "refine what still need to be fixed and **decide in which order we present the data**" | mail 25.08. |
| Riccardo has built a **live-demo entry point** | New folder `0_Live_demo` with `Main_menu` linking both IPScore and the Antibiotic report, plus the two decks | mail 25.08. |
| He changed the **IPScore entry point** | A new `0_questionnaire` notebook generates an HTML questionnaire; the user saves it as JSON and uploads it. Notebooks 2–4 keep Arne's logic | mail 25.08. |
| His stated concern about our IPScore | "very exhaustive and rather sophisticated… I am not economist so it took a while"; fears the audience finds Excel → json → notebooks uncomfortable | mail 20.08. |
| He is willing to **share material with participants** | "I can share this material with the participants" | mail 25.08. |
| Status caveat | He was on vacation writing; refinements expected; the questionnaire change is **not yet tested** | mail 25.08. |

**What the mails do not contain — do not assume it from them:** no date, no venue, no room or
session format, no audience size, no agreed division of labour. The date and place come from the
repository instead (`prep_workshop_todo.md:3` — "PATLIB Warsaw workshop, 18 September 2026";
`slides.yaml` — "PATLIB Workshop · Warsaw · 18 September 2026").

---

## 3 · Inventory, with a verdict

### The course material (`9_documentation/course/`)

| Module | What it is | 90-min verdict |
|---|---|---|
| **1 · Start with TIP** | environment, persistence, first query — 28 min of hands-on in the course | **Leave out as a block.** Keep one orientation slide. Riccardo's Antibiotic slide 2 ("BEFORE WE START — for anyone new to TIP") already does this job in a single slide |
| **3 · Query Library** | pick a query, adapt it, read the result | **Leave out.** It is a working session, not a showcase; it needs hands on keyboards |
| **4 · PATSTAT Explorer** | applicant consolidation — one company, forty names | **Leave out of the running order.** Name it in one sentence where it bites (inside the landscape demo, when applicant counts appear) |
| **5 · Lead Generation** | region → applicants → lead tiers | **Leave out.** Excellent material, no demo partner on stage, and it shares no thread with the other two |
| **6 · Patent Landscape** | corpus → analyses → report | **Keep — one of the two demos** |
| **8 · IPScore** | model → evidence → valuation | **Keep — the other demo** |

The seven A4 handouts already rendered in `9_documentation/course/` are the right home for
everything cut. They exist, they are complete, and they are what a participant takes away.

### The notebooks

| Folder | Notebooks | Role on 18 September |
|---|---|---|
| `6_patentreports/2_antibiotic_resistance_rebuild/` | 4 (`1_dataset…` → `4_assemble_report`) | **the landscape demo** |
| `8_ipscore_rebuild/` | 4 (`1_the_model` → `4_assemble_tool`) | **the valuation demo** |
| `6_patentreports/1_antibiotic_resistance/`, `…_mvp/` | 7 | reference only — do not open on stage |
| `7_ipscore/` | 2 | Riccardo's untouched original — the fallback if the rebuild misbehaves |
| `1_`, `2_`, `3_`, `4_`, `5_` | 13 | not in this session |

---

## 4 · Riccardo's PR #3 — what it adds, and what to take

`rickypriore/patlib-sessions` PR #3, *"Warsaw 2026: live-demo menu + IPScore and Antibiotic
Resistance rebuilds"*, opened 25.08.2026, **260 files, +293,297 lines, still open**.

**Most of it is not new.** The PR carries a **full copy of this repository** — `CLAUDE.md`,
`README.md`, `prep_workshop_todo.md`, `5_lead_generation/`, `3_querylib/tests`,
`9_documentation/course/` and the rest — nested under `PATLIB_Conference_2026_Warsaw/`. That
explains the file count and is the reason the PR cannot simply be merged anywhere.

**What is genuinely new — three things:**

| New | What it does | Verdict |
|---|---|---|
| `8_ipscore_rebuild_v2/0_questionnaire.ipynb` + `0_questionnaire_tool.html` + `tools/build_questionnaire_html.py` | An HTML questionnaire the participant fills in for **their own patent**; it downloads a JSON, the notebook picks it up, and notebooks 2–4 read it. Also offers a plain "edit the values here" path, and documents that `ipywidgets` fails on TIP | **Adopt.** This is the answer to his own objection in the 20.08. mail, and it turns module 8 from a worked example into something a participant can run on their own patent |
| The `kit.EXAMPLE_PATH` pinning in `1_the_model` | Notebook 1 always reproduces the module's shipped example even when a questionnaire has been uploaded | **Adopt** — it is the correct companion to the change above |
| `0_live_demo/Main_menu.ipynb` | A 9-cell launcher: two topics, each with its deck and its finished HTML outcome, opened through `tip_tools.open_html()` | **Adopt the pattern**, review the detail (it opens `.pptx` through `open_html()`, which serves a binary rather than rendering it) |

**Everything else in the v2 tree is a copy.** Compared cell by cell against `8_ipscore_rebuild/`,
notebooks 2, 3 and 4 differ only by **empty trailing cells**; notebook 1 differs by the two cells
named above. There is no second body of work to merge.

**Recommendation (execution is a separate job, not this briefing's):** cherry-pick the
questionnaire trio and the notebook-1 pinning into `8_ipscore_rebuild/` — **do not** take
`_v2/` as a parallel folder, and do not mirror the repo copy. One module 8, not two.

> **Worth saying out loud to Riccardo, kindly.** He committed to his own repository, so the work
> is currently a 260-file PR that nobody can merge. The two genuinely new pieces are small and
> welcome. Agreeing where new work lands — before the next round — costs one sentence now and
> saves this every time.

---

## 5 · The core message, before any slides

The course's own goal sentence is scoped to 4.5 hours and ends on the evidence/judgement split
that module 8 exists to deliver. A 90-minute showcase with two speakers cannot carry it. What the
two remaining demos genuinely share is narrower, and better:

> **A PATLIB can take a real client question — *what does this field look like?*, *what is this
> patent worth?* — and answer it from PATSTAT on TIP with a method that survives being asked
> "how do you know?"**

Everything in the 90 minutes should be justifiable as evidence for that one sentence. That is the
test for each cut below.

---

## 6 · A 90-minute running order (a straw man for your meeting with Riccardo)

| Time | Who | What | From |
|---|---|---|---|
| **0–8** | Arne | The sentence above. The two questions. What TIP and PATSTAT are, for anyone new — **one slide** | Antibiotic deck slide 2 |
| **8–35** | Riccardo | **Demo 1 — the landscape.** The search strategy live (notebook 1 only: keywords **AND** classification, and why the ambiguous acronyms are excluded), then the **finished** report opened from the repo | rebuild notebooks 1 + `4_report/` |
| **35–40** | both | Questions, handover | — |
| **40–67** | Arne | **Demo 2 — the valuation.** The 40 questions and the 8 that move the money; the finished valuation; the one lever worth arguing about | `8_ipscore_rebuild/`, deck slides for module 8 |
| **67–75** | Arne | **The line.** None of the 11 questions PATSTAT can check is one of the 8 that carry money — what a database can check and what a valuation depends on barely overlap | module 8 takeaway |
| **75–85** | both | What you take home, and where it lives: the repo, the seven handouts, the questionnaire for your own patent | handouts + `0_questionnaire` |
| **85–90** | — | **Buffer.** Deliberate. The first demo will overrun | — |

**Why this split.** Each speaker presents the material he authored: Riccardo the antibiotic
landscape, Arne the IPScore rebuild. It also means neither has to present the other's work under
time pressure. **This contradicts one thing Riccardo has prepared** — see the open questions.

---

## 7 · The three decisions that actually buy the time

**1 · Four modules leave the stage: 1, 3, 4 and 5.**
They are 60% of the course deck and none of them is a demo. A showcase earns its keep by showing
two finished things well, not six things at two minutes each. *Where they go instead:* the seven
A4 handouts, already rendered, plus the repository. Say this out loud in the closing — "there are
four more modules and you have them in your hand" lands better than rushing them.

**2 · The live run shrinks to one notebook.**
Not four. Notebook 1 of the landscape chain is the one worth watching, because the search strategy
is the actual professional skill and it is the step that is invisible in a finished report — this
is already the repository's stated position (`prep_workshop_todo.md:157`, *"show the whole chain,
not just the last step"*). Notebooks 2–4 are shown as **their finished outputs**, opened from
disk. *Reason:* tens of seconds per PATSTAT query, ten queries in notebook 2 alone, and a
conference network you do not control.

**3 · Riccardo's IPScore deck becomes the follow-up, not stage time.**
Eleven slides walking notebooks 1→4 with speaker notes is genuinely good material — and it is a
*second* pass over module 8, after Arne's. There is no room for both. *Where it goes instead:*
shared with participants after the session, exactly as Riccardo offered in his 25.08. mail, and
linked from `Main_menu`. It is the best thing to hand someone who wants to go deeper.

---

## 8 · Open questions

### For Arne

1. **The split in section 6 overrides something Riccardo prepared.** His IPScore deck's speaker
   notes describe it as covering "the second block of module 8 that in *your* main part you left
   out" — he has prepared to present the IPScore chain himself. Section 6 gives module 8 to you
   and moves his deck to follow-up. Is that the trade you want, or would you rather hand him
   module 8 entirely and take the landscape yourself?
2. **The screenshot session is still open and the date is close.**
   `plan-tipsession-3-screenshots.md` is unresolved, dated "before 18 September". Until it runs,
   a demo that stalls has **no fallback image**. Either book that TIP session or accept that the
   live part cannot fail.
3. **Do the questionnaire pieces come into `8_ipscore_rebuild/` before Warsaw**, or after? It is
   the difference between "run this on your own patent tonight" and "watch me run it on mine".
4. **Who is the audience, and how many?** Nothing in the repository or the mails says. It changes
   whether section 6 is a demo or a hands-on.

### For Riccardo

1. **Live or slides — and in which order?** Still open per your 20.08. mail; the meeting you
   proposed for the week of 31.08. is the place to settle it. Section 6 is a straw man for it.
2. **Would you take the landscape demo and leave module 8 with Arne?** It concentrates each of us
   on our own material, and your IPScore deck reaches participants as the follow-up instead.
3. **Is the new `0_questionnaire` flow tested yet?** Your 25.08. mail says not. If it is to be
   shown, it needs one full run on TIP first — including the case where the participant has not
   filed anything.
4. **Can the two new pieces land in `mtcberlin/epo-tip4patlibs` rather than as a 260-file PR on
   your side?** The questionnaire and the notebook-1 pinning are small and wanted; the rest of
   PR #3 is a copy of this repository and cannot be merged.
5. **Who authored the two decks?** Both carry python-pptx template metadata rather than a person;
   the IPScore one lists you as author with your speaker notes added on 19.08. Neither came from
   this repository's `build_slides.py` — its slide vocabulary is different. Worth knowing before
   either is re-cut.

---

## Sources

Everything above is from: `~/Downloads/Mails Riccardo.pdf` · the two `.pptx` in `~/Downloads`
(text, speaker notes and file metadata) · `rickypriore/patlib-sessions` PR #3 read via `gh`
(metadata, file list, and file contents compared cell-by-cell against this repository) ·
`prep_workshop_todo.md` · `9_documentation/course/source/slides.yaml` and the module documents ·
the repository's notebook folders at commit `bc7d327`.
