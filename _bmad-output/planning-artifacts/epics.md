---
stepsCompleted: [1, 2, 3, 4]
status: complete
completedAt: 2026-02-01
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

### Epic 1: Query Library

#### Story 1.1: Initialize QueryLib Core Module

**As a** PATLIB staff member,
**I want** the Query Library notebook to initialize with a single setup cell,
**So that** I can start using queries without technical configuration steps.

**Acceptance Criteria:**

**Given** I open the Query Library notebook for the first time
**When** I run the "Initialize" cell
**Then** the PatstatClient connection is established
**And** a success message displays with emoji status (✅)
**And** any missing dependencies are installed automatically
**And** the `querylib_core.py` module is loaded with shared functions

**Given** the PatstatClient connection fails
**When** the initialization cell completes
**Then** a user-friendly error message displays with suggested actions
**And** technical details are printed below for troubleshooting

**Given** I have already run the initialization cell
**When** I run it again
**Then** the notebook reinitializes cleanly without errors
**And** no duplicate widgets or state issues occur

**Technical Notes:**
- Creates `querylib_core.py` with: error display helper, progress indicator, export functions
- Follows ADR-015 (per-notebook module organization)
- Establishes patterns for FR33, FR34, FR35, FR39, FR40

---

#### Story 1.2: Query Registry and Categorization

**As a** PATLIB staff member,
**I want** all 42 queries organized into logical categories,
**So that** I can quickly find queries relevant to my analysis task.

**Acceptance Criteria:**

**Given** the notebook is initialized
**When** the query registry loads
**Then** all 42 queries from `patstat_bigquery_queries_v2.sql` are available
**And** each query has: id, title, description, category, SQL template, parameters metadata

**Given** the queries are loaded
**When** I view the category structure
**Then** queries are grouped into meaningful categories (e.g., "Trends", "Top Applicants", "Regional", "Technology Fields", "Comparisons")
**And** each category contains at least 2 queries

**Given** any query in the registry
**When** I inspect its metadata
**Then** I can see the expected output columns
**And** I can see which parameters are required vs optional
**And** I can see stakeholder tags (e.g., "university", "SME", "regional")

**Technical Notes:**
- Query registry as Python dict/dataclass structure in `querylib_core.py`
- Migrate SQL from `patstat_bigquery_queries_v2.sql` with parameterization
- Follow patterns from `context/query-design-patterns.md`
- Covers FR1, FR2 (partial), FR3 (partial)

---

#### Story 1.3: Query Browser Widget

**As a** PATLIB staff member,
**I want** to browse and search queries through a visual interface,
**So that** I can find the right query without reading code or documentation.

**Acceptance Criteria:**

**Given** the notebook is initialized
**When** I run the Query Browser cell
**Then** a categorized dropdown displays all query categories
**And** selecting a category shows queries in that category

**Given** the Query Browser is displayed
**When** I type a keyword in the search box
**Then** queries are filtered by title, description, and tags
**And** results update as I type (debounced)

**Given** I select a query from the browser
**When** the selection is made
**Then** the query description displays below
**And** expected output columns are shown
**And** the "View SQL" button becomes active

**Given** I click "View SQL"
**When** the SQL panel opens
**Then** the full SQL template displays in a readable format
**And** parameter placeholders are highlighted

**Technical Notes:**
- Uses ipywidgets: Dropdown, Text, HTML, Button
- Covers FR1, FR2, FR3, FR9
- Follows FR36 (consistent UI patterns)

---

#### Story 1.4: Parameter Configuration UI

**As a** PATLIB staff member,
**I want** to configure query parameters using intuitive controls,
**So that** I can customize queries without editing SQL.

**Acceptance Criteria:**

**Given** I have selected a query in the browser
**When** the parameter panel loads
**Then** each parameter displays with an appropriate widget:
- Country selection → Dropdown with country names
- Date range → Two date pickers (start/end)
- Top N → Slider with sensible range
- IPC/CPC codes → Text input with validation hint
- Technology field → Dropdown from WIPO 35 fields

**Given** a parameter has a default value
**When** the parameter widget loads
**Then** the default is pre-selected
**And** the default source is indicated (e.g., "Default: last 5 years")

**Given** a required parameter is empty
**When** I attempt to execute the query
**Then** the missing parameter is highlighted
**And** execution is blocked with a clear message

**Given** I enter an invalid parameter value
**When** validation runs
**Then** a helpful error message explains the expected format
**And** an example valid value is shown

**Technical Notes:**
- Dynamic widget generation based on query parameter metadata
- Covers FR4
- Validation patterns from `context/what-worked-well.md`

---

#### Story 1.5: Query Execution with Progress

**As a** PATLIB staff member,
**I want** to see progress while queries run,
**So that** I know the system is working and can estimate wait time.

**Acceptance Criteria:**

**Given** I have configured all required parameters
**When** I click "Execute Query"
**Then** the Execute button disables to prevent double-submission
**And** a progress indicator appears with spinner emoji (⏳)

**Given** a query is executing
**When** more than 5 seconds have passed
**Then** the progress indicator updates with elapsed time
**And** updates continue every 5 seconds (NFR5)

**Given** a query completes successfully
**When** results are ready
**Then** the progress indicator shows success (✅)
**And** the results panel activates
**And** execution time is displayed

**Given** a query exceeds 120 seconds (NFR1)
**When** timeout is reached
**Then** the query is cancelled gracefully
**And** a user-friendly timeout message displays
**And** suggestions for reducing scope are provided

**Given** a query fails with an error
**When** the error is caught
**Then** a user-friendly error message displays (FR12)
**And** technical details print below for debugging
**And** the Execute button re-enables

**Technical Notes:**
- Uses PatstatClient for execution (FR39, FR40)
- Progress indicator pattern from Architecture (ipywidgets HTML)
- Covers FR5, FR11, FR12, FR41
- Handles NFR6 (graceful recovery)

---

#### Story 1.6: Results Display and Export

**As a** PATLIB staff member,
**I want** to view results clearly and export them,
**So that** I can use the data in reports and presentations.

**Acceptance Criteria:**

**Given** a query has completed successfully
**When** results are displayed
**Then** data shows as a formatted pandas DataFrame
**And** columns have readable headers
**And** large numbers are formatted with thousand separators
**And** the row count is displayed

**Given** results are displayed
**When** I click "Export CSV"
**Then** a CSV file downloads with a descriptive filename
**And** filename includes query name and timestamp
**And** export completes within 10 seconds (NFR4)

**Given** a visualization is displayed
**When** I click "Export PNG"
**Then** a PNG file downloads with the chart
**And** resolution is suitable for presentations (300 DPI)
**And** export completes within 10 seconds (NFR4)

**Given** a query returns zero results
**When** the results panel loads
**Then** a helpful message explains possible reasons
**And** suggestions for broadening the search are provided

**Given** I want to customize the analysis
**When** I use "Copy cell for editing"
**Then** a new cell is created below with the query code
**And** the SQL is exposed for modification (FR10)

**Technical Notes:**
- Export functions in `querylib_core.py` for reuse
- Covers FR6, FR7, FR8, FR10
- Zero-results handling for data quality (future Epic 5 cross-reference)

---

### Epic 2: Interactive Demo

#### Story 2.1: Demo Notebook Structure and Navigation

**As a** workshop participant,
**I want** a clearly structured demo notebook with logical sections,
**So that** I can follow along during training and return to specific topics later.

**Acceptance Criteria:**

**Given** I open the Interactive Demo notebook
**When** I view the table of contents
**Then** I see numbered sections covering TIP capabilities
**And** sections are ordered from basic to advanced
**And** estimated time per section is indicated

**Given** I am in any section of the notebook
**When** I look at the markdown headers
**Then** I can identify where I am in the overall flow
**And** navigation hints point to next/previous sections

**Given** the demo notebook is opened
**When** I run the initialization cell
**Then** it reuses the initialization pattern from Epic 1
**And** a welcome message explains the demo purpose
**And** instructions for self-paced vs trainer-led modes appear

**Technical Notes:**
- Imports shared functions from `querylib_core.py`
- Covers FR13, FR17 (partial)
- Clear markdown structure for presentation use (FR16)

---

#### Story 2.2: Guided Query Execution Cells

**As a** workshop participant,
**I want** to execute pre-configured demo queries with explanations,
**So that** I learn how TIP works through hands-on practice.

**Acceptance Criteria:**

**Given** I reach a demo query section
**When** I read the markdown cell above the code
**Then** I understand what this query demonstrates
**And** the business question being answered is stated
**And** expected output is described

**Given** I run a demo query cell
**When** execution completes
**Then** results display inline below the cell
**And** a markdown cell below explains how to interpret results
**And** key insights are highlighted

**Given** a demo query has parameters
**When** I view the code cell
**Then** parameters are clearly commented
**And** suggestions for modifications are provided
**And** I can change values and re-run to explore

**Given** I am following trainer-led mode
**When** the trainer advances to next query
**Then** each query builds on concepts from previous ones
**And** complexity increases gradually

**Technical Notes:**
- 5-7 carefully selected demo queries covering different categories
- Covers FR14, FR15
- Queries selected from Epic 1 registry

---

#### Story 2.3: Inline Visualizations with Explanations

**As a** workshop participant,
**I want** to see charts and visualizations with clear explanations,
**So that** I understand how to present patent data visually.

**Acceptance Criteria:**

**Given** a demo query produces trend data
**When** results are displayed
**Then** a line chart renders inline
**And** axes are labeled clearly
**And** a markdown cell explains what the trend shows

**Given** a demo query produces ranking data
**When** results are displayed
**Then** a bar chart renders inline
**And** top items are highlighted
**And** interpretation guidance is provided

**Given** a demo query produces geographic data
**When** results are displayed
**Then** an appropriate visualization renders (bar chart by country)
**And** comparison insights are explained

**Given** any visualization is displayed
**When** I want to save it
**Then** export instructions reference the PNG export from Epic 1
**And** the visualization is presentation-ready

**Technical Notes:**
- Uses matplotlib/plotly consistent with Epic 1
- Covers FR15
- Supports FR16 (presentation tool)

---

#### Story 2.4: Self-Paced Completion Mode

**As a** PATLIB staff member learning independently,
**I want** to complete the demo without a trainer,
**So that** I can learn TIP at my own pace after the workshop.

**Acceptance Criteria:**

**Given** I am working through the demo alone
**When** I reach each section
**Then** all instructions are self-explanatory
**And** no verbal explanation from a trainer is needed
**And** "Try it yourself" prompts encourage exploration

**Given** I complete a section
**When** I check my understanding
**Then** a "What you learned" summary appears
**And** key takeaways are bulleted
**And** links to Query Library for further exploration are provided

**Given** I finish the entire demo
**When** I reach the conclusion section
**Then** a completion summary shows what I covered
**And** next steps for independent use are listed
**And** links to the handbook and quick reference are provided

**Given** I encounter an error during self-paced learning
**When** the error message displays
**Then** troubleshooting steps are included
**And** I can recover without trainer assistance (NFR7)

**Technical Notes:**
- Covers FR17
- Error handling reuses Epic 1 patterns
- Cross-references Epic 5 educational materials

---

### Epic 3: AI Query Builder

#### Story 3.1: AI Query Builder Notebook Setup

**As a** PATLIB staff member,
**I want** to initialize the AI Query Builder with my API key,
**So that** I can use natural language to generate queries.

**Acceptance Criteria:**

**Given** I open the AI Query Builder notebook
**When** I run the initialization cell
**Then** the PatstatClient connection is established (reusing Epic 1 pattern)
**And** the Claude API client initializes using anthropic package
**And** API key is loaded from `.env` file (ADR-013)

**Given** the `.env` file is missing or has no API key
**When** initialization runs
**Then** a clear message explains how to set up the API key
**And** instructions for creating `.env` file are provided
**And** a template `.env.example` location is referenced

**Given** the API key is invalid
**When** a test call is made
**Then** a user-friendly error explains the key is invalid
**And** links to Anthropic console for key management are provided

**Given** initialization succeeds
**When** the status displays
**Then** both PatstatClient (✅) and Claude API (✅) show ready
**And** the natural language input cell is activated

**Technical Notes:**
- Creates `aiquery_core.py` with AI-specific functions
- Follows ADR-013 (Claude API via anthropic package)
- Reuses initialization pattern from Epic 1

---

#### Story 3.2: Natural Language Query Input

**As a** PATLIB staff member,
**I want** to describe my business question in plain English,
**So that** I don't need to know SQL to query patent data.

**Acceptance Criteria:**

**Given** the notebook is initialized
**When** I view the query input section
**Then** a text area widget accepts multi-line input
**And** placeholder text shows example questions
**And** a "Generate SQL" button is visible

**Given** I type a business question
**When** I review example prompts
**Then** helpful examples are shown:
- "Show patent applications in Germany for the last 5 years"
- "Who are the top 10 applicants in medical devices?"
- "Compare renewable energy patents between France and Spain"

**Given** I enter a question and click "Generate SQL"
**When** the request is sent
**Then** a progress indicator shows "Generating query..."
**And** the input is disabled during generation
**And** generation typically completes within 10-15 seconds

**Given** I enter an empty question
**When** I click "Generate SQL"
**Then** validation prevents submission
**And** a message prompts me to enter a question

**Technical Notes:**
- Uses ipywidgets Textarea and Button
- Covers FR18
- Context includes PATSTAT schema hints for Claude

---

#### Story 3.3: SQL Generation and Explanation

**As a** PATLIB staff member,
**I want** to see the generated SQL with a clear explanation,
**So that** I understand what the query does before running it.

**Acceptance Criteria:**

**Given** I submit a business question
**When** Claude generates the SQL
**Then** the SQL query displays in a formatted code block
**And** syntax highlighting makes it readable
**And** an explanation section appears below

**Given** the SQL is generated
**When** I read the explanation
**Then** it describes what the query does in plain English
**And** key tables and joins are explained
**And** any assumptions made are noted

**Given** the question is ambiguous
**When** Claude generates the SQL
**Then** the explanation notes the interpretation chosen
**And** alternative interpretations are suggested
**And** I can refine my question if needed

**Given** the question cannot be answered with PATSTAT
**When** Claude processes it
**Then** a polite message explains the limitation
**And** suggestions for rephrasing are provided
**And** no invalid SQL is generated

**Technical Notes:**
- System prompt includes PATSTAT schema context
- Covers FR19, FR20
- Claude response structured as JSON with sql + explanation fields

---

#### Story 3.4: SQL Validation and Editing

**As a** PATLIB staff member,
**I want** to validate and optionally edit the generated SQL,
**So that** I can fix issues or customize the query before running it.

**Acceptance Criteria:**

**Given** SQL has been generated
**When** the validation step runs
**Then** basic syntax checks are performed
**And** table/column names are verified against PATSTAT schema
**And** validation status displays (✅ Valid or ⚠️ Issues found)

**Given** validation finds issues
**When** issues are displayed
**Then** each issue is listed with location in SQL
**And** suggestions for fixing are provided
**And** I can request Claude to fix the issues

**Given** I want to modify the SQL
**When** I click "Edit SQL"
**Then** the SQL becomes editable in a text area
**And** I can make changes directly
**And** re-validation runs when I finish editing

**Given** I edit the SQL
**When** I click "Validate Changes"
**Then** the modified SQL is re-validated
**And** the explanation updates if structure changed significantly
**And** I can proceed to execution when valid

**Technical Notes:**
- Covers FR22, FR23
- Schema validation against known PATSTAT tables
- Edit mode uses ipywidgets Textarea

---

#### Story 3.5: Query Execution and Results

**As a** PATLIB staff member,
**I want** to execute the generated query and see results,
**So that** I can get answers to my business questions.

**Acceptance Criteria:**

**Given** the SQL is validated
**When** I click "Execute Query"
**Then** the query runs via PatstatClient (reusing Epic 1 pattern)
**And** progress indicator shows execution status
**And** timeout handling applies (120 second limit)

**Given** the query executes successfully
**When** results are returned
**Then** data displays as formatted DataFrame
**And** export options (CSV, PNG) are available
**And** execution time is shown

**Given** the query fails during execution
**When** the error is caught
**Then** a user-friendly message explains the issue
**And** common causes are listed (timeout, invalid syntax, no data)
**And** I can return to editing the SQL

**Given** the query returns zero results
**When** the message displays
**Then** possible reasons are explained
**And** suggestions for broadening the query are provided

**Technical Notes:**
- Reuses execution and display patterns from Epic 1
- Covers FR21
- Error handling follows established patterns

---

#### Story 3.6: Save Successful Queries

**As a** PATLIB staff member,
**I want** to save successful AI-generated queries for reuse,
**So that** I can run them again without regenerating.

**Acceptance Criteria:**

**Given** a query has executed successfully
**When** I click "Save Query"
**Then** a dialog prompts for a query name
**And** the original question is shown as default name
**And** I can edit the name before saving

**Given** I save a query
**When** the save completes
**Then** the query is stored in a local JSON file
**And** metadata includes: name, original question, SQL, timestamp
**And** confirmation message shows save location

**Given** I want to view saved queries
**When** I open the "Saved Queries" section
**Then** a list of previously saved queries displays
**And** each shows name, date saved, original question preview
**And** I can select one to load

**Given** I load a saved query
**When** it loads into the notebook
**Then** the SQL displays in the editor
**And** I can execute it directly
**And** I can modify it before execution

**Technical Notes:**
- Saves to `saved_queries.json` in notebook directory
- Covers FR24
- Simple file-based persistence (no database needed)

---

### Epic 4: University Analysis

#### Story 4.1: University Analysis Notebook Setup

**As a** university PATLIB staff member,
**I want** to initialize the University Analysis notebook with university data,
**So that** I can analyze my institution's patent activity.

**Acceptance Criteria:**

**Given** I open the University Analysis notebook
**When** I run the initialization cell
**Then** the PatstatClient connection is established (reusing Epic 1 pattern)
**And** the university reference CSV loads (ADR-014)
**And** success status shows universities loaded count

**Given** the university CSV loads successfully
**When** I view the data summary
**Then** the count of European universities displays
**And** countries covered are listed
**And** data freshness date is shown

**Given** the university CSV is missing or corrupted
**When** initialization runs
**Then** a clear error explains the issue
**And** instructions for obtaining the reference file are provided

**Technical Notes:**
- Creates `university_core.py` with university-specific functions
- University CSV bundled with notebook (ADR-014)
- Reuses initialization pattern from Epic 1
- Refactors existing notebook to PatstatClient

---

#### Story 4.2: University Selection and Metadata

**As a** university PATLIB staff member,
**I want** to select my university and see its metadata,
**So that** I can confirm I'm analyzing the correct institution.

**Acceptance Criteria:**

**Given** the notebook is initialized
**When** I view the university selector
**Then** a searchable dropdown lists all European universities
**And** I can type to filter by name
**And** universities are grouped by country

**Given** I select a university
**When** the selection is confirmed
**Then** university metadata displays:
- Full institution name
- Country and city
- Type (public/private, technical/general)
- Student count (if available)
- PATSTAT applicant ID(s)

**Given** a university has multiple PATSTAT IDs
**When** metadata displays
**Then** all known IDs are listed
**And** analysis will aggregate across all IDs

**Given** I cannot find my university
**When** I search the list
**Then** a "Request university" note provides contact info
**And** manual ID entry option is available for advanced users

**Technical Notes:**
- Covers FR25, FR32
- University metadata from reference CSV
- Maps university names to PATSTAT person_id(s)

---

#### Story 4.3: Patent Application Trends

**As a** university PATLIB staff member,
**I want** to view my university's patent application trends over time,
**So that** I can understand our innovation trajectory.

**Acceptance Criteria:**

**Given** I have selected a university
**When** I run the "Application Trends" cell
**Then** a query retrieves yearly application counts
**And** progress indicator shows during execution
**And** data covers the last 20 years by default

**Given** trend data is retrieved
**When** results display
**Then** a line chart shows applications per year
**And** the chart title includes university name
**And** key statistics display (total, peak year, growth rate)

**Given** the university has limited patent history
**When** fewer than 5 years of data exist
**Then** a bar chart is used instead of line
**And** a note explains the limited history

**Given** I want to adjust the time range
**When** I modify the year parameters
**Then** the chart updates with the new range
**And** statistics recalculate

**Technical Notes:**
- Covers FR27
- Reuses visualization patterns from Epic 1
- Export to CSV/PNG available (FR31)

---

#### Story 4.4: Top Inventors Analysis

**As a** university PATLIB staff member,
**I want** to see top inventors at my university,
**So that** I can identify key researchers and potential collaborators.

**Acceptance Criteria:**

**Given** I have selected a university
**When** I run the "Top Inventors" cell
**Then** a query retrieves inventors ranked by application count
**And** default shows top 20 inventors
**And** progress indicator shows during execution

**Given** inventor data is retrieved
**When** results display
**Then** a table shows: inventor name, application count, technology fields
**And** a horizontal bar chart visualizes the top 10
**And** clicking an inventor name could filter further analysis

**Given** I want to see more inventors
**When** I adjust the "Top N" slider
**Then** the table and chart update accordingly
**And** maximum is capped at 100 for performance

**Given** inventor names have variations
**When** results display
**Then** a note explains that name matching is approximate
**And** PATSTAT person_id is shown for disambiguation

**Technical Notes:**
- Covers FR28
- Inventor name standardization challenges noted
- Export available (FR31)

---

#### Story 4.5: Industry Collaboration Patterns

**As a** university PATLIB staff member,
**I want** to see which companies my university collaborates with,
**So that** I can understand our industry partnerships.

**Acceptance Criteria:**

**Given** I have selected a university
**When** I run the "Industry Collaborations" cell
**Then** a query identifies co-applicants on university patents
**And** filters to corporate applicants (excludes individuals, other universities)
**And** progress indicator shows during execution

**Given** collaboration data is retrieved
**When** results display
**Then** a table shows: company name, joint application count, technology fields
**And** a bar chart shows top 10 collaborating companies
**And** collaboration trend over time is available

**Given** I click on a company name
**When** the detail view opens
**Then** specific joint applications are listed
**And** patent titles and years are shown
**And** links to full patent records are provided (if available)

**Given** the university has no industry collaborations
**When** results are empty
**Then** a helpful message explains this is not uncommon
**And** suggestions for building partnerships are provided

**Technical Notes:**
- Covers FR29
- Uses applicant type classification from PATSTAT
- Export available (FR31)

---

#### Story 4.6: Technology Field Distribution

**As a** university PATLIB staff member,
**I want** to see which technology fields my university patents in,
**So that** I can understand our research strengths.

**Acceptance Criteria:**

**Given** I have selected a university
**When** I run the "Technology Fields" cell
**Then** a query retrieves applications grouped by WIPO 35 field
**And** progress indicator shows during execution

**Given** technology data is retrieved
**When** results display
**Then** a treemap or pie chart shows field distribution
**And** percentages are shown for each field
**And** a table lists all fields with counts

**Given** I want to see IPC-level detail
**When** I click on a technology field
**Then** the top IPC subclasses within that field display
**And** specific application counts per IPC are shown

**Given** I want to compare over time
**When** I enable "Show by period"
**Then** the distribution shows for early vs recent periods
**And** emerging and declining fields are highlighted

**Technical Notes:**
- Covers FR30
- Uses WIPO 35 technology field concordance
- Export available (FR31)

---

#### Story 4.7: Multi-University Comparison

**As a** university PATLIB staff member,
**I want** to compare my university with peer institutions,
**So that** I can benchmark our patent performance.

**Acceptance Criteria:**

**Given** I have selected my primary university
**When** I click "Add comparison university"
**Then** I can select additional universities (up to 4 total)
**And** each selection shows in a comparison panel

**Given** I have selected multiple universities
**When** I run a comparison analysis
**Then** charts show all universities side-by-side:
- Application trends (multi-line chart)
- Total applications (grouped bar)
- Technology field overlap (comparison table)

**Given** comparison results display
**When** I view the summary
**Then** key differences are highlighted
**And** universities are ranked on each metric
**And** my primary university is visually emphasized

**Given** I want to export the comparison
**When** I click "Export Comparison"
**Then** a CSV with all universities' data downloads
**And** charts can be exported as PNG
**And** a comparison summary table is included

**Technical Notes:**
- Covers FR26
- Performance consideration: limit to 4 universities max
- Export covers FR31

---

### Epic 5: Educational Materials

#### Story 5.1: TIP for PATLIBs Handbook

**As a** PATLIB staff member,
**I want** a comprehensive handbook covering all 4 notebooks,
**So that** I have a single reference for all TIP capabilities.

**Acceptance Criteria:**

**Given** I access the handbook
**When** I view the table of contents
**Then** all 4 notebooks are covered in dedicated chapters:
- Chapter 1: Getting Started (setup, prerequisites)
- Chapter 2: Query Library
- Chapter 3: Interactive Demo
- Chapter 4: AI Query Builder
- Chapter 5: University Analysis
- Appendix: Troubleshooting

**Given** I read a notebook chapter
**When** I review the content
**Then** each feature is explained with:
- Purpose and use case
- Step-by-step instructions
- Screenshots of key screens
- Tips and best practices

**Given** I encounter a problem
**When** I consult the troubleshooting appendix
**Then** common issues are listed with solutions
**And** error messages are explained
**And** contact information for support is provided

**Given** I am a new user
**When** I read Chapter 1
**Then** I understand prerequisites (TIP access, browser)
**And** first-time setup is explained
**And** I can complete initial notebook run successfully

**Technical Notes:**
- Covers FR43
- Format: PDF and/or Markdown in docs folder
- Screenshots captured from stable notebooks
- Written after Epics 1-4 are complete

---

#### Story 5.2: Quick Reference Guides

**As a** PATLIB staff member,
**I want** a one-page quick reference for each notebook,
**So that** I can quickly recall key features during daily use.

**Acceptance Criteria:**

**Given** I access quick reference guides
**When** I view the collection
**Then** 4 guides are available (one per notebook)
**And** each is 1-2 pages maximum
**And** they can be printed as desk references

**Given** I view the Query Library quick reference
**When** I read the content
**Then** key actions are listed:
- How to search for queries
- How to configure parameters
- How to execute and export
- Common shortcuts and tips

**Given** I view the AI Query Builder quick reference
**When** I read the content
**Then** key actions are listed:
- How to phrase effective questions
- How to validate and edit SQL
- How to save queries
- Example question patterns

**Given** I view any quick reference
**When** I look for help
**Then** a "Need more help?" section points to:
- Full handbook chapter
- Troubleshooting guide
- Support contact

**Technical Notes:**
- Covers FR44
- Format: PDF (printable), one per notebook
- Visual layout with icons and minimal text
- Lamination-friendly design

---

#### Story 5.3: Trainer Presentation Materials

**As an** EPO Academy trainer,
**I want** presentation slides for TIP workshops,
**So that** I can deliver consistent, professional training sessions.

**Acceptance Criteria:**

**Given** I prepare for a workshop
**When** I access trainer materials
**Then** a complete slide deck is available
**And** slides are organized by workshop module
**And** speaker notes explain key talking points

**Given** I view the slide deck
**When** I review the structure
**Then** modules align with the 4-hour workshop:
- Module 1: Introduction to TIP (30 min)
- Module 2: Query Library hands-on (60 min)
- Module 3: Interactive Demo walkthrough (45 min)
- Module 4: AI Query Builder exploration (45 min)
- Module 5: University Analysis (30 min)
- Module 6: Q&A and next steps (30 min)

**Given** I am presenting a module
**When** I reach hands-on sections
**Then** slides indicate "Switch to notebook"
**And** specific cells to demonstrate are noted
**And** expected outcomes are listed for verification

**Given** participants have questions
**When** I consult speaker notes
**Then** common questions are anticipated
**And** suggested answers are provided
**And** "parking lot" topics for advanced follow-up are listed

**Technical Notes:**
- Covers FR45
- Format: PowerPoint/Google Slides
- EPO Academy branding guidelines followed
- Includes timing guidance per slide

---

#### Story 5.4: Step-by-Step Tutorials

**As a** PATLIB staff member learning independently,
**I want** detailed tutorials with screenshots,
**So that** I can learn specific tasks without trainer assistance.

**Acceptance Criteria:**

**Given** I access the tutorials section
**When** I view available tutorials
**Then** task-based tutorials are organized by goal:
- "Find patents in my technology field"
- "Identify top applicants in my region"
- "Generate a custom query with AI"
- "Analyze my university's patent portfolio"
- "Export data for a report"

**Given** I follow a tutorial
**When** I work through each step
**Then** numbered steps guide me through the task
**And** each step has a screenshot showing expected result
**And** "Checkpoint" boxes verify I'm on track

**Given** I complete a tutorial
**When** I reach the end
**Then** a "What you accomplished" summary appears
**And** variations and next steps are suggested
**And** related tutorials are linked

**Given** my screen doesn't match a screenshot
**When** I look for help
**Then** "Troubleshooting" callouts address common deviations
**And** I can recover and continue the tutorial

**Technical Notes:**
- Covers FR46
- Format: PDF with screenshots, or web-based (HTML)
- 5-8 tutorials covering common user journeys
- Screenshots annotated with callouts and arrows

---

## Story Summary

| Epic | Title | Stories | FRs Covered |
|------|-------|---------|-------------|
| 1 | Query Library | 6 | FR1-FR12, FR33-FR42 |
| 2 | Interactive Demo | 4 | FR13-FR17 |
| 3 | AI Query Builder | 6 | FR18-FR24 |
| 4 | University Analysis | 7 | FR25-FR32 |
| 5 | Educational Materials | 4 | FR43-FR46 |

**Total: 27 stories covering all 46 functional requirements**

