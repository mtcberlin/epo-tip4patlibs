# TIP for PATLIBs - Product Requirements Document

**Author:** BMad
**Date:** 2026-01-10
**Version:** 1.0

---

## Executive Summary

**TIP for PATLIBs** is a ready-to-use Python analysis environment for EPO's Technology Intelligence Platform, enabling PATLIB staff to perform sophisticated patent analysis without programming skills.

The solution delivers a Jupyter notebook application with transparent Python scripts and no-code UI controls (dropdowns, buttons, input fields) that make TIP's powerful PATSTAT backend accessible to entry-level users.

### What Makes This Special

> **A product, not education.** Despite extensive training materials, PATLIB staff lack developer experience. This solution meets them where they are - no learning curve, immediate value, transparent code they can see but don't need to touch.

---

## Project Classification

**Technical Type:** Data Analysis Tool / Jupyter Application
**Domain:** Patent Information / PATSTAT Analytics
**Complexity:** Medium (PATSTAT complexity, focused scope)
**Field Type:** Greenfield

### Platform Context

- **Environment:** EPO Technology Intelligence Platform (TIP)
- **Interface:** Jupyter Notebook (JupyterLab)
- **Backend:** PATSTAT via EPO patstat Python library + SQLAlchemy ORM
- **Data Source:** PATSTAT Global Database (66 tables, key: TLS201_APPLN, TLS206_PERSON, TLS209_APPLN_IPC)

---

## Success Criteria

### Primary Success Indicators

| Stakeholder | Success Looks Like |
|-------------|-------------------|
| Rainer Kaysen (EPO) | Happy, wants Round 2 contract |
| PATLIB Conference (May 2026) | Enthusiastic demo reception |
| German PATLIBs (16 centres) | Active usage, sharing on LinkedIn |
| Pilot Phase | 5+ PATLIB centres using regularly |

### Business Metrics

- Increase TIP adoption across PATLIB network
- Demonstrate TIP value to justify continued EPO investment
- Position contractor as trusted TIP solutions partner
- Create foundation for expanded tooling (Round 2+)

---

## Product Scope

### MVP - Minimum Viable Product (Round 1: 10k EUR, 4 weeks to prototype)

**Core Analysis Flow:**
```
Country Selection → Region Selection (optional) → Technology Sector → Date Range → Analyze → Visualize → Export
```

**Deliverables:**
1. Single Jupyter notebook with all functionality
2. Setup cell that initializes environment
3. No-code UI for all user interactions
4. 4 core visualizations (Plotly)
5. CSV/PNG export capability

### Growth Features (Round 2 - Out of Scope)

- European universities innovation network analysis
- External data integration (EUROSTAT, World Bank, OECD)
- Streamlit companion site
- Power user custom query builder
- Advanced analytics/correlations

### Vision (Future)

- Multi-language UI
- User profiles and saved queries
- Automated report generation
- API for programmatic access

---

## User Experience Principles

### Design Philosophy

- **Transparent but hands-off:** Code is visible (Jupyter), interaction is no-code
- **Progressive disclosure:** Start simple (country), add complexity (region, sector) as needed
- **Immediate feedback:** Every selection updates available options
- **No dead ends:** Always show what can be done next

### Key Interactions

1. **First Contact:** "Execute this cell first!" - single click to initialize
2. **Selection Flow:** Cascading dropdowns that filter based on previous choices
3. **Analysis Trigger:** Clear "Run Analysis" button
4. **Results:** Interactive Plotly charts with hover details
5. **Export:** One-click CSV/PNG download

### Visual Personality

- Professional, clean, institutional (EPO context)
- Clear typography, sufficient whitespace
- Consistent color scheme aligned with EPO branding
- Charts optimized for presentations and reports

---

## Functional Requirements

### Setup & Initialization

- **FR1:** System provides a single initialization cell that loads all dependencies when executed
- **FR2:** System automatically checks environment compatibility and reports issues clearly
- **FR3:** System handles library installation/updates via pip when needed
- **FR4:** System displays initialization status (success/failure) with actionable messages

### Country Selection

- **FR5:** Users can select a country from a dropdown of all TIP-supported jurisdictions
- **FR6:** System displays country names in a user-friendly format (not just ISO codes)
- **FR7:** Country selection is required before any analysis can proceed
- **FR8:** System remembers the last selected country within a session

### Region Selection

- **FR9:** Users can optionally select a region/federal state within the chosen country
- **FR10:** Region dropdown dynamically populates based on selected country (NUTS regions)
- **FR11:** Users can analyze at country level without selecting a region
- **FR12:** System clearly indicates when regional data is not available for a country

### Technology Sector Selection

- **FR13:** Users can select from 35 WIPO technology fields via dropdown
- **FR14:** Technology fields are grouped by sector (Electrical engineering, Instruments, Chemistry, Mechanical engineering, Other)
- **FR15:** System displays both field number and descriptive name (e.g., "13 - Medical technology")
- **FR16:** Users can view the IPC codes mapped to each technology field
- **FR17:** System uses PATSTAT built-in concordance tables (tls901_techn_field_ipc for mapping, tls230_appln_techn_field for pre-computed assignments)

### Date Range Selection

- **FR18:** Users can specify start year and end year for analysis
- **FR19:** System provides sensible defaults (e.g., last 10 years)
- **FR20:** System validates date range (start < end, within available data)
- **FR21:** Users can select preset ranges (5 years, 10 years, 15 years) via quick buttons

### Data Query & Processing

- **FR22:** System queries PATSTAT using EPO patstat library and SQLAlchemy ORM
- **FR23:** System filters patent applications by jurisdiction, region (if selected), technology sector (via IPC concordance), and date range
- **FR24:** System retrieves applicant information including names and countries
- **FR25:** System aggregates data appropriately for each visualization type
- **FR26:** System displays query progress indicator during data retrieval
- **FR27:** System handles query errors gracefully with user-friendly error messages

### Visualization - Patent Application Trends

- **FR28:** System displays patent application count over time as interactive line/bar chart
- **FR29:** Chart shows year-over-year trends within selected date range
- **FR30:** Users can hover over data points to see exact values
- **FR31:** Chart title reflects current filter selections (country, region, sector, dates)

### Visualization - Top Applicants

- **FR32:** System displays top N applicants as horizontal bar chart
- **FR33:** Users can configure N (default: 10, options: 5, 10, 20, 50)
- **FR34:** Chart shows applicant names and application counts
- **FR35:** Users can hover to see additional applicant details (country)

### Visualization - Geographic Distribution

- **FR36:** System displays regional patent distribution when region data is available
- **FR37:** Visualization shows relative patent activity across regions
- **FR38:** Users can compare regions within a country

### Visualization - Technology Sector Breakdown

- **FR39:** System displays distribution across technology sub-fields (IPC classes) as pie/treemap chart
- **FR40:** Chart shows which specific IPC areas within the selected sector are most active
- **FR41:** Users can drill down to see individual IPC class details

### Export Capability

- **FR42:** Users can export analysis results to CSV file
- **FR43:** CSV export includes all retrieved data with clear column headers
- **FR44:** Users can export charts as PNG images
- **FR45:** Export files are named descriptively (include country, sector, date range)
- **FR46:** System provides download links/buttons for exported files

### User Interface Components

- **FR47:** All user inputs use ipywidgets (dropdowns, buttons, text inputs)
- **FR48:** UI components are clearly labeled with descriptive text
- **FR49:** Required fields are visually distinguished from optional fields
- **FR50:** System provides "Reset" functionality to clear all selections
- **FR51:** UI layout is responsive within Jupyter notebook constraints

### Error Handling & Feedback

- **FR52:** System displays clear error messages when queries fail
- **FR53:** System indicates when no data matches the selected criteria
- **FR54:** System warns users about known PATSTAT data quality limitations where relevant
- **FR55:** System provides suggestions when zero results are returned

---

## Non-Functional Requirements

### Performance

- **NFR1:** Initial cell execution (setup) completes within 30 seconds
- **NFR2:** Standard queries (single country, single sector, 10-year range) complete within 60 seconds
- **NFR3:** UI remains responsive during query execution (progress indicator shown)
- **NFR4:** Visualizations render within 5 seconds of data retrieval

### Reliability

- **NFR5:** System handles PATSTAT connection failures gracefully
- **NFR6:** System recovers from interrupted queries without crashing the notebook
- **NFR7:** Export functionality works consistently across supported data sizes

### Compatibility

- **NFR8:** Solution runs on TIP's Jupyter environment without modification
- **NFR9:** Solution is compatible with available Jupyter extensions (jupyter-widgets, etc.)
- **NFR10:** Visualizations render correctly in JupyterLab output cells
- **NFR11:** Exported CSVs are compatible with Excel (proper encoding, delimiters)

### Maintainability

- **NFR12:** Code is organized into logical modules/cells with clear comments
- **NFR13:** Configuration (e.g., default values, colors) is centralized
- **NFR14:** WIPO concordance file can be updated without code changes
- **NFR15:** New technology sectors or countries can be added via data files

### Security

- **NFR16:** Solution uses existing TIP authentication (no new credentials required)
- **NFR17:** No sensitive data is logged or exposed in error messages
- **NFR18:** Solution does not store user data beyond session

---

## Technical Constraints

### TIP Environment

- Python version determined by TIP (likely 3.10+)
- Libraries must be pip-installable or pre-installed
- No external network access beyond what TIP provides
- Jupyter cell output rendering limitations (no iframe, limited interactivity)

### PATSTAT Data

- Data quality varies (applicant name variations, address inconsistencies)
- Regional attribution depends on NUTS mapping quality
- Classification coverage may be incomplete for older patents
- Query performance depends on filter selectivity

### Known Limitations to Document

- Applicant name normalization is imperfect (same company may appear multiple times)
- Some countries have limited regional data
- Very broad queries (all countries, all sectors) may timeout

---

## Data Dependencies

### Required Data Sources

| Source | Location | Purpose |
|--------|----------|---------|
| PATSTAT | TIP Platform | Patent applications, applicants, classifications |
| **tls901_techn_field_ipc** | PATSTAT | Built-in sector-to-IPC concordance (35 fields) |
| **tls230_appln_techn_field** | PATSTAT | Pre-computed technology field assignments per application (with weights) |
| Country/Region Reference | TBD (derive from PATSTAT or provide) | Country and NUTS region lists |

### Key PATSTAT Tables

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| tls201_appln | Patent applications | appln_id, appln_auth, appln_filing_year |
| tls206_person | Applicants/Inventors | person_id, person_name, person_ctry_code |
| tls207_pers_appln | Person-Application link | appln_id, person_id, applt_seq_nr |
| tls230_appln_techn_field | Tech field assignments | appln_id, techn_field_nr, weight |
| tls901_techn_field_ipc | Tech field concordance | techn_field_nr, techn_sector, techn_field, ipc_maingroup_symbol |

### Reference Files (Provided)

- `input/ipc_technology.xlsx` - WIPO concordance (backup reference, 35 technology fields)
- `input/patstat_global_schema.json` - PATSTAT table structure reference
- `input/claude_patstat_architecture.md` - ORM usage patterns
- `input/example_medtech_ep_fulldataset.py` - Working query example

---

## Implementation Planning

### Epic Breakdown Required

Requirements must be decomposed into epics and bite-sized stories (200k context limit per dev session).

**Suggested Epic Structure:**

1. **Epic 1: Environment Setup & Initialization** (FR1-4, NFR1, NFR8-9)
2. **Epic 2: Selection UI Components** (FR5-21, FR47-51)
3. **Epic 3: PATSTAT Query Engine** (FR22-27, NFR2-3, NFR5-6)
4. **Epic 4: Visualizations** (FR28-41, NFR4, NFR10)
5. **Epic 5: Export & Polish** (FR42-46, FR52-55, NFR7, NFR11-15)

**Next Step:** Run `workflow create-epics-and-stories` to decompose into implementable stories.

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| PATSTAT data quality issues | High | Medium | Document limitations, implement quality indicators |
| TIP environment constraints | Medium | Medium | Early testing, adaptive design |
| Query performance on broad filters | Medium | Medium | Add warnings for expensive queries, implement limits |
| Timeline pressure (4 weeks) | High | High | Ruthless prioritization, defer nice-to-haves |
| Scope creep from EPO | Medium | High | Clear MVP definition, change control process |

---

## Timeline

| Milestone | Date | Deliverable |
|-----------|------|-------------|
| PRD Complete | 2026-01-10 | This document |
| Architecture | 2026-01-11 | Technical design decisions |
| Sprint Planning | 2026-01-12 | Stories ready for development |
| Working Prototype | Mid-February 2026 | Core features functional |
| Rainer Review | Feb-March 2026 | Feedback incorporation |
| Production Ready | April 2026 | Polish and testing complete |
| PATLIB Conference | May 2026 | Live demo |

---

## References

- **Product Brief:** `docs/product-brief-tip-for-patlibs-2026-01-10.md`
- **Customer Briefing:** `input/PRD_TIP4PATLIBS_Technical_Document.pdf`
- **WIPO Concordance:** `input/ipc_technology.xlsx`
- **PATSTAT Schema:** `input/patstat_global_schema.json`
- **Example Queries:** `input/example_medtech_ep_fulldataset.py`

---

## Next Steps

1. **Epic & Story Breakdown** - Run: `workflow create-epics-and-stories`
2. **Architecture** - Run: `workflow create-architecture`
3. **Sprint Planning** - Run: `workflow sprint-planning`

---

_This PRD captures the complete requirements for TIP for PATLIBs - a solution that makes patent analysis accessible to everyone in the PATLIB network._

_Created through collaborative discovery between BMad and AI facilitator._

---

# PHASE 2 EXTENSION (Added 2026-01-21)

## Phase 2 Overview

Based on stakeholder analysis and review of existing validated queries in `context/QueryLib_for_PATLIBs.ipynb`, Phase 2 introduces two major features that evolve TIP for PATLIBs from "demonstration notebooks" to "production-ready tools."

| Feature | Phase | Primary Users | Status |
|---------|-------|---------------|--------|
| Query Library | Phase 2 MVP | PATLIBs, Patent Attorneys, IP Managers | Planning |
| MCP Server | Future/Marketing | Developers, Query Library Managers | Deferred |

**Critical Constraint:** Phase 2 features are **additive** - they do not modify or delay Round 1 deliverables.

---

## Feature: Query Library (Phase 2 MVP)

### Vision

A curated library of validated PATSTAT queries with parameter-based UI, enabling end users to execute sophisticated patent analyses without writing SQL.

### Problem Statement

The existing 11+ validated queries in `QueryLib_for_PATLIBs.ipynb` demonstrate powerful analyses, but:

1. Users must understand and modify SQL to change parameters
2. No systematic parameter validation or guidance
3. Queries are embedded in notebook cells, not reusable
4. No documentation of what parameters are configurable

### Target Users

| User Type | Role | Primary Value |
|-----------|------|---------------|
| PATLIB Staff | Primary | Quick access to validated analyses for customer work |
| Patent Attorneys | Secondary | Competitive landscape analysis for clients |
| IP Managers (SME) | Secondary | Portfolio benchmarking, technology scouting |

---

## Query Library - Functional Requirements

### Query Selection & Management

- **FR-QL1:** System provides a dropdown listing all available validated queries by business question title
- **FR-QL2:** System displays query description and expected output format before execution
- **FR-QL3:** System shows which parameters are configurable for each query
- **FR-QL4:** System maintains a query metadata schema with: id, title, description, category, parameters[], sql_template, validation_status
- **FR-QL5:** Queries are categorized by type: Country Analysis, Technology Analysis, Applicant Analysis, Regional Analysis, Competitive Intelligence

### Parameter Configuration

- **FR-QL6:** System dynamically generates parameter input form based on selected query's metadata
- **FR-QL7:** System supports the following parameter types:
  - `year_range`: Start year / End year with validation
  - `single_select`: Dropdown with predefined options (countries, offices, sectors)
  - `multi_select`: Multiple selection (countries[], competitor_names[])
  - `text_input`: Free text (applicant name filter)
  - `numeric`: Integer with min/max bounds (min_patents, top_n)
  - `ipc_class`: IPC classification input with format validation
- **FR-QL8:** System provides sensible default values for all parameters
- **FR-QL9:** System validates parameter inputs before query execution
- **FR-QL10:** System shows parameter descriptions/help text on hover or info icon

### Query Execution

- **FR-QL11:** System constructs parameterized BigQuery SQL from template and user inputs
- **FR-QL12:** System executes query via PatstatClient: `patstat.sql_query(query, use_legacy_sql=False)`
- **FR-QL13:** System displays execution progress with timing information
- **FR-QL14:** System handles query errors with user-friendly messages
- **FR-QL15:** System displays results as formatted DataFrame in notebook output

### Results Display & Export

- **FR-QL16:** System displays query execution time and row count
- **FR-QL17:** System provides DataFrame display with sorting and filtering capabilities
- **FR-QL18:** Users can export results to CSV with descriptive filename
- **FR-QL19:** Users can export results to Excel with multiple sheets (data + metadata)
- **FR-QL20:** System stores last query results for comparison

---

## Query Library - Validated Query Inventory

Based on analysis of `context/QueryLib_for_PATLIBs.ipynb`:

### Category: Country & Regional Analysis

| ID | Business Question | Parameters | Status |
|----|-------------------|------------|--------|
| Q01 | Country Patent Activity & Grant Rates | year_from, min_patents | Validated |
| Q05 | Green Tech Evolution by Country | year_from, year_to, countries[] | Validated |
| Q06 | German Federal States by IPC Class | year_from, year_to, ipc_class | Validated |
| Q10 | Patents per Million Inhabitants (DE) | year_from, ipc_class | Validated |
| Q13 | Regional Tech Sector Comparison | regions[], year_from | Review needed |

### Category: Technology Analysis

| ID | Business Question | Parameters | Status |
|----|-------------------|------------|--------|
| Q02 | Technology Fields by Citations | year_from, year_to, weight_threshold | Validated |
| Q09 | AI-based ERP Patent Landscape | year_from | Validated |
| Q11 | Fastest-growing Technology Subclasses | base_year, comparison_year, cpc_prefix | Validated |
| Q12 | AI-assisted Diagnostics Companies | (none) | Review needed |

### Category: Applicant Analysis

| ID | Business Question | Parameters | Status |
|----|-------------------|------------|--------|
| Q03 | Top Patent Applicants | year_from, min_applications | Validated |
| Q04 | Citation Network Analysis | citing_year | Validated |
| Q07 | Competitor Geographic Filing Strategy | competitor_names[], tech_sector | Validated |

### Category: Office Comparison

| ID | Business Question | Parameters | Status |
|----|-------------------|------------|--------|
| Q08 | Grant Rates by Patent Office | year_from, year_to, ipc_class, offices[] | Validated |

---

## Query Library - Non-Functional Requirements

### Performance

- **NFR-QL1:** Query selection and parameter form generation completes within 1 second
- **NFR-QL2:** Parameter validation completes within 500ms
- **NFR-QL3:** Query execution timeout matches underlying PATSTAT limits (configurable, default 120s)

### Usability

- **NFR-QL4:** Parameter form is intuitive for non-technical users
- **NFR-QL5:** Error messages provide actionable guidance
- **NFR-QL6:** UI is consistent with Round 1 visualization style

### Extensibility

- **NFR-QL7:** New queries can be added via metadata file without code changes
- **NFR-QL8:** Query templates support BigQuery syntax only
- **NFR-QL9:** Parameter types are extensible via configuration

---

## Query Library - Technical Specification

### Query Metadata Schema

```yaml
query:
  id: "Q01"
  title: "Country Patent Activity & Grant Rates"
  description: "Identifies leading innovation hubs and their success rates"
  category: "country_analysis"
  validation_status: "validated"  # validated | review_needed | draft

  parameters:
    - name: "year_from"
      type: "year"
      label: "Start Year"
      default: 2015
      min: 1990
      max: 2025
      required: true

    - name: "min_patents"
      type: "numeric"
      label: "Minimum Patents"
      default: 100
      min: 1
      max: 10000
      required: false
      help: "Filter countries with fewer patents than this threshold"

  sql_template: |
    SELECT p.person_ctry_code,
           COUNT(DISTINCT a.appln_id) AS patent_count,
           COUNT(DISTINCT CASE WHEN a.granted = 'Y' THEN a.appln_id END) AS granted_count,
           ROUND(COUNT(DISTINCT CASE WHEN a.granted = 'Y' THEN a.appln_id END) * 100.0 /
                 COUNT(DISTINCT a.appln_id), 2) AS grant_rate
    FROM tls207_pers_appln pa
    JOIN tls206_person p ON pa.person_id = p.person_id
    JOIN tls201_appln a ON pa.appln_id = a.appln_id
    WHERE pa.applt_seq_nr > 0
      AND a.appln_filing_year >= {{year_from}}
      AND p.person_ctry_code IS NOT NULL
    GROUP BY p.person_ctry_code
    HAVING COUNT(DISTINCT a.appln_id) >= {{min_patents}}
    ORDER BY patent_count DESC
    LIMIT 20

  output:
    columns: ["person_ctry_code", "patent_count", "granted_count", "grant_rate"]
    expected_rows: "20"
```

### File Structure

```
context/
├── QueryLib_for_PATLIBs.ipynb     # Original notebook with SQL
├── query_library/
│   ├── queries.yaml               # Query metadata registry
│   ├── templates/                 # SQL template files
│   │   ├── Q01_country_activity.sql
│   │   ├── Q02_tech_fields.sql
│   │   └── ...
│   └── parameters/                # Parameter definitions
│       ├── countries.yaml         # Country dropdown options
│       ├── tech_sectors.yaml      # Technology sector options
│       └── offices.yaml           # Patent office options
```

### Integration with Round 1

- Query Library UI uses same ipywidgets approach as Round 1
- Visualization components from Round 1 can be applied to Query Library results
- Export functionality reuses Round 1 implementation

---

## Feature: MCP Server (Future/Marketing)

### Vision

An AI-powered query generation service that converts natural language business questions into validated PATSTAT BigQuery queries, enabling rapid expansion of the Query Library.

### Strategic Purpose

1. **Internal:** Enable Query Library managers to rapidly add new queries
2. **External:** Demonstrate AI capability as marketing differentiator
3. **Future:** Standalone service offering outside TIP environment

### Phase

**Deferred** - To be developed after Query Library MVP is stable. Not in current scope.

### MCP Context Package (Preparation Tasks)

| Asset | Current Status | Required Action |
|-------|----------------|-----------------|
| `patstat-2026-01-19-context.json` | Exists (28 tables) | Remove `public.` prefix for BigQuery |
| `patstat_global_schema.json` | Exists (54k tokens) | Create summarized version for LLM context |
| `patstat_table_relations.md` | Does not exist | Document FK relationships and common JOINs |
| `query_examples.json` | Does not exist | Extract validated queries as few-shot examples |
| `bigquery_syntax_notes.md` | Does not exist | Document BigQuery-specific syntax |

### Dream Workflow (Future State)

```
1. IP Manager submits business question
       ↓
2. MCP generates query + description
       ↓
3. Developer tests query in TIP environment
       ↓
4. Validated query added to Query Library
       ↓
5. End users can immediately use new query
```

---

## Phase 2 - Epic Structure

### Epic 6: Query Library Core

**Goal:** Extract and parameterize existing queries, build core library infrastructure

**Stories:**

| ID | Story | Acceptance Criteria |
|----|-------|-------------------|
| 6.1 | Create query metadata schema | YAML schema defined, validated against 3 sample queries |
| 6.2 | Extract Q01-Q05 as parameterized templates | 5 queries converted, SQL templates work with parameter substitution |
| 6.3 | Build parameter input form generator | Dynamic form renders for each parameter type |
| 6.4 | Implement query execution wrapper | Queries execute via PatstatClient, errors handled gracefully |
| 6.5 | Build query selection dropdown | All queries listed, description shown on selection |

### Epic 7: Query Library Polish

**Goal:** Complete query inventory, add export and documentation

**Stories:**

| ID | Story | Acceptance Criteria |
|----|-------|-------------------|
| 7.1 | Extract Q06-Q11 as parameterized templates | 6 additional queries converted and validated |
| 7.2 | Review and fix Q12-Q13 | Empty result issues resolved or documented |
| 7.3 | Implement results export (CSV/Excel) | Export works with descriptive filenames |
| 7.4 | Add parameter help and validation messages | All parameters have help text, validation is clear |
| 7.5 | Create Query Library documentation | User guide with query descriptions and parameter explanations |

### Epic 8: MCP Preparation (Future)

**Goal:** Prepare context package for MCP development

**Stories (Deferred):**

| ID | Story | Notes |
|----|-------|-------|
| 8.1 | Clean context JSON for BigQuery | Remove `public.` prefix |
| 8.2 | Create schema summary for LLM context | Compress 54k tokens to ~10k |
| 8.3 | Document table relationships | FK diagram and common JOIN patterns |
| 8.4 | Extract validated queries as examples | JSON format for few-shot prompting |
| 8.5 | MCP server implementation | Full implementation, deferred |

---

## Phase 2 - Timeline

| Milestone | Target Date | Deliverable |
|-----------|-------------|-------------|
| Round 1 Complete | May 2026 | Conference demo successful |
| Phase 2 Planning | May 2026 | Epic 6-7 stories refined |
| Epic 6 Complete | June 2026 | Query Library core functional |
| Epic 7 Complete | July 2026 | Query Library polished, documented |
| MCP Planning | TBD | Epic 8 scoped based on demand |

---

## Phase 2 - Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Phase 2 delays Round 1 | Low | High | Strict phase separation, no shared code dependencies |
| Query parameterization harder than expected | Medium | Medium | Start with 5 simplest queries, iterate |
| Existing queries have edge case bugs | Medium | Low | Test with various parameter combinations |
| MCP scope creep | Medium | Medium | Keep MCP strictly deferred until Query Library stable |

---

## Phase 2 - Technical Decisions

### Database

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| Target Database | BigQuery exclusively | TIP environment uses BigQuery, not Postgres |
| Schema References | No `public.` prefix | BigQuery uses unqualified table names |
| Client | PatstatClient | `epo.tipdata.patstat` library is standard |

### Existing Assets

| Asset | Location | Usage |
|-------|----------|-------|
| Validated Queries | `context/QueryLib_for_PATLIBs.ipynb` | Source for Q01-Q13 |
| Business Schema | `context/patstat-2026-01-19-context.json` | 28 tables with descriptions |
| Technical Schema | `context/patstat_global_schema.json` | Full schema reference |
| Sample Queries | `context/patstat-2026-01-19-sample.json` | 5 example queries |

---

## References (Phase 2)

- **Extended Product Brief:** `docs/product-brief-tip-for-patlibs-2026-01-10.md` (Phase 2 section)
- **Validated Queries:** `context/QueryLib_for_PATLIBs.ipynb`
- **Schema Context:** `context/patstat-2026-01-19-context.json`

---

_Phase 2 Extension added: 2026-01-21_
_Context: Party Mode discussion with full BMAD agent team (PM, Analyst, Architect, Dev, SM, TEA, UX, Tech Writer)_
_Status: Ready for Epic 6-7 story creation after Round 1 completion_
