# Product Brief: TIP for PATLIBs

**Date:** 2026-01-10
**Author:** BMad
**Context:** Enterprise/Institutional (EPO initiative for PATLIB network)

---

## Executive Summary

**TIP for PATLIBs** is a ready-to-use Python analysis environment for the EPO's Technology Intelligence Platform (TIP), designed specifically for PATLIB centres. The solution enables patent information professionals to perform sophisticated regional, sectoral, and comparative patent analysis without programming skills.

Despite extensive PATSTAT, Python, and Jupyter training materials, PATLIB staff lack basic developer experience and time to learn. This project delivers a **product, not more education** - pre-built Jupyter notebooks with transparent Python scripts and no-code UI controls that demonstrate TIP's capabilities while being immediately useful.

The solution will be demonstrated at the PATLIB Conference in May 2026 and forms the basis for a pilot scheme targeting adoption across the European PATLIB network.

**Budget:** 10,000 EUR (Round 1)
**Prototype Deadline:** Mid-February 2026 (4 weeks)
**Conference Demo:** May 2026

---

## Core Vision

### Problem Statement

PATLIB centres are staffed by patent information professionals who need to analyse patent and innovation data for their advisory work. However:

1. **Skills Gap:** Despite extensive training materials, PATLIB staff lack basic developer experience to use TIP effectively
2. **Time Constraints:** Entry-level TIP users have limited time to invest in learning Python
3. **Analysis Limitations:** They need regional and sectoral comparisons they cannot easily perform today
4. **Tool Competition:** TIP's Jupyter output is "limited and unimpressive" compared to commercial tools like lens.org

The result: TIP adoption among PATLIBs remains low despite its powerful PATSTAT backend.

### Problem Impact

- EPO's investment in TIP is underutilized by a key target audience
- PATLIBs cannot deliver data-driven insights to their customers (SME inventors, tech transfer agencies)
- Training efforts have failed to bridge the skills gap
- Questionnaire feedback confirms: training isn't the solution

### Why Existing Solutions Fall Short

| Current State | Why It Fails |
|---------------|--------------|
| Raw TIP/Jupyter | Requires Python knowledge |
| PATSTAT training | PATLIBs lack time and developer mindset |
| Documentation | Reading docs ≠ being productive |
| Commercial tools | Not integrated with TIP, not free |

### Proposed Solution

A Jupyter notebook application with:

1. **Transparent script loading** - "Execute this cell first!" initializes all dependencies
2. **No-code UI layer** - Dropdowns, input fields, and buttons for all user interactions
3. **Plotly visualizations** - Interactive charts rendered in Jupyter cells
4. **Pre-built analysis workflows** - Regional, sectoral, and temporal patent analysis ready to use

```
┌─────────────────────────────────────────────────────┐
│  Jupyter Notebook (TIP Environment)                 │
├─────────────────────────────────────────────────────┤
│  Cell 1: "Execute this cell first!" (loads scripts) │
│  Cell 2+: No-code UI                                │
│    → Dropdowns (country, region, sector)            │
│    → Input fields (date range, keywords)            │
│    → Buttons ("Run Analysis", "Export")             │
│    → Plotly visualizations (interactive charts)     │
└─────────────────────────────────────────────────────┘
```

**Future enhancement (out of scope for Round 1):** Streamlit or D3-based companion site for richer visualization outside TIP's rendering limitations.

### Key Differentiators

- **Transparency:** Code is visible (learning by seeing), but interaction is no-code
- **Immediate value:** Useful from first use, no learning curve
- **TIP-native:** Built for the platform PATLIBs already have access to
- **Free:** No licensing costs, shareable across the network
- **PATSTAT expertise:** Handles the complexity of PATSTAT queries under the hood

---

## Target Users

### Primary Users

**PATLIB Staff (Entry-Level TIP Users)**

- Patent information professionals at PATLIB centres across Europe
- Limited or no Python/programming experience
- Limited time to invest in learning new tools
- Need to deliver patent analysis for advisory work
- Value: Quick insights for marketing their services and serving customers

**Characteristics:**
- Understand patent data conceptually (IPC, applicants, jurisdictions)
- Comfortable with web interfaces and basic data tools
- Frustrated by the gap between TIP's potential and their ability to use it

### Secondary Users (Downstream)

PATLIBs will share this free tool with their networks:

| User Type | Use Case |
|-----------|----------|
| Chambers of Commerce | Innovation/entrepreneurship consulting |
| Tech Transfer Agencies | University-industry collaboration analysis |
| SME Inventors | Understanding their competitive landscape |

### Key Stakeholder

**Rainer Kaysen (EPO)** - Project sponsor, success gatekeeper. His satisfaction determines project success and future contracts.

---

## Success Metrics

### Quantitative (Pilot Phase)

| Metric | Target |
|--------|--------|
| PATLIBs actively using the tool | 5+ centres in pilot |
| LinkedIn posts sharing analyses | Evidence of organic adoption |
| German PATLIB adoption | Traction among the 16 German PATLIBs |

### Qualitative

| Stakeholder | Success Indicator |
|-------------|-------------------|
| Rainer Kaysen (EPO) | "Happy and loves it" - wants to continue/expand |
| PATLIB Conference audience | Enthusiastic reception at May demo |
| German PATLIBs | Find it useful for marketing and customer work |
| TU Chemnitz PATLIB | Positive feedback (strategic relationship) |

### Business Objectives

- Increase TIP adoption across PATLIB network
- Demonstrate TIP value to justify continued EPO investment
- Create foundation for expanded tooling (Round 2+)
- Position contractor (BMad) as trusted TIP solutions partner

---

## MVP Scope

### Core Features (Round 1 - 10k EUR)

1. **Setup Cell**
   - "Execute this cell first!" initialization
   - Loads all dependencies
   - Handles library installation/updates
   - Environment compatibility checks

2. **Country Selector**
   - Dropdown for all TIP-supported countries
   - Foundation for all analyses

3. **Region Selector**
   - NUTS regions / federal states
   - Cascading from country selection
   - Optional (can analyze at country level only)

4. **Technology Sector Selector**
   - 35 predefined PATSTAT sectors
   - IPC concordance validation
   - Clear sector descriptions

5. **Date Range Selector**
   - Input fields for start/end year
   - Support for 5/10/15 year trend analysis

6. **Core Visualizations (Plotly)**
   - Patent application trends over time
   - Top N applicants ranking
   - Geographic distribution (regional analysis)
   - Technology sector breakdown

7. **Export Capability**
   - Download results as CSV
   - Export charts as PNG

### Example Query (The "Killer Demo")

> "Show me all medtech patents and the top 10 applicants in Wales"

This translates to:
- Country: United Kingdom
- Region: Wales
- Sector: Medical Technology
- Output: Top 10 applicants + trend visualization

### Nice-to-Have (If Time/Budget Allows)

- European universities innovation network analysis
- External data correlation (EUROSTAT, World Bank, OECD)
- Streamlit companion site prototype

### Explicitly Out of Scope (Round 2)

- Power user code editing features
- Custom query builder interface
- Advanced analytics/correlations
- Multi-language UI
- User authentication/personalization

**Note:** Code is transparent by nature (Jupyter). Power users CAN read/modify code anytime - we're just not designing for that use case in Round 1.

---

## Technical Preferences

### Platform

- **Environment:** EPO Technology Intelligence Platform (TIP)
- **Interface:** Jupyter Notebook (JupyterLab)
- **Backend:** PATSTAT via EPO patstat Python library + SQLAlchemy ORM

### Technology Stack

| Component | Technology |
|-----------|------------|
| Data Access | EPO patstat library, SQLAlchemy |
| Data Processing | Pandas |
| Visualizations | Plotly |
| UI Widgets | ipywidgets (jupyter-widgets) |
| Future UI | Streamlit or D3 (Round 2+) |

### Environment Considerations

- Discover TIP environment constraints during development
- Tests must verify environment compatibility
- Solution must handle own dependencies (install/update via pip)
- Available extensions: jupyter-ai-core, jupyter-widgets-jupyterlab-manager, PYPI manager

### Data Sources

| Source | Priority | Purpose |
|--------|----------|---------|
| PATSTAT | Core | Patent applications, applicants, IPC/CPC |
| 35 Technology Sectors | Core | Predefined sector classification |
| IPC Concordance | Core | Sector-to-IPC mapping validation |
| European Universities | Nice-to-have | Innovation network analysis |
| EUROSTAT/World Bank/OECD | Nice-to-have | Socioeconomic correlations |

---

## Risks and Assumptions

### Critical Risk

**PATSTAT Complexity and Data Quality**

This is the primary concern. PATSTAT has known challenges:
- Applicant name variations (same company, different spellings)
- Address parsing inconsistencies
- Classification gaps and errors
- Regional attribution complexity (NUTS mapping)

**Mitigation:**
- Build on proven query patterns
- Implement data quality indicators in UI
- Set realistic expectations with users
- Document known limitations

### Other Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| TIP environment constraints | Medium | Medium | Early testing, adaptive design |
| Scope creep from EPO | Medium | High | Clear MVP definition, change control |
| Timeline pressure (4 weeks) | High | High | Prioritize ruthlessly, defer nice-to-haves |
| Conference demo failure | Low | Critical | Multiple dry runs, backup demos |

### Assumptions

- TIP environment supports required Python libraries (or allows installation)
- PATSTAT data access via existing EPO patstat library works as documented
- 35 technology sectors and IPC concordance are stable/documented
- Rainer Kaysen remains the primary stakeholder

---

## Timeline

| Milestone | Date | Deliverable |
|-----------|------|-------------|
| Project Start | 2026-01-10 | Product Brief approved |
| Working Prototype | Mid-February 2026 | Core features functional |
| Rainer Review | Feb-March 2026 | Feedback incorporation |
| Polish & Testing | March-April 2026 | Production-ready |
| PATLIB Conference | May 2026 | Live demo |
| Pilot Launch | 2026 | Rollout to select PATLIBs |

---

## Supporting Materials

### Input Documents

- PRD_TIP4PATLIBS_Technical_Document.pdf (EPO customer briefing)
- PATLIB interview findings (6 structured interviews)

### Reference

- EPO patstat Python library documentation
- PATSTAT data model
- 35 Technology Sectors concordance list
- NUTS regional classification

---

_This Product Brief captures the vision and requirements for TIP for PATLIBs._

_It was created through collaborative discovery and reflects the unique needs of this enterprise/institutional project._

_Next: PRD workflow will transform this brief into detailed product requirements with epics and user stories._

---

## EXTENSION: Phase 2 Features (Added 2026-01-21)

### Context

Based on stakeholder discussions and analysis of the existing `QueryLib_for_PATLIBs.ipynb` notebook (containing 11+ validated BigQuery queries), two major features have been identified for Phase 2 development:

1. **Query Library** - End-user product for PATLIBs
2. **MCP Server** - Developer/marketing tool for query generation

These features build upon the Round 1 MVP and represent the evolution from "demonstration notebooks" to "production-ready tools."

---

## Feature 1: Query Library (Phase 2 MVP)

### Vision

A curated library of validated PATSTAT queries with a parameter-based UI, enabling PATLIBs, patent attorneys, and IP managers to execute sophisticated patent analyses without writing SQL.

### Problem Statement

The existing 11+ validated queries in `QueryLib_for_PATLIBs.ipynb` demonstrate powerful analyses, but:

1. Users must understand and modify SQL to change parameters
2. No systematic parameter validation or guidance
3. Queries are embedded in notebook cells, not reusable
4. No documentation of what parameters are configurable

### Proposed Solution

```
┌─────────────────────────────────────────────────────────────────────┐
│                        QUERY LIBRARY UI                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Step 1: SELECT QUERY                                               │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ [Dropdown: Select Business Question]                         │    │
│  │  • Country Patent Activity & Grant Rates                     │    │
│  │  • Technology Fields by Citations                            │    │
│  │  • Top Patent Applicants                                     │    │
│  │  • German Federal States (A61B)                              │    │
│  │  • Competitor Filing Strategy                                │    │
│  │  • ... (11+ queries)                                         │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  Step 2: CONFIGURE PARAMETERS                                       │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ [Dynamic form based on selected query]                       │    │
│  │  • Time Period: [2015] to [2024]                             │    │
│  │  • IPC Class: [A61B______]                                   │    │
│  │  • Country: [DE, US, CN, ...]                                │    │
│  │  • Region: [NUTS Level 1]                                    │    │
│  │  • Applicant Filter: [Optional text]                         │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  Step 3: EXECUTE & DISPLAY                                          │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ [Execute Query]  [Export CSV]  [Export PNG]                  │    │
│  │                                                               │    │
│  │ Results: DataFrame display                                   │    │
│  │ Visualization: Plotly chart (later phase)                    │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Validated Queries (Existing Assets)

Based on analysis of `QueryLib_for_PATLIBs.ipynb`:

| # | Business Question | Status | Key Parameters |
|---|-------------------|--------|----------------|
| 1 | Country Patent Activity & Grant Rates | Validated | year_from, min_patents |
| 2 | Technology Fields by Citations | Validated | year_from, year_to, weight_threshold |
| 3 | Top Patent Applicants | Validated | year_from, min_applications |
| 4 | Citation Network Analysis | Validated | citing_year |
| 5 | Green Tech Evolution by Country | Validated | year_from, year_to, countries[] |
| 6 | German Federal States (A61B) | Validated | year_from, year_to, ipc_class |
| 7 | Competitor Geographic Filing Strategy | Validated | competitor_names[], tech_sector |
| 8 | Diagnostic Imaging Grant Rates | Validated | year_from, year_to, offices[] |
| 9 | AI-based ERP Patent Landscape | Validated | year_from |
| 10 | Patents per Mio Inhabitants (DE) | Validated | year_from, ipc_class |
| 11 | Fastest-growing G06Q Subclasses | Validated | base_year, comparison_year |
| 12 | AI-assisted Diagnostics Companies | Review needed | - |
| 13 | Regional Tech Sector Comparison | Review needed | regions[], year_from |

### Target Users

| User Type | Role | Value |
|-----------|------|-------|
| PATLIB Staff | Primary | Quick access to validated analyses for customer work |
| Patent Attorneys | Secondary | Competitive landscape analysis |
| IP Managers (SME) | Secondary | Portfolio benchmarking |

### Technical Implementation

- **Database:** BigQuery exclusively (no Postgres)
- **Client:** `PatstatClient` from `epo.tipdata.patstat`
- **UI Framework:** ipywidgets for Jupyter integration
- **Query Storage:** Parameterized SQL templates with metadata
- **Visualization:** Plotly (later phase), Pygwalker (exploration)

### Success Metrics

| Metric | Target |
|--------|--------|
| Queries in library | 15+ validated |
| Parameter coverage | All common use cases |
| User adoption | 10+ active PATLIBs |

---

## Feature 2: MCP Server (Future/Marketing)

### Vision

An AI-powered query generation service that converts natural language business questions into validated PATSTAT BigQuery queries, enabling rapid expansion of the Query Library.

### Strategic Purpose

1. **Internal:** Enable Query Library managers to rapidly add new queries
2. **External:** Demonstrate AI capability as marketing differentiator
3. **Future:** Standalone service offering outside TIP environment

### Proposed Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        QUERY LIBRARY ECOSYSTEM                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────────┐         ┌──────────────────────────────┐  │
│  │   MCP SERVER         │         │      QUERY LIBRARY           │  │
│  │   (Query Factory)    │         │      (End User Product)      │  │
│  │                      │         │                              │  │
│  │  Business Question   │ ──────▶ │  Validated Queries           │  │
│  │        ↓             │  TEST   │  with Parameter UI           │  │
│  │  Generated Query     │ ──────▶ │        ↓                     │  │
│  │        ↓             │ VALIDATE│  Execute & Display           │  │
│  │  Query Description   │         │        ↓                     │  │
│  │                      │         │  Visualization               │  │
│  │  Users: Developers,  │         │                              │  │
│  │  Query Lib Managers  │         │  Users: PATLIBs, IP Mgrs,    │  │
│  │                      │         │  Patent Attorneys            │  │
│  └──────────────────────┘         └──────────────────────────────┘  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### MCP Context Package (Required Assets)

| Asset | Status | Purpose |
|-------|--------|---------|
| `patstat-2026-01-19-context.json` | Exists | Business descriptions of 28 tables/columns |
| `patstat_global_schema.json` | Exists (54k tokens) | Technical schema (needs summarization) |
| `patstat_table_relations.md` | To create | FK/JOIN documentation |
| `query_examples.json` | To extract | 11+ validated queries as few-shot examples |
| `bigquery_syntax_notes.md` | To create | BigQuery-specific syntax guidance |

### Dream Workflow

1. IP Manager submits new business question
2. MCP generates query + description
3. Developer/Manager tests query in TIP environment
4. Validated query added to Query Library
5. End users can immediately use new query with parameters

### Technical Notes

- Context JSON currently uses `public.tls201_appln` format (Postgres)
- BigQuery uses `tls201_appln` format (no schema prefix)
- Schema cleanup task required before MCP implementation

### Phase

**Future/Marketing** - Not in current Round 1 or immediate Phase 2 scope. To be developed after Query Library MVP is stable.

---

## Updated Technical Findings

### Database Clarification

| Aspect | Decision |
|--------|----------|
| Primary Database | BigQuery exclusively |
| Postgres References | Legacy, to be ignored |
| Schema Documentation | `patstat-2026-01-19-context.json` (28 tables, business descriptions) |
| Raw Schema | `patstat_global_schema.json` (54k tokens, needs summarization for MCP) |

### Existing Assets Inventory

| Asset | Location | Status |
|-------|----------|--------|
| Validated Queries | `context/QueryLib_for_PATLIBs.ipynb` | 11 validated, 2 need review |
| Business Context | `context/patstat-2026-01-19-context.json` | Ready for MCP use |
| Technical Schema | `context/patstat_global_schema.json` | Too large, needs processing |
| Sample Queries | `context/patstat-2026-01-19-sample.json` | 5 example queries |

### Implementation Notes

- PatstatClient wrapper: `from epo.tipdata.patstat import PatstatClient`
- Query execution: `patstat.sql_query(query, use_legacy_sql=False)`
- All queries must use BigQuery syntax (not Postgres)

---

## Updated Phasing

### Round 1 (Current - 10k EUR)
- Core MVP as originally defined
- Working prototype by mid-February 2026
- Conference demo in May 2026

### Phase 2 (Post-Conference)
**Query Library MVP:**
- Epic 6: Query Library Core
  - Extract and parameterize existing 11+ queries
  - Build parameter UI components
  - Create query metadata schema
  - Implement query execution wrapper
- Epic 7: Query Library Polish
  - Documentation of configurable parameters
  - Error handling and validation
  - Export capabilities (CSV, PNG)

### Future Phase (Marketing/Service)
**MCP Server:**
- Schema cleanup (remove public. prefix)
- Context package assembly
- MCP implementation
- Query validation workflow
- Standalone service packaging

---

## Risk Update

### New Risk: Scope Expansion

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Phase 2 scope delays Round 1 | Low | High | Keep phases strictly separate |
| Query Library complexity underestimated | Medium | Medium | Start with 5 core queries, expand incrementally |
| MCP distracts from user-facing features | Medium | Medium | Defer MCP until Query Library stable |

### Assumption Update

- Phase 2 features (Query Library, MCP) are **additive** and do not modify Round 1 deliverables
- Existing validated queries in notebook are production-quality
- BigQuery is the only target database

---

_Extension added: 2026-01-21_
_Context: Party Mode discussion with full BMAD agent team_
_Next: Extend PRD with Epic 6+ for Phase 2 features_
