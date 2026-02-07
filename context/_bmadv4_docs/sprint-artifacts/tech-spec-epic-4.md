# Epic Technical Specification: Visualizations

Date: 2026-01-12
Author: BMad
Epic ID: 4
Status: Draft

---

## Overview

Epic 4 implements the visualization layer for TIP for PATLIBs, transforming the DataFrames produced by Epic 3's query engine into interactive Plotly charts with EPO styling. This epic delivers four core visualizations: trend line chart for patent applications over time, horizontal bar chart for top applicants, bar chart for regional distribution, and treemap for technology breakdown.

The ChartBuilder class centralizes all visualization logic, applying consistent EPO branding (EPO Red #C8102E) and professional typography (Arial) across all charts. Charts are rendered in Jupyter Output widgets with full interactivity (hover, zoom, pan) and are designed for both analysis and presentation/export use cases.

## Objectives and Scope

### In Scope

- ChartBuilder class with factory methods for all chart types
- Trend line chart: Patent applications/inventions by year (dual line)
- Top applicants horizontal bar chart: Ranked by application count, configurable limit (10/25)
- Regional distribution bar chart: NUTS regions when data available
- Technology breakdown treemap: IPC class distribution within selected tech field
- EPO brand styling: Colors, fonts, clean axes
- Interactive features: Hover tooltips, zoom/pan
- Chart titles dynamically reflecting user selections

### Out of Scope

- Export to PNG (Epic 5)
- Geographic choropleth maps (deferred - bar chart simpler)
- Complex drill-down interactions (future enhancement)
- Animation/transitions (keep simple for TIP performance)
- Custom color selection by users

## System Architecture Alignment

### Components Referenced

| Component | Purpose | Source |
|-----------|---------|--------|
| `ChartBuilder` | Visualization factory class | Architecture - Visualization Pattern |
| `PatstatQueries` | Data source | Epic 3 / Story 3.1 |
| `AnalysisState` | State for titles/context | Epic 1 / ADR-006 |
| `run_analysis()` | Results dict | Epic 3 / Story 3.4 |
| `EPO_COLORS` | Brand constants | Architecture - Visualization Pattern |

### Architecture Constraints

- **ADR-001**: ChartBuilder lives in `tip4patlibs_core.py` module
- **ADR-003**: Prevention by design - valid data guaranteed from query layer
- **Performance**: Charts render within 5 seconds of data availability (NFR4)
- **Visual**: EPO Red primary (#C8102E), Arial font, clean professional styling

## Detailed Design

### Services and Modules

| Component | Responsibility | Inputs | Outputs |
|-----------|----------------|--------|---------|
| `ChartBuilder.trend_line(df, state)` | Line chart for yearly trends | DataFrame, AnalysisState | plotly.graph_objects.Figure |
| `ChartBuilder.top_applicants_bar(df, state, limit)` | Horizontal bar chart for rankings | DataFrame, AnalysisState, int | plotly.graph_objects.Figure |
| `ChartBuilder.regional_bar(df, state)` | Bar chart for regional distribution | DataFrame, AnalysisState | plotly.graph_objects.Figure |
| `ChartBuilder.tech_treemap(df, state)` | Treemap for IPC breakdown | DataFrame, AnalysisState | plotly.graph_objects.Figure |
| `display_results(results, state)` | Render all charts in output area | Dict[str, DataFrame], AnalysisState | None (displays widgets) |

### Data Models and Contracts

#### Input DataFrames (from Epic 3)

**Trend Data:**
```
| year (int) | application_count (int) | invention_count (int) |
|------------|------------------------|----------------------|
| 2019       | 1234                   | 987                  |
| 2020       | 1456                   | 1102                 |
```

**Top Applicants:**
```
| applicant_name (str) | application_count (int) | invention_count (int) | country (str) |
|---------------------|------------------------|----------------------|---------------|
| SIEMENS AG          | 523                    | 412                  | DE            |
| ROBERT BOSCH GMBH   | 498                    | 387                  | DE            |
```

**Regional Distribution:**
```
| region (str) | region_label (str) | count (int) |
|--------------|-------------------|-------------|
| DE2          | Bayern            | 1234        |
| DE7          | Hessen            | 987         |
```

**Tech Breakdown:**
```
| ipc_class (str) | ipc_label (str) | count (int) |
|-----------------|-----------------|-------------|
| A61B            | Diagnosis...    | 234         |
| A61C            | Dentistry...    | 156         |
```

#### Output: Plotly Figures

All chart methods return `plotly.graph_objects.Figure` objects configured with:
- EPO color scheme
- Arial font family
- Descriptive title based on state
- Axis labels
- Hover templates
- Responsive layout

### APIs and Interfaces

#### EPO Brand Constants

```python
# EPO brand colors
EPO_COLORS = {
    'primary': '#C8102E',      # EPO Red
    'secondary': '#6D6E71',    # EPO Gray
    'light': '#F5F5F5',        # Light background
    'dark': '#1D1D1B',         # Dark text
}

EPO_PALETTE = ['#C8102E', '#6D6E71', '#A6093D', '#8B8D8E', '#D4495B', '#B0B1B3']

EPO_LAYOUT = {
    'font_family': 'Arial',
    'title_font_size': 16,
    'paper_bgcolor': 'white',
    'plot_bgcolor': 'white',
}
```

#### ChartBuilder Class

```python
class ChartBuilder:
    """Plotly chart builders with EPO styling."""

    @staticmethod
    def trend_line(df: pd.DataFrame, state: AnalysisState) -> go.Figure:
        """
        Create line chart for patent applications over time.

        Args:
            df: DataFrame with columns [year, application_count, invention_count]
            state: AnalysisState for title generation

        Returns:
            Plotly Figure with dual lines (applications solid, inventions dashed)
            X-axis: Years
            Y-axis: Count
            Title: "Patent Applications: {country} - {tech_field} ({year_start}-{year_end})"
        """
        ...

    @staticmethod
    def top_applicants_bar(df: pd.DataFrame, state: AnalysisState, limit: int = 10) -> go.Figure:
        """
        Create horizontal bar chart for top applicants.

        Args:
            df: DataFrame with columns [applicant_name, application_count, invention_count, country]
            state: AnalysisState for title generation
            limit: Number of applicants to show (default 10)

        Returns:
            Plotly Figure with horizontal bars
            Y-axis: Applicant names (truncated if >30 chars)
            X-axis: Application count
            Title: "Top {limit} Applicants: {country} - {tech_field}"
            Hover: Full name, count, country
        """
        ...

    @staticmethod
    def regional_bar(df: pd.DataFrame, state: AnalysisState) -> go.Figure:
        """
        Create bar chart for regional distribution.

        Args:
            df: DataFrame with columns [region, region_label, count]
            state: AnalysisState for title generation

        Returns:
            Plotly Figure with vertical bars
            X-axis: Region labels
            Y-axis: Application count
            Title: "Regional Distribution: {country} - {tech_field}"
        """
        ...

    @staticmethod
    def tech_treemap(df: pd.DataFrame, state: AnalysisState) -> go.Figure:
        """
        Create treemap for technology breakdown.

        Args:
            df: DataFrame with columns [ipc_class, ipc_label, count]
            state: AnalysisState for title generation

        Returns:
            Plotly Figure treemap
            Hierarchy: IPC classes sized by count
            Title: "Technology Breakdown: {country} ({year_start}-{year_end})"
            Labels visible in boxes
        """
        ...
```

#### Display Function

```python
def display_results(results: Dict[str, pd.DataFrame], state: AnalysisState):
    """
    Render all charts in Cell 6 output area.

    Args:
        results: Dict with keys 'trend', 'applicants', 'tech_breakdown', 'regional'
        state: AnalysisState for chart configuration

    Behavior:
        - Creates Output widget for each chart
        - Checks for empty DataFrames before rendering
        - Shows "No data available" message for empty results
        - Displays charts in vertical layout
        - Includes Top 10/25 toggle for applicants chart
    """
    ...
```

### Workflows and Sequencing

```
run_analysis() completes (Epic 3)
    │
    ▼
Store results in module-level analysis_results dict
    │
    ▼
Call display_results(results, state)
    │
    ├─► Check results['trend'] not empty
    │   └─► ChartBuilder.trend_line(results['trend'], state)
    │       └─► Display in Output widget
    │
    ├─► Check results['applicants'] not empty
    │   └─► ChartBuilder.top_applicants_bar(results['applicants'], state)
    │       └─► Display in Output widget
    │       └─► Add Top 10/25 dropdown (re-renders on change)
    │
    ├─► Check results['regional'] not empty AND len > 1
    │   └─► ChartBuilder.regional_bar(results['regional'], state)
    │       └─► Display in Output widget
    │   └─► Else: Show "Regional breakdown not available"
    │
    ├─► Check results['tech_breakdown'] not empty
    │   └─► ChartBuilder.tech_treemap(results['tech_breakdown'], state)
    │       └─► Display in Output widget
    │
    ▼
All charts rendered in Cell 6
```

## Non-Functional Requirements

### Performance

| Metric | Target | Measurement |
|--------|--------|-------------|
| Chart render time | <5 seconds per chart | Time from Figure creation to display |
| Total display time | <10 seconds | Time for all 4 charts to render |
| Interaction response | <500ms | Hover/zoom response time |
| Memory | <100MB | DataFrame + Figure memory footprint |

**Optimization Strategies:**
- Use plotly.graph_objects (go) over express for fine control
- Limit data points (trend: max ~25 years, applicants: top 10/25, regions: top 10, IPC: top 20)
- Disable animations for faster render
- Use efficient hover templates (not per-point customdata)

### Security

- Charts render from validated DataFrames (no injection risk)
- No user data persisted beyond session
- No external chart libraries (Plotly is TIP-provided)

### Reliability/Availability

- Empty DataFrame handling: Show message instead of crashing
- Missing columns: Graceful fallback with warning
- Figure creation errors: Catch and display error message
- Charts independent: One failure doesn't block others

### Observability

- Chart titles reflect exact query parameters
- Hover tooltips provide data transparency
- Zero-data warnings clearly indicate issue
- Console logging for debugging (optional)

## Dependencies and Integrations

### Python Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `plotly` | TIP-provided | Chart creation |
| `pandas` | TIP-provided | DataFrame operations |
| `ipywidgets` | TIP-provided | Output widgets, dropdown |

### Integration Points

- **Input**: DataFrames from Epic 3 `run_analysis()`
- **Input**: AnalysisState for titles and context
- **Output**: Plotly Figures displayed in Output widgets
- **Output**: Figures stored for Epic 5 PNG export

### PATSTAT Tables (Indirect)

Charts visualize data queried in Epic 3. No direct PATSTAT access in Epic 4.

## Acceptance Criteria (Authoritative)

### AC1: Trend Line Chart Rendering
- Given trend DataFrame with year, application_count, invention_count
- When ChartBuilder.trend_line(df, state) is called
- Then returns Plotly Figure with:
  - Dual lines (applications solid, inventions dashed)
  - X-axis: Years
  - Y-axis: Application count
  - Title includes country, tech field, date range
  - EPO Red (#C8102E) primary color
  - Hover shows exact values

### AC2: Top Applicants Bar Chart Rendering
- Given applicants DataFrame with name, count, country
- When ChartBuilder.top_applicants_bar(df, state, limit=10) is called
- Then returns Plotly Figure with:
  - Horizontal bars ordered largest at top
  - Y-axis: Applicant names (truncated >30 chars)
  - X-axis: Application count
  - Title includes country, tech field
  - Hover shows full name, count, country

### AC3: Top Applicants Limit Toggle
- Given Top Applicants chart displayed
- When user selects "Top 25" from dropdown
- Then chart re-renders with 25 applicants
- And toggle options are 10 / 25

### AC4: Regional Distribution Chart Rendering
- Given regional DataFrame with region_label, count
- When ChartBuilder.regional_bar(df, state) is called
- Then returns Plotly Figure with:
  - Vertical bars
  - X-axis: Region names
  - Y-axis: Application count
  - Title includes country, tech field

### AC5: Regional Data Unavailable Message
- Given regional DataFrame is empty OR has only 1 region
- When display_results() processes regional data
- Then displays: "Regional breakdown not available for this selection"
- And does not crash or show empty chart

### AC6: Technology Treemap Rendering
- Given tech_breakdown DataFrame with ipc_class, ipc_label, count
- When ChartBuilder.tech_treemap(df, state) is called
- Then returns Plotly Figure treemap with:
  - Boxes sized by count
  - Labels visible in boxes
  - EPO color palette
  - Title includes country, date range

### AC7: EPO Brand Styling
- Given any chart is rendered
- When user views the chart
- Then chart uses:
  - EPO Red (#C8102E) as primary color
  - Arial font family
  - Clean axis labels
  - Professional appearance suitable for presentations

### AC8: Chart Interactivity
- Given any chart is displayed
- When user hovers over data points
- Then tooltip shows relevant values
- And zoom/pan are enabled (for line/bar charts)

### AC9: Empty Data Handling
- Given a query returns empty DataFrame
- When display_results() processes that chart
- Then displays friendly message: "No data available for [chart name]"
- And other charts still render normally

### AC10: Dynamic Titles
- Given state with country="EP", tech_field=13, year_start=2019, year_end=2023
- When charts are rendered
- Then titles reflect these values:
  - Trend: "Patent Applications: EP - Medical technology (2019-2023)"
  - Applicants: "Top 10 Applicants: EP - Medical technology"
  - Regional: "Regional Distribution: EP - Medical technology"
  - Treemap: "Technology Breakdown: EP (2019-2023)"

## Traceability Mapping

| AC | PRD FR | Story | Component/API | Test Idea |
|----|--------|-------|---------------|-----------|
| AC1 | FR28-31 | 4.1 | `trend_line()` | Render with sample data, verify schema |
| AC2 | FR32-35 | 4.2 | `top_applicants_bar()` | Verify horizontal bars, truncation |
| AC3 | FR33 | 4.2 | Dropdown widget | Toggle between 10/25, verify re-render |
| AC4 | FR36-38 | 4.3 | `regional_bar()` | Render DE regions, verify labels |
| AC5 | FR12 | 4.3 | `display_results()` | Pass empty DataFrame, verify message |
| AC6 | FR39-41 | 4.4 | `tech_treemap()` | Render IPC breakdown, verify hierarchy |
| AC7 | UX Principles | 4.1-4.4 | `EPO_COLORS` | Visual inspection of colors, fonts |
| AC8 | FR30, FR35 | 4.1, 4.2 | Plotly config | Hover over chart, verify tooltip |
| AC9 | FR53 | 4.1-4.4 | Error handling | Pass empty DataFrames, verify messages |
| AC10 | FR31 | 4.1-4.4 | Title generation | Verify titles match state parameters |

## Risks, Assumptions, Open Questions

### Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Long applicant names overflow | Medium | Low | Truncate at 30 chars, full name in tooltip |
| Many IPC classes in treemap | Medium | Medium | Limit to top 20 IPC classes |
| TIP Plotly version limitations | Low | Medium | Use basic Plotly features, test on TIP |
| Chart render slow with large data | Low | Medium | Data already limited by Epic 3 queries |

### Assumptions

- Plotly is available and functional on TIP JupyterLab
- EPO color hex codes render correctly in Plotly
- Arial font is available in TIP environment
- Output widgets render Plotly figures correctly
- DataFrames from Epic 3 have consistent schema
- Users have modern browsers supporting Plotly interactivity

### Open Questions

1. **Q: Should dual-line trend chart be default or optional?**
   A: Default - shows both applications and inventions for richer insight.

2. **Q: How to handle very long German company names?**
   A: Truncate to 30 characters in chart, show full name in hover tooltip.

3. **Q: Should regional chart show all regions or top N?**
   A: Show top 10 regions if more than 10 exist, to keep chart readable.

4. **Q: Should treemap support click-to-drill-down?**
   A: Deferred to future enhancement. MVP shows flat IPC distribution.

## Test Strategy Summary

### Manual Testing on TIP

1. **Happy Path**: Run analysis for DE, Field 13 (Medical), 2019-2023
   - Verify trend chart shows dual lines
   - Verify top applicants shows 10 companies with German names
   - Verify regional chart shows DE NUTS regions (or unavailable message)
   - Verify treemap shows IPC breakdown

2. **Edge Cases**:
   - Single year: Trend chart with one point
   - Single applicant: Bar chart with one bar
   - Zero results: Verify "No data" messages
   - Very long applicant names: Verify truncation

3. **Styling Verification**:
   - EPO Red color visible on all charts
   - Fonts are Arial
   - Titles reflect selections
   - Professional appearance

4. **Interactivity Testing**:
   - Hover over data points
   - Zoom and pan on line/bar charts
   - Toggle Top 10/25 applicants

### Validation Approach

- Manual visual inspection per story acceptance criteria
- Compare against Architecture Visualization Pattern samples
- Test on TIP platform for compatibility

---

*Generated by BMAD Epic Tech Context Workflow*
*Date: 2026-01-12*
