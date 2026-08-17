# Module 6 — Patent Landscape Reports

*45-minute block · TIP4PATLIBS course material*

> Landscape analyses after **Riccardo Priore**, Centro PATLIB, AREA Science Park.
> This module is contributed material, reworked to match the course's look. The analytical
> approach and the worked example are his.

> **How to read this document.** The running text addresses **you, the participant**.
> Boxes marked 🎓 are for whoever is **running the session**; boxes marked ⚠️ are traps that
> have caught people before.

---

## Learning objective

**I can define a patent corpus with a search strategy I am able to defend, run a battery of
standard analyses over it, and assemble the result into one self-contained report a client can
keep.**

## Prerequisites

- **Module 1** — TIP is running, PATSTAT connects.
- **Module 3** — you can read a query and judge a result.
- **Module 4** — you know that an applicant name is not a company.

## Sub-objectives

By the end you can:

1. **Build a corpus as an intersection**, not as a keyword search: keywords **AND** (IPC OR CPC),
   and explain what each half of that rule is for.
2. **Justify an exclusion** — say why generic terms and bare acronyms were deliberately left out,
   and what precision that bought.
3. **Recognise the report pipeline's one shape**: a question in markdown → one code cell that
   reads the shared corpus, queries PATSTAT and builds one figure → one `record(...)` call.
4. **Read a landscape report critically** — which of its thirteen charts answers *who*, which
   answers *where*, which answers *when*, and which answers *how it connects*.
5. **Say what the assembled artifact is**: one self-contained HTML file plus one workbook, no
   internet required.

## Material

| | |
|---|---|
| Folder | `6_patentreports/2_antibiotic_resistance_rebuild/` |
| Notebooks | `1_dataset_and_search_strategy` · `2_core_landscape_analyses` · `3_advanced_analyses` · `4_assemble_report` |
| Artifact | `4_report/antibiotic_resistance_report.html` + `…_report_data.xlsx` |
| Runs on | EPO TIP, PATSTAT PROD (notebook 2's citation analysis uses BigQuery) |
| Ships | **pre-executed** — 29 of 29 code cells, outputs kept |

> ⚠️ **This module ships with its outputs, and that is deliberate.** Modules 1–5 clear their
> outputs because participants are meant to run them. Module 6 is read as a **finished report** in
> a showcase. The outputs *are* the deliverable — never re-run the cells to "tidy" them.

> 🎓 **Trainer.** The sibling folders `1_antibiotic_resistance/` (the imported reference) and
> `2_antibiotic_resistance_mvp/` (the frozen MVP) are **not** course material. Use the rebuild.
> If someone asks about t-SNE clusters or triadic families, those live in the reference folder and
> are a future phase of the rebuild — say so rather than improvising.

---

## Phase 1 · Introduction (≈ 7 min)

### The question this module answers

> *A regional cluster manager asks: "give us a picture of what is happening in antibiotic
> resistance." Where do you start?*

Everyone starts in the same place — a keyword — and this is where a landscape report is won or
lost. Ask the room what they would search for. Somebody will say **"drug resistance"**. Somebody
will say **MRSA**.

Both are the wrong answer, and for opposite reasons:

- **"drug resistance"** is dominated by **cancer**. Your antibiotic landscape would be an oncology
  landscape wearing the wrong label.
- **MRSA, VRE, ESBL** — bare acronyms — are noisy. They collide with unrelated strings and appear
  in documents that are not about the thing at all.

Neither problem is visible in the result. You get a large corpus, it looks healthy, and it is
about something else.

The fix is not a better keyword. It is a **rule with two independent halves**: a family must match
a keyword **and** carry a relevant classification. Keywords bring recall; classification brings
precision. Neither alone is defensible.

| | Teaching and learning activity | ⏱ |
|---|---|---|
| Opening | Trainer asks for search terms for "antibiotic resistance"; collects them | 2 min |
| Tension | Trainer names what "drug resistance" and bare acronyms actually return | 3 min |
| Framing | Trainer states the module's rule: **keywords AND (IPC OR CPC)** — and that the exclusions are part of the method, to be written down | 2 min |

---

## Phase 2 · Working through (≈ 28 min)

Four notebooks, one pipeline. **Run them in order 1 → 2 → 3 → 4** — each writes what the next
reads.

### Step 1 — Define the corpus (10 min) · `1_dataset_and_search_strategy.ipynb`

Eight steps that end in one file.

| | What happens |
|---|---|
| 1 | Connect to PATSTAT PROD via the SQLAlchemy ORM interface, and import `report_kit` |
| 2 | **The keyword strategy** — three groups of terms: the core concept, the resistance *mechanisms*, and an explicit bacterial context. Generic "drug resistance" and bare acronyms are excluded on purpose |
| 3 | **Classification filters (IPC / CPC)**, one code list serving both |
| 4 | **Combine**: intersect the keyword families with the classification families |
| 5 | **One representative publication per family**, 2000 onwards, preferring **EP > WO > US** |
| 6 | **Export** `dataset.xlsx` — the single shared corpus notebooks 2 and 3 read |
| 7 | First chart — how the field has grown, by earliest filing year |
| 8 | Second chart — the twenty leading IPC classes |

> ⚠️ **Watch the spacing in IPC symbols.** An 8-character IPC symbol is a 4-character subclass,
> then padding spaces, then the main-group number: `A61K  31` is **two** spaces, `C12Q   1` is
> **three**. Get the padding wrong and the filter matches nothing — silently, with no error.

> 🎓 **Trainer.** Step 5 is a decision worth naming: *one representative publication per family*,
> preferring EP then WO then US. That is a choice, and a different preference order would give a
> different citable number for the same invention. It is the module 4 lesson again — the
> defensible part is that it was written down.

### Step 2 — The core landscape battery (10 min) · `2_core_landscape_analyses.ipynb`

Ten charts, all reading the same corpus. Do not walk through all ten — walk through the
**structure**, then let the room read.

| The question | The charts |
|---|---|
| **Where?** | filings by international/regional authority · national filing trends · national vs international filing strategy |
| **When?** | WO (PCT) vs EP over time · innovation waves by technology area |
| **How far?** | family size & global reach |
| **Who?** | top applicants by families · applicants by institutional sector · grant rate by top applicant · most influential organisations (forward citations) |

> 🎓 **Trainer.** The sector chart and the grant-rate chart are the two a PATLIB audience reacts
> to, because they separate universities from companies and separate *filing a lot* from *getting
> granted*. If time is short, spend it on those two and let the rest be read.

> ⚠️ The forward-citation analysis runs against **BigQuery**, not the TIP PATSTAT client — a
> citation self-join is the honest tool for that question and BigQuery is where it is affordable.
> That cell therefore needs separate credentials and will not run for a participant who only has
> TIP. Its output ships with the notebook.

### Step 3 — One advanced analysis (4 min) · `3_advanced_analyses.ipynb`

A **technology co-occurrence network**: which IPC fields appear together on the same families.
Five steps — load the corpus, map IPC codes to technology fields, keep the codes with at least 50
families, self-join to find co-occurrences, draw the network above an edge threshold.

This is the one chart in the report that answers a question the others cannot: **how the field is
connected**, rather than how big it is or who is in it.

### Step 4 — Assemble the report (4 min) · `4_assemble_report.ipynb`

Four steps, and this is where the pipeline pays off.

Every analysis in notebooks 1–3 ended with a `report_kit.record(...)` call that showed the figure
inline *and* saved two things: the figure as an inline HTML fragment, and the data behind it.
Notebook 4 collects every contribution from the output manifests, orders them, and stitches them
into:

- **one self-contained HTML report** — a single embedded copy of `plotly.js`, **no iframes**, so
  it renders inside TIP and works with no internet at all. It has two view modes switched by a
  header button: **Paged** (one chart at a time, step bar, Previous/Next, ←/→ keys) and **One
  page** (everything stacked).
- **one data workbook** — one sheet per chart, so a client can check any number.

It is opened with the course's shared `open_html()` helper.

> ⚠️ **Never open a TIP-generated report with `IFrame`.** TIP's content-security policy sandboxes
> iframes and disables their JavaScript, so an interactive report renders as a blank or dead box.
> `open_html()` goes through jupyter-server-proxy and works. This applies to modules 6, 7 and 8
> alike.

| Step | What you do | What you see | ⏱ |
|---|---|---|---|
| 1 | Build the corpus | One `dataset.xlsx`, and two charts | 10 min |
| 2 | Run the core battery | Ten charts: where, when, how far, who | 10 min |
| 3 | Run the network analysis | How the technology fields connect | 4 min |
| 4 | Assemble | One HTML report + one workbook | 4 min |

---

## Phase 3 · Learning outcome (≈ 10 min)

### What now exists

- **One self-contained HTML landscape report** — **13 charts** (2 from notebook 1, 10 from
  notebook 2, 1 from notebook 3) — that opens on any machine with a browser and no internet.
- **One workbook** carrying the data behind every chart.
- **A written search strategy** — including its exclusions — that you can hand to anyone who
  disputes the corpus.

The third item is what makes the first two worth anything.

### Self-check

1. **Why is `keywords AND (IPC OR CPC)` better than either half alone?** *(Keywords give recall
   but no precision; classification gives precision but misses anything classified oddly. The
   intersection is defensible in both directions.)*
2. **You are asked why MRSA is not in your search terms.** Your answer? *(Bare acronyms are noisy;
   precision comes from requiring a classification match. Note that this is an argued choice, not
   an oversight.)*
3. **Your IPC filter returns zero families and throws no error.** *(Check the padding: `A61K  31`
   is two spaces, `C12Q   1` is three.)*
4. **A client opens your report on a laptop with no internet. Does it work?** *(Yes — the plotly
   library is embedded and there are no external requests. That was a design requirement, not a
   convenience.)*

### Transfer to your own work

Take the pipeline and change **only notebook 1**. Pick a technology your region actually cares
about, write the three keyword groups and the classification list, and run notebooks 2–4 unchanged.

That is the real lesson of the module: the analyses are generic; **the corpus definition is the
part that is yours**, and it is the part you have to be able to defend.

> 🎓 **Trainer.** Close by opening the shipped report in Paged mode and walking the last three
> slides of it. The participants have just seen how each chart is made; seeing them assembled as a
> client-facing document is what makes the pipeline feel worth building.

---

## Where this leads

| Next | Why |
|---|---|
| **Module 8** — IPScore | Module 6 describes a whole field. Module 8 asks what **one patent** in it is worth — and how much of that answer is evidence. The worked example in module 8 is drawn from *this* corpus. |
| **Module 7** — IPScore (Riccardo's tools) | The companion valuation module, outside this course block. |

---

## Notes for the next revision

- The rebuild's `README.md` states that notebook 3 holds the technology network only, and that
  temporal, citation, t-SNE, SDG and triadic analyses are "the next phase". The repository-level
  `CLAUDE.md` describes module 6 as including t-SNE clusters and triadic families — that describes
  the older `1_antibiotic_resistance/` folder. **Align the two descriptions** before the workshop
  so nobody promises a chart that is not in the report.
- The forward-citation cell's BigQuery dependency should be stated in the notebook header, not
  only in the cell comment — a participant who tries to re-run notebook 2 on TIP alone will hit it.
