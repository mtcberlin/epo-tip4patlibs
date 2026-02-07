# Epic Technical Specification: Selection Interface

Date: 2026-01-11
Author: BMad
Epic ID: 2
Status: Draft

---

## Overview

Epic 2 builds the user selection interface for TIP for PATLIBs, enabling non-technical PATLIB staff to specify patent analysis parameters through intuitive no-code controls. This epic creates all user-facing widgets: jurisdiction dropdown, region selector, technology field picker, custom IPC entry, date range slider, and the review/run panel.

The selection interface follows ADR-003 (Prevention by Design) - widgets constrain input to valid, tested ranges loaded from ReferenceData (Epic 1). Users cannot enter invalid data because the UI only presents valid options.

This epic depends on Epic 1's foundation: PATSTAT connection (`get_db()`), ReferenceData (jurisdictions, tech_fields, sectors), and AnalysisState class with `summary()` and `is_valid()` methods.

## Objectives and Scope

### In Scope

- Jurisdiction selection dropdown (ADR-008: uses `appln_auth` filing jurisdiction)
- Region selection dropdown (NUTS codes, dynamically loaded per jurisdiction)
- Technology field selection (35 WIPO fields grouped by 5 sectors)
- Custom IPC/CPC entry mode (dual mode per ADR-004)
- Date range slider with dynamic performance tips
- Review panel with state summary, SME filter, Reset and Run buttons
- UI framework decision spike (ADR-007: ipywidgets vs ipyvuetify)
- WidgetFactory class for creating pre-configured widgets

### Out of Scope

- Query execution (Epic 3)
- Chart visualizations (Epic 4)
- CSV/PNG export (Epic 5)
- NUTS region data loading at startup (loaded dynamically per-jurisdiction)

## System Architecture Alignment

This epic implements decisions from `docs/architecture.md`:

| Architecture Decision | Implementation in Epic 2 |
|-----------------------|--------------------------|
| **ADR-001: Hybrid Structure** | WidgetFactory class in tip4patlibs_core.py |
| **ADR-003: Prevention by Design** | Widgets show only valid options from ReferenceData |
| **ADR-004: Tech Field Dual Mode** | Toggle between WIPO fields and custom IPC/CPC |
| **ADR-006: State Class** | Widgets update AnalysisState via observe() callbacks |
| **ADR-007: UI Framework** | PENDING - Spike in Story 2.1 determines ipywidgets vs ipyvuetify |
| **ADR-008: Filing Jurisdiction** | Dropdown uses ReferenceData.jurisdictions (from appln_auth) |
| **ADR-009: No Hardcoded Data** | All options from PATSTAT lookup tables |

**Components Created/Modified:**
- `tip4patlibs_core.py` - Add WidgetFactory class
- `TIP_for_PATLIBs.ipynb` - Cells 2-5 with selection widgets

## Detailed Design

### Services and Modules

| Module | Responsibility | Dependencies |
|--------|---------------|--------------|
| `WidgetFactory` | Create pre-configured widgets with valid options | ReferenceData, AnalysisState, ipywidgets/ipyvuetify |
| `tip4patlibs_core.py` | Contains WidgetFactory, state callbacks | Epic 1 components |
| Notebook Cell 2 | Jurisdiction & Region selection | WidgetFactory |
| Notebook Cell 3 | Technology selection (field/IPC mode) | WidgetFactory |
| Notebook Cell 4 | Date range with performance tips | WidgetFactory |
| Notebook Cell 5 | Review panel, SME filter, Run button | WidgetFactory, AnalysisState |

### Data Models and Contracts

#### WidgetFactory Class

```python
class WidgetFactory:
    """Creates pre-configured widgets with valid options only (ADR-003)"""

    def __init__(self, reference_data: ReferenceData, state: AnalysisState):
        self.ref = reference_data
        self.state = state

    def jurisdiction_dropdown(self) -> widgets.Dropdown:
        """Jurisdiction selection from ReferenceData.jurisdictions"""

    def region_dropdown(self, jurisdiction_code: str) -> widgets.Dropdown:
        """NUTS regions for jurisdiction, dynamically loaded"""

    def tech_field_dropdown(self) -> widgets.Dropdown:
        """35 WIPO fields grouped by sector"""

    def ipc_input(self) -> widgets.Text:
        """Custom IPC/CPC entry with validation"""

    def tech_mode_toggle(self) -> widgets.RadioButtons:
        """Toggle: Tech Field | Custom IPC/CPC"""

    def year_range_slider(self) -> widgets.IntRangeSlider:
        """Year range 2000-2024 with default 2019-2023"""

    def performance_tip(self) -> widgets.HTML:
        """Dynamic tip based on year span"""

    def sme_checkbox(self) -> widgets.Checkbox:
        """SME filter (<100 applications)"""

    def summary_panel(self) -> widgets.HTML:
        """Display state.summary()"""

    def reset_button(self) -> widgets.Button:
        """Clear all selections"""

    def run_button(self) -> widgets.Button:
        """Run Analysis - disabled until state.is_valid()"""
```

#### Widget Callbacks Pattern

```python
def _on_jurisdiction_change(self, change):
    """Callback when jurisdiction selection changes"""
    self.state.country = change['new']
    # Trigger region dropdown refresh
    self._refresh_region_dropdown()
    self._update_run_button_state()

def _on_tech_field_change(self, change):
    """Callback when tech field selection changes"""
    self.state.tech_field = change['new']
    self.state.tech_mode = "field"
    self._update_run_button_state()
```

### APIs and Interfaces

No external APIs. Internal widget interfaces:

| Widget | Input | Output | Callback |
|--------|-------|--------|----------|
| `jurisdiction_dropdown` | ReferenceData.jurisdictions | Selected code | Updates state.country |
| `region_dropdown` | NUTS query for jurisdiction | Selected NUTS code | Updates state.region |
| `tech_field_dropdown` | ReferenceData.tech_fields | Field number (1-35) | Updates state.tech_field, tech_mode="field" |
| `ipc_input` | User text | List of IPC codes | Updates state.ipc_codes, tech_mode="ipc" |
| `year_range_slider` | Fixed range 2000-2024 | (start, end) tuple | Updates state.year_start, year_end |
| `sme_checkbox` | None | Boolean | Updates state.sme_filter |
| `run_button` | state.is_valid() | Click event | Triggers Epic 3 query |

### Workflows and Sequencing

**User Selection Flow:**

```
Cell 2: Jurisdiction & Region
├─► User selects jurisdiction from dropdown
│   └─► state.country updates
│   └─► Region dropdown refreshes with NUTS regions
├─► User optionally selects region
│   └─► state.region updates
└─► "All regions" default if no selection

Cell 3: Technology Selection
├─► User sees mode toggle: "Tech Field" | "Custom IPC/CPC"
├─► If Tech Field mode:
│   └─► User selects from 35 WIPO fields (grouped by sector)
│   └─► state.tech_field updates, state.tech_mode = "field"
├─► If Custom IPC mode:
│   └─► User enters comma-separated IPC codes
│   └─► Validation: A-H + 2 digits, max 5 codes
│   └─► state.ipc_codes updates, state.tech_mode = "ipc"
└─► Mode switch clears the other mode's selection

Cell 4: Date Range
├─► IntRangeSlider with 2000-2024 range
├─► Default: [2019, 2023]
├─► Dynamic performance tip:
│   ├─► ≤5 years: "⚡ Fast query (~10 sec)"
│   ├─► 6-10 years: "⏱️ Medium query (~30 sec)"
│   └─► >10 years: "🐢 Large query (~2 min)"
└─► state.year_start, state.year_end update

Cell 5: Review & Run
├─► Summary panel displays state.summary()
├─► SME Filter checkbox
├─► Reset button clears to defaults
├─► Run Analysis button:
│   ├─► Disabled until state.is_valid() == True
│   └─► Shows validation message if disabled
└─► Click triggers Epic 3 query execution
```

**NUTS Region Loading (Dynamic):**

```python
def load_regions_for_jurisdiction(db, jurisdiction_code: str) -> List[Tuple[str, str]]:
    """Query NUTS regions for a jurisdiction"""
    # Query tls904_nuts WHERE nuts LIKE '{jurisdiction_code}%' AND nuts_level <= 2
    # Returns: [("Bavaria", "DE2"), ("Baden-Württemberg", "DE1"), ...]
    # Returns empty list if no NUTS data for jurisdiction
```

## Non-Functional Requirements

### Performance

| Metric | Target | Source |
|--------|--------|--------|
| Widget render time | < 1 second | Derived from NFR4 |
| Region dropdown refresh | < 2 seconds | NUTS query performance |
| Selection response | < 100ms | User experience expectation |
| All cells render | < 5 seconds total | NFR4 |

**Implementation:**
- Pre-load jurisdictions and tech fields at startup (Epic 1)
- Load NUTS regions on-demand per jurisdiction
- Use observe() callbacks for immediate UI response

### Security

| Requirement | Implementation |
|-------------|----------------|
| Input validation | Widgets constrain to valid options |
| IPC validation | Regex pattern `/^[A-H]\d{2}[A-Z]?$/` |
| No SQL injection | All queries use ORM with parameters |

No additional security needed - widgets prevent invalid input by design (ADR-003).

### Reliability/Availability

| Scenario | Handling |
|----------|----------|
| NUTS query fails | Show "All regions" only, log warning |
| Empty jurisdiction list | Should not happen (sanity check in Epic 1) |
| Widget callback error | Log error, don't crash notebook |

### Observability

| Signal | Implementation |
|--------|----------------|
| Selection state | state.summary() displayed in Cell 5 |
| Validation status | state.is_valid() message shown |
| Performance tip | Dynamic label in Cell 4 |

## Dependencies and Integrations

### From Epic 1 (Required)

| Component | Usage |
|-----------|-------|
| `ReferenceData.jurisdictions` | Jurisdiction dropdown options |
| `ReferenceData.tech_fields` | Technology field dropdown options |
| `ReferenceData.sectors` | Grouping for tech field display |
| `AnalysisState` | State management, summary(), is_valid() |
| `get_db()` | For NUTS region queries |
| `init_patstat()` | Must be run before widgets |

### PATSTAT Tables (New in Epic 2)

| Table | Purpose | Query |
|-------|---------|-------|
| `tls904_nuts` | NUTS region lookup | `SELECT DISTINCT nuts, nuts_label WHERE nuts LIKE '{code}%' AND nuts_level <= 2` |

### UI Framework (TBD)

| Option | Pros | Cons |
|--------|------|------|
| **ipywidgets** | Standard, well-documented, familiar | Basic styling |
| **ipyvuetify** | Material Design polish | Learning curve |

**Decision:** Spike in Story 2.1 will evaluate and update ADR-007.

## Acceptance Criteria (Authoritative)

### AC1: Jurisdiction Selection (Story 2.1)
- [ ] Dropdown shows all jurisdictions from ReferenceData.jurisdictions (208+ offices)
- [ ] Format: Display name (e.g., "Germany") not code (e.g., "DE")
- [ ] Placeholder: "Select jurisdiction..."
- [ ] Selection immediately updates state.country
- [ ] Selection triggers region dropdown refresh

### AC2: Region Selection (Story 2.2)
- [ ] Dropdown dynamically loads NUTS regions for selected jurisdiction
- [ ] Query: tls904_nuts WHERE nuts LIKE '{code}%' AND nuts_level <= 2
- [ ] Default option: "All regions" (state.region = None)
- [ ] Shows helper text when no NUTS data: "Regional data not available"
- [ ] Selection updates state.region

### AC3: Technology Field Selection (Story 2.3)
- [ ] Dropdown shows all 35 WIPO technology fields
- [ ] Fields grouped by sector (5 groups: Electrical, Instruments, Chemistry, Mechanical, Other)
- [ ] Format: "13 - Medical technology"
- [ ] Selection updates state.tech_field and sets state.tech_mode = "field"
- [ ] IPC mapping viewable via tooltip/info button

### AC4: Custom IPC/CPC Mode (Story 2.4)
- [ ] Mode toggle: RadioButtons "Tech Field" | "Custom IPC/CPC"
- [ ] Text input for comma-separated IPC codes
- [ ] Validation: Pattern A-H + 2 digits (e.g., A61B, H01L)
- [ ] Maximum 5 codes enforced
- [ ] Valid input updates state.ipc_codes, sets state.tech_mode = "ipc"
- [ ] Shows validation feedback: "✓ Valid" or "✗ Invalid format"

### AC5: Date Range Selection (Story 2.5)
- [ ] IntRangeSlider with range 2000-2024
- [ ] Default value: [2019, 2023]
- [ ] Labels show selected years
- [ ] Performance tip updates dynamically based on span
- [ ] Selection updates state.year_start, state.year_end

### AC6: Review Panel (Story 2.6)
- [ ] Displays state.summary() with current selections
- [ ] SME Filter checkbox updates state.sme_filter
- [ ] Reset button clears all selections to defaults (new AnalysisState())
- [ ] Run Analysis button prominent (green styling)
- [ ] Run button disabled until state.is_valid() returns (True, "Ready")
- [ ] Shows validation message when disabled

### AC7: UI Framework Decision (Story 2.1 Spike)
- [ ] Spike evaluates ipywidgets vs ipyvuetify
- [ ] Criteria: Visual polish, code complexity, responsiveness, layout control, edge cases
- [ ] Findings documented with scores
- [ ] ADR-007 updated with chosen framework and rationale

## Traceability Mapping

| AC | PRD FR | Architecture | Component | Test Approach |
|----|--------|--------------|-----------|---------------|
| AC1 | FR5-8 | ADR-008 | jurisdiction_dropdown | Manual: select, verify state |
| AC2 | FR9-12 | - | region_dropdown | Manual: cascade test |
| AC3 | FR13-17 | ADR-004 | tech_field_dropdown | Manual: grouping, selection |
| AC4 | FR13-17 | ADR-004 | ipc_input, tech_mode_toggle | Manual: validation test |
| AC5 | FR18-21 | - | year_range_slider | Manual: range, tip update |
| AC6 | FR47-51 | ADR-006 | summary_panel, run_button | Manual: is_valid integration |
| AC7 | FR47 | ADR-007 | WidgetFactory | Spike deliverable |

## Risks, Assumptions, Open Questions

### Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| ipyvuetify not available on TIP | Medium | High | Spike validates availability first |
| NUTS data sparse for non-EU offices | High | Low | Graceful fallback to "All regions" |
| 208 jurisdictions overwhelms dropdown | Low | Medium | Consider search/filter enhancement |
| Widget callbacks cause state bugs | Medium | Medium | Clear callback flow, testing |

### Assumptions

| ID | Assumption | Validation |
|----|------------|------------|
| A1 | ipywidgets available on TIP | Verified in Epic 1 |
| A2 | tls904_nuts queryable via ORM | Test in Story 2.2 |
| A3 | observe() callbacks work reliably | Standard ipywidgets pattern |

### Open Questions

| ID | Question | Impact | Resolution Path |
|----|----------|--------|-----------------|
| Q1 | ipywidgets or ipyvuetify? | All widget code | Story 2.1 spike |
| Q2 | NUTS regions for US, JP, CN? | Story 2.2 edge case | Query test, graceful fallback |
| Q3 | How to group 35 fields by sector? | Story 2.3 UI | Use optgroup or nested layout |

## Test Strategy Summary

### Manual Validation (on TIP)

| Test | Criteria |
|------|----------|
| Jurisdiction dropdown | Shows 208+ options, selection updates state |
| Region cascade | Changes on jurisdiction change, shows NUTS or fallback |
| Tech field grouping | 5 sectors visible, 35 fields total |
| IPC validation | Accepts "A61B", rejects "ZZZ", max 5 codes |
| Year slider | Range 2000-2024, default [2019, 2023], tip updates |
| Run button | Disabled when invalid, enabled when valid |
| Reset button | Clears all selections |

### Integration Tests

| Test | Coverage |
|------|----------|
| Full selection flow | Jurisdiction → Region → Tech → Date → Run |
| Mode switching | Tech Field ↔ IPC mode preserves other state |
| State consistency | All selections reflected in summary panel |

---

_Tech Spec generated by BMAD epic-tech-context workflow_
