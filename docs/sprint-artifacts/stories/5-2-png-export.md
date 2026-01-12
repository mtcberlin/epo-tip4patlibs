# Story 5.2: PNG Export

Status: drafted

## Story

As a **PATLIB user**,
I want **to export my charts as PNG images**,
so that **I can include them in presentations and reports**.

## Acceptance Criteria

1. **AC1: PNG Export Button**
   - Given analysis has completed with charts
   - When display_results() renders
   - Then "Export Charts (PNG)" button appears next to CSV button
   - And button is styled with image/camera icon

2. **AC2: PNG Quality**
   - Given user clicks "Export Charts (PNG)"
   - When PNGs are generated
   - Then images are:
     - 2x scale for high DPI (presentation quality)
     - Clean white background
     - Suitable for printing/presentations
     - At least 1200px wide

3. **AC3: PNG Filenames**
   - Given state with country=EP, tech_field=13, years 2019-2023
   - When charts are exported
   - Then each filename includes chart name:
     - tip4patlibs_EP_field13_2019-2023_20260112_1430_trend.png
     - tip4patlibs_EP_field13_2019-2023_20260112_1430_applicants.png
     - tip4patlibs_EP_field13_2019-2023_20260112_1430_tech_breakdown.png
     - tip4patlibs_EP_field13_2019-2023_20260112_1430_regional.png

4. **AC4: Multiple Chart Export**
   - Given 3-4 charts are displayed
   - When "Export Charts" is clicked
   - Then all visible charts are exported as separate PNGs
   - And success message lists all exported files

5. **AC5: Export Success Message**
   - Given PNG export completes successfully
   - When user views the interface
   - Then success message shows: "Exported {n} charts to: {path}"
   - And lists filenames of exported charts

6. **AC6: Graceful Fallback**
   - Given kaleido/orca not installed on TIP
   - When PNG export is attempted
   - Then helpful message displayed: "PNG export requires kaleido package"
   - And suggests: "Use browser's screenshot function as alternative"
   - And no crash or error

## Tasks / Subtasks

- [ ] **Task 1: Implement Exporter.to_png()** (AC: 2, 3)
  - [ ] 1.1: Create to_png() static method
  - [ ] 1.2: Use fig.write_image() with scale=2 for high DPI
  - [ ] 1.3: Set format='png', engine='kaleido'
  - [ ] 1.4: Call generate_filename() with chart_name parameter
  - [ ] 1.5: Return full filepath for success message

- [ ] **Task 2: Add kaleido availability check** (AC: 6)
  - [ ] 2.1: Create _check_kaleido_available() helper
  - [ ] 2.2: Try import kaleido and catch ImportError
  - [ ] 2.3: Cache result for performance

- [ ] **Task 3: Implement export_all_charts()** (AC: 4, 5)
  - [ ] 3.1: Create export_all_charts(figures, state) function
  - [ ] 3.2: Iterate over figures dict
  - [ ] 3.3: Skip None figures (e.g., no regional data)
  - [ ] 3.4: Collect exported filepaths
  - [ ] 3.5: Return list of filepaths

- [ ] **Task 4: Create PNG export button** (AC: 1)
  - [ ] 4.1: Add PNG button to create_export_buttons()
  - [ ] 4.2: Style with image/camera icon
  - [ ] 4.3: Add click callback to trigger export
  - [ ] 4.4: Handle success/error display

- [ ] **Task 5: Graceful fallback handling** (AC: 6)
  - [ ] 5.1: Check kaleido before export attempt
  - [ ] 5.2: If unavailable, show helpful message widget
  - [ ] 5.3: Suggest screenshot alternative
  - [ ] 5.4: Keep button visible but explain limitation

- [ ] **Task 6: Validation** (AC: 1-6)
  - [ ] 6.1: Test PNG export on TIP
  - [ ] 6.2: Open PNGs, verify quality (2x scale)
  - [ ] 6.3: Verify all 4 chart types export
  - [ ] 6.4: Verify filename format includes chart name
  - [ ] 6.5: Test fallback message if kaleido missing

## Dev Notes

### Learnings from Previous Story

**From Story 5-1-csv-export**

- **Exporter class**: Already has generate_filename() method
- **Button pattern**: create_export_buttons() returns HBox with buttons
- **Success message**: Use HTML widget styled green
- **Error handling**: Wrap in try/except, show user-friendly message

### Architecture Notes

Per Architecture Export Pattern:
```python
@staticmethod
def to_png(fig, state: AnalysisState, chart_name: str) -> str:
    filename = Exporter.generate_filename(state, 'png').replace('.png', f'_{chart_name}.png')
    fig.write_image(filename, scale=2)  # 2x for high DPI
    return filename
```

### Plotly Static Export

Plotly supports multiple static image export engines:
1. **kaleido** (recommended): Pure Python, pip-installable
2. **orca**: Electron-based, requires separate install

Check availability:
```python
def _check_kaleido_available():
    try:
        import kaleido
        return True
    except ImportError:
        return False
```

### Scale Factor

- scale=1: Standard resolution (~72 DPI)
- scale=2: High DPI (~144 DPI, recommended for presentations)
- scale=3: Ultra-high DPI (larger files)

### Figures Dict Structure

From Epic 4 display_results():
```python
figures = {
    'trend': go.Figure,           # Always present
    'applicants': go.Figure,      # Always present
    'tech_breakdown': go.Figure,  # Always present (may be empty treemap)
    'regional': go.Figure or None  # Only if regional data available
}
```

### Fallback Message Content

```python
def _show_png_fallback():
    return widgets.HTML(
        value='''
        <div style="background: #fff3cd; padding: 10px; border-radius: 5px;">
            <b>PNG export not available</b><br>
            The kaleido package is not installed on this system.<br><br>
            <b>Alternative:</b> Use your browser's screenshot function
            (Cmd+Shift+4 on Mac, Win+Shift+S on Windows) to capture charts.
        </div>
        '''
    )
```

### References

- [Source: docs/sprint-artifacts/tech-spec-epic-5.md#AC7-AC11]
- [Source: docs/architecture.md#Export-Pattern]
- [Source: docs/PRD.md#FR44-46]

---

## Changelog

| Date | Author | Change |
|------|--------|--------|
| 2026-01-12 | SM (Bob) | Story drafted from tech-spec-epic-5.md |

---

## Dev Agent Record

### Context Reference

Pending story context generation

### Agent Model Used

Pending implementation

### Debug Log References

### Completion Notes List

### File List
