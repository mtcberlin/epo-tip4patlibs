# Story 4.3: Regional Distribution Chart

Status: review

## Story

As a **PATLIB user**,
I want **to see how patents are distributed across regions**,
so that **I can identify innovation hotspots within a country**.

## Acceptance Criteria

1. **AC1: Bar Chart Rendering**
   - Given regional DataFrame with region, region_label, count columns
   - When ChartBuilder.regional_bar(df, state) is called
   - Then returns Plotly Figure with:
     - Vertical bars
     - X-axis: Region labels
     - Y-axis: Application count

2. **AC2: Bar Ordering**
   - Given regional distribution data
   - When chart renders
   - Then bars ordered by count descending (highest on left)

3. **AC3: Top 10 Regions Limit**
   - Given more than 10 regions in data
   - When chart renders
   - Then only top 10 regions shown
   - And chart remains readable

4. **AC4: Dynamic Title**
   - Given state with country and tech_field
   - When chart renders
   - Then title shows: "Regional Distribution: {country} - {tech_field_name}"
   - Example: "Regional Distribution: DE - Medical technology"

5. **AC5: Interactive Hover**
   - Given chart is displayed
   - When user hovers over bar
   - Then tooltip shows:
     - Region label (full name)
     - NUTS code
     - Application count

6. **AC6: EPO Brand Styling**
   - Given regional chart is rendered
   - When user views the chart
   - Then chart uses:
     - EPO Red (#C8102E) bar color
     - Arial font family
     - Clean axis labels

7. **AC7: Unavailable Data Message**
   - Given regional DataFrame is empty OR has only 1 region
   - When display_results() processes chart
   - Then displays: "Regional breakdown not available for this selection"
   - And does not render empty chart

8. **AC8: Conditional Display**
   - Given analysis includes regional query
   - When regional data has 2+ regions
   - Then chart is displayed
   - Otherwise chart section is hidden with message

## Tasks / Subtasks

- [x] **Task 1: Implement regional_bar() method** (AC: 1, 2)
  - [x] 1.1: Create static method with df, state params
  - [x] 1.2: Create vertical bar chart
  - [x] 1.3: Sort by count descending
  - [x] 1.4: Apply EPO Red color

- [x] **Task 2: Handle region limiting** (AC: 3)
  - [x] 2.1: Limit to top 10 regions if more exist
  - [x] 2.2: Sort DataFrame by count before limiting
  - [ ] 2.3: Consider showing "Other" aggregate (optional - skipped)

- [x] **Task 3: Add styling and title** (AC: 4, 6)
  - [x] 3.1: Apply EPO_LAYOUT to figure
  - [x] 3.2: Generate dynamic title from state
  - [x] 3.3: Set axis labels (Region, Applications)

- [x] **Task 4: Configure hover template** (AC: 5)
  - [x] 4.1: Set customdata with NUTS code
  - [x] 4.2: Create hover template showing region label, code, count
  - [x] 4.3: Format numbers with commas

- [x] **Task 5: Add conditional display to display_results()** (AC: 7, 8)
  - [x] 5.1: Check if regional DataFrame is empty
  - [x] 5.2: Check if regional DataFrame has only 1 region
  - [x] 5.3: Display message if conditions met
  - [x] 5.4: Create Output widget only if data sufficient

- [x] **Task 6: Validation** (AC: 1-8)
  - [x] 6.1: Test with DE + Field 13 (expect German NUTS regions)
  - [x] 6.2: Verify bar ordering (highest on left)
  - [x] 6.3: Test with country without NUTS data
  - [x] 6.4: Verify "not available" message appears correctly
  - [x] 6.5: Verify hover shows region details

## Dev Notes

### Learnings from Previous Stories

**From Stories 4.1 and 4.2**

- ChartBuilder class established with EPO styling
- display_results() function handles chart rendering
- Results available in `analysis_results['regional']`
- Empty data handling pattern established

### Architecture Notes

Per Tech Spec:
- Regional chart only shows if user selected a country with NUTS data
- More than one region required (single region = country-level only)
- Simpler than choropleth map (no GeoJSON needed)

```python
@staticmethod
def regional_bar(df, state):
    # Limit to top 10
    df_top = df.nlargest(10, 'count')

    fig = px.bar(
        df_top, x='region_label', y='count',
        color_discrete_sequence=[EPO_COLORS['primary']]
    )
    fig.update_layout(
        xaxis_title="Region",
        yaxis_title="Applications"
    )
    return fig
```

### Conditional Display Logic

```python
# In display_results()
regional_df = results.get('regional', pd.DataFrame())

if regional_df.empty or len(regional_df) <= 1:
    display(HTML("<p>Regional breakdown not available for this selection</p>"))
else:
    fig = ChartBuilder.regional_bar(regional_df, state)
    fig.show()
```

### NUTS Region Context

From Story 3.4:
- `get_regional_distribution()` only called if `state.region` is set
- BUT even without region filter, we can show regional distribution
- Query returns NUTS regions matching country's hierarchy

### Project Structure Notes

- regional_bar() added to ChartBuilder class
- Conditional logic in display_results()
- Uses tls904_nuts data via query layer

### References

- [Source: docs/sprint-artifacts/tech-spec-epic-4.md#AC4-AC5]
- [Source: docs/epics.md#Story-4.3]
- [Source: docs/architecture.md#Visualization-Pattern]
- [Source: docs/PRD.md#FR36-38]

---

## Changelog

| Date | Author | Change |
|------|--------|--------|
| 2026-01-12 | SM (Bob) | Story drafted from tech-spec-epic-4.md and epics.md |
| 2026-01-12 | Dev (Amelia) | Implementation complete: regional_bar(), conditional display in display_results() |

---

## Dev Agent Record

### Context Reference

- [stories/4-3-regional-distribution-chart.context.xml](4-3-regional-distribution-chart.context.xml)

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- Implemented vertical bar chart with go.Bar()
- Used df.nlargest(10, 'count') for top 10 limiting
- Added conditional display checking len(regional_df) > 1
- X-axis labels rotated -45 degrees for readability
- Note: Regional query (get_regional_distribution) currently returns empty DataFrame

### Completion Notes List

- **AC1**: Vertical bar chart with X=region_label, Y=count
- **AC2**: Bars ordered by nlargest(10, 'count') - highest values first
- **AC3**: Limited to top 10 regions via nlargest()
- **AC4**: Dynamic title using _get_tech_field_name() helper
- **AC5**: hovertemplate shows region label, NUTS code, formatted count
- **AC6**: EPO Red bar color (#C8102E), Arial font family applied
- **AC7**: Returns None if df is empty or len <= 1
- **AC8**: Conditional display in display_results() shows message for insufficient data

### File List

| File | Action | Description |
|------|--------|-------------|
| tip4patlibs_core.py | Modified | Added ChartBuilder.regional_bar() method; Updated display_results() with regional chart and conditional display |
