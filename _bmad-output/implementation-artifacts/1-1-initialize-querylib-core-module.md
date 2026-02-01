# Story 1.1: Initialize QueryLib Core Module

Status: ready-for-dev

## Story

As a **PATLIB staff member**,
I want **the Query Library notebook to initialize with a single setup cell**,
so that **I can start using queries without technical configuration steps**.

## Acceptance Criteria

### AC1: Successful Initialization
**Given** I open the Query Library notebook for the first time
**When** I run the "Initialize" cell
**Then** the PatstatClient connection is established
**And** a success message displays with emoji status (✅)
**And** any missing dependencies are installed automatically
**And** the `querylib_core.py` module is loaded with shared functions

### AC2: Connection Failure Handling
**Given** the PatstatClient connection fails
**When** the initialization cell completes
**Then** a user-friendly error message displays with suggested actions
**And** technical details are printed below for troubleshooting

### AC3: Idempotent Reinitialization
**Given** I have already run the initialization cell
**When** I run it again
**Then** the notebook reinitializes cleanly without errors
**And** no duplicate widgets or state issues occur

## Tasks / Subtasks

- [ ] Task 1: Create `querylib_core.py` module file (AC: 1)
  - [ ] 1.1: Create module with docstring and imports
  - [ ] 1.2: Implement `init_patstat()` connection function
  - [ ] 1.3: Implement `display_status()` helper for emoji status messages
  - [ ] 1.4: Implement `display_error()` helper for user-friendly errors
  - [ ] 1.5: Implement `show_progress()` helper for progress indicators
  - [ ] 1.6: Add module-level exports (`__all__`)

- [ ] Task 2: Update notebook initialization cell (AC: 1, 2, 3)
  - [ ] 2.1: Add dependency check and auto-install logic
  - [ ] 2.2: Import querylib_core module
  - [ ] 2.3: Call init_patstat() with error handling
  - [ ] 2.4: Display success/failure status with emoji
  - [ ] 2.5: Ensure idempotent behavior (no duplicate state)

- [ ] Task 3: Test all acceptance criteria (AC: 1, 2, 3)
  - [ ] 3.1: Test fresh notebook initialization
  - [ ] 3.2: Test re-running initialization cell
  - [ ] 3.3: Test error path (simulate connection failure if possible)

## Dev Notes

### Critical Architecture Requirements

**Source:** [architecture.md - ADR-015]
- Each notebook has its own `*_core.py` module
- Module file: `querylib_core.py` (NOT `query_lib_core.py`)
- Notebook file: `TIP_for_PATLIBs_QueryLib_for_PATLIBs.ipynb` (already exists)

**Source:** [architecture.md - Dependency Check Pattern]
```python
# Install dependencies if needed
try:
    import some_package
except ImportError:
    !pip install some_package
    import some_package
```

**Source:** [architecture.md - Error Handling Pattern]
```python
def run_query(state):
    try:
        # query execution
    except Exception as e:
        display(HTML(f"""
            <div style="color: #C8102E; padding: 10px; border: 1px solid #C8102E;">
                <b>Query Error</b><br>
                Unable to execute query. Please check your parameters and try again.
            </div>
        """))
        # Log technical error for debugging (visible in notebook output)
        print(f"Technical details: {e}")
```

**Source:** [architecture.md - Progress Indicator Pattern]
```python
from IPython.display import display, clear_output
import ipywidgets as widgets

progress = widgets.HTML(value="⏳ Running query...")
display(progress)
# ... execute query ...
progress.value = "✅ Complete!"
```

### Existing Code Reference

**CRITICAL:** There is an existing `tip4patlibs_core.py` with ~700 lines of working code. This story creates a NEW `querylib_core.py` specifically for the Query Library notebook, following ADR-015 per-notebook module pattern.

**Reusable patterns from existing code:**
- `init_patstat()` function pattern (lines 88-112)
- EPO_COLORS palette (use same colors)
- Module-level connection management (`patstat_client`, `db` globals)

**Source:** [tip4patlibs_core.py]
```python
def init_patstat() -> Tuple[PatstatClient, Any]:
    global patstat_client, db
    try:
        patstat_client = PatstatClient(env='PROD')
        db = patstat_client.orm()
        return patstat_client, db
    except Exception as e:
        raise ConnectionError(f"Could not connect to PATSTAT: {e}") from e
```

### Project Structure Notes

**File locations:**
```
tip4patlibs/
├── TIP_for_PATLIBs_QueryLib_for_PATLIBs.ipynb  # EXISTS - update init cell
├── querylib_core.py                            # CREATE - new module
├── tip4patlibs_core.py                         # EXISTS - reference only
```

**Naming convention:** snake_case for Python files (PEP 8)

### Technical Requirements

| Requirement | Specification | Source |
|-------------|---------------|--------|
| Python naming | snake_case | [architecture.md - Established Patterns] |
| UI framework | ipywidgets | [architecture.md - ADR-007] |
| Data access | PatstatClient only | [architecture.md - NFR11] |
| Error messages | User-friendly, no tracebacks | [architecture.md - FR35, NFR7] |
| Colors | EPO_COLORS palette | [architecture.md - Phase 1] |

### Library/Framework Requirements

| Package | Version | Purpose | Pre-installed |
|---------|---------|---------|---------------|
| ipywidgets | latest | UI controls | Yes (TIP) |
| pandas | latest | Data handling | Yes (TIP) |
| PatstatClient | TIP version | PATSTAT access | Yes (TIP) |
| IPython | latest | Display utilities | Yes (TIP) |

### Functions to Implement in querylib_core.py

```python
# Module structure for querylib_core.py

"""
QueryLib Core Module
====================
Core functions for the Query Library notebook.
Provides initialization, status display, and error handling.
"""

from typing import Tuple, Optional, Any
import ipywidgets as widgets
from IPython.display import display, HTML

# PATSTAT imports
from epo.tipdata.patstat import PatstatClient

# Module-level connection
patstat_client: Optional[PatstatClient] = None
db: Optional[Any] = None

__all__ = [
    'init_patstat',
    'display_status',
    'display_error',
    'show_progress',
    'patstat_client',
    'db',
]

def init_patstat() -> Tuple[PatstatClient, Any]:
    """Initialize PATSTAT connection. Returns (client, session)."""
    # Implementation follows existing pattern

def display_status(message: str, success: bool = True) -> None:
    """Display status message with emoji (✅ or ❌)."""
    # Use ipywidgets HTML

def display_error(title: str, message: str, details: str = None) -> None:
    """Display user-friendly error with optional technical details."""
    # Red styled box with helpful message

def show_progress(message: str = "Loading...") -> widgets.HTML:
    """Create and display a progress indicator. Returns widget for updating."""
    # Return widget so caller can update .value
```

### What Worked Well (from past learnings)

**Source:** [context/what-worked-well.md]

1. **Modular Refactoring** - Keep modules focused, single responsibility
2. **Query-as-Data Pattern** - Will be implemented in Story 1.2
3. **Progressive Disclosure** - Show essential info first (applies to error messages)
4. **TIP Bridge Pattern** - Already established in existing code

### FRs Covered by This Story

| FR | Description | Implementation |
|----|-------------|----------------|
| FR33 | All notebooks initialize with single "Run this cell first" setup cell | Init cell pattern |
| FR34 | All notebooks display clear status messages during operations | display_status() |
| FR35 | All notebooks handle errors gracefully with actionable messages | display_error() |
| FR39 | System connects to PATSTAT via PatstatClient | init_patstat() |
| FR40 | System executes queries against BigQuery backend | PatstatClient.orm() |

### Testing Approach

1. **Manual Testing in TIP:**
   - Upload notebook to TIP
   - Run initialization cell
   - Verify success message appears
   - Re-run cell, verify no errors

2. **Error Testing:**
   - Temporarily break connection (if possible)
   - Verify error message is user-friendly
   - Verify technical details are logged

### References

- [Source: _bmad-output/planning-artifacts/architecture.md#ADR-015]
- [Source: _bmad-output/planning-artifacts/architecture.md#Error-Handling-Pattern]
- [Source: _bmad-output/planning-artifacts/architecture.md#Progress-Indicator-Pattern]
- [Source: _bmad-output/planning-artifacts/epics.md#Story-1.1]
- [Source: context/what-worked-well.md]
- [Source: tip4patlibs_core.py - existing patterns]

## Dev Agent Record

### Agent Model Used

_To be filled by dev agent_

### Debug Log References

_To be filled during implementation_

### Completion Notes List

_To be filled during implementation_

### File List

_Files created/modified during implementation:_
- [ ] `querylib_core.py` - NEW
- [ ] `TIP_for_PATLIBs_QueryLib_for_PATLIBs.ipynb` - MODIFIED (init cell)
