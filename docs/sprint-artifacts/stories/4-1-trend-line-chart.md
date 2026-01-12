# Story 4.1: Trend Line Chart

Status: review

## Story

As a **PATLIB user**,
I want **to see patent applications over time as a line chart**,
so that **I can spot trends and patterns in innovation activity**.

## Acceptance Criteria

1. **AC1: Line Chart Rendering**
   - Given trend DataFrame with year, application_count, invention_count columns
   - When ChartBuilder.trend_line(df, state) is called
   - Then returns Plotly Figure with:
     - X-axis: Years
     - Y-axis: Application count
     - Line connecting data points

2. **AC2: Dual Line Display**
   - Given trend data is available
   - When chart renders
   - Then displays two lines:
     - Applications: solid line
     - Inventions/families: dashed line
   - And legend distinguishes both metrics

3. **AC3: EPO Brand Styling**
   - Given any trend chart is rendered
   - When user views the chart
   - Then chart uses:
     - EPO Red (#C8102E) as primary color
     - Arial font family
     - Clean axis labels
     - White background

4. **AC4: Dynamic Title**
   - Given state with country, tech_field, year_start, year_end
   - When chart renders
   - Then title shows: "Patent Applications: {country} - {tech_field_name} ({year_start}-{year_end})"
   - Example: "Patent Applications: EP - Medical technology (2019-2023)"

5. **AC5: Interactive Hover**
   - Given chart is displayed
   - When user hovers over data point
   - Then tooltip shows:
     - Year
     - Exact application count
     - Exact invention count

6. **AC6: Zoom/Pan Enabled**
   - Given chart is displayed
   - When user interacts with chart
   - Then zoom and pan are functional
   - And toolbar buttons visible

7. **AC7: Empty Data Handling**
   - Given trend DataFrame is empty
   - When display_results() processes chart
   - Then displays: "No trend data available for this selection"
   - And does not crash or show empty chart

8. **AC8: Single Year Handling**
   - Given trend DataFrame has only one year
   - When chart renders
   - Then displays single point with marker
   - And chart remains readable

## Tasks / Subtasks

- [x] **Task 1: Create ChartBuilder class foundation** (AC: 3)
  - [x] 1.1: Add ChartBuilder class to tip4patlibs_core.py
  - [x] 1.2: Define EPO_COLORS constant dict (#C8102E, #6D6E71, etc.)
  - [x] 1.3: Define EPO_PALETTE list for multi-series
  - [x] 1.4: Define EPO_LAYOUT dict (font_family, title_font_size)

- [x] **Task 2: Implement trend_line() method** (AC: 1, 2)
  - [x] 2.1: Create static method signature with df, state params
  - [x] 2.2: Add applications line (solid) with EPO Red
  - [x] 2.3: Add inventions line (dashed) with secondary color
  - [x] 2.4: Configure legend for both traces

- [x] **Task 3: Add styling and title** (AC: 3, 4)
  - [x] 3.1: Apply EPO_LAYOUT to figure
  - [x] 3.2: Generate dynamic title from state
  - [x] 3.3: Add helper to get tech field name from state.tech_field

- [x] **Task 4: Configure interactivity** (AC: 5, 6)
  - [x] 4.1: Set up hover template with year and counts
  - [x] 4.2: Enable zoom/pan (modebar)
  - [x] 4.3: Configure responsive layout

- [x] **Task 5: Add display_results() foundation** (AC: 7, 8)
  - [x] 5.1: Create display_results() function
  - [x] 5.2: Check for empty trend DataFrame
  - [x] 5.3: Display message if empty
  - [x] 5.4: Handle single data point case

- [x] **Task 6: Wire up to notebook** (AC: 1-8)
  - [x] 6.1: Call display_results() after run_analysis() completes
  - [x] 6.2: Pass analysis_results and state
  - [x] 6.3: Create Output widget in Cell 6

- [x] **Task 7: Validation** (AC: 1-8)
  - [x] 7.1: Test with EP + Field 13 + 2019-2023
  - [x] 7.2: Verify dual lines visible
  - [x] 7.3: Verify hover tooltips
  - [x] 7.4: Verify title reflects selections
  - [x] 7.5: Test with single year selection

## Dev Notes

### Learnings from Previous Story

**From Story 3-4-query-execution-progress (Status: done)**

- **Results Storage**: Query results stored in `analysis_results` dict:
  - `analysis_results['trend']` = DataFrame[year, application_count, invention_count]
  - Epic 4 visualizations consume from this dict
- **Pattern**: `_on_run_click()` method stores results after queries complete
- **Error Handling**: Empty DataFrame stored on query failure - check for empty before rendering
- **Module**: All code in `tip4patlibs_core.py`

[Source: docs/sprint-artifacts/3-4-query-execution-progress.md#Dev-Agent-Record]

### Architecture Notes

Per Architecture visualization pattern:
```python
EPO_COLORS = {
    'primary': '#C8102E',      # EPO Red
    'secondary': '#6D6E71',    # EPO Gray
}

class ChartBuilder:
    @staticmethod
    def trend_line(df, state) -> go.Figure:
        fig = px.line(df, x='year', y='application_count', ...)
        fig.update_layout(font_family="Arial", ...)
        return fig
```

### Implementation Approach

1. Add ChartBuilder class after PatstatQueries in module
2. Use plotly.graph_objects for fine control over dual lines
3. Generate title using ReferenceData for tech field name lookup
4. Wire display_results() call in _on_run_click() after queries complete

### Tech Field Name Lookup

To display "Medical technology" instead of "13":
```python
tech_name = reference_data.get_field_name(state.tech_field)
title = f"Patent Applications: {state.country} - {tech_name} ({state.year_start}-{state.year_end})"
```

### Project Structure Notes

- All chart code in `tip4patlibs_core.py` (per ADR-001)
- Import plotly.graph_objects and plotly.express at module level
- ChartBuilder is stateless (all static methods)

### References

- [Source: docs/sprint-artifacts/tech-spec-epic-4.md#AC1-Trend-Line-Chart]
- [Source: docs/epics.md#Story-4.1]
- [Source: docs/architecture.md#Visualization-Pattern]
- [Source: docs/PRD.md#FR28-31]

---

## Changelog

| Date | Author | Change |
|------|--------|--------|
| 2026-01-12 | SM (Bob) | Story drafted from tech-spec-epic-4.md and epics.md |
| 2026-01-12 | Dev (Amelia) | Implementation complete: ChartBuilder, trend_line(), display_results(), notebook wiring |

---

## Dev Agent Record

### Context Reference

- [stories/4-1-trend-line-chart.context.xml](4-1-trend-line-chart.context.xml)

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- Implementation follows Architecture visualization pattern with EPO brand constants
- Used plotly.graph_objects for fine control over dual lines
- Added _get_tech_field_name() helper for dynamic title generation
- Integrated display_results() into _on_run_click() callback

### Completion Notes List

- **AC1-AC2**: Implemented dual-line chart with applications (solid EPO Red) and inventions (dashed gray)
- **AC3**: EPO_COLORS, EPO_PALETTE, EPO_LAYOUT constants defined; Arial font, white background applied
- **AC4**: Dynamic title generated using _get_tech_field_name() helper method
- **AC5**: hovertemplate configured with year and formatted counts
- **AC6**: Plotly modebar enabled for zoom/pan interactivity
- **AC7**: display_results() shows "No trend data available" for empty DataFrames
- **AC8**: Single year data shows markers (mode='lines+markers')

### File List

| File | Action | Description |
|------|--------|-------------|
| tip4patlibs_core.py | Modified | Added EPO_COLORS, EPO_PALETTE, EPO_LAYOUT constants; Implemented ChartBuilder.trend_line(); Added display_results() function; Added chart_output() to WidgetFactory; Wired display into _on_run_click() |
| TIP_for_PATLIBs.ipynb | Modified | Updated Cell 6 (results-placeholder) to create chart output widget |
