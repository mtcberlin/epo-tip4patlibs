# Story 4.2: Top Applicants Bar Chart

Status: review

## Story

As a **PATLIB user**,
I want **to see top applicants as a horizontal bar chart**,
so that **I can quickly identify leading innovators in my selection**.

## Acceptance Criteria

1. **AC1: Horizontal Bar Chart Rendering**
   - Given applicants DataFrame with applicant_name, application_count, invention_count, country
   - When ChartBuilder.top_applicants_bar(df, state, limit=10) is called
   - Then returns Plotly Figure with:
     - Horizontal bars
     - Y-axis: Applicant names
     - X-axis: Application count

2. **AC2: Bar Ordering**
   - Given top applicants data
   - When chart renders
   - Then bars ordered with largest at top
   - And smallest at bottom

3. **AC3: Name Truncation**
   - Given applicant names longer than 30 characters
   - When chart renders
   - Then names truncated to 30 chars with "..."
   - And full name shown in hover tooltip

4. **AC4: Dynamic Title**
   - Given state with country and tech_field
   - When chart renders
   - Then title shows: "Top {limit} Applicants: {country} - {tech_field_name}"
   - Example: "Top 10 Applicants: EP - Medical technology"

5. **AC5: Interactive Hover**
   - Given chart is displayed
   - When user hovers over bar
   - Then tooltip shows:
     - Full applicant name (untruncated)
     - Application count
     - Invention count
     - Country code

6. **AC6: Top 10/25 Toggle**
   - Given Top Applicants chart displayed
   - When user selects "Top 25" from dropdown
   - Then chart re-renders with 25 applicants
   - And toggle options are 10 / 25

7. **AC7: EPO Brand Styling**
   - Given any applicants chart is rendered
   - When user views the chart
   - Then chart uses:
     - EPO Red (#C8102E) bar color
     - Arial font family
     - Clean axis labels

8. **AC8: Empty Data Handling**
   - Given applicants DataFrame is empty
   - When display_results() processes chart
   - Then displays: "No applicant data available for this selection"
   - And does not crash or show empty chart

## Tasks / Subtasks

- [x] **Task 1: Implement top_applicants_bar() method** (AC: 1, 2)
  - [x] 1.1: Create static method with df, state, limit params
  - [x] 1.2: Create horizontal bar chart with orientation='h'
  - [x] 1.3: Configure yaxis categoryorder='total ascending' for largest at top
  - [x] 1.4: Apply EPO Red color

- [x] **Task 2: Handle name truncation** (AC: 3)
  - [x] 2.1: Create truncate helper function (30 chars + "...")
  - [x] 2.2: Apply truncation to y-axis labels
  - [x] 2.3: Store full names for hover

- [x] **Task 3: Add styling and title** (AC: 4, 7)
  - [x] 3.1: Apply EPO_LAYOUT to figure
  - [x] 3.2: Generate dynamic title from state and limit
  - [x] 3.3: Set axis labels (Applications, empty for y)

- [x] **Task 4: Configure hover template** (AC: 5)
  - [x] 4.1: Set customdata with full name, invention_count, country
  - [x] 4.2: Create hover template showing all fields
  - [x] 4.3: Format numbers with commas

- [x] **Task 5: Create limit toggle widget** (AC: 6)
  - [x] 5.1: Add Dropdown widget with options [10, 25]
  - [x] 5.2: Create on_change callback to re-render chart
  - [x] 5.3: Position toggle above/beside chart

- [x] **Task 6: Add to display_results()** (AC: 8)
  - [x] 6.1: Check for empty applicants DataFrame
  - [x] 6.2: Display message if empty
  - [x] 6.3: Create Output widget for chart
  - [x] 6.4: Wire up toggle to Output widget

- [x] **Task 7: Validation** (AC: 1-8)
  - [x] 7.1: Test with EP + Field 13 (expect well-known companies)
  - [x] 7.2: Verify bar ordering (largest at top)
  - [x] 7.3: Test toggle between 10 and 25
  - [x] 7.4: Verify long German company names truncated
  - [x] 7.5: Verify hover shows full details

## Dev Notes

### Learnings from Previous Story

**From Story 4-1 (if completed) or Story 3-4**

- ChartBuilder class foundation established in Story 4.1
- EPO_COLORS and EPO_LAYOUT constants defined
- display_results() function created
- Results available in `analysis_results['applicants']`

### Architecture Notes

Per Architecture visualization pattern:
```python
@staticmethod
def top_applicants_bar(df, state, limit=10):
    df_top = df.head(limit)
    fig = px.bar(
        df_top, x='application_count', y='applicant_name',
        orientation='h',
        color_discrete_sequence=[EPO_COLORS['primary']]
    )
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        xaxis_title="Applications",
        yaxis_title=""
    )
    return fig
```

### Name Truncation Pattern

German company names can be very long:
```python
def truncate_name(name, max_length=30):
    if len(name) > max_length:
        return name[:max_length-3] + "..."
    return name

# Apply to DataFrame copy before plotting
df_display = df.copy()
df_display['display_name'] = df_display['applicant_name'].apply(truncate_name)
```

### Toggle Widget Pattern

```python
limit_dropdown = widgets.Dropdown(
    options=[('Top 10', 10), ('Top 25', 25)],
    value=10,
    description='Show:'
)

def on_limit_change(change):
    with applicants_output:
        applicants_output.clear_output()
        fig = ChartBuilder.top_applicants_bar(
            analysis_results['applicants'], state, limit=change['new']
        )
        fig.show()

limit_dropdown.observe(on_limit_change, names='value')
```

### Project Structure Notes

- top_applicants_bar() added to ChartBuilder class
- Toggle widget created in display_results() function
- Uses Output widget for dynamic re-rendering

### References

- [Source: docs/sprint-artifacts/tech-spec-epic-4.md#AC2-AC3]
- [Source: docs/epics.md#Story-4.2]
- [Source: docs/architecture.md#Visualization-Pattern]
- [Source: docs/PRD.md#FR32-35]

---

## Changelog

| Date | Author | Change |
|------|--------|--------|
| 2026-01-12 | SM (Bob) | Story drafted from tech-spec-epic-4.md and epics.md |
| 2026-01-12 | Dev (Amelia) | Implementation complete: top_applicants_bar(), truncate_name(), toggle widget |

---

## Dev Agent Record

### Context Reference

- [stories/4-2-top-applicants-bar-chart.context.xml](4-2-top-applicants-bar-chart.context.xml)

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- Implemented horizontal bar chart with go.Bar(orientation='h')
- Used categoryorder='total ascending' for largest-at-top ordering
- Added truncate_name() helper for 30-char name truncation
- Created Top 10/25 Dropdown toggle with re-render callback
- Integrated into display_results() with nested Output widget

### Completion Notes List

- **AC1**: Horizontal bar chart with Y=applicant names, X=application count
- **AC2**: Bars ordered with categoryorder='total ascending' for largest at top
- **AC3**: truncate_name() helper truncates to 30 chars; full name in customdata for hover
- **AC4**: Dynamic title using _get_tech_field_name() helper
- **AC5**: hovertemplate shows full name, application_count, invention_count, country
- **AC6**: Dropdown widget with observe callback re-renders chart on limit change
- **AC7**: EPO Red bar color (#C8102E), Arial font family applied
- **AC8**: Empty DataFrame check returns None, display_results shows message

### File List

| File | Action | Description |
|------|--------|-------------|
| tip4patlibs_core.py | Modified | Added truncate_name() helper; Added ChartBuilder.top_applicants_bar() method; Updated display_results() with applicants chart and toggle widget; Added truncate_name to exports |
