# Story 1.1: Project Structure & Module Setup

Status: review

## Story

As a **developer**,
I want **a well-organized project structure with notebook and supporting module**,
so that **code is maintainable and the notebook stays clean**.

## Acceptance Criteria

1. **AC1: Project Files Exist**
   - Given a fresh TIP JupyterLab environment
   - When I open the project folder
   - Then I see:
     - `TIP_for_PATLIBs.ipynb` - main notebook
     - `tip4patlibs_core.py` - supporting module
     - `README.md` - brief setup instructions

2. **AC2: Module Import Works**
   - Given the notebook and module are in the same directory
   - When I run `from tip4patlibs_core import *` in the notebook
   - Then import succeeds without errors
   - And all placeholder classes are available

3. **AC3: Placeholder Classes Defined**
   - Given `tip4patlibs_core.py` is loaded
   - Then the following classes exist (can be empty/stub implementations):
     - `AnalysisState` - state management dataclass
     - `PatstatQueries` - query builder (placeholder)
     - `WidgetFactory` - UI components (placeholder)
     - `ChartBuilder` - visualization builders (placeholder)
     - `Exporter` - CSV/PNG export (placeholder)

4. **AC4: Notebook Structure**
   - Given the notebook is opened
   - Then Cell 1 exists with header markdown: "▶️ Run this cell first!"
   - And Cell 1 contains `from tip4patlibs_core import *`
   - And additional cells are placeholders for future functionality

5. **AC5: LOC Tracking**
   - Given the module file
   - When checking line count
   - Then total LOC is documented in README
   - And note that split to lib/ folder occurs if >500 LOC

## Tasks / Subtasks

- [x] **Task 1: Create tip4patlibs_core.py module** (AC: 3)
  - [x] 1.1: Create file with module docstring and imports
  - [x] 1.2: Define `AnalysisState` dataclass with all attributes from architecture
  - [x] 1.3: Add `summary()` method stub (returns placeholder text)
  - [x] 1.4: Add `is_valid()` method stub (returns (False, "Not implemented"))
  - [x] 1.5: Create `PatstatQueries` class placeholder with `__init__(self, db)`
  - [x] 1.6: Create `WidgetFactory` class placeholder
  - [x] 1.7: Create `ChartBuilder` class placeholder
  - [x] 1.8: Create `Exporter` class placeholder
  - [x] 1.9: Add `__all__` export list

- [x] **Task 2: Create TIP_for_PATLIBs.ipynb notebook** (AC: 1, 2, 4)
  - [x] 2.1: Create new Jupyter notebook
  - [x] 2.2: Add Cell 1 markdown header with emoji marker
  - [x] 2.3: Add Cell 1 code with import statement
  - [x] 2.4: Add placeholder cells for future sections (Setup, Selection, Results)
  - [x] 2.5: Verify import works by running Cell 1

- [x] **Task 3: Create README.md** (AC: 1, 5)
  - [x] 3.1: Add brief project description
  - [x] 3.2: Document file structure
  - [x] 3.3: Add setup instructions (just "open notebook, run Cell 1")
  - [x] 3.4: Note current LOC count and split threshold

- [x] **Task 4: Validation** (AC: 1-5)
  - [x] 4.1: Verify all files exist in project folder
  - [x] 4.2: Open notebook and run import cell
  - [x] 4.3: Confirm no import errors
  - [x] 4.4: Verify all classes importable

## Dev Notes

### Architecture Alignment

- Implements **ADR-001: Hybrid Structure** - notebook + single module file
- Module structure follows architecture pattern from `docs/architecture.md`
- Target: <500 LOC in single file; split to `lib/` folder if exceeded

### File Structure Target

```
tip4patlibs/
├── TIP_for_PATLIBs.ipynb      # User-facing notebook
├── tip4patlibs_core.py        # Core logic module
└── README.md                  # Setup instructions
```

### AnalysisState Dataclass (from Architecture)

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
```

### Module Imports (Architecture Pattern)

All heavy imports in module, not notebook:
- `pandas`
- `plotly.express`
- `ipywidgets`
- Type hints from `typing`
- Dataclasses from `dataclasses`

Note: Do NOT import `epo.tipdata.patstat` yet - that's Story 1.2

### Project Structure Notes

- This is a greenfield project - no existing files to modify
- Files created in project root directory
- Notebook cells should be minimal code - mostly calling module functions
- Use `__all__` to control what `import *` exposes

### Testing Approach

Manual validation on TIP:
1. Open notebook in JupyterLab
2. Run Cell 1
3. Verify no errors
4. In new cell, verify `AnalysisState()` creates instance

### References

- [Source: docs/architecture.md#Project-Structure]
- [Source: docs/architecture.md#ADR-001]
- [Source: docs/sprint-artifacts/tech-spec-epic-1.md#Data-Models-and-Contracts]
- [Source: docs/epics.md#Story-1.1]

## Dev Agent Record

### Context Reference

- `docs/sprint-artifacts/stories/1-1-project-structure-module-setup.context.xml`

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- Implemented all 4 tasks in sequence
- Module created with 168 LOC (well under 500 LOC threshold)
- All imports validated via Python test script
- Notebook structure follows progressive cell pattern from architecture

### Completion Notes List

- Created `tip4patlibs_core.py` with full AnalysisState dataclass and placeholder classes
- Created `TIP_for_PATLIBs.ipynb` with setup cell, selection placeholder, results placeholder, export placeholder
- Created `README.md` with project overview, file structure, and LOC tracking
- All acceptance criteria validated:
  - AC1: All three files exist
  - AC2: `from tip4patlibs_core import *` works without errors
  - AC3: All 5 classes (AnalysisState, PatstatQueries, WidgetFactory, ChartBuilder, Exporter) accessible
  - AC4: Notebook has "Run this cell first!" header with emoji marker
  - AC5: LOC (168) documented in README with 500 LOC split threshold noted

### File List

- NEW: `tip4patlibs_core.py` (168 LOC)
- NEW: `TIP_for_PATLIBs.ipynb` (8 cells)
- NEW: `README.md`

---

## Changelog

| Date | Author | Change |
|------|--------|--------|
| 2026-01-12 | SM (Bob) | Story drafted from epics.md and tech-spec |
| 2026-01-11 | Dev (Amelia) | Implementation complete - all ACs satisfied, ready for review |
