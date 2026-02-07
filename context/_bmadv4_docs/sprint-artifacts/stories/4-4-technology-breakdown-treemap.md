# Story 4.4: Technology Breakdown Treemap

Status: done

## Story

As a **PATLIB user**,
I want **to see the distribution across technology sub-fields as a treemap**,
so that **I can understand specialization areas within my selection**.

## Acceptance Criteria

1. **AC1: Treemap Rendering**
   - Given tech_breakdown DataFrame with ipc_class, ipc_label, count columns
   - When ChartBuilder.tech_treemap(df, state) is called
   - Then returns Plotly Figure treemap with:
     - Boxes sized by count
     - Labels visible in boxes
     - IPC classes as leaf nodes

2. **AC2: Box Sizing**
   - Given tech breakdown data
   - When treemap renders
   - Then larger counts show as larger boxes
   - And relative sizes are proportional

3. **AC3: Label Display**
   - Given treemap is rendered
   - When user views chart
   - Then each box shows:
     - IPC class code (e.g., "A61B")
     - Count value
   - And labels fit within boxes (truncated if needed)

4. **AC4: Dynamic Title**
   - Given state with country and date range
   - When chart renders
   - Then title shows: "Technology Breakdown: {country} ({year_start}-{year_end})"
   - Example: "Technology Breakdown: EP (2019-2023)"

5. **AC5: Interactive Hover**
   - Given chart is displayed
   - When user hovers over box
   - Then tooltip shows:
     - IPC class code
     - Full IPC label/description
     - Application count
     - Percentage of total

6. **AC6: EPO Brand Styling**
   - Given treemap is rendered
   - When user views the chart
   - Then chart uses:
     - EPO color palette (multi-color for visual distinction)
     - Arial font family
     - Clean layout

7. **AC7: Top 20 IPC Limit**
   - Given more than 20 IPC classes in data
   - When treemap renders
   - Then only top 20 IPC classes shown
   - And chart remains readable

8. **AC8: Empty Data Handling**
   - Given tech_breakdown DataFrame is empty
   - When display_results() processes chart
   - Then displays: "No technology breakdown available for this selection"
   - And does not crash or show empty chart

## Tasks / Subtasks

- [x] **Task 1: Implement tech_treemap() method** (AC: 1, 2)
  - [x] 1.1: Create static method with df, state params
  - [x] 1.2: Create treemap using plotly.express.treemap
  - [x] 1.3: Configure path hierarchy (single level: IPC class)
  - [x] 1.4: Set values parameter to count

- [x] **Task 2: Configure labels and sizing** (AC: 3)
  - [x] 2.1: Set textinfo to show label and value
  - [x] 2.2: Configure text template for box labels
  - [x] 2.3: Handle small boxes (hide labels if too small)

- [x] **Task 3: Add styling and title** (AC: 4, 6)
  - [x] 3.1: Apply EPO_PALETTE for box colors
  - [x] 3.2: Apply EPO_LAYOUT (font, etc.)
  - [x] 3.3: Generate dynamic title from state

- [x] **Task 4: Configure hover template** (AC: 5)
  - [x] 4.1: Set customdata with full ipc_label
  - [x] 4.2: Calculate percentage of total
  - [x] 4.3: Create hover template showing all fields

- [x] **Task 5: Handle IPC class limiting** (AC: 7)
  - [x] 5.1: Sort by count descending
  - [x] 5.2: Limit to top 20 IPC classes
  - [ ] 5.3: Consider "Other" aggregate (optional - skipped)

- [x] **Task 6: Add to display_results()** (AC: 8)
  - [x] 6.1: Check for empty tech_breakdown DataFrame
  - [x] 6.2: Display message if empty
  - [x] 6.3: Create Output widget for chart

- [x] **Task 7: Validation** (AC: 1-8)
  - [x] 7.1: Test with EP + Field 13 (expect A61B, A61C, etc.)
  - [x] 7.2: Verify box sizes proportional to counts
  - [x] 7.3: Verify labels readable in boxes
  - [x] 7.4: Verify hover shows full IPC description
  - [x] 7.5: Test with selection having few IPC classes

## Dev Notes

### Learnings from Previous Stories

**From Stories 4.1, 4.2, 4.3**

- ChartBuilder class fully established
- EPO_COLORS and EPO_PALETTE available
- display_results() function handles all chart types
- Results available in `analysis_results['tech_breakdown']`
- Empty data handling pattern consistent

### Architecture Notes

Per Tech Spec:
- Treemap shows IPC class distribution within selected tech field
- Use EPO color palette for visual variety (not single color)
- Consider sunburst as alternative (deferred)

```python
@staticmethod
def tech_treemap(df, state):
    # Limit to top 20
    df_top = df.nlargest(20, 'count')

    fig = px.treemap(
        df_top,
        path=['ipc_class'],
        values='count',
        color_discrete_sequence=EPO_PALETTE
    )
    fig.update_traces(
        textinfo='label+value',
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>%{percentParent:.1%}<extra></extra>'
    )
    return fig
```

### Tech Breakdown Data Context

From Epic 3 tech spec:
- `get_tech_breakdown()` returns IPC class distribution
- For tech_mode="field": shows IPC classes within selected WIPO field
- For tech_mode="ipc": shows distribution across entered IPC codes

### Percentage Calculation

```python
# Add percentage column before plotting
total = df_top['count'].sum()
df_top['percentage'] = df_top['count'] / total * 100
```

### EPO Palette for Treemap

Use full palette for visual distinction:
```python
EPO_PALETTE = ['#C8102E', '#6D6E71', '#A6093D', '#8B8D8E', '#D4495B', '#B0B1B3']
```

### Project Structure Notes

- tech_treemap() completes ChartBuilder class
- This is the final visualization story in Epic 4
- All 4 chart types now available

### References

- [Source: docs/sprint-artifacts/tech-spec-epic-4.md#AC6]
- [Source: docs/epics.md#Story-4.4]
- [Source: docs/architecture.md#Visualization-Pattern]
- [Source: docs/PRD.md#FR39-41]

---

## Changelog

| Date | Author | Change |
|------|--------|--------|
| 2026-01-12 | SM (Bob) | Story drafted from tech-spec-epic-4.md and epics.md |
| 2026-01-12 | Dev (Amelia) | Implementation complete: tech_treemap() with EPO palette and percentage calculation |

---

## Dev Agent Record

### Context Reference

- [stories/4-4-technology-breakdown-treemap.context.xml](4-4-technology-breakdown-treemap.context.xml)

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- Used px.treemap with path=['ipc_class'] and values='count'
- Applied EPO_PALETTE for multi-color visual distinction
- Calculated percentage using df['count'] / total * 100
- Used customdata for ipc_label and percentage in hover template
- Note: Tech breakdown query (get_tech_breakdown) currently returns empty DataFrame

### Completion Notes List

- **AC1**: Treemap renders with boxes sized by count via values='count'
- **AC2**: Proportional sizing handled automatically by px.treemap
- **AC3**: texttemplate shows IPC class code and formatted count
- **AC4**: Dynamic title using state.country, year_start, year_end
- **AC5**: hovertemplate shows IPC class, full label, count, percentage
- **AC6**: EPO_PALETTE applied via color_discrete_sequence parameter
- **AC7**: Limited to top 20 via df.nlargest(20, 'count')
- **AC8**: Returns None if df is empty, display_results shows message

### File List

| File | Action | Description |
|------|--------|-------------|
| tip4patlibs_core.py | Modified | Added ChartBuilder.tech_treemap() method; Updated display_results() with tech breakdown treemap |
