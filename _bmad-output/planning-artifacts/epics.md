---
stepsCompleted: [1, 2]
status: in-progress
resumeAt: step-03-create-stories
inputDocuments:
  - _bmad-output/planning-artifacts/prd.md
  - _bmad-output/planning-artifacts/architecture.md
  - context/query-design-patterns.md
  - context/what-worked-well.md
  - context/patstat_bigquery_queries_v2.sql
  - TIP_for_PATLIBs_QueryLib_for_PATLIBs.ipynb
  - TIP_for_PATLIBs_InteractiveQueryDemo.ipynb
  - context/DTF_OPS_University_Analysis.ipynb
---

# TIP for PATLIBs Phase 2 - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for TIP for PATLIBs Phase 2, decomposing the requirements from the PRD and Architecture into implementable stories.

**Project Context:** Brownfield - extending existing notebooks and migrating queries from Streamlit app.

## Requirements Inventory

### Functional Requirements

**Query Library Notebook (FR1-FR12):**
- FR1: Users can browse all 42 available queries via a categorized selector
- FR2: Users can search/filter queries by keyword, category, or stakeholder tag
- FR3: Users can view query description and expected output before execution
- FR4: Users can configure query parameters via UI controls (dropdowns, sliders, text inputs)
- FR5: Users can execute a selected query with configured parameters
- FR6: Users can view query results as a formatted DataFrame
- FR7: Users can export query results to CSV
- FR8: Users can export visualizations to PNG
- FR9: Users can view the underlying SQL for any query
- FR10: Users can copy and modify query cells for customization
- FR11: System provides progress indicator during query execution
- FR12: System displays user-friendly error messages when queries fail

**Interactive Demo Notebook (FR13-FR17):**
- FR13: Users can follow a guided walkthrough of TIP capabilities
- FR14: Users can execute demo queries step-by-step with explanations
- FR15: Users can see example outputs and visualizations inline
- FR16: Trainers can use the notebook as a presentation tool
- FR17: Users can complete the demo independently without trainer assistance

**AI Query Builder Notebook (FR18-FR24):**
- FR18: Users can describe a business question in natural language
- FR19: System generates valid PATSTAT/BigQuery SQL from natural language input
- FR20: System displays generated SQL with explanation of query logic
- FR21: Users can execute the generated query directly
- FR22: Users can modify the generated SQL before execution
- FR23: System validates generated SQL before execution
- FR24: Users can save successful AI-generated queries for reuse

**University Analysis Notebook (FR25-FR32):**
- FR25: Users can select a university from a list of European universities
- FR26: Users can compare multiple universities side-by-side
- FR27: Users can view university patent application trends over time
- FR28: Users can view top inventors at a selected university
- FR29: Users can view industry collaboration patterns for a university
- FR30: Users can view technology field distribution for a university
- FR31: Users can export university analysis results to CSV
- FR32: System provides university metadata (student count, location, type)

**Common Notebook Features (FR33-FR38):**
- FR33: All notebooks initialize with a single "Run this cell first" setup cell
- FR34: All notebooks display clear status messages during operations
- FR35: All notebooks handle errors gracefully with actionable messages
- FR36: All notebooks use consistent UI patterns (ipywidgets)
- FR37: All notebooks include inline documentation explaining each section
- FR38: All notebooks can be reset to initial state

**Data Access & Integration (FR39-FR42):**
- FR39: System connects to PATSTAT via PatstatClient
- FR40: System executes queries against BigQuery backend
- FR41: System handles query timeouts gracefully
- FR42: System respects TIP environment constraints

**Educational Materials (FR43-FR46):**
- FR43: Users can access a handbook covering all 4 notebooks
- FR44: Users can access quick reference guides (one per notebook)
- FR45: Trainers can access presentation materials for workshops
- FR46: Users can access step-by-step tutorials with screenshots

### Non-Functional Requirements

**Performance (NFR1-NFR5):**
- NFR1: Standard queries complete within 120 seconds
- NFR2: UI controls respond to user input within 1 second
- NFR3: Notebook initialization (setup cell) completes within 30 seconds
- NFR4: Export operations (CSV, PNG) complete within 10 seconds
- NFR5: Progress indicators update at least every 5 seconds during long operations

**Reliability (NFR6-NFR9):**
- NFR6: Notebooks recover gracefully from interrupted queries
- NFR7: Error messages are user-friendly and suggest next actions
- NFR8: Notebooks can be re-run from any cell without side effects
- NFR9: System handles PATSTAT connection failures without crashing

**Integration (NFR10-NFR13):**
- NFR10: All notebooks run in TIP's JupyterLab environment without modification
- NFR11: PatstatClient is the only data access method (no direct BigQuery)
- NFR12: Notebooks are compatible with TIP's pre-installed package versions
- NFR13: No external network calls required (except PATSTAT via PatstatClient)

**Maintainability (NFR14-NFR17):**
- NFR14: Code is organized into logical cells with clear markdown documentation
- NFR15: Query SQL is readable and commented
- NFR16: Configuration values (defaults, colors) are centralized
- NFR17: New queries can be added without restructuring the notebook

**Usability (NFR18-NFR20):**
- NFR18: Non-technical users can execute queries without reading code
- NFR19: UI labels and messages use plain language (no jargon)
- NFR20: Notebooks are usable without trainer assistance after initial training

### Additional Requirements

**From Architecture:**
- ADR-013: Claude API integration via anthropic package with .env for API key
- ADR-014: University reference data as static CSV file bundled with notebook
- ADR-015: Per-notebook module organization (each notebook has own *_core.py)
- Dependency check pattern: pip install if needed in initialization cell
- Error handling pattern: User-friendly HTML messages, technical details in print()
- Progress indicator pattern: ipywidgets HTML with emoji status

**Existing Assets to Extend (not recreate):**
- `TIP_for_PATLIBs_QueryLib_for_PATLIBs.ipynb` - Query Library base
- `TIP_for_PATLIBs_InteractiveQueryDemo.ipynb` - Interactive Demo base
- `context/DTF_OPS_University_Analysis.ipynb` - University Analysis (refactor to PatstatClient)
- `context/patstat_bigquery_queries_v2.sql` - 42 queries to migrate
- `context/query-design-patterns.md` - Query patterns to follow
- `context/what-worked-well.md` - Lessons learned to apply

### FR Coverage Map

| FR | Epic | Description |
|----|------|-------------|
| FR1-FR12 | Epic 1 | Query Library core features |
| FR13-FR17 | Epic 2 | Interactive Demo features |
| FR18-FR24 | Epic 3 | AI Query Builder features |
| FR25-FR32 | Epic 4 | University Analysis features |
| FR33-FR38 | Epic 1 | Common patterns (established in Epic 1, applied to all) |
| FR39-FR42 | Epic 1 | Data access patterns (established in Epic 1, applied to all) |
| FR43-FR46 | Epic 5 | Educational materials |

## Epic List

### Epic 1: Query Library
> PATLIB staff can browse 42 categorized queries, configure parameters via UI controls, execute queries, view results, and export to CSV/PNG - all without writing code.

**FRs covered:** FR1-FR12 (core), FR33-FR42 (common + data access patterns established here)

**Note:** This epic establishes all the patterns (initialization, error handling, progress, export) that other notebooks will follow.

**Existing asset:** Extend `TIP_for_PATLIBs_QueryLib_for_PATLIBs.ipynb`, migrate queries from `patstat_bigquery_queries_v2.sql`

---

### Epic 2: Interactive Demo
> EPO Academy trainers can deliver 4-hour TIP workshops using a guided notebook. Participants execute queries step-by-step and leave confident to use TIP independently.

**FRs covered:** FR13-FR17

**Note:** Reuses patterns from Epic 1. Minimal module code - mostly markdown cells with guided execution.

**Existing asset:** Extend `TIP_for_PATLIBs_InteractiveQueryDemo.ipynb`

---

### Epic 3: AI Query Builder
> Users describe a business question in plain English and receive valid PATSTAT SQL with explanation. They can execute, modify, and save successful queries.

**FRs covered:** FR18-FR24

**Note:** New notebook. Requires Claude API integration (ADR-013).

**Existing asset:** Port from Streamlit app pattern

---

### Epic 4: University Analysis
> University PATLIB staff select their institution, view patent trends, identify top inventors, discover industry collaborations, and compare with peer universities.

**FRs covered:** FR25-FR32

**Note:** Refactor existing notebook to use PatstatClient. University CSV data (ADR-014).

**Existing asset:** Refactor `context/DTF_OPS_University_Analysis.ipynb`

---

### Epic 5: Educational Materials
> Users access a handbook covering all 4 notebooks, quick reference guides for each notebook, and trainers have presentation materials for workshops.

**FRs covered:** FR43-FR46

**Note:** Documentation deliverable, written after notebooks are stable. Can be done in parallel with Epic 3/4.

---

## Stories

<!-- Stories will be created in Step 3 -->

