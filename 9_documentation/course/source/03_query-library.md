# Module 3 — The Query Library

*45-minute block · TIP4PATLIBS course material*

> **How to read this document.** The running text addresses **you, the participant**.
> Boxes marked 🎓 are for whoever is **running the session**; boxes marked ⚠️ are traps that
> have caught people before.

---

## Learning objective

**I can pick a ready-made PATSTAT query, adapt its parameters to my own question, and judge
whether the result is plausible — without writing SQL.**

## Prerequisites

- **Module 1** — TIP is running, PATSTAT connects with `PatstatClient(env='PROD')`.
- No SQL knowledge. That is the point of this module.

## Sub-objectives

By the end you can:

1. **Map a client's question onto a query category** — decide *which* of the library's queries
   answers what you were actually asked.
2. **Change parameters safely** — country, year window, technology field — and know which
   changes are cheap and which are expensive.
3. **Judge plausibility** — recognise a result that is suspiciously large, suspiciously small,
   or silently truncated.
4. **Know when to stop** — recognise the questions the library cannot answer, and what to reach
   for instead.

## Material

| | |
|---|---|
| Folder | `2_querylib/` |
| Notebooks | `TIP_for_PATLIBs_QueryLib.ipynb` (the browser) · `TIP_for_PATLIBs_InteractiveQueryDemo.ipynb` (point-and-click) |
| Runs on | EPO TIP, PATSTAT PROD |

---

## Phase 1 · Introduction (≈ 7 min)

### The question this module answers

> *A client walks in: "Who in Europe is working on solid-state batteries?"*

Give the room two minutes to say how they would answer it. Collect the proposals.

**What almost always comes back first is a keyword search.** And a keyword search is not wrong —
it is just not defensible. Ask the follow-up: *how would you prove to that client that your list
is complete?* Keywords miss everything phrased differently, and catch everything that merely
mentions the term. Neither problem is visible in the result.

That gap is what a curated query library exists to close. Someone has already decided which
tables to join, which filters are non-negotiable, and what "complete" means for each type of
question. Your job shifts from *writing* the query to *choosing* it and *reading* it.

| | Teaching and learning activity | ⏱ |
|---|---|---|
| Opening | Trainer poses the client question; room proposes approaches out loud | 2 min |
| Tension | Trainer asks "how do you prove it is complete?" — the proposals fall apart | 2 min |
| Framing | Trainer introduces the library as *pre-made professional decisions*, not as a shortcut | 3 min |

> 🎓 **Trainer.** The expected wrong answer is *"search Google Patents"* or *"type keywords into
> Espacenet"*. Take it seriously — it is what most people do and it is often adequate. Do not
> mock it; ask what happens when the client's competitor turns up a patent that your list missed.
> The room will get there on its own.

> 🎓 **Trainer.** If the room is quiet, name a concrete failure: a search for *"battery"* misses
> every document that says *"accumulator"* or *"electrochemical cell"*.

---

## Phase 2 · Working through (≈ 28 min)

### Step 1 — Open the library and look at what is there (8 min)

Run `TIP_for_PATLIBs_QueryLib.ipynb` top to bottom. It has only two cells: a setup cell that
initialises the registry, and the **Query Browser**.

In the browser:

- **Browse by category** using the dropdown.
- **Search** by typing a keyword — it searches titles, descriptions and tags.
- **Preview** a query to see what it needs and what it returns.
- **View SQL** to see the template with its parameters highlighted.

**Do this deliberately: open "View SQL" at least once.** You are not expected to read it fluently.
You are expected to see that there *is* something to read — that the number the library gives you
comes from a statement you could inspect, hand to a colleague, or argue about.

> 🎓 **Trainer.** This is the moment worth slowing down for. The difference between a tool and a
> black box is whether you can open it. Say it out loud: *an analysis you cannot open up is one
> you cannot defend.* The same sentence returns in modules 4 and 8.

### Step 2 — Adapt one query to your own question (12 min)

Pick a query that matches a question you actually get asked. Change its parameters — country,
year window, technology field — and run it.

Two rules while you do this:

- **Change one thing at a time.** If the result surprises you, you want to know which change
  caused it.
- **Watch the clock on the query.** The library reports how long each query took.

> ⚠️ **PATSTAT PROD is not fast.** A query scanning a full year of filings takes tens of seconds
> to a minute or more. That is normal, not a fault. Widening a year window or dropping a country
> filter multiplies the work; a query that ran in 10 seconds can take several minutes with the
> filter removed. Say this to the room *before* someone decides the notebook has crashed.

### Step 3 — The interactive demo (8 min)

Open `TIP_for_PATLIBs_InteractiveQueryDemo.ipynb` and run the first cell to load the components.
Then use the **Selection** controls — jurisdiction, region, technology field or custom IPC/CPC,
date range — and read the **Results**: a table and a chart, no code touched.

This is the same data through a different door. Note which door you would put in front of a
client, and which you would use yourself.

> ⚠️ **Stop after the "Data Validation" section.** The notebook ends with two cells headed
> *"Story 3.2 AC Validation"* and *"Story 3.3 AC Validation"*. Those are developer acceptance
> tests left over from building the tool — not course content. Skip them; they will run, and
> their output means nothing to a participant.

> 🎓 **Trainer.** Note this as a known rough edge rather than apologising for it. It is honest,
> and it is on the cleanup list.

| Step | What you do | What you see | ⏱ |
|---|---|---|---|
| 1 | Browse the library, open one query's SQL | The decisions someone made for you | 8 min |
| 2 | Adapt parameters, run, time it | Your own question answered — and what it costs | 12 min |
| 3 | Drive the interactive demo | The same data through a point-and-click door | 8 min |

---

## Phase 3 · Learning outcome (≈ 10 min)

### What now exists

- One query adapted to a question **you** are actually asked, with its result table.
- A first feel for what a PATSTAT query costs in time.

### Self-check

Answer these before moving on. If one is unclear, go back to the query that raised it.

1. **Which query would you use** for *"has patenting in my region gone up or down over ten
   years?"* — and which would you use for *"who are the biggest filers in this technology?"*
2. **Why does the same question return fewer rows** when you filter `appln_auth = 'EP'` than when
   you count `docdb_family_id`? *(Because one counts filings at one office, the other counts
   inventions wherever they were filed. Module 4 makes this the centre of the lesson.)*
3. **You widened the year window from 5 to 20 years and the query is still running after three
   minutes.** Broken, or working? *(Working. Narrow it, get the answer, then widen deliberately.)*
4. **A client asks which of two companies has the "better" portfolio.** Can the library answer
   that? *(No. It can measure size, reach and technology mix. "Better" is a judgement — and
   module 8 is about exactly that boundary.)*

### Transfer to your own work

Write down the **three questions you are asked most often** at your PATLIB desk. For each, note
which library query comes closest, and what is missing. That list is your agenda for modules 4
and 5 — and it is worth keeping.

> 🎓 **Trainer.** Close by collecting two or three of those questions from the room. If one of
> them is *"who around here is patenting?"*, you have your bridge into module 5. If it is *"is
> this company big or small in IP?"*, that is module 4.

---

## Where this leads

| Next | Why |
|---|---|
| **Module 4** — PATSTAT Explorer | The library counts *names*. Module 4 shows why one company is forty different names, and how to consolidate them. |
| **Module 5** — Lead Generation | The first full application: a region's applicants, ranked and segmented. |

---

## Notes for the next revision

- The two *"Story 3.x AC Validation"* cells at the end of the interactive demo are developer
  scaffolding and should be removed from the course version of the notebook.
- Module 3 is the shortest module in the course (≈ 8 minutes of notebook content). This block
  works because the introduction and the transfer exercise carry real weight — do not cut them to
  save time.
