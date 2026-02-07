# Story 5.3: Zero Results & Data Quality Handling

Status: review

## Story

As a **PATLIB user**,
I want **to receive helpful guidance when my search returns no results and understand data limitations**,
so that **I can adjust my filters effectively and interpret results correctly**.

## Acceptance Criteria

1. **AC1: Zero Results Detection**
   - Given query returns empty DataFrames
   - When display_results() processes results
   - Then zero-results state is detected
   - And export buttons are hidden (nothing to export)

2. **AC2: Zero Results Message**
   - Given zero results detected
   - When message is displayed
   - Then clear heading: "No patents found for this selection"
   - And shows current filter summary
   - And is styled as info/warning (not error)

3. **AC3: Actionable Suggestions - Date Range**
   - Given zero results with narrow date range (3 years or less)
   - When suggestions are generated
   - Then includes: "Try expanding the date range (currently {n} years)"

4. **AC4: Actionable Suggestions - SME Filter**
   - Given zero results with SME filter enabled
   - When suggestions are generated
   - Then includes: "Try disabling the SME filter"

5. **AC5: Actionable Suggestions - Region**
   - Given zero results with region selected
   - When suggestions are generated
   - Then includes: "Try selecting 'All regions'"

6. **AC6: Actionable Suggestions - IPC Mode**
   - Given zero results with custom IPC codes
   - When suggestions are generated
   - Then includes: "Try using a WIPO Technology Field instead of custom IPC codes"

7. **AC7: Data Quality Warning Display**
   - Given any analysis completes with results (non-empty)
   - When results are displayed
   - Then data quality warning section appears below export buttons

8. **AC8: Warning Content (FR54)**
   - Given data quality warning is displayed
   - When user reads the content
   - Then it explains:
     - "Applicant names may appear multiple times with variations"
     - "Regional data coverage varies by country"
     - "Older patents may have incomplete classification data"

9. **AC9: Warning Collapsible**
   - Given data quality warning is displayed
   - When user first views results
   - Then warning section is collapsed by default
   - And has "Data Quality Notes" header to expand

10. **AC10: Warning Non-Intrusive**
    - Given data quality warning is displayed
    - When user views results
    - Then warning is:
      - Visually subtle (muted colors, small icon)
      - Does not obstruct charts
      - Easy to dismiss/ignore

## Tasks / Subtasks

- [x] **Task 1: Implement handle_zero_results()** (AC: 1, 2)
  - [x] 1.1: Create handle_zero_results(state) function
  - [x] 1.2: Build message header with emoji
  - [x] 1.3: Include state.summary() as current filter display
  - [x] 1.4: Style as warning box (yellow/amber background)
  - [x] 1.5: Return widgets.VBox with message

- [x] **Task 2: Implement suggestion generator** (AC: 3, 4, 5, 6)
  - [x] 2.1: Create _generate_suggestions(state) helper
  - [x] 2.2: Check year span (year_end - year_start + 1)
  - [x] 2.3: Check sme_filter flag
  - [x] 2.4: Check if region is selected
  - [x] 2.5: Check if tech_mode is 'ipc'
  - [x] 2.6: Build bullet list of applicable suggestions

- [x] **Task 3: Integrate zero results handling** (AC: 1)
  - [x] 3.1: Add check at start of display_results()
  - [x] 3.2: If all DataFrames empty, call handle_zero_results()
  - [x] 3.3: Skip chart rendering and export buttons
  - [x] 3.4: Return early after displaying message

- [x] **Task 4: Implement data_quality_warning()** (AC: 7, 8)
  - [x] 4.1: Create data_quality_warning() function
  - [x] 4.2: Build HTML content with 3 limitation points
  - [x] 4.3: Use info icon and muted styling
  - [x] 4.4: Return widgets.Accordion for collapsible behavior

- [x] **Task 5: Make warning collapsible** (AC: 9)
  - [x] 5.1: Wrap content in widgets.Accordion
  - [x] 5.2: Set selected_index=None for collapsed default
  - [x] 5.3: Title: "Data Quality Notes"

- [x] **Task 6: Style warning non-intrusively** (AC: 10)
  - [x] 6.1: Use light gray or info-blue background
  - [x] 6.2: Small font size
  - [x] 6.3: Info icon (not warning/error icon)
  - [x] 6.4: Minimal padding

- [x] **Task 7: Integrate into display_results()** (AC: 7)
  - [x] 7.1: Add data_quality_warning() call after export buttons
  - [x] 7.2: Only show if results are non-empty

- [x] **Task 8: Validation** (AC: 1-10)
  - [x] 8.1: Test with combination that returns zero results
  - [x] 8.2: Verify suggestions match filter state
  - [x] 8.3: Verify data quality warning appears with results
  - [x] 8.4: Verify warning is collapsed by default
  - [x] 8.5: Verify warning can be expanded

## Dev Notes

### Learnings from Previous Stories

**From Story 5-1 and 5-2**

- **display_results()**: Entry point for all result rendering
- **Widget layout**: Use VBox for vertical stacking
- **Message styling**: Use HTML widget with inline styles
- **Conditional display**: Check DataFrame.empty before rendering

### Zero Results Detection

Check if ALL DataFrames are empty:
```python
def _is_zero_results(results: dict) -> bool:
    trend_empty = results.get('trend', pd.DataFrame()).empty
    applicants_empty = results.get('applicants', pd.DataFrame()).empty
    # If both primary results are empty, treat as zero results
    return trend_empty and applicants_empty
```

### Suggestion Logic

```python
def _generate_suggestions(state: AnalysisState) -> List[str]:
    suggestions = []

    # Check date range
    year_span = state.year_end - state.year_start + 1
    if year_span <= 3:
        suggestions.append(f"Try expanding the date range (currently {year_span} years)")

    # Check SME filter
    if state.sme_filter:
        suggestions.append("Try disabling the SME filter")

    # Check region
    if state.region is not None:
        suggestions.append("Try selecting 'All regions'")

    # Check IPC mode
    if state.tech_mode == 'ipc':
        suggestions.append("Try using a WIPO Technology Field instead of custom IPC codes")

    return suggestions
```

### Data Quality Warning Content

From PRD FR54:
- Document applicant name normalization issues (same company appears multiple times)
- Document regional data coverage variations
- Document classification coverage for older patents

```html
<div style="background: #f8f9fa; padding: 10px; font-size: 0.9em; color: #666;">
  <b>Data Quality Notes</b>
  <ul>
    <li><b>Applicant names:</b> The same organization may appear multiple times
        under different name variations (e.g., "SIEMENS AG" vs "SIEMENS AKTIENGESELLSCHAFT")</li>
    <li><b>Regional data:</b> NUTS region data coverage varies by country.
        Some countries may have limited or no regional attribution.</li>
    <li><b>Classifications:</b> Older patents (pre-2000) may have incomplete
        IPC/CPC classification data.</li>
  </ul>
</div>
```

### Collapsible Widget Pattern

```python
from ipywidgets import Accordion, HTML

def data_quality_warning():
    content = HTML(value='''
        <ul style="margin: 0; padding-left: 20px; color: #666;">
            <li>...</li>
        </ul>
    ''')

    accordion = Accordion(children=[content], titles=['Data Quality Notes'])
    accordion.selected_index = None  # Collapsed by default
    return accordion
```

### Integration Point

```python
def display_results(results, state):
    # Check for zero results FIRST
    if _is_zero_results(results):
        display(handle_zero_results(state))
        return  # Don't render charts or export buttons

    # ... render charts ...

    # Add export buttons
    display(create_export_buttons(results, figures, state))

    # Add data quality warning (collapsed)
    display(data_quality_warning())
```

### References

- [Source: docs/sprint-artifacts/tech-spec-epic-5.md#AC12-AC16]
- [Source: docs/PRD.md#FR52-55]

---

## Changelog

| Date | Author | Change |
|------|--------|--------|
| 2026-01-12 | SM (Bob) | Story drafted from tech-spec-epic-5.md |
| 2026-01-12 | Dev (Amelia) | Implementation complete: Zero results handling and data quality warning |

---

## Dev Agent Record

### Context Reference

- [stories/5-3-zero-results-data-quality-handling.context.xml](5-3-zero-results-data-quality-handling.context.xml)

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- Implemented _is_zero_results() to check if trend and applicants DataFrames are empty
- Implemented _generate_suggestions() with 4 contextual suggestions based on state
- Created handle_zero_results() with amber warning box and filter summary
- Created data_quality_warning() as collapsible Accordion widget
- Integrated both functions into display_results()

### Completion Notes List

- **AC1**: _is_zero_results() checks both trend and applicants DataFrames
- **AC2**: handle_zero_results() displays clear heading with current filter summary
- **AC3**: Suggestion for date range when span <= 3 years
- **AC4**: Suggestion to disable SME filter if enabled
- **AC5**: Suggestion for "All regions" if region selected
- **AC6**: Suggestion for WIPO field if using custom IPC codes
- **AC7**: data_quality_warning() displayed after export buttons when results exist
- **AC8**: Warning content explains name variations, regional coverage, and classification issues
- **AC9**: Accordion with selected_index=None for collapsed default
- **AC10**: Light gray background (#f8f9fa), small font, info icon

### File List

| File | Action | Description |
|------|--------|-------------|
| tip4patlibs_core.py | Modified | Added _is_zero_results(), _generate_suggestions(), handle_zero_results(), data_quality_warning(); Integrated into display_results() |
