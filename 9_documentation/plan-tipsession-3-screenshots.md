# TIP session 3 — capture: the screenshots the workshop material is missing

**What this is.** The briefing for the **third** TIP session. It is a **capture** session: run
three notebooks that ship deliberately unexecuted, photograph what they produce, and bring the
images back into the repo. Nothing is investigated and nothing is built — sessions 1 and 2 did
that. This one exists because three of the course's own notebooks cannot be screenshotted from a
laptop, by design.

**What it is not.** It is not module 8 work. Module 8 is complete; one cosmetic re-run rides
along as task 3 because it needs TIP and nothing else does.

**Read it for** the shot list. Each image has a slide waiting for it and a filename it must have,
so the deck picks it up on the next build with no further editing.

---

> ## ⏳ Not yet run.
>
> **Blocks:** the workshop deck's *Working through* slides for modules 1, 3 and 5 — currently
> framed placeholders. **Deadline: the workshop is 18 September 2026.**
>
> | Task | | Needs TIP because |
> |---|---|---|
> | **1** screenshots, modules 1 · 3 · 5 | ⏳ | those notebooks ship with cleared outputs — there is nothing to photograph until they run |
> | **2** clear the outputs again before committing | ⏳ | running them dirties notebooks that are *meant* to ship clean |
> | **3** re-run `4_assemble_tool.ipynb` | ⏳ | the report footer is two commits stale; re-rendering off TIP swaps 4.9 MB of `plotly.js` |

| | |
|---|---|
| **Where** | EPO TIP JupyterLab, base conda env, `PatstatClient(env='PROD')` |
| **Time** | ~50 minutes — most of it query latency in module 5 |
| **Deadline** | Workshop **18 September 2026** |
| **Predecessors** | [session 1](plan-tipsession-1-recon.md) · [session 2](plan-tipsession-2-evidence-run.md) · findings in [`results-tipsession.md`](results-tipsession.md) |

---

## Why only these three modules

The course splits on purpose, and the split decides the work:

| Module | Code cells with output | Screenshot |
|---|---|---|
| 1 Start with TIP | **0 of 25** | ⏳ this session |
| 3 Query Library | **6 of 10** | ⏳ this session — the browser is an **ipywidget**: the committed notebook holds a widget reference, not a rendered state, so it cannot be cut offline |
| 5 Lead Generation | **8 of 31** | ⏳ this session |
| 4 PATSTAT Explorer | 7 of 7 | ✅ **done** — cut offline by `course/source/build_shots.py` |
| 6 Patent Reports | 29 of 29 | ✅ **done** — ditto |
| 8 IPScore Rebuild | 37 of 38 | ✅ **done** — ditto |

Modules 1–5 clear their outputs because participants are meant to run them; 6 and 8 ship executed
because they are read as finished reports. That convention is *why* this session exists, so
do not "fix" it — see task 2.

---

## Task 1 · The three screenshots

Save each as **`9_documentation/course/source/shots/NN.png`**, where `NN` is the module number,
zero-padded: `01.png`, `03.png`, `05.png`. `build_slides.py` looks for exactly those names and
drops the image into the slide in place of the placeholder frame. Nothing else has to be edited.

Landscape, roughly 3:2, wide enough that the numbers are legible when projected. Capture the
notebook region — code cell plus its output — not the whole browser with its tab bar.

### 01.png — module 1

> **The applicant search with its result table.**
> `1_startwithtip/2_getting-started-with-patstat.ipynb` · **Part 1, Query 1**

Run the setup cell, then Query 1 with its shipped default (`'%siemens%'`). The shot wants the
`--- CHANGE THIS ---` parameter block **and** the resulting DataFrame in one frame — the slide's
point is that a participant edits one line and gets a table.

*Sections 6–8 of notebook 1 (the Claude Code install) are not needed. Do not run them.*

### 03.png — module 3

> **The Query Browser with a query's SQL open.**
> `3_querylib/TIP_for_PATLIBs_QueryLib.ipynb`

Run both cells, pick any query, and press **View SQL** so the statement is visible. The slide's
point is that the library can be opened up, so the SQL has to be *on screen* — a browser showing
only titles and descriptions misses it.

### 05.png — module 5

> **The lead-tier grid and the named shortlist for Alsace.**
> `5_lead_generation/1_regional-leads.ipynb` · **Step 6**

Run steps 1–6 with the shipped Alsace default (`FR421`, `FR422`, `FRF11`, `FRF12`). Both outputs
of step 6 matter — the depth × reach grid *and* the named shortlist underneath it. If they do not
fit one frame, capture the **shortlist**: it is the artifact a PATLIB acts on, and the module's
whole argument.

> ⚠️ **Sanity check before you photograph it.** Alsace must come out at **78 companies / 396
> families**. If you see **52 / 280**, step 3 lost a NUTS vintage — the number is wrong and so
> would the screenshot be.

---

## Task 2 · Put the notebooks back the way they shipped

> ⚠️ **This is the one way this session can do damage.** Running modules 1, 3 and 5 fills them
> with outputs. Committing them in that state breaks the course convention — participants are
> supposed to receive empty notebooks and run them.

After the screenshots are taken, before anything is committed:

```
Kernel → Restart Kernel and Clear Outputs of All Cells
```

for **each** notebook you ran, then check:

```bash
git -C <repo> status --short          # only the new PNGs should appear
git -C <repo> diff --stat -- '*.ipynb'  # ideally empty
```

If a notebook still shows a diff after clearing, it is execution counts or metadata. Discard it:
`git checkout -- <notebook>`. **The screenshots are the deliverable; the notebooks are not.**

---

## Task 3 · Re-run `4_assemble_tool.ipynb` (module 8, cosmetic)

Two one-line edits were made to notebook 4 in August and never rendered, because re-running it
off TIP swaps the embedded `plotly.js` — TIP builds 3.0.1, a laptop builds a newer one — which is
4.9 MB of library churn for a text change. So the committed report still carries the old footer.

The edits are already in the notebook source (cells 0 and 15): the footer credits **Arne Krüger**
and names **Riccardo Priore's NPV Target Planner** as the source of the scenario analysis.
Running notebook 4 top to bottom picks both up.

> ⚠️ **Cell 19 calls `open_html()` and must ship with its output cleared.** Clear that one cell by
> hand before committing.

**Optional, while you are there.** The data workbook numbers two sheets `6 …` — `6 evidence` and
`6 sensitivity` — because notebook 4 prefixes every contributed section with `6`. Purely
cosmetic. If it is worth fixing, number them by section order instead.

Verify after the run:

| | Expect |
|---|---|
| provenance panel | `2 measured · 6 informed · 32 judgement` |
| NPV | `1,248,870 EUR` — unchanged; if it moved, something else did too |
| footer | names Arne Krüger and the NPV Target Planner |
| report | 9 sections, 6 charts |

---

## Afterwards — what to commit

```
9_documentation/course/source/shots/01.png
9_documentation/course/source/shots/03.png
9_documentation/course/source/shots/05.png
8_ipscore_rebuild/4_assemble_tool.ipynb              # re-run, cell 19 cleared
8_ipscore_rebuild/4_tool/ipscore_valuation.html      # new footer
8_ipscore_rebuild/4_tool/ipscore_valuation_data.xlsx
```

and **nothing under `1_`, `3_` or `5_`**.

Then, off TIP, rebuild the deck so the images land in it:

```bash
cd 9_documentation/course/source
uv run --with python-pptx --with pyyaml python build_slides.py
```

It prints which screenshots are still placeholders. Modules 4, 6 and 8 are already in;
**after this session the list should be empty.**

> ⚠️ **Signing.** Commits made from TIP go in **unsigned**: the 1Password agent is not reachable
> there (`SSH_AUTH_SOCK` is unset) and the only local key is a different one. This has already
> happened once. Either commit from the laptop after pulling, or re-sign on the laptop before the
> release PR into `main`.

---

## Not part of this session

- ~~**Screenshots for modules 4, 6 and 8**~~ ✅ **done.** Their notebooks ship executed, so the
  images were cut from what is already committed, by `course/source/build_shots.py`. That script
  documents the four traps it hit — chief among them that module 8's report has a dark palette and
  headless Chrome asks for dark, and that a pandas header row cannot be counted as a `<tr>`.
- **The handouts.** The seven A4 PDFs currently carry no screenshots. The same PNGs could be
  placed into `course/source/*.md` later; `build_handouts.py` would pick them up. Deliberately
  out of scope here — get the deck complete first.
- **O3 — what does a PATLIB actually get asked?** Still a conversation with Riccardo, not a
  query. Carried over from session 1.
