# TIP for PATLIBs - Epic Breakdown

**Author:** BMad
**Date:** 2026-01-12
**Project Type:** Data Analysis Tool (Jupyter Notebook)
**Field Type:** Greenfield

---

## Overview

This document provides the complete epic and story breakdown for TIP for PATLIBs, decomposing the 55 functional requirements from the [PRD](./PRD.md) into implementable stories.

**Living Document Notice:** This is the initial version created during planning. It will be updated as implementation progresses.

### Epic Summary

| Epic | Title | Stories | FRs Covered |
|------|-------|---------|-------------|
| 1 | Foundation & Setup | 4 | FR1-4, FR47 |
| 2 | Selection Interface | 6 | FR5-21, FR48-51 |
| 3 | Query Engine | 4 | FR22-27 |
| 4 | Visualizations | 4 | FR28-41 |
| 5 | Export & Polish | 3 | FR42-46, FR52-55 |

**Total: 21 stories**

---

## Functional Requirements Inventory

### Setup & Init (FR1-4)
- FR1: Single initialization cell loads all dependencies
- FR2: Environment compatibility check
- FR3: Library installation/updates via pip
- FR4: Initialization status display

### Country Selection (FR5-8)
- FR5: Country dropdown selection
- FR6: User-friendly country names
- FR7: Country required before analysis
- FR8: Remember last country in session

### Region Selection (FR9-12)
- FR9: Optional region/state selection
- FR10: Dynamic region dropdown based on country
- FR11: Country-level analysis without region
- FR12: Indicate unavailable regional data

### Tech Sector Selection (FR13-17)
- FR13: Select from 35 WIPO technology fields
- FR14: Fields grouped by sector
- FR15: Display field number and name
- FR16: View IPC codes for each field
- FR17: Use PATSTAT concordance tables

### Date Range (FR18-21)
- FR18: Specify start/end year
- FR19: Sensible defaults (10 years)
- FR20: Validate date range
- FR21: Preset range quick buttons

### Query & Processing (FR22-27)
- FR22: Query via EPO patstat + SQLAlchemy
- FR23: Filter by jurisdiction, region, sector, dates
- FR24: Retrieve applicant information
- FR25: Aggregate data per visualization
- FR26: Progress indicator
- FR27: Graceful error handling

### Visualizations (FR28-41)
- FR28-31: Trend line chart
- FR32-35: Top applicants bar chart
- FR36-38: Geographic distribution
- FR39-41: Tech breakdown treemap

### Export (FR42-46)
- FR42-43: CSV export with headers
- FR44-45: PNG export with naming
- FR46: Download links

### UI & Error Handling (FR47-55)
- FR47-51: ipywidgets, labels, reset
- FR52-55: Error messages, suggestions

---

## FR Coverage Map

| FR Range | Epic | Stories |
|----------|------|---------|
| FR1-4 | Epic 1 | 1.1, 1.2 |
| FR5-8 | Epic 2 | 2.1 |
| FR9-12 | Epic 2 | 2.2 |
| FR13-17 | Epic 2 | 2.3, 2.4 |
| FR18-21 | Epic 2 | 2.5 |
| FR22-27 | Epic 3 | 3.1, 3.2, 3.3, 3.4 |
| FR28-31 | Epic 4 | 4.1 |
| FR32-35 | Epic 4 | 4.2 |
| FR36-38 | Epic 4 | 4.3 |
| FR39-41 | Epic 4 | 4.4 |
| FR42-46 | Epic 5 | 5.1, 5.2 |
| FR47-51 | Epic 2 | 2.6 |
| FR52-55 | Epic 5 | 5.3 |

---

## Epic 1: Foundation & Setup

**Goal:** Users can open the notebook and get started instantly with a working PATSTAT connection and all reference data loaded.

**FRs Covered:** FR1, FR2, FR3, FR4, FR47

---

### Story 1.1: Project Structure & Module Setup

**As a** developer,
**I want** a well-organized project structure with notebook and supporting module,
**So that** code is maintainable and the notebook stays clean.

**Acceptance Criteria:**

**Given** a fresh TIP JupyterLab environment
**When** I open the project folder
**Then** I see:
- `TIP_for_PATLIBs.ipynb` - main notebook
- `tip4patlibs_core.py` - supporting module
- `README.md` - brief setup instructions

**And** the notebook imports from `tip4patlibs_core` without errors
**And** the module contains placeholder classes: `AnalysisState`, `PatstatQueries`, `WidgetFactory`, `ChartBuilder`, `Exporter`
**And** total module LOC is tracked (split to lib/ if >500)

**Prerequisites:** None (first story)

**Technical Notes:**
- Follow Architecture ADR-001 structure
- Use Python dataclasses for AnalysisState
- All ipywidgets imports in module, not notebook
- Notebook cells should be mostly widget displays and function calls

---

### Story 1.2: Initialization Cell & PATSTAT Connection

**As a** PATLIB user,
**I want** to run one cell and have everything ready,
**So that** I don't need to understand Python setup.

**Acceptance Criteria:**

**Given** a user opens the notebook for the first time
**When** they execute Cell 1 (marked "Run this cell first!")
**Then** the system:
- Imports all required libraries (pandas, plotly, ipywidgets)
- Establishes PATSTAT connection via `PatstatClient()`
- Displays success message: "✅ Connected to PATSTAT"
- Shows PATSTAT version/date if available

**And** if connection fails:
- Displays clear error: "❌ Could not connect to PATSTAT"
- Suggests: "Please check TIP platform status"

**And** initialization completes within 30 seconds (NFR1)

**Given** required libraries are missing
**When** initialization runs
**Then** system attempts `pip install` for missing packages
**And** reports what was installed

**Prerequisites:** Story 1.1

**Technical Notes:**
- Use try/except for connection handling
- Store PatstatClient in module-level variable
- Pre-load reference data in Story 1.3 (not here)
- Cell should have clear visual marker ("▶️ Run this cell first!")

---

### Story 1.3: Reference Data Loading

**As a** system,
**I want** to pre-load all dropdown options at startup,
**So that** users see instant responses when selecting filters.

**Acceptance Criteria:**

**Given** PATSTAT connection is established
**When** initialization completes
**Then** system loads and caches:
- Country list from `tls206_person.person_ctry_code` (DISTINCT values)
- Technology fields from `tls901_techn_field_ipc` (35 WIPO fields)
- Sectors from `tls901_techn_field_ipc.techn_sector` (5 sectors)

**And** country list shows user-friendly names (map codes to names)
**And** tech fields show: "13 - Medical technology" format
**And** fields are grouped by sector in display

**And** reference data is stored in `ReferenceData` class:
```python
class ReferenceData:
    countries: List[Tuple[str, str]]  # (display_name, code)
    tech_fields: List[Tuple[str, int]]  # (display_name, field_nr)
    sectors: List[str]
```

**Prerequisites:** Story 1.2

**Technical Notes:**
- Query DISTINCT values, not full tables
- Cache in memory (no file caching needed)
- Country name mapping: Use ISO country names or PATSTAT's own labels
- NUTS regions loaded dynamically per-country (not here)

---

### Story 1.4: AnalysisState Class Implementation

**As a** developer,
**I want** a central state management class,
**So that** all widgets and queries share consistent state.

**Acceptance Criteria:**

**Given** the module is loaded
**When** I create `state = AnalysisState()`
**Then** it has these attributes with defaults:
- `country: Optional[str] = None`
- `region: Optional[str] = None`
- `tech_mode: str = "field"` (or "ipc")
- `tech_field: Optional[int] = None`
- `ipc_codes: List[str] = []` (max 5)
- `year_start: int = 2019`
- `year_end: int = 2023`
- `sme_filter: bool = False`

**And** `state.summary()` returns human-readable string:
```
📍 Country: Germany
🗺️  Region: Bavaria
🔬 Technology: Field 13 - Medical technology
📅 Period: 2019-2023
🏢 SME Focus: Yes
```

**And** `state.is_valid()` returns `(True, "Ready")` when all required fields set
**And** `state.is_valid()` returns `(False, "Please select a country")` when country missing

**Prerequisites:** Story 1.1

**Technical Notes:**
- Use Python dataclass with field() for list default
- summary() uses emoji for visual scanning
- is_valid() checks: country required, tech_field OR ipc_codes required
- Follow Architecture ADR-006

---

## Epic 2: Selection Interface

**Goal:** Users can specify exactly what they want to analyze through intuitive, constrained dropdowns and controls.

**FRs Covered:** FR5-21, FR47-51

---

### Story 2.1: Country Selection Widget

**As a** PATLIB user,
**I want** to select a country from a dropdown,
**So that** I can analyze patent activity for a specific jurisdiction.

**Acceptance Criteria:**

**Given** Cell 2 is displayed
**When** user views the country dropdown
**Then** they see:
- Label: "Country:"
- Placeholder: "Select country..."
- Options: All countries from reference data (sorted A-Z)
- Format: "Germany" not "DE" (user-friendly names)

**And** when user selects a country:
- `state.country` updates immediately
- Region dropdown enables (Story 2.2)
- Selection persists within session (FR8)

**And** dropdown uses ipywidgets.Dropdown with:
- `style={'description_width': '100px'}`
- `layout={'width': '300px'}`

**Prerequisites:** Story 1.3 (reference data), Story 1.4 (state)

**Technical Notes:**
- Countries from ReferenceData.countries
- observe() callback updates state
- Cascading: region dropdown re-populates on country change
- Consider ~50-100 countries in list

---

### Story 2.2: Region Selection Widget (NUTS)

**As a** PATLIB user,
**I want** to optionally filter by region within my country,
**So that** I can focus on local innovation activity.

**Acceptance Criteria:**

**Given** a country is selected
**When** user views the region dropdown
**Then** they see:
- Label: "Region:"
- Default option: "All regions" (no filter)
- Options: NUTS regions for selected country from tls904_nuts

**And** regions are loaded dynamically via query:
```sql
SELECT DISTINCT nuts, nuts_label
FROM tls904_nuts
WHERE nuts LIKE '{country_code}%'
AND nuts_level <= 2
ORDER BY nuts_label
```

**And** when country has no NUTS data:
- Dropdown shows only "All regions"
- Helper text: "Regional data not available for this country"

**And** when user selects a region:
- `state.region` updates
- Selection is optional (can proceed without)

**Prerequisites:** Story 2.1

**Technical Notes:**
- Query NUTS on country change (not at startup)
- nuts_level 0=country, 1=large region, 2=smaller region
- Use level 1-2 for meaningful regional breakdown
- ~20-50 regions per country typically

---

### Story 2.3: Technology Field Selection (WIPO 35)

**As a** PATLIB user,
**I want** to select a technology sector from predefined fields,
**So that** I don't need to know IPC codes.

**Acceptance Criteria:**

**Given** Cell 3 is displayed with tech_mode = "field"
**When** user views the technology dropdown
**Then** they see:
- Label: "Technology Field:"
- Options grouped by sector:
  ```
  -- Electrical engineering --
  1 - Electrical machinery, apparatus, energy
  2 - Audio-visual technology
  ...
  -- Instruments --
  9 - Optics
  10 - Measurement
  ...
  ```

**And** format is: "{field_nr} - {field_name}"
**And** all 35 WIPO fields are available

**And** when user selects a field:
- `state.tech_field` updates
- `state.tech_mode` = "field"

**And** user can see IPC mapping via info button/tooltip:
- "Includes: A61B, A61C, A61F..." (FR16)

**Prerequisites:** Story 1.3 (reference data)

**Technical Notes:**
- Data from tls901_techn_field_ipc
- Group by techn_sector for display
- Architecture ADR-004: This is primary mode
- IPC tooltip from tls901 ipc_maingroup_symbol

---

### Story 2.4: Custom IPC/CPC Entry (Dual Mode)

**As a** power user,
**I want** to enter specific IPC/CPC codes instead of predefined fields,
**So that** I can do targeted analysis.

**Acceptance Criteria:**

**Given** Cell 3 with mode toggle
**When** user switches to "Custom IPC/CPC" mode
**Then** they see:
- Text input field for IPC codes
- Helper text: "Enter up to 5 IPC main groups (e.g., A61B, H01L)"
- Validation feedback

**And** input accepts:
- Single code: "A61B"
- Multiple codes: "A61B, A61C, A61F"
- Max 5 codes enforced

**And** validation checks:
- Pattern: `/^[A-H]\d{2}[A-Z]?$/` (IPC main group format)
- Displays: "✓ Valid" or "✗ Invalid format"

**And** when valid codes entered:
- `state.ipc_codes` updates (list)
- `state.tech_mode` = "ipc"

**And** mode toggle is clear:
- RadioButtons: "Tech Field" | "Custom IPC/CPC"
- Only one mode active at a time

**Prerequisites:** Story 2.3

**Technical Notes:**
- Architecture ADR-004: Dual mode design
- Custom mode queries tls209_appln_ipc instead of tls230
- Consider autocomplete (future enhancement)
- Regex validation in widget callback

---

### Story 2.5: Date Range Selection

**As a** PATLIB user,
**I want** to specify the time period for analysis,
**So that** I can focus on recent trends or historical patterns.

**Acceptance Criteria:**

**Given** Cell 4 is displayed
**When** user views date range controls
**Then** they see:
- IntRangeSlider: 2000-2024
- Default: [2019, 2023] (5 years)
- Labels showing selected range

**And** performance tip updates dynamically:
- Span ≤5 years: "⚡ Fast query (~10 sec)"
- Span 6-10 years: "⏱️ Medium query (~30 sec)"
- Span >10 years: "🐢 Large query (~2 min)"

**And** validation ensures:
- start < end
- Range within available data

**And** quick preset buttons (optional):
- "Last 5 years" | "Last 10 years" | "Last 15 years"

**And** when range selected:
- `state.year_start` and `state.year_end` update

**Prerequisites:** Story 1.4 (state)

**Technical Notes:**
- Use IntRangeSlider from ipywidgets
- Performance tip from Architecture patterns
- observe() callback for dynamic tip update
- Max year should be current year or PATSTAT data cutoff

---

### Story 2.6: Options & Review Panel

**As a** PATLIB user,
**I want** to see my selections summarized and have additional options,
**So that** I can verify my query before running.

**Acceptance Criteria:**

**Given** Cell 5 is displayed
**When** user has made selections
**Then** they see summary panel showing `state.summary()`:
```
📍 Country: Germany
🗺️  Region: Bavaria
🔬 Technology: Field 13 - Medical technology
📅 Period: 2019-2023
```

**And** additional options:
- SME Filter checkbox: "Focus on SMEs (<100 applications)"
- When checked: `state.sme_filter = True`

**And** Reset button:
- Clears all selections to defaults
- Re-initializes state object

**And** "Run Analysis" button:
- Prominent styling (green background)
- Disabled until `state.is_valid()` returns True
- Shows validation message if invalid

**Prerequisites:** Stories 2.1-2.5

**Technical Notes:**
- Summary uses HTML widget for formatting
- Reset creates new AnalysisState()
- Run button triggers Epic 3 query logic
- Consider VBox/HBox layout for organization

---

## Epic 3: Query Engine

**Goal:** System retrieves the right data from PATSTAT efficiently and returns clean DataFrames for visualization.

**FRs Covered:** FR22-27

---

### Story 3.1: PatstatQueries Class & Base Query

**As a** developer,
**I want** a query builder class that handles all PATSTAT interactions,
**So that** query logic is centralized and testable.

**Acceptance Criteria:**

**Given** `PatstatQueries(db)` is initialized with PATSTAT connection
**When** I call query methods
**Then** they return pandas DataFrames

**And** class implements:
```python
class PatstatQueries:
    def __init__(self, db): ...
    def get_trend_data(self, state) -> pd.DataFrame: ...
    def get_top_applicants(self, state, limit=10) -> pd.DataFrame: ...
    def get_tech_breakdown(self, state) -> pd.DataFrame: ...
    def get_regional_distribution(self, state) -> pd.DataFrame: ...
```

**And** base query pattern established:
- ORM primary for simple queries
- SQL escape hatch for complex aggregations
- All queries respect state filters

**Prerequisites:** Story 1.2 (PATSTAT connection)

**Technical Notes:**
- Follow Architecture ADR-002 patterns
- Use patstat.df() or pd.read_sql() for results
- Parameterized queries to prevent SQL injection
- Connection passed at init, not per-method

---

### Story 3.2: Trend Query (Applications Over Time)

**As a** PATLIB user,
**I want** to see patent application counts by year,
**So that** I can identify trends in innovation activity.

**Acceptance Criteria:**

**Given** valid state with country, tech field/IPC, date range
**When** `get_trend_data(state)` is called
**Then** returns DataFrame with columns:
- `year`: Filing year (int)
- `application_count`: Number of applications
- `invention_count`: Number of unique families (docdb_family_id)

**And** query joins:
- tls201_appln (applications)
- tls230_appln_techn_field OR tls209_appln_ipc (based on tech_mode)
- tls207_pers_appln (person link, applt_seq_nr > 0)
- tls206_person (country/region filter)

**And** if state.region is set:
- Additional filter on tls206_person.nuts LIKE '{region}%'

**And** if state.sme_filter is True:
- Filter to applicants with <100 total applications

**And** results grouped by year, ordered ascending

**Prerequisites:** Story 3.1, Story 1.4

**Technical Notes:**
- Use ORM for this query (straightforward aggregation)
- GROUP BY appln_filing_year
- COUNT(appln_id) for applications
- COUNT(DISTINCT docdb_family_id) for inventions
- Query should complete in <60 seconds (NFR2)

---

### Story 3.3: Top Applicants Query

**As a** PATLIB user,
**I want** to see who files the most patents in my selection,
**So that** I can identify key players.

**Acceptance Criteria:**

**Given** valid state
**When** `get_top_applicants(state, limit=10)` is called
**Then** returns DataFrame with columns:
- `applicant_name`: psn_name from tls206_person
- `application_count`: Number of applications
- `invention_count`: Unique families
- `country`: Applicant country code

**And** results sorted by application_count DESC
**And** limited to top N (default 10, options 10/25)

**And** uses SQL escape hatch for complex aggregation:
```sql
SELECT p.psn_name, p.person_ctry_code,
       COUNT(DISTINCT a.appln_id) as application_count,
       COUNT(DISTINCT a.docdb_family_id) as invention_count
FROM tls201_appln a
JOIN tls207_pers_appln pa ON a.appln_id = pa.appln_id
JOIN tls206_person p ON pa.person_id = p.person_id
JOIN tls230_appln_techn_field tf ON a.appln_id = tf.appln_id
WHERE [filters from state]
GROUP BY p.psn_name, p.person_ctry_code
ORDER BY application_count DESC
LIMIT :limit
```

**And** SME filter (if enabled) adds subquery constraint

**Prerequisites:** Story 3.1

**Technical Notes:**
- SQL escape hatch preferred here (complex GROUP BY)
- psn_name is PATSTAT Standardized Name (best for grouping)
- Handle NULL names gracefully
- Architecture provides SQL template

---

### Story 3.4: Query Execution & Progress

**As a** PATLIB user,
**I want** to see progress while queries run,
**So that** I know the system is working.

**Acceptance Criteria:**

**Given** user clicks "Run Analysis"
**When** queries execute
**Then** user sees:
- Loading spinner or progress indicator
- Status: "Querying PATSTAT..."
- Time elapsed (optional)

**And** queries run in sequence:
1. Trend data (for line chart)
2. Top applicants (for bar chart)
3. Tech breakdown (for treemap)
4. Regional distribution (if region selected)

**And** on completion:
- Spinner removed
- Results displayed (Epic 4)
- Status: "✅ Analysis complete"

**And** if any query fails:
- Other queries continue
- Error shown: "⚠️ Could not load [chart name]"
- Suggestion provided

**Prerequisites:** Stories 3.1-3.3

**Technical Notes:**
- Use ipywidgets Output() for status area
- Simple spinner (not fake progress bar)
- Architecture says PATSTAT is reliable on TIP
- Queries are independent, run sequentially for simplicity
- Store results in module-level variables for viz access

---

## Epic 4: Visualizations

**Goal:** Users see insights through interactive Plotly charts with EPO styling.

**FRs Covered:** FR28-41

---

### Story 4.1: Trend Line Chart

**As a** PATLIB user,
**I want** to see patent applications over time as a line chart,
**So that** I can spot trends and patterns.

**Acceptance Criteria:**

**Given** trend data from Story 3.2
**When** chart renders
**Then** user sees:
- Line chart (Plotly)
- X-axis: Years
- Y-axis: Application count
- Title: "Patent Applications: [Country] - [Tech Field] (2019-2023)"

**And** styling:
- EPO Red primary color (#C8102E)
- Arial font family
- Clean axis labels

**And** interactivity:
- Hover shows exact values
- Zoom/pan enabled

**And** optionally show dual line:
- Applications (solid)
- Inventions/families (dashed) for comparison

**Prerequisites:** Story 3.2

**Technical Notes:**
- Use ChartBuilder.trend_line() from Architecture
- plotly.express.line with styling
- Title dynamically reflects state
- Render in Output widget in Cell 6

---

### Story 4.2: Top Applicants Bar Chart

**As a** PATLIB user,
**I want** to see top applicants as a horizontal bar chart,
**So that** I can quickly identify leading innovators.

**Acceptance Criteria:**

**Given** top applicants data from Story 3.3
**When** chart renders
**Then** user sees:
- Horizontal bar chart
- Y-axis: Applicant names (sorted by count)
- X-axis: Application count
- Title: "Top 10 Applicants: [Country] - [Tech Field]"

**And** applicant names readable:
- Truncate if >30 chars
- Tooltip shows full name

**And** styling:
- EPO Red (#C8102E)
- Bars ordered largest at top

**And** interactivity:
- Hover shows: name, count, country

**And** user can switch between Top 10 / Top 25:
- Dropdown or toggle
- Re-renders chart with new limit

**Prerequisites:** Story 3.3

**Technical Notes:**
- Use ChartBuilder.top_applicants_bar() from Architecture
- plotly.express.bar with orientation='h'
- yaxis categoryorder='total ascending'
- Consider long German company names

---

### Story 4.3: Regional Distribution Chart

**As a** PATLIB user,
**I want** to see how patents are distributed across regions,
**So that** I can identify innovation hotspots.

**Acceptance Criteria:**

**Given** regional distribution data
**When** chart renders
**Then** user sees:
- Bar chart showing regions
- X-axis: Region names
- Y-axis: Application count
- Title: "Regional Distribution: [Country] - [Tech Field]"

**And** only shows if:
- User selected a country with NUTS data
- More than one region has data

**And** if no regional data:
- Display: "Regional breakdown not available for this selection"

**Prerequisites:** Story 3.1 (regional query)

**Technical Notes:**
- Simpler than choropleth map (no GeoJSON needed)
- Consider top 10 regions if many exist
- NUTS labels from tls904_nuts
- Could enhance to map in future version

---

### Story 4.4: Technology Breakdown Treemap

**As a** PATLIB user,
**I want** to see the distribution across technology sub-fields,
**So that** I can understand specialization areas.

**Acceptance Criteria:**

**Given** tech breakdown data
**When** chart renders
**Then** user sees:
- Treemap chart
- Hierarchy: Sector → Field (if showing all) OR IPC classes (if specific field)
- Size: Application count
- Title: "Technology Breakdown: [Country] (2019-2023)"

**And** if tech_mode = "field":
- Show IPC classes within selected field
- Data from tls209_appln_ipc for applications in selection

**And** if tech_mode = "ipc":
- Show distribution across entered IPC codes
- Compare relative sizes

**And** styling:
- EPO color palette
- Labels visible in boxes

**And** interactivity:
- Click to drill down (optional)
- Hover shows details

**Prerequisites:** Story 3.1

**Technical Notes:**
- Use ChartBuilder.tech_treemap() from Architecture
- plotly.express.treemap
- May need additional query for IPC detail
- Consider sunburst as alternative

---

## Epic 5: Export & Polish

**Goal:** Users can take results away, share them, and get help when things don't work as expected.

**FRs Covered:** FR42-46, FR52-55

---

### Story 5.1: CSV Export

**As a** PATLIB user,
**I want** to export analysis results to CSV,
**So that** I can use them in Excel or other tools.

**Acceptance Criteria:**

**Given** analysis has completed
**When** user clicks "Export CSV" button
**Then** system:
- Generates CSV file with all data
- Uses semicolon delimiter (European standard)
- Uses UTF-8 with BOM encoding (Excel-friendly)
- Includes clear column headers

**And** filename format:
- `tip4patlibs_{country}_{tech}_{years}_{timestamp}.csv`
- Example: `tip4patlibs_DE_field13_2019-2023_20260112_1430.csv`

**And** CSV includes:
- Trend data (year, applications, inventions)
- Top applicants (name, count, country)
- Metadata header rows (query parameters)

**And** user sees download link:
- Clickable link to download
- Or automatic download trigger

**Prerequisites:** Epic 3 (data), Epic 4 (results displayed)

**Technical Notes:**
- Use Exporter.to_csv() from Architecture
- pandas to_csv with sep=';', encoding='utf-8-sig'
- Consider FileLink from IPython.display
- May need to save to /tmp or user's folder

---

### Story 5.2: PNG Export

**As a** PATLIB user,
**I want** to export charts as PNG images,
**So that** I can use them in presentations and reports.

**Acceptance Criteria:**

**Given** charts are displayed
**When** user clicks "Export PNG" for a chart
**Then** system:
- Generates PNG image at high resolution (300 DPI)
- Saves with descriptive filename

**And** filename format:
- `tip4patlibs_{country}_{tech}_{years}_{chartname}.png`
- Example: `tip4patlibs_DE_field13_2019-2023_trend.png`

**And** each chart has its own export button:
- "📷 Export" below each chart
- Or single "Export All Charts" button

**And** user sees download link(s)

**Prerequisites:** Epic 4 (charts rendered)

**Technical Notes:**
- Use Exporter.to_png() from Architecture
- Plotly write_image() requires kaleido
- Check if kaleido available on TIP
- Fallback: Plotly has built-in download button

---

### Story 5.3: Zero Results & Data Quality Handling

**As a** PATLIB user,
**I want** helpful messages when queries return no data,
**So that** I can adjust my search.

**Acceptance Criteria:**

**Given** a query returns zero results
**When** results are displayed
**Then** user sees:
- Message: "No patents found for this selection"
- Suggestions:
  - "Try expanding the date range"
  - "Try a different technology field"
  - "Try removing the region filter"

**And** data quality warnings show when relevant:
- "Note: Applicant names may have variations (same company listed multiple times)"
- "Note: Regional data depends on address quality in PATSTAT"

**And** low result warning:
- If <10 results: "Limited data available for this selection"

**And** all messages use friendly language (non-technical)

**Prerequisites:** Story 3.4 (query execution)

**Technical Notes:**
- Check DataFrame length after each query
- Messages stored in module (easy to update)
- Architecture says prevent bad inputs, but edge cases exist
- Consider showing data coverage info

---

## FR Coverage Matrix

| FR | Description | Epic | Story |
|----|-------------|------|-------|
| FR1 | Single initialization cell | 1 | 1.2 |
| FR2 | Environment compatibility check | 1 | 1.2 |
| FR3 | Library installation via pip | 1 | 1.2 |
| FR4 | Initialization status display | 1 | 1.2 |
| FR5 | Country dropdown selection | 2 | 2.1 |
| FR6 | User-friendly country names | 2 | 2.1 |
| FR7 | Country required before analysis | 2 | 2.6 |
| FR8 | Remember last country | 2 | 2.1 |
| FR9 | Optional region selection | 2 | 2.2 |
| FR10 | Dynamic region dropdown | 2 | 2.2 |
| FR11 | Country-level analysis | 2 | 2.2 |
| FR12 | Indicate unavailable regional data | 2 | 2.2 |
| FR13 | Select from 35 WIPO fields | 2 | 2.3 |
| FR14 | Fields grouped by sector | 2 | 2.3 |
| FR15 | Display field number and name | 2 | 2.3 |
| FR16 | View IPC codes for field | 2 | 2.3 |
| FR17 | Use PATSTAT concordance tables | 2 | 2.3, 3.2 |
| FR18 | Specify start/end year | 2 | 2.5 |
| FR19 | Sensible defaults | 2 | 2.5 |
| FR20 | Validate date range | 2 | 2.5 |
| FR21 | Preset range buttons | 2 | 2.5 |
| FR22 | Query via EPO patstat + SQLAlchemy | 3 | 3.1 |
| FR23 | Filter by jurisdiction, region, sector, dates | 3 | 3.2, 3.3 |
| FR24 | Retrieve applicant information | 3 | 3.3 |
| FR25 | Aggregate data per visualization | 3 | 3.2, 3.3 |
| FR26 | Progress indicator | 3 | 3.4 |
| FR27 | Graceful error handling | 3 | 3.4 |
| FR28 | Patent count over time | 4 | 4.1 |
| FR29 | Year-over-year trends | 4 | 4.1 |
| FR30 | Hover for exact values | 4 | 4.1, 4.2 |
| FR31 | Chart title reflects selections | 4 | 4.1, 4.2 |
| FR32 | Top N applicants bar chart | 4 | 4.2 |
| FR33 | Configure N (5, 10, 20, 50) | 4 | 4.2 |
| FR34 | Show applicant names and counts | 4 | 4.2 |
| FR35 | Hover for additional details | 4 | 4.2 |
| FR36 | Regional distribution | 4 | 4.3 |
| FR37 | Relative activity visualization | 4 | 4.3 |
| FR38 | Compare regions | 4 | 4.3 |
| FR39 | Tech sub-field distribution | 4 | 4.4 |
| FR40 | Show active IPC areas | 4 | 4.4 |
| FR41 | Drill down to IPC details | 4 | 4.4 |
| FR42 | Export to CSV | 5 | 5.1 |
| FR43 | CSV with clear headers | 5 | 5.1 |
| FR44 | Export charts as PNG | 5 | 5.2 |
| FR45 | Descriptive filenames | 5 | 5.1, 5.2 |
| FR46 | Download links | 5 | 5.1, 5.2 |
| FR47 | All inputs use ipywidgets | 1, 2 | 1.1, 2.1-2.6 |
| FR48 | Components clearly labeled | 2 | 2.1-2.6 |
| FR49 | Required fields distinguished | 2 | 2.6 |
| FR50 | Reset functionality | 2 | 2.6 |
| FR51 | Responsive UI layout | 2 | 2.1-2.6 |
| FR52 | Clear error messages | 5 | 5.3 |
| FR53 | Indicate no data matches | 5 | 5.3 |
| FR54 | Warn about data quality | 5 | 5.3 |
| FR55 | Suggestions for zero results | 5 | 5.3 |

**Coverage: 55/55 FRs mapped (100%)**

---

## Summary

### Epic Breakdown Complete

| Epic | Stories | Key Deliverable |
|------|---------|-----------------|
| 1. Foundation & Setup | 4 | Working notebook with PATSTAT connection |
| 2. Selection Interface | 6 | Full filter UI with cascading dropdowns |
| 3. Query Engine | 4 | PATSTAT queries returning DataFrames |
| 4. Visualizations | 4 | Interactive Plotly charts |
| 5. Export & Polish | 3 | CSV/PNG export and user guidance |

**Total: 21 stories**

### Implementation Order

```
Epic 1 (Foundation) → Epic 2 (Selection) → Epic 3 (Query) → Epic 4 (Viz) → Epic 5 (Export)
     4 stories           6 stories          4 stories       4 stories      3 stories
```

### Ready for Implementation

All 55 functional requirements from the PRD are covered by stories with:
- BDD-style acceptance criteria
- Clear prerequisites
- Technical implementation notes
- References to Architecture decisions

---

_For implementation: Use sprint-planning workflow to organize stories into sprints._

_This document will be updated as implementation progresses and edge cases are discovered._
