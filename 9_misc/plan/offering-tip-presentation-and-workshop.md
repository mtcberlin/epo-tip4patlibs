# Work order · Two TIP offerings for patentreports.depa.tech

**For:** the agent maintaining the `patentreports.depa.tech` site
**From:** the TIP4PATLIBS repository (`mtcberlin/epo-tip4patlibs`)
**Date:** 2026-09-17 · **Status:** ready to implement, prices confirmed by Arne

> **What is being asked.** Add a **fourth and fifth offering** to
> patentreports.depa.tech: a free 30-minute presentation and a paid 2-hour hands-on
> workshop, both about the **EPO Technology Intelligence Platform (TIP)**. The material
> exists, is public, and was delivered successfully on 16–17 September 2026 at the PATLIB
> conference in Warsaw.

---

## 1 · Why these two belong on that page

The site sells three things today, on one axis — *who operates the analysis*:

| | Offering | Positioning | Price |
|---|---|---|---|
| 1 | Report | *"We run it. Once."* | from €1,500 |
| 2 | Toolchain | *"You run it. Continuously."* | €6,000/yr · €500/mo |
| 3 | Custom Solution | *"We run it with you."* | on request |

All three are **independent of TIP**. The two new ones are the opposite: they are *about*
TIP, they are cheap or free, and they are an **on-ramp**, not a competing product.

Someone who attends the workshop has, at the end, a working analysis environment they did
not have before — and a concrete sense of where their own capability stops and a
commissioned report starts. That is the commercial logic: the workshop qualifies leads for
offerings 1–3 without selling them.

**Do not position them as a cheaper Report.** They are a different axis: *teaching*, not
*delivery*.

---

## 2 · The two offerings

### 4 · Presentation — *"We show you."* · **free** · 30 minutes

**TIP for Patent Intelligence.** What the EPO's Technology Intelligence Platform is, what
it can answer, and what it takes to get a first result. Five worked modules shown live,
each one a finished analysis with its result on screen.

- Remote or on site, for a PATLIB, a university library or an IP department
- No prerequisites, nothing to install, nobody has to write a query
- Ends with the repository link — everything shown is public and re-runnable

### 5 · Workshop — *"You run it. On your own TIP."* · **€80 per participant, up to 3** · 2 hours

**Hands-on.** Participants bring their own laptops, log into their own TIP account, and
install the course repository into their own environment with a single command. They then
work through the modules with their own region, their own company, their own question.

- **Up to 3 participants: €80 each** (€240 total)
- Larger groups: see §5 — pricing to be decided
- Prerequisite: each participant needs their **own EPO TIP account** (free, but must exist
  *before* the session — arrange this in the booking confirmation, it is the single most
  likely thing to derail a workshop)
- Installation is one command; see §4

---

## 3 · What is actually shown — the five modules

This is the running order, and it is deliberately an **escalation**. Confirmed in Warsaw on
17 September 2026: participants understood all five and were visibly impressed, and the
escalation is what carried it.

| # | Module | What the audience sees | Why it sits here |
|---|--------|------------------------|------------------|
| **1** | Query Library | A result table, and not much else | **Deliberately the plainest thing in the course.** It is raw output — that is the point. Everything after this is a step up from it |
| **2** | PATSTAT Explorer | A real web application running inside TIP | The first "oh" — the same data, but an interface |
| **3** | Regional Lead Generation | *Who are the applicants in my region?* | The first module that is immediately **useful to a PATLIB's own job**. The one participants ask about afterwards |
| **4** | Antibiotic Resistance Report | A publishable multi-section landscape report | Scale. A finished deliverable, not a query result |
| **5** | IPScore | A questionnaire page in, a valuation page out | The most finished artifact — two web pages, no notebook needed |

**Two notes from the Warsaw delivery, and they matter for timing:**

- **Module 4 was shown as the result only.** Time ran short and the multi-step notebooks
  were skipped. It still landed. Treat the report itself as the deliverable to show; the
  notebooks behind it are optional depth.
- **Module 5 was shown as the two web pages only** — the input questionnaire and the output
  valuation. The notebooks were never opened and it still came across well. In a
  30-minute slot, **do not open the module 5 notebooks.**

**The AI assistant is mentioned, not demonstrated.** In Warsaw it came up only indirectly:
*these five modules exist, and the way to extend them or build your own is an assistant
that writes the SQL for you.* Nobody was asked to install or use one during the session.
Keep it that way — the offering is about patent intelligence, not about AI tooling.

---

## 4 · What the participant installs

One command in a TIP terminal:

```bash
curl -fsSL https://raw.githubusercontent.com/mtcberlin/epo-tip4patlibs/main/install.sh | bash
```

It installs an assistant that survives a TIP restart, configures it, and clones the course
material into `~/epo-tip4patlibs`. It is idempotent, so it can be re-run when TIP rebuilds
the machine.

**The notebooks ship executed with their code folded away**, so a participant sees the
explanation and the result without reading a line of code — and without waiting for a query
to return. The cells they are meant to change (search term, region) stay open.

**Two things need credentials, and neither blocks the workshop:**

| What | Needed for | When |
|---|---|---|
| Anthropic subscription | Changing notebooks with the assistant | Only if a participant wants to extend the material |
| `DPMA_USER` / `DPMA_PASS` | Module 3's *second* notebook (German national coverage) | Optional extension. Module 3's main notebook runs on PATSTAT alone |

Mention both as *"if you want to go further"*, not as prerequisites.

---

## 5 · Open decisions for Arne

1. **Pricing above 3 participants.** €80 × 3 = €240 for two hours. A per-group price
   probably serves better beyond that — e.g. a flat rate per session up to ~10, since the
   effort barely changes with headcount. Needs a number.
2. **Remote or on site**, and whether travel is billed separately.
3. **Language.** The site is English throughout; the material is English; a PATLIB audience
   in Germany may expect German. Decide whether the offering is bilingual.
4. **Does the free presentation need a booking form**, or is a mail link enough?

---

## 6 · Implementation notes for the site agent

- **Match the existing pattern.** Each offering on the page has a positioning line in the
  form *"<who> runs it. <how often>."* — the two suggested above follow it.
- **English**, matching the rest of the page.
- **Keep the same tone:** concrete, technical, no adjectives doing work that facts should
  do. The page's credibility comes from specificity ("queries.sql ships with the report",
  "13 numbered QA checks") — these two offerings should be equally specific: five named
  modules, one install command, two hours.
- **Link the repository** — `github.com/mtcberlin/epo-tip4patlibs`. It is public, and the
  fact that the entire course is inspectable before booking is a selling point in exactly
  the way the rest of the page argues.
- **Do not claim** that the workshop teaches SQL or programming. It teaches reading a
  result critically and deciding what to ask. That distinction is the course's whole
  premise.
- Consider placing them **before** the three paid offerings or in a separate band —
  free-then-cheap-then-paid reads better than a €1,500 report followed by a free talk.

---

## 7 · Source material in this repository

| What | Where |
|---|---|
| The five modules | `1_querylib/` … `5_ipscore/` |
| Workshop deck (19 slides, as delivered) | `9_misc/handouts/source/TIP4PATLIBS_1_Workshop_v4.pptx` |
| 45-minute written version per module | `9_misc/handouts/*.pdf` |
| Installer | `install.sh` |
| How the Warsaw session was planned | `9_misc/plan/archive/plan-workshop-warsaw.md` |
