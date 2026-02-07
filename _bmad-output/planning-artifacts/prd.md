---
stepsCompleted: [step-01-init, step-02-discovery, step-03-success, step-04-journeys, step-05-domain, step-06-innovation-skipped, step-07-project-type, step-08-scoping, step-09-functional, step-10-nonfunctional, step-11-polish, step-12-complete]
status: complete
completedAt: 2026-02-01
inputDocuments:
  - _bmad-output/planning-artifacts/product-brief-epo-tip4patlibs-bmad-2026-02-01.md
  - context/BPM001977_Technical_Specifications__TIP4PATLIB.pdf
  - context/index.md
  - context/project-overview.md
workflowType: 'prd'
classification:
  projectType: developer_tool
  domain: patent_information_institutional
  complexity: medium
  projectContext: brownfield
---

# Product Requirements Document - TIP for PATLIBs Phase 2

**Author:** Arne
**Date:** 2026-02-01

---

## Executive Summary

**TIP for PATLIBs Phase 2** delivers four production-ready Jupyter notebooks and educational materials for EPO Academy's PATLIB training program as part of the PATLIB2028 roadmap.

**Budget:** 14,000 EUR

### Deliverables

| # | Notebook | Description |
|---|----------|-------------|
| 1 | **Query Library** | 42 parameterized PATSTAT queries with selector UI |
| 2 | **Interactive Demo** | Guided TIP walkthrough for training sessions |
| 3 | **AI Query Builder** | Natural language → PATSTAT SQL generation |
| 4 | **University Analysis** | European university patent portfolio analysis |

**Plus:** Handbook, quick reference guides, 20 hours training delivery, Streamlit app maintenance

### Target Users

- **PATLIB Staff (Entry-Level):** Run queries without coding
- **PATLIB Staff (Multiplicators):** Extend and share customizations
- **University PATLIB Staff:** Analyze university innovation landscapes

### Key Differentiators

- **Learn by doing:** Notebooks are useful from first cell execution
- **TIP-native:** Built for the platform PATLIBs already have access to
- **Transparent code:** Users see Python/SQL but interact via UI controls
- **Dual-purpose:** Training material AND practical tool

---

## Project Classification

| Attribute | Value |
|-----------|-------|
| Project Type | Jupyter notebook training toolkit |
| Domain | Patent Information (Institutional) |
| Complexity | Medium |
| Context | Brownfield (existing notebooks to refactor) |

---

## Success Criteria

### User Success

**PATLIB Staff (Entry-Level):**
- Can run a query and present results to a client without writing code
- Feels confident using TIP after training session
- Returns to use notebooks independently for real client work

**PATLIB Staff (Multiplicators):**
- Can modify queries for new use cases
- Shares customizations within their regional network
- Becomes local TIP expert others turn to for help

**University PATLIB Staff:**
- Can analyze their university's patent portfolio
- Identifies top inventors and industry collaborations
- Presents innovation insights to university leadership

### Business Success

| Metric | Target |
|--------|--------|
| Contract deliverables | 4 notebooks + 20 hours training + educational materials |
| Stakeholder satisfaction | Rainer Kaysen wants to continue partnership |
| Training effectiveness | Participants can use notebooks independently after training |
| PATLIB2028 contribution | Measurable increase in TIP adoption across network |

### Technical Success

| Metric | Target |
|--------|--------|
| TIP compatibility | All notebooks run in TIP Jupyter environment |
| Query execution | Queries complete within reasonable time (< 2 min) |
| Documentation | Each notebook is self-documenting and didactic |
| Extensibility | PATLIBs can add/modify queries without breaking things |

---

## Product Scope

### Core Deliverables (14k EUR)

| # | Notebook | Scope |
|---|----------|-------|
| 1 | **Query Library** | 42 queries migrated, query selector UI, extensibility mechanism |
| 2 | **Interactive Demo** | Training-ready walkthrough of TIP capabilities |
| 3 | **AI Query Builder** | Natural language → PATSTAT SQL (Jupyter version) |
| 4 | **University Analysis** | European university selector, portfolio analysis, inventor networks |

**Plus:** Handbook, quick guides, 20 hours training delivery, Streamlit app maintenance

### Out of Scope

- Multi-language UI (English only)
- Non-TIP deployments
- Custom development per PATLIB centre

### Future Considerations

- Query sharing/collaboration between PATLIBs
- Community-contributed queries workflow
- Extended university coverage

---

## User Journeys

### Journey 1: Maria - First Query Success (Entry-Level)

**Maria** is a patent information specialist at a PATLIB centre in Portugal. She's been to PATSTAT training twice but still feels lost when she opens TIP. Her boss wants her to prepare a report on medtech innovation in the Lisbon region for a local startup accelerator.

**Opening Scene:** Maria logs into TIP, opens the Query Library notebook. She sees a friendly selector: "What would you like to analyze?" She picks "Regional Technology Analysis."

**Rising Action:** The notebook shows her simple dropdowns: Country → Portugal, Region → Lisboa, Technology → Medical Technology, Years → 2019-2024. No code visible, just clear labels. She clicks "Run Query."

**Climax:** Results appear in 45 seconds. A table shows top applicants, a chart shows the trend. Maria realizes she just did in 2 minutes what she couldn't figure out in 2 hours last time.

**Resolution:** She exports to CSV, pastes into her PowerPoint, and delivers the report. Her boss is impressed. Maria bookmarks the notebook and returns weekly.

---

### Journey 2: Thomas - Building Local Expertise (Multiplicator)

**Thomas** works at the German PATLIB in Munich. He's technically curious and has done some Python tutorials. After the training session, he wants to create a custom query for automotive patents in Bavaria.

**Opening Scene:** Thomas opens the Query Library notebook, runs a standard regional query, then scrolls down to see the SQL. He thinks "I could modify this."

**Rising Action:** He copies the query cell, changes the IPC filter from medtech to automotive (F02, B60), adjusts the NUTS region to Bavaria. The query runs. He gets excited.

**Climax:** Thomas saves his modified notebook, shares it with colleagues at other German PATLIBs. They start asking him for help with their own modifications.

**Resolution:** Thomas becomes the go-to TIP expert in the German PATLIB network. He presents his customizations at the next working group meeting.

---

### Journey 3: Dr. Chen - University Innovation Report (University PATLIB)

**Dr. Chen** runs the IP office at a technical university in the Netherlands. The rector wants a report on the university's patent position compared to peer institutions for a board meeting.

**Opening Scene:** Dr. Chen opens the University Analysis notebook. She selects her university from the dropdown, then adds two peer universities for comparison.

**Rising Action:** The notebook runs PATSTAT queries showing: total applications by year, top inventor names, technology field distribution, industry collaboration patterns.

**Climax:** Dr. Chen discovers that her university has strong collaboration with Philips in medical imaging - a partnership she didn't know existed at this scale.

**Resolution:** She exports the analysis, presents to the board. The rector asks her to run quarterly reports. The notebook becomes a core tool for her office.

---

### Journey 4: Trainer - Delivering the Workshop

**EPO Academy trainer** is delivering a 4-hour online workshop to 25 PATLIB staff from across Europe.

**Opening Scene:** Trainer shares screen showing the Interactive Demo notebook. Explains "Today we'll learn TIP by doing, not reading."

**Rising Action:** Participants follow along, running the same queries. Trainer shows how to change parameters. Participants experiment with their own regions.

**Climax:** A participant asks "Can I do this for universities?" Trainer opens the University Analysis notebook, shows it's the same pattern.

**Resolution:** Workshop ends with participants having run 5+ queries on their own. They leave with bookmarked notebooks and a quick reference guide.

---

### Journey Requirements Summary

| Journey | Capabilities Revealed |
|---------|----------------------|
| Maria (Entry-Level) | Query selector UI, parameter dropdowns, one-click execution, CSV export |
| Thomas (Multiplicator) | Visible SQL, copy-modify pattern, notebook saving, sharing mechanism |
| Dr. Chen (University) | University selector, peer comparison, inventor networks, industry collaboration |
| Trainer | Demo flow, training structure, quick reference materials |

---

## Domain-Specific Requirements

### TIP Environment Constraints

| Constraint | Implication |
|------------|-------------|
| Jupyter-only execution | All notebooks must run in JupyterLab; no standalone apps |
| PatstatClient required | Data access via `from epo.tipdata.patstat import PatstatClient` only |
| BigQuery backend | SQL must be BigQuery-compatible (not Postgres) |
| Package availability | Only pip-installable packages; check TIP's pre-installed list |
| No external network | Cannot call external APIs from within TIP (except PATSTAT) |
| Cell output limits | Large result sets may truncate; pagination needed |

### PATSTAT Data Quality Considerations

| Issue | Mitigation |
|-------|------------|
| Applicant name variations | Document limitation; consider fuzzy matching for future |
| NUTS region mapping gaps | Show "data unavailable" gracefully for unmapped regions |
| IPC classification gaps | Older patents may lack classifications; filter appropriately |
| Query performance | Add progress indicators; warn users about broad queries |
| Data freshness | PATSTAT updates quarterly; document data vintage |

### Institutional Context Requirements

| Requirement | Rationale |
|-------------|-----------|
| Didactic structure | Notebooks are training materials first, tools second |
| Self-contained documentation | Each notebook must be usable without trainer present |
| Cascadable training | Materials support "train the trainer" / multiplicator model |
| Multi-centre sharing | Notebooks become shared assets across 300+ PATLIB centres |
| EPO Academy alignment | Materials must fit EPO training curriculum standards |

### Technical Standards

- **Code visibility:** SQL and Python visible but interaction via UI (ipywidgets)
- **Consistent patterns:** All 4 notebooks use same data access and UI patterns
- **Error handling:** User-friendly messages, no raw tracebacks
- **Export formats:** CSV and PNG minimum; Excel nice-to-have

---

## Developer Tool Specific Requirements

### Project-Type Overview

This is a **Jupyter notebook-based training toolkit** - notebooks that function as both documentation and executable tools. Unlike typical developer tools (libraries, SDKs), these are end-user products for non-developers.

### Technical Architecture Considerations

**Notebook Structure Pattern:**
```
┌─────────────────────────────────────────┐
│ Cell 1: Setup (PatstatClient init)      │
│ Cell 2: UI Controls (ipywidgets)        │
│ Cell 3: Query Execution                 │
│ Cell 4: Results Display                 │
│ Cell 5: Export Options                  │
│ (Repeat pattern for each feature)       │
└─────────────────────────────────────────┘
```

**Shared Components:**
- `PatstatClient` wrapper for all data access
- Common ipywidgets patterns (dropdowns, buttons, progress)
- Consistent error handling and user feedback
- Unified export functionality (CSV, PNG)

### Language & Runtime

| Aspect | Specification |
|--------|---------------|
| Language | Python 3.10+ (TIP's version) |
| Execution | JupyterLab cells |
| Data access | `from epo.tipdata.patstat import PatstatClient` |
| UI framework | ipywidgets |
| Visualization | Plotly (interactive) or Matplotlib (static) |

### Installation & Dependencies

| Package | Purpose | Installation |
|---------|---------|--------------|
| ipywidgets | UI controls | Pre-installed in TIP |
| pandas | Data manipulation | Pre-installed in TIP |
| plotly | Interactive charts | pip install if needed |
| PatstatClient | PATSTAT access | Pre-installed in TIP |

### Code Examples Strategy

Each notebook IS an example. Code visibility philosophy:
- SQL queries visible in cells (transparency)
- Python logic visible but abstracted where possible
- ipywidgets hide complexity behind UI controls
- Users can copy/modify cells for customization

### Documentation Approach

| Layer | Content |
|-------|---------|
| In-notebook | Markdown cells explaining each section |
| Handbook | PDF/HTML guide covering all 4 notebooks |
| Quick reference | One-page cheat sheet per notebook |
| Training slides | For EPO Academy workshops |

---

## Project Scoping & Phased Development

### Scoping Philosophy

This is a **contract delivery** project, not a startup MVP. The scope is fixed by the EPO agreement. Our focus is:
1. Prioritize within the fixed scope
2. Identify dependencies between deliverables
3. Define what "done" looks like for each notebook
4. Plan for potential scope creep resistance

### Delivery Prioritization

| Priority | Deliverable | Rationale |
|----------|-------------|-----------|
| **P1** | Query Library | Foundation - 42 queries, most training value |
| **P1** | Interactive Demo | Needed for training sessions |
| **P2** | AI Query Builder | Depends on Query Library patterns |
| **P2** | University Analysis | Standalone, can develop in parallel |
| **P3** | Handbook & Guides | Write after notebooks are stable |
| **P3** | Training Delivery | After materials are ready |

### Notebook Dependencies

```
Query Library ──────┬──────> AI Query Builder
                    │        (reuses query patterns)
                    │
Interactive Demo ───┴──────> Training Sessions
                             (demo + library together)

University Analysis ───────> (independent track)
```

### Definition of Done (per Notebook)

| Notebook | "Done" Criteria |
|----------|-----------------|
| Query Library | 42 queries migrated, selector UI works, extensibility tested |
| Interactive Demo | Training flow complete, runs in TIP, tested with non-developer |
| AI Query Builder | Claude integration works, generates valid PATSTAT SQL |
| University Analysis | European universities list, PatstatClient queries, portfolio analysis |

### Risk Mitigation

| Risk | Mitigation |
|------|------------|
| TIP environment issues | Early testing, adaptive design |
| Query migration takes longer | Start with 20 core queries, add rest iteratively |
| AI Builder complexity | Keep simple - single prompt, no conversation |
| University list incomplete | Start with German universities (have data), expand to EU |

### Out of Scope (Resist Scope Creep)

- Multi-language UI
- Custom PATLIB deployments
- New query development beyond migration
- Streamlit app new features (maintenance only)

---

## Functional Requirements

### Query Library Notebook

- **FR1:** Users can browse all 42 available queries via a categorized selector
- **FR2:** Users can search/filter queries by keyword, category, or stakeholder tag
- **FR3:** Users can view query description and expected output before execution
- **FR4:** Users can configure query parameters via UI controls (dropdowns, sliders, text inputs)
- **FR5:** Users can execute a selected query with configured parameters
- **FR6:** Users can view query results as a formatted DataFrame
- **FR7:** Users can export query results to CSV
- **FR8:** Users can export visualizations to PNG
- **FR9:** Users can view the underlying SQL for any query
- **FR10:** Users can copy and modify query cells for customization
- **FR11:** System provides progress indicator during query execution
- **FR12:** System displays user-friendly error messages when queries fail

### Interactive Demo Notebook

- **FR13:** Users can follow a guided walkthrough of TIP capabilities
- **FR14:** Users can execute demo queries step-by-step with explanations
- **FR15:** Users can see example outputs and visualizations inline
- **FR16:** Trainers can use the notebook as a presentation tool
- **FR17:** Users can complete the demo independently without trainer assistance

### AI Query Builder Notebook

- **FR18:** Users can describe a business question in natural language
- **FR19:** System generates valid PATSTAT/BigQuery SQL from natural language input
- **FR20:** System displays generated SQL with explanation of query logic
- **FR21:** Users can execute the generated query directly
- **FR22:** Users can modify the generated SQL before execution
- **FR23:** System validates generated SQL before execution
- **FR24:** Users can save successful AI-generated queries for reuse

### University Analysis Notebook

- **FR25:** Users can select a university from a list of European universities
- **FR26:** Users can compare multiple universities side-by-side
- **FR27:** Users can view university patent application trends over time
- **FR28:** Users can view top inventors at a selected university
- **FR29:** Users can view industry collaboration patterns for a university
- **FR30:** Users can view technology field distribution for a university
- **FR31:** Users can export university analysis results to CSV
- **FR32:** System provides university metadata (student count, location, type)

### Common Notebook Features

- **FR33:** All notebooks initialize with a single "Run this cell first" setup cell
- **FR34:** All notebooks display clear status messages during operations
- **FR35:** All notebooks handle errors gracefully with actionable messages
- **FR36:** All notebooks use consistent UI patterns (ipywidgets)
- **FR37:** All notebooks include inline documentation explaining each section
- **FR38:** All notebooks can be reset to initial state

### Data Access & Integration

- **FR39:** System connects to PATSTAT via PatstatClient
- **FR40:** System executes queries against BigQuery backend
- **FR41:** System handles query timeouts gracefully
- **FR42:** System respects TIP environment constraints

### Educational Materials

- **FR43:** Users can access a handbook covering all 4 notebooks
- **FR44:** Users can access quick reference guides (one per notebook)
- **FR45:** Trainers can access presentation materials for workshops
- **FR46:** Users can access step-by-step tutorials with screenshots

---

## Non-Functional Requirements

### Performance

- **NFR1:** Standard queries complete within 120 seconds
- **NFR2:** UI controls respond to user input within 1 second
- **NFR3:** Notebook initialization (setup cell) completes within 30 seconds
- **NFR4:** Export operations (CSV, PNG) complete within 10 seconds
- **NFR5:** Progress indicators update at least every 5 seconds during long operations

### Reliability

- **NFR6:** Notebooks recover gracefully from interrupted queries
- **NFR7:** Error messages are user-friendly and suggest next actions
- **NFR8:** Notebooks can be re-run from any cell without side effects
- **NFR9:** System handles PATSTAT connection failures without crashing

### Integration

- **NFR10:** All notebooks run in TIP's JupyterLab environment without modification
- **NFR11:** PatstatClient is the only data access method (no direct BigQuery)
- **NFR12:** Notebooks are compatible with TIP's pre-installed package versions
- **NFR13:** No external network calls required (except PATSTAT via PatstatClient)

### Maintainability

- **NFR14:** Code is organized into logical cells with clear markdown documentation
- **NFR15:** Query SQL is readable and commented
- **NFR16:** Configuration values (defaults, colors) are centralized
- **NFR17:** New queries can be added without restructuring the notebook

### Usability

- **NFR18:** Non-technical users can execute queries without reading code
- **NFR19:** UI labels and messages use plain language (no jargon)
- **NFR20:** Notebooks are usable without trainer assistance after initial training
