# Story 5.1: CSV Export

Status: drafted

## Story

As a **PATLIB user**,
I want **to export my analysis results as a CSV file**,
so that **I can use the data in Excel for further analysis or reporting**.

## Acceptance Criteria

1. **AC1: CSV Export Button**
   - Given analysis has completed with results
   - When display_results() renders
   - Then "Export CSV" button appears below charts
   - And button is styled consistently with UI

2. **AC2: CSV Format (European)**
   - Given user clicks "Export CSV"
   - When CSV is generated
   - Then file uses:
     - Semicolon (;) delimiter (European standard)
     - UTF-8 with BOM encoding (Excel compatibility)
     - No index column
     - Clear column headers

3. **AC3: CSV Content**
   - Given analysis results available
   - When CSV is exported
   - Then file contains:
     - Trend data (year, application_count, invention_count)
     - Top applicants data (name, counts, country)
   - And all German characters (umlauts) display correctly in Excel

4. **AC4: Descriptive Filename**
   - Given state with country=DE, tech_field=13, years 2019-2023
   - When CSV is exported
   - Then filename follows pattern: tip4patlibs_{country}_{tech}_{year_start}-{year_end}_{timestamp}.csv
   - Example: tip4patlibs_DE_field13_2019-2023_20260112_1430.csv

5. **AC5: Export Success Message**
   - Given CSV export completes successfully
   - When user views the interface
   - Then success message shows: "Exported to: {filename}"
   - And message is styled green/success

6. **AC6: Export Error Handling**
   - Given export fails (e.g., permission error)
   - When error occurs
   - Then clear error message displayed
   - And other functionality continues working
   - And user can retry export

## Tasks / Subtasks

- [ ] **Task 1: Implement Exporter.generate_filename()** (AC: 4)
  - [ ] 1.1: Create generate_filename() static method
  - [ ] 1.2: Build filename from state.country, tech_field/ipc, year_start, year_end
  - [ ] 1.3: Add timestamp component (YYYYMMDD_HHMM format)
  - [ ] 1.4: Handle IPC mode (use "ipc" instead of field number)
  - [ ] 1.5: Add optional chart_name parameter for PNG (Story 5.2)

- [ ] **Task 2: Implement Exporter.to_csv()** (AC: 2, 3)
  - [ ] 2.1: Create to_csv() static method
  - [ ] 2.2: Use pandas to_csv() with sep=';', encoding='utf-8-sig'
  - [ ] 2.3: Set index=False to exclude row numbers
  - [ ] 2.4: Call generate_filename() for output path
  - [ ] 2.5: Return full filepath for success message

- [ ] **Task 3: Combine DataFrames for export** (AC: 3)
  - [ ] 3.1: Create method to combine trend + applicants data
  - [ ] 3.2: Add section headers or separate sheets indicator
  - [ ] 3.3: Handle missing data (empty DataFrames)

- [ ] **Task 4: Create export button** (AC: 1, 5)
  - [ ] 4.1: Add create_export_buttons() function
  - [ ] 4.2: Create "Export CSV" button widget
  - [ ] 4.3: Style button with download icon
  - [ ] 4.4: Add click callback to trigger export
  - [ ] 4.5: Create success message HTML widget
  - [ ] 4.6: Display filename on success

- [ ] **Task 5: Integrate with display_results()** (AC: 1)
  - [ ] 5.1: Add export button row after charts in display_results()
  - [ ] 5.2: Pass analysis_results and state to create_export_buttons()
  - [ ] 5.3: Only show button if results not empty

- [ ] **Task 6: Error handling** (AC: 6)
  - [ ] 6.1: Wrap export in try/except
  - [ ] 6.2: Display user-friendly error message
  - [ ] 6.3: Log detailed error for debugging

- [ ] **Task 7: Validation** (AC: 1-6)
  - [ ] 7.1: Test export with DE + Field 13 data
  - [ ] 7.2: Open CSV in Excel, verify semicolon delimiter
  - [ ] 7.3: Verify umlauts display correctly
  - [ ] 7.4: Verify filename format
  - [ ] 7.5: Test export error handling

## Dev Notes

### Learnings from Previous Story

**From Story 4-4-technology-breakdown-treemap (Epic 4)**

- **ChartBuilder Pattern**: All chart methods are static, return Plotly Figures
- **Display Integration**: display_results() receives results dict and state
- **Module Structure**: All code in tip4patlibs_core.py per ADR-001
- **Widget Layout**: Use VBox/HBox for consistent layouts

### Architecture Notes

Per Architecture Export Pattern:
```python
class Exporter:
    @staticmethod
    def to_csv(df: pd.DataFrame, state: AnalysisState) -> str:
        filename = Exporter.generate_filename(state, 'csv')
        df.to_csv(
            filename,
            index=False,
            sep=';',                    # European standard
            encoding='utf-8-sig',       # UTF-8 with BOM for Excel
        )
        return filename
```

### CSV Format Rationale

- **Semicolon delimiter**: In Europe, comma is the decimal separator (3,14 not 3.14), so CSV uses semicolon
- **UTF-8 BOM**: Excel on Windows requires BOM to auto-detect UTF-8 encoding
- **No index**: Row numbers not useful for users

### Filename Format

```
tip4patlibs_{country}_{tech}_{year_start}-{year_end}_{timestamp}.csv

Components:
- country: 2-letter code (DE, EP, US, etc.)
- tech: "field{nr}" or "ipc" (e.g., field13, ipc)
- year_start-year_end: Date range (e.g., 2019-2023)
- timestamp: YYYYMMDD_HHMM (e.g., 20260112_1430)
```

### Integration Point

Export button appears after charts in display_results():
```python
def display_results(results, figures, state):
    # ... render charts ...

    # Add export buttons (Story 5.1, 5.2)
    export_row = create_export_buttons(results, figures, state)
    display(export_row)
```

### References

- [Source: docs/sprint-artifacts/tech-spec-epic-5.md#AC1-AC6]
- [Source: docs/architecture.md#Export-Pattern]
- [Source: docs/PRD.md#FR42-46]

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
