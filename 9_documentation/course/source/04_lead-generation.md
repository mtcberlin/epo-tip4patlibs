# Module 4 — Regional Lead Generation

*45-minute block · TIP4PATLIBS course material*

> **How to read this document.** The running text addresses **you, the participant**.
> Boxes marked 🎓 are for whoever is **running the session**; boxes marked ⚠️ are traps that
> have caught people before.

---

## Learning objective

**I can profile the applicants of my own region from PATSTAT, segment them into lead tiers along
portfolio depth and geographic reach, and say precisely which companies my method cannot see.**

## Prerequisites

- **Module 1** — TIP is running, PATSTAT connects.
- **Module 2** — you can adapt a query's parameters and judge whether a result is plausible.
- **Module 3** — you count `docdb_family_id`, not applications, and you know that a name is not a
  company.

## Sub-objectives

By the end you can:

1. **Find the NUTS codes for your own region** — *all* of them, across both vintages PATSTAT
   stores side by side — and explain why using only one silently loses a third of your data.
2. **Produce the ranked applicant list** for a region and a time window: companies, by families.
3. **Add the second axis** — geographic reach — and explain what it tells you that depth does not.
4. **Segment into lead tiers** and translate each tier into a concrete PATLIB action.
5. **State the coverage limit out loud**: this is the EP/PCT-active subset of your region, not
   your region.

## Material

| | |
|---|---|
| Folder | `4_lead_generation/` |
| Core notebook | `1_regional-leads.ipynb` — seven steps, default region **Alsace (FR42)** |
| Extensions | `2_national-coverage.ipynb` (the DPMA route) · `3_belgien.ipynb` — optional, not part of this block |
| Runs on | EPO TIP, PATSTAT PROD |
| Ships | with most outputs cleared (8 of 31 cells) — you are meant to run it |

> 🎓 **Trainer.** The full module is about 34 minutes of notebook content across three notebooks.
> **This block is notebook 1 only.** Notebooks 2 and 3 are handed over in Phase 3 as extensions
> for anyone whose region needs national-office data. Announce that split at the start so nobody
> feels rushed past something.

---

## Phase 1 · Introduction (≈ 7 min)

### The question this module answers

> *Your PATLIB is asked to justify its outreach budget. Which companies in your region should you
> actually be talking to — and why those?*

Every PATLIB has a list of contacts. Almost none can say how the list was built. It is usually a
mixture of who walked in, who came to the last event, and who somebody remembered.

This module builds the list from the record instead: **every company in your region that has filed
via the EPO or PCT in a chosen window, ranked, and sorted into tiers you can act on.**

But the module's real lesson is the sentence that comes with the list. Ask the room:

> *If I hand you a ranked list of 78 companies in your region, what is the first question you
> should ask about it?*

The answer you want is **"which companies are missing?"** — and this module can answer it, with a
number.

| | Teaching and learning activity | ⏱ |
|---|---|---|
| Opening | Trainer asks how the PATLIB's current contact list was built | 2 min |
| Tension | Trainer poses the "what is missing" question — nobody's current list can answer it | 2 min |
| Framing | Trainer introduces the two axes (**depth** × **reach**) and the coverage caveat as part of the deliverable, not a footnote | 3 min |

---

## Phase 2 · Working through (≈ 28 min)

Run `1_regional-leads.ipynb`. It ships with **Alsace** as the default so it works out of the box;
you switch it to your own region in step 3.

### Step 1 — Check which data edition you are on (2 min)

One query, one row. Every number in the notebook depends on the PATSTAT edition; on **Global
Autumn 2025** you should see roughly `2025-09-23`. If you see something else, your numbers will
not match the examples in the text — and that is information, not a failure.

### Step 2 — Find your region's NUTS codes (7 min)

This is the step that decides whether the whole analysis is right, and it is the one everybody
skips.

**PATSTAT stores two NUTS vintages side by side**, and a region has a different code in each:

| | carries | labelled? | Alsace |
|---|---|---|---|
| **level 3** | the older codes (EPO) | yes — with a name | `FR421` (Bas-Rhin), `FR422` (Haut-Rhin) |
| **level 4** | the current REGPAT codes (OECD) | **no label in PATSTAT** | `FRF11`, `FRF12` |

> ⚠️ **Filter on one vintage and you silently drop every record stored under the other.** For
> Alsace, `SUBSTR(nuts,1,4) = 'FR42'` returns **52 companies / 280 families**. The correct answer
> is **78 / 396**. Nothing in the output tells you a third of it is missing.

Run the query for your country, read off **all** the codes for your area — the labelled level-3
ones *and* their unlabelled level-4 counterparts — and carry them to step 3.

> 🎓 **Trainer.** Two contrasting cases are worth naming, because they set expectations:
> **France** renumbered its regions between NUTS 2016 and 2021, so Alsace needs four codes.
> **Germany** kept its codes stable, so a whole Bundesland is a single prefix — Saxony is `DED`.
> Let step 2 tell each participant the truth for their own region; do not generalise from one.

### Step 3 — Set your region and window (2 min)

**The only cell you have to edit.** Paste in all your NUTS codes and pick a year window — five or
six years works well: long enough for a portfolio to show, recent enough to be current.

> ⚠️ **A note on speed.** The Alsace default runs in a few seconds. A large Bundesland
> (Bavaria `DE2`, North Rhine-Westphalia `DEA`) covers far more applicants and families, so
> steps 5–6 scan much more data and take noticeably longer. That is expected, not an error.
> Queries on TIP carry no query cost.

### Step 4 — Axis 1: portfolio depth (6 min)

The core deliverable: the **ranked list of company applicants based in your region**, by family
count. For Alsace the head of the list is HAGER ELECTRO SAS (63 families) and KUHN SAS (38),
followed by a long tail — the regional "SME pyramid" almost every European region shows.

### Step 5 — Axis 2: geographic reach (5 min)

Depth tells you *how much* a company files. Reach tells you *how far* it protects. In the Alsace
example HAGER ELECTRO protects broadly in Asia (35 families) and Oceania (20); others lean North
American; and a company whose families almost never leave Europe is a different kind of lead
entirely.

### Step 6 — Segment into lead tiers (6 min)

Combine the two axes into a grid, using neutral tiers:

- **Depth** — `small` (1–2 families) · `medium` (3–10) · `large` (>10)
- **Reach** — `local` (each family uses a single filing route) · `regional` (spans two
  routes/zones but stays within Europe/PCT) · `global` (at least one family reaches North America,
  Asia or Oceania)

And read the grid as **lead priority**:

| Tier | What it usually means for a PATLIB |
|---|---|
| large × global | Established international filers — candidates to **invite as speakers or partners** |
| medium/small × global or regional | Growing filers — the group that most often **needs IP services and training** |
| small × local | Early-stage contacts — awareness and first-consultation work |

The grid totals back to your company count (78 for Alsace). The cell after it turns the map into
the **named shortlist**: one row per company with its family count, its depth and reach tier, and
how many families reach each zone. That is the list you actually act on.

### Step 7 — What this can and cannot see (2 min, and it is the most important 2 minutes)

> ⚠️ **A NUTS filter finds only the EP/PCT-active companies of a region.** NUTS codes are attached
> *only* on the European/PCT route. A purely national filing — a French application that never
> goes to the EPO or via PCT — carries no NUTS code at all. Measured on the current edition,
> roughly **70% of national patent families never take the EP/PCT route**, and about **77% of
> company applicant records have no NUTS at all**. Those are typically the smaller, locally-filing
> firms — often exactly the ones a PATLIB most wants to reach.

So your list is the **EP/PCT-active subset** of your region. Excellent for finding
internationally-minded filers; blind to the national-only tail. PATSTAT cannot recover them by
postcode either — the structured ZIP field is empty and addresses are sparse. For the full
regional population you need national-office data (INPI, DPMA/DEPATISnet) or an external
city → region lookup.

> ⚠️ **One more caveat before you publish a league table.** `han_name` sometimes splits one group
> across several rows — `HAGER ELECTRO` vs `HAGER CONTROLS`, `KUHN SAS` vs `KUHN SA`. This is the
> module 3 problem, arriving in module 4. Consolidate via `doc_std_name_id` / `psn_id` before you
> publish a ranking.

| Step | What you do | What you see | ⏱ |
|---|---|---|---|
| 1 | Check the data edition | The date every number depends on | 2 min |
| 2 | Find *all* your NUTS codes | Two vintages of the same geography | 7 min |
| 3 | Set region + window | The one cell you edit | 2 min |
| 4 | Depth | The ranked company list | 6 min |
| 5 | Reach | How far each one protects | 5 min |
| 6 | Segment | The grid, and the named shortlist | 6 min |
| 7 | Coverage limits | The number that goes under the table | 2 min |

---

## Phase 3 · Learning outcome (≈ 10 min)

### What now exists

- A **named shortlist of companies in your own region**, each with family count, depth tier, reach
  tier and zone breakdown.
- The grid that shows how your region distributes across the tiers.
- One sentence you can defend about what the list does not contain.

This is the first artifact in the course a client can keep.

### Self-check

1. **Your region returns far fewer companies than a neighbouring one of the same size.** First
   thing to check? *(Your NUTS codes — did you collect both vintages in step 2?)*
2. **A colleague reports "there are 78 patenting companies in Alsace."** What is wrong with that
   sentence? *(There are 78 *EP/PCT-active* company applicants in the window you chose. Roughly
   three quarters of company applicant records carry no NUTS code at all.)*
3. **Which tier would you approach first, and what would you offer them?** *(No single right
   answer — but the answer has to name a tier and an offer, not a company.)*
4. **Why does reach matter if you already have depth?** *(A firm with three families in five
   continents behaves nothing like a firm with three families in one country. Depth alone cannot
   tell them apart.)*

### Transfer to your own work

Run the notebook for **your own region and a six-year window**, export the shortlist, and pick
**three companies from the medium × global tier** you have never contacted. That is a concrete
outreach plan, derived from the record, that you can put in front of your director.

> 🎓 **Trainer.** Two extensions to hand over, for anyone whose region is badly served by the
> EP/PCT-only view:
> - **`2_national-coverage.ipynb`** — the DPMA route, for German regions where the national-only
>   tail matters.
> - **`3_belgien.ipynb`** — a second worked region.
>
> Also hand over the known-good check: **Saxony (`DED`, 2017–2022) returns 287 companies / 920
> families, led by NOVALED GMBH (155).** If someone's region swap matches that, they did it right.

---

## Where this leads

| Next | Why |
|---|---|
| **Module 5** — Patent Reports | Module 4 profiles a *region*. Module 5 profiles a *technology field*, and turns it into a publishable report. |
| **Module 6** — IPScore | Your shortlist says which companies matter. Module 6 asks what a single patent of theirs is worth — and how much of that answer is evidence. |

---

## Notes for the next revision

- Module 4 ships with **8 of 31 cells executed**, on purpose. Screenshots for the PDF and the
  slides therefore require a separate TIP run — and unlike module 1, the point of module 4 *is*
  the resulting table, so shipping-state screenshots would be weak. Schedule the run.
- The 70% / 77% coverage figures are stated as "measured on the current edition". Confirm they
  still hold on PATSTAT Global Autumn 2025 before the workshop, or restate them with the edition
  they were measured on.
