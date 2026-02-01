# Epic Technical Specification: Foundation & Setup

Date: 2026-01-12
Author: BMad
Epic ID: 1
Status: Draft

---

## Overview

Epic 1 establishes the foundational infrastructure for TIP for PATLIBs - a Jupyter notebook application enabling PATLIB staff to perform patent analysis without programming skills. This epic creates the project structure, establishes the PATSTAT database connection, loads reference data for UI dropdowns, and implements the core state management class.

This foundation epic is critical because all subsequent epics (Selection Interface, Query Engine, Visualizations, Export) depend on the structures and patterns established here. The goal is a working notebook that connects to PATSTAT and can display "Connected successfully" - proving the environment works before building features.

## Objectives and Scope

### In Scope

- Create hybrid project structure: `TIP_for_PATLIBs.ipynb` + `tip4patlibs_core.py`
- Establish PATSTAT connection via `epo.tipdata.patstat.PatstatClient`
- Load reference data: countries, technology fields (35 WIPO), sectors
- Implement `AnalysisState` dataclass with `summary()` and `is_valid()` methods
- Create initialization cell with clear visual markers and status feedback
- Handle connection failures gracefully with user-friendly messages

### Out of Scope

- UI widgets (Epic 2)
- PATSTAT queries (Epic 3)
- Visualizations (Epic 4)
- Export functionality (Epic 5)
- NUTS region loading (deferred to Epic 2 - loaded per-country dynamically)

## System Architecture Alignment

This epic implements decisions from `docs/architecture.md`:

| Architecture Decision | Implementation in Epic 1 |
|-----------------------|--------------------------|
| **ADR-001: Hybrid Structure** | Create notebook + single module file |
| **ADR-006: State Class** | Implement `AnalysisState` with `summary()` |
| **ADR-003: Prevention by Design** | Pre-load valid dropdown options |

**Components Created:**
- `TIP_for_PATLIBs.ipynb` - User-facing notebook
- `tip4patlibs_core.py` - Core module containing:
  - `AnalysisState` class
  - `ReferenceData` class
  - Connection utilities

## Detailed Design

### Services and Modules

| Module | Responsibility | Dependencies |
|--------|---------------|--------------|
| `tip4patlibs_core.py` | Core logic container | pandas, epo.tipdata.patstat |
| `AnalysisState` | State management | dataclasses |
| `ReferenceData` | Cache dropdown options | PatstatClient |
| Notebook Cell 1 | Initialization & setup | tip4patlibs_core |

### Data Models and Contracts

#### AnalysisState Dataclass

```python
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class AnalysisState:
    """Single source of truth for user selections"""
    country: Optional[str] = None           # ISO country code (e.g., "DE")
    region: Optional[str] = None            # NUTS code (e.g., "DE2")
    tech_mode: str = "field"                # "field" or "ipc"
    tech_field: Optional[int] = None        # 1-35 (WIPO field number)
    ipc_codes: List[str] = field(default_factory=list)  # Max 5 codes
    year_start: int = 2019
    year_end: int = 2023
    sme_filter: bool = False                # <100 applications filter

    def summary(self) -> str:
        """Human-readable query summary"""
        # Returns formatted string with emoji indicators

    def is_valid(self) -> tuple[bool, str]:
        """Validate required fields are set"""
        # Returns (True, "Ready") or (False, "error message")
```

#### ReferenceData Class

```python
@dataclass
class ReferenceData:
    """Cached reference data for dropdowns"""
    countries: List[tuple[str, str]]        # (display_name, code)
    tech_fields: List[tuple[str, int]]      # (display_name, field_nr)
    sectors: List[str]                       # Sector names for grouping

    @classmethod
    def load(cls, db) -> 'ReferenceData':
        """Load all reference data from PATSTAT"""
        # Queries tls206_person for countries
        # Queries tls901_techn_field_ipc for tech fields
```

### APIs and Interfaces

No external APIs. Internal interfaces:

| Function | Signature | Purpose |
|----------|-----------|---------|
| `init_patstat()` | `() -> PatstatClient` | Establish PATSTAT connection |
| `load_reference_data(db)` | `(PatstatClient) -> ReferenceData` | Load dropdown options |
| `state.summary()` | `() -> str` | Human-readable state display |
| `state.is_valid()` | `() -> tuple[bool, str]` | Validation check |

### Workflows and Sequencing

**Initialization Flow (Cell 1):**

```
User runs Cell 1
    │
    ├─► Import tip4patlibs_core
    │
    ├─► Try: PatstatClient()
    │       │
    │       ├─► Success: Display "✅ Connected to PATSTAT"
    │       │
    │       └─► Failure: Display "❌ Connection failed" + suggestion
    │
    ├─► Load ReferenceData
    │       │
    │       ├─► Query DISTINCT person_ctry_code
    │       │
    │       └─► Query tls901_techn_field_ipc
    │
    ├─► Create global state = AnalysisState()
    │
    └─► Display "Ready! Proceed to next cell."
```

## Non-Functional Requirements

### Performance

| Metric | Target | Source |
|--------|--------|--------|
| Cell 1 execution | < 30 seconds | NFR1 (PRD) |
| Reference data load | < 10 seconds | Derived |
| Memory footprint | < 50 MB for ref data | Derived |

**Implementation:**
- Query only DISTINCT values (not full tables)
- Store as lightweight Python lists/tuples
- No caching to disk needed

### Security

| Requirement | Implementation |
|-------------|----------------|
| Authentication | TIP platform handles (N/A) |
| Data access | Read-only PATSTAT access |
| Credential storage | None - uses TIP session |

No additional security implementation needed - TIP platform manages access.

### Reliability/Availability

| Scenario | Handling |
|----------|----------|
| PATSTAT unavailable | Display clear error, suggest retry |
| TIP session timeout | User re-authenticates via TIP |
| Partial data load | Fail fast, report which query failed |

**Key principle:** If PATSTAT is unavailable at init, there's nothing useful the notebook can do. Fail clearly rather than partially.

### Observability

| Signal | Implementation |
|--------|----------------|
| Connection status | Print statement in cell output |
| Load times | Optional timing display |
| Error details | Full exception in debug mode |

Minimal observability for MVP - cell outputs provide sufficient feedback.

## Dependencies and Integrations

### TIP Platform Dependencies (Pre-installed)

| Package | Purpose | Version |
|---------|---------|---------|
| `epo.tipdata.patstat` | PATSTAT ORM access | TIP-provided |
| `pandas` | DataFrame operations | TIP-provided |
| `ipywidgets` | UI components (Epic 2) | TIP-provided |
| `plotly` | Visualizations (Epic 4) | TIP-provided |

### PATSTAT Tables Used

| Table | Purpose | Query Type |
|-------|---------|------------|
| `tls206_person` | Country list extraction | `SELECT DISTINCT person_ctry_code` |
| `tls901_techn_field_ipc` | Tech field reference | `SELECT DISTINCT techn_field_nr, techn_sector, techn_field` |

### Integration Points

| Integration | Protocol | Notes |
|-------------|----------|-------|
| PATSTAT BigQuery | Via `epo.tipdata.patstat` | ORM + raw SQL |
| TIP JupyterLab | Native execution | No special integration |

## Acceptance Criteria (Authoritative)

### AC1: Project Structure
- [ ] `TIP_for_PATLIBs.ipynb` exists and opens in JupyterLab
- [ ] `tip4patlibs_core.py` exists in same directory
- [ ] Notebook can `from tip4patlibs_core import *` without errors

### AC2: PATSTAT Connection
- [ ] Cell 1 establishes PATSTAT connection via `PatstatClient()`
- [ ] Success displays: "✅ Connected to PATSTAT"
- [ ] Failure displays: "❌ Could not connect to PATSTAT" with suggestion
- [ ] Connection completes within 30 seconds

### AC3: Reference Data Loading
- [ ] Countries loaded as list of (display_name, code) tuples
- [ ] All 35 WIPO technology fields loaded
- [ ] Tech fields include sector grouping information
- [ ] At least 50 countries available (sanity check)

### AC4: AnalysisState Class
- [ ] Dataclass with all specified attributes and defaults
- [ ] `summary()` returns formatted string with emoji indicators
- [ ] `is_valid()` returns `(False, "Please select a country")` when country is None
- [ ] `is_valid()` returns `(True, "Ready")` when country and tech selection are set

### AC5: User Experience
- [ ] Cell 1 has clear visual marker ("▶️ Run this cell first!")
- [ ] Status messages are user-friendly (no stack traces in normal flow)
- [ ] Initialization completes within 30 seconds (NFR1)

## Traceability Mapping

| AC | PRD FR | Architecture | Component | Test Approach |
|----|--------|--------------|-----------|---------------|
| AC1 | FR1 | ADR-001 | Project files | Manual: open notebook |
| AC2 | FR1, FR2, FR4 | - | `init_patstat()` | Integration: run on TIP |
| AC3 | FR13, FR17 | ADR-004 | `ReferenceData` | Unit: check counts |
| AC4 | - | ADR-006 | `AnalysisState` | Unit: test methods |
| AC5 | FR1, FR4 | ADR-003 | Cell 1 | Manual: UX review |

## Risks, Assumptions, Open Questions

### Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| TIP environment differs from expected | Medium | High | Test early on actual TIP |
| PATSTAT table names/columns changed | Low | High | Verify against schema.json |
| Large country list overwhelms dropdown | Low | Medium | Limit to relevant countries if needed |

### Assumptions

| ID | Assumption | Validation |
|----|------------|------------|
| A1 | `epo.tipdata.patstat` available on TIP | Verify in first test |
| A2 | `PatstatClient()` requires no arguments | Check TIP docs |
| A3 | All 35 WIPO fields exist in tls901 | Verify row count |

### Open Questions

| ID | Question | Impact | Resolution Path |
|----|----------|--------|-----------------|
| Q1 | Exact country code to name mapping? | Display quality | Check PATSTAT or use ISO mapping |
| Q2 | Are all TIP library versions compatible? | Functionality | Test on TIP early |

## Test Strategy Summary

### Unit Tests (tip4patlibs_core.py)

| Test | Coverage |
|------|----------|
| `test_analysis_state_defaults` | Default values correct |
| `test_analysis_state_summary` | summary() format |
| `test_analysis_state_is_valid` | Validation logic |
| `test_reference_data_structure` | Data shapes |

### Integration Tests (on TIP)

| Test | Coverage |
|------|----------|
| `test_patstat_connection` | Connection establishes |
| `test_load_countries` | Countries query works |
| `test_load_tech_fields` | Tech fields query works |

### Manual Validation

| Check | Criteria |
|-------|----------|
| Open notebook | No import errors |
| Run Cell 1 | Completes < 30s, shows success |
| Check state | `state.summary()` displays correctly |

---

_Tech Spec generated by BMAD epic-tech-context workflow_
