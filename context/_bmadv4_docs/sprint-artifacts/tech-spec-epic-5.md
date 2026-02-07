# Epic Technical Specification: Export & Polish

Date: 2026-01-12
Author: Bob (SM)
Epic ID: 5
Status: Draft

---

## Overview

Epic 5 completes the TIP for PATLIBs analysis workflow by implementing export functionality and data quality handling. Users can export their analysis results as CSV files (European format with semicolon delimiter) and chart images as PNG files (high-resolution for presentations). The epic also implements graceful zero-results handling with actionable suggestions and data quality warnings.

The Exporter class centralizes all export logic, generating descriptive filenames that reflect the analysis parameters (country, technology, date range). Export buttons appear in the results cell after analysis completes, providing one-click download capability.

## Objectives and Scope

### In Scope

- Exporter class with CSV and PNG export methods
- CSV export: semicolon delimiter, UTF-8 BOM for Excel compatibility
- PNG export: high-resolution charts (2x scale) for presentations
- Descriptive filename generation based on AnalysisState
- Export buttons in results cell with download links
- Zero results message with actionable suggestions
- Data quality warnings for known PATSTAT limitations
- Integration with ChartBuilder output (Epic 4)

### Out of Scope

- Excel (.xlsx) export (deferred - CSV sufficient for MVP)
- PDF report generation (future enhancement)
- Batch export of multiple analyses (future enhancement)
- Email/share functionality (future enhancement)
- Custom filename input by users (use generated names)

## System Architecture Alignment

### Components Referenced

| Component | Purpose | Source |
|-----------|---------|--------|
| `Exporter` | Export utility class | Architecture - Export Pattern |
| `ChartBuilder` | Source of Plotly Figures | Epic 4 |
| `AnalysisState` | Filename parameters | Epic 1 / ADR-006 |
| `analysis_results` | DataFrames to export | Epic 3 / Story 3.4 |
| `display_results()` | Integration point | Epic 4 |

### Architecture Constraints

- **ADR-001**: Exporter class lives in `tip4patlibs_core.py` module
- **NFR7**: Export functionality works consistently across supported data sizes
- **NFR11**: CSVs compatible with Excel (proper encoding, delimiters)
- **European Format**: Semicolon delimiter for CSV (comma is decimal separator in Europe)
- **UTF-8 BOM**: Required for Excel to recognize UTF-8 encoding

## Detailed Design

### Services and Modules

| Component | Responsibility | Inputs | Outputs |
|-----------|----------------|--------|---------|
| `Exporter.generate_filename(state, ext, chart_name)` | Create descriptive filename | AnalysisState, extension, chart_name | str (filename) |
| `Exporter.to_csv(df, state)` | Export DataFrame to CSV | DataFrame, AnalysisState | str (filepath) |
| `Exporter.to_png(fig, state, chart_name)` | Export Plotly figure to PNG | Figure, AnalysisState, chart_name | str (filepath) |
| `create_export_buttons(results, figures, state)` | Create export UI | results dict, figures dict, state | widgets.HBox |
| `handle_zero_results(state)` | Show helpful message | AnalysisState | widgets.HTML |
| `data_quality_warning()` | Show PATSTAT limitations | None | widgets.HTML |

### Data Models and Contracts

#### Input: Analysis Results (from Epic 3/4)

```python
# analysis_results dict structure
{
    'trend': pd.DataFrame,        # year, application_count, invention_count
    'applicants': pd.DataFrame,   # applicant_name, application_count, invention_count, country
    'tech_breakdown': pd.DataFrame,  # ipc_class, ipc_label, count
    'regional': pd.DataFrame      # region, region_label, count
}

# figures dict structure (from display_results in Epic 4)
{
    'trend': go.Figure,
    'applicants': go.Figure,
    'tech_breakdown': go.Figure,
    'regional': go.Figure  # May be None if no regional data
}
```

#### Output: Export Files

**CSV Format:**
```
applicant_name;application_count;invention_count;country
SIEMENS AG;523;412;DE
ROBERT BOSCH GMBH;498;387;DE
```

**Filename Convention:**
```
tip4patlibs_{country}_{tech}_{year_start}-{year_end}_{timestamp}.csv
tip4patlibs_{country}_{tech}_{year_start}-{year_end}_{timestamp}_{chart_name}.png

Examples:
tip4patlibs_DE_field13_2019-2023_20260112_1430.csv
tip4patlibs_DE_field13_2019-2023_20260112_1430_trend.png
tip4patlibs_EP_ipc_2019-2023_20260112_1430_applicants.png
```

### APIs and Interfaces

#### Exporter Class

```python
from pathlib import Path
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go

class Exporter:
    """CSV and PNG export with consistent naming and European formatting."""

    @staticmethod
    def generate_filename(state: AnalysisState, extension: str, chart_name: str = None) -> str:
        """
        Generate descriptive filename based on analysis parameters.

        Args:
            state: AnalysisState with country, tech_field/ipc_codes, year range
            extension: File extension ('csv' or 'png')
            chart_name: Optional chart identifier for PNG exports ('trend', 'applicants', etc.)

        Returns:
            Filename string (not full path)

        Example:
            >>> Exporter.generate_filename(state, 'csv')
            'tip4patlibs_DE_field13_2019-2023_20260112_1430.csv'
        """
        ...

    @staticmethod
    def to_csv(df: pd.DataFrame, state: AnalysisState, data_type: str = 'data') -> str:
        """
        Export DataFrame to CSV with European formatting.

        Args:
            df: DataFrame to export
            state: AnalysisState for filename generation
            data_type: Type identifier for filename ('trend', 'applicants', etc.)

        Returns:
            Full path to exported file

        Format:
            - Separator: semicolon (;)
            - Encoding: UTF-8 with BOM (utf-8-sig)
            - No index column

        Example:
            >>> filepath = Exporter.to_csv(trend_df, state, 'trend')
            >>> print(filepath)
            '/home/user/tip4patlibs_DE_field13_2019-2023_20260112_1430_trend.csv'
        """
        ...

    @staticmethod
    def to_png(fig: go.Figure, state: AnalysisState, chart_name: str) -> str:
        """
        Export Plotly figure to PNG with high resolution.

        Args:
            fig: Plotly Figure object
            state: AnalysisState for filename generation
            chart_name: Chart identifier ('trend', 'applicants', 'tech_breakdown', 'regional')

        Returns:
            Full path to exported file

        Format:
            - Scale: 2x for high DPI (presentation quality)
            - Format: PNG

        Note:
            Requires kaleido or orca for Plotly static export.
            Falls back gracefully if not available.

        Example:
            >>> filepath = Exporter.to_png(trend_fig, state, 'trend')
            >>> print(filepath)
            '/home/user/tip4patlibs_DE_field13_2019-2023_20260112_1430_trend.png'
        """
        ...
```

#### Export UI Functions

```python
def create_export_buttons(
    results: Dict[str, pd.DataFrame],
    figures: Dict[str, go.Figure],
    state: AnalysisState
) -> widgets.HBox:
    """
    Create export buttons for CSV and PNG downloads.

    Args:
        results: Dict of DataFrames from analysis
        figures: Dict of Plotly Figures from ChartBuilder
        state: AnalysisState for filename generation

    Returns:
        HBox containing export buttons with download functionality

    Buttons:
        - "Export CSV" - Exports all data to single CSV
        - "Export Charts (PNG)" - Exports all charts as PNG files

    Behavior:
        - Shows success message with filename after export
        - Handles export errors gracefully with message
        - Creates download links in Jupyter environment
    """
    ...

def handle_zero_results(state: AnalysisState) -> widgets.HTML:
    """
    Display helpful message when analysis returns no results.

    Args:
        state: AnalysisState with current filter parameters

    Returns:
        HTML widget with message and suggestions

    Message includes:
        - Clear "No results found" indication
        - Current filter summary
        - Specific suggestions based on state:
          - If narrow date range: "Try expanding date range"
          - If custom IPC: "Try broader IPC codes"
          - If SME filter on: "Try disabling SME filter"
          - If region selected: "Try 'All regions'"
    """
    ...

def data_quality_warning() -> widgets.HTML:
    """
    Display PATSTAT data quality limitations (FR54).

    Returns:
        HTML widget with collapsible data quality notes

    Content:
        - Applicant name normalization limitations
        - Regional data coverage variations
        - Classification coverage for older patents
    """
    ...
```

### Workflows and Sequencing

```
run_analysis() completes (Epic 3)
    │
    ▼
display_results() renders charts (Epic 4)
    │
    ├─► Check if all DataFrames empty
    │   └─► Yes: handle_zero_results(state)
    │             └─► Display message with suggestions (FR53, FR55)
    │   └─► No: Continue
    │
    ├─► Store figures dict from ChartBuilder
    │
    ├─► create_export_buttons(results, figures, state)
    │   └─► Display export buttons below charts
    │
    └─► data_quality_warning()
        └─► Display collapsible warning (FR54)

User clicks "Export CSV"
    │
    ▼
Exporter.to_csv(combined_df, state)
    │
    ├─► Generate filename
    ├─► Write CSV with semicolon delimiter, UTF-8 BOM
    ├─► Show success message with filepath
    └─► Create download link (if Jupyter supports)

User clicks "Export Charts (PNG)"
    │
    ▼
For each figure in figures dict:
    │
    ├─► Exporter.to_png(fig, state, chart_name)
    │   ├─► Check kaleido/orca availability
    │   ├─► Generate filename
    │   └─► Write PNG at 2x scale
    │
    └─► Show success message with filepaths
```

## Non-Functional Requirements

### Performance

| Metric | Target | Measurement |
|--------|--------|-------------|
| CSV export time | <2 seconds | For typical result sizes (<10k rows) |
| PNG export time | <5 seconds per chart | Including figure rendering |
| Total export time | <15 seconds | All 4 charts + CSV |

### Security

- No sensitive data in filenames
- Files written to user's workspace only
- No external upload functionality

### Reliability/Availability

- CSV export always works (pandas core functionality)
- PNG export graceful fallback if kaleido unavailable
- Clear error messages for any export failures
- Partial export succeeds if some charts fail

### Observability

- Success/failure messages for each export
- Filepath displayed after export
- File size indication (optional)

## Dependencies and Integrations

### Python Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `pandas` | TIP-provided | DataFrame to CSV |
| `plotly` | TIP-provided | Figure.write_image() |
| `kaleido` | TIP-provided (if available) | Static image export |
| `ipywidgets` | TIP-provided | Export buttons |

### Integration Points

- **Input**: analysis_results dict from Story 3.4
- **Input**: Plotly Figures from Epic 4 ChartBuilder
- **Input**: AnalysisState for filename parameters
- **Output**: CSV files in user workspace
- **Output**: PNG files in user workspace

## Acceptance Criteria (Authoritative)

### Story 5-1: CSV Export

#### AC1: CSV Export Button
- Given analysis has completed with results
- When display_results() renders
- Then "Export CSV" button appears below charts

#### AC2: CSV Format (European)
- Given user clicks "Export CSV"
- When CSV is generated
- Then file uses:
  - Semicolon (;) delimiter
  - UTF-8 with BOM encoding
  - No index column

#### AC3: CSV Content
- Given analysis results available
- When CSV is exported
- Then file contains:
  - Clear column headers
  - All data from trend DataFrame
  - Top applicants data (Top 25)

#### AC4: Descriptive Filename
- Given state with country=DE, tech_field=13, years 2019-2023
- When CSV is exported
- Then filename is like: tip4patlibs_DE_field13_2019-2023_20260112_1430.csv

#### AC5: Export Success Message
- Given CSV export completes
- When user views the interface
- Then success message shows filename/path
- And download link is provided (if supported)

#### AC6: Export Error Handling
- Given export fails (e.g., disk full)
- When error occurs
- Then clear error message displayed
- And other functionality continues working

### Story 5-2: PNG Export

#### AC7: PNG Export Button
- Given analysis has completed with charts
- When display_results() renders
- Then "Export Charts (PNG)" button appears below charts

#### AC8: PNG Quality
- Given user clicks "Export Charts (PNG)"
- When PNGs are generated
- Then images are:
  - 2x scale for high DPI
  - Suitable for presentations
  - Clean white background

#### AC9: PNG Filenames
- Given state with country=EP, tech_field=13
- When trend chart is exported
- Then filename is like: tip4patlibs_EP_field13_2019-2023_20260112_1430_trend.png

#### AC10: Multiple Chart Export
- Given 4 charts are displayed
- When "Export Charts" is clicked
- Then all 4 PNGs are exported
- And each has unique filename with chart name

#### AC11: Graceful Fallback
- Given kaleido/orca not installed
- When PNG export attempted
- Then message explains: "PNG export requires kaleido"
- And suggests alternative (screenshot)

### Story 5-3: Zero Results & Data Quality Handling

#### AC12: Zero Results Message
- Given query returns empty DataFrames
- When display_results() processes
- Then clear message: "No patents found for this selection"
- And export buttons are hidden

#### AC13: Actionable Suggestions (FR55)
- Given zero results with narrow date range (3 years)
- When message is displayed
- Then suggests: "Try expanding the date range"

#### AC14: Filter-Specific Suggestions
- Given zero results with SME filter enabled
- When message is displayed
- Then suggests: "Try disabling SME filter"

#### AC15: Data Quality Warning (FR54)
- Given any analysis completes with results
- When results are displayed
- Then data quality note appears (collapsible)
- And explains:
  - Applicant names may have variations
  - Regional data coverage varies by country
  - Older patents may have incomplete classifications

#### AC16: Warning Non-Intrusive
- Given data quality warning
- When user views results
- Then warning is:
  - Collapsed by default
  - Visually subtle (info style, not error)
  - Does not obstruct main results

## Traceability Mapping

| AC | PRD FR | Story | Component/API | Test Idea |
|----|--------|-------|---------------|-----------|
| AC1 | FR46 | 5.1 | `create_export_buttons()` | Verify button appears |
| AC2 | FR42, NFR11 | 5.1 | `Exporter.to_csv()` | Check delimiter and encoding |
| AC3 | FR43 | 5.1 | `Exporter.to_csv()` | Verify column headers, data completeness |
| AC4 | FR45 | 5.1 | `Exporter.generate_filename()` | Verify filename format |
| AC5 | FR46 | 5.1 | Export callback | Verify success message |
| AC6 | FR52 | 5.1 | Exception handling | Simulate disk error |
| AC7 | FR46 | 5.2 | `create_export_buttons()` | Verify PNG button appears |
| AC8 | FR44 | 5.2 | `Exporter.to_png()` | Verify image quality |
| AC9 | FR45 | 5.2 | `Exporter.generate_filename()` | Verify chart name in filename |
| AC10 | FR44 | 5.2 | Export callback | Verify all charts exported |
| AC11 | NFR7 | 5.2 | Fallback handling | Test without kaleido |
| AC12 | FR53 | 5.3 | `handle_zero_results()` | Pass empty DataFrames |
| AC13 | FR55 | 5.3 | `handle_zero_results()` | Test narrow date range |
| AC14 | FR55 | 5.3 | `handle_zero_results()` | Test with SME filter |
| AC15 | FR54 | 5.3 | `data_quality_warning()` | Verify content |
| AC16 | UX | 5.3 | `data_quality_warning()` | Verify collapsed default |

## Risks, Assumptions, Open Questions

### Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| kaleido not installed on TIP | Medium | Medium | Graceful fallback with clear message |
| Large exports slow | Low | Low | Data already limited by queries |
| Filename too long (Windows) | Low | Low | Truncate tech field display |
| Excel encoding issues | Low | Medium | UTF-8 BOM, semicolon delimiter proven |

### Assumptions

- TIP JupyterLab supports file downloads via links
- pandas to_csv works with UTF-8 BOM encoding
- Plotly write_image available (kaleido may need install)
- Users have write access to their workspace
- European users expect semicolon CSV delimiter

### Open Questions

1. **Q: Should we export all DataFrames to one CSV or separate files?**
   A: Single combined export for simplicity. Can add per-DataFrame export later.

2. **Q: What if applicant names contain semicolons?**
   A: pandas handles quoting automatically in to_csv().

3. **Q: Should PNG export include all charts in one click or individual buttons?**
   A: Single "Export All Charts" button for simplicity.

4. **Q: Where to save exported files?**
   A: Current working directory (user's notebook location).

## Test Strategy Summary

### Manual Testing on TIP

1. **CSV Export Happy Path**:
   - Run analysis for DE, Field 13, 2019-2023
   - Click "Export CSV"
   - Open in Excel, verify columns and data
   - Verify semicolon delimiter (no comma issues)
   - Verify umlauts display correctly (UTF-8)

2. **PNG Export Happy Path**:
   - Run same analysis
   - Click "Export Charts"
   - Open PNG files, verify quality
   - Verify all 4 charts exported

3. **Zero Results Testing**:
   - Select obscure combination (e.g., small country, narrow tech field, 1 year)
   - Verify "No results" message
   - Verify suggestions are relevant

4. **Data Quality Warning**:
   - Run any successful analysis
   - Verify warning appears (collapsed)
   - Expand and verify content

5. **Error Handling**:
   - Test with read-only directory (if possible)
   - Verify error message is helpful

### Edge Cases

- Very long applicant names in CSV
- Export with only 1 year of data
- Export with IPC mode (not tech field)
- Export when only some charts have data

---

*Generated by BMAD SM Workflow*
*Date: 2026-01-12*
