# Story 1.3: Reference Data Loading

Status: ready-for-dev

## Story

As a **system**,
I want **to pre-load all dropdown options at startup**,
so that **users see instant responses when selecting filters**.

## Acceptance Criteria

1. **AC1: Country Data Loaded**
   - Given PATSTAT connection is established
   - When initialization completes
   - Then system loads country list from `tls206_person.person_ctry_code` (DISTINCT values)
   - And country list contains at least 50 countries (sanity check)
   - And countries are sorted alphabetically by display name

2. **AC2: Country Names User-Friendly**
   - Given country data is loaded
   - Then each country shows user-friendly name (e.g., "Germany" not "DE")
   - And format is: `(display_name, code)` tuple
   - And mapping uses ISO country names or built-in mapping

3. **AC3: Technology Fields Loaded**
   - Given PATSTAT connection is established
   - When initialization completes
   - Then system loads all 35 WIPO technology fields from `tls901_techn_field_ipc`
   - And fields show format: "13 - Medical technology"
   - And format is: `(display_name, field_nr)` tuple

4. **AC4: Sectors Loaded**
   - Given technology fields are loaded
   - Then system extracts 5 distinct sectors from `tls901_techn_field_ipc.techn_sector`
   - And fields can be grouped by sector for display

5. **AC5: ReferenceData Class**
   - Given data is loaded
   - Then it is stored in `ReferenceData` dataclass with attributes:
     - `countries: List[Tuple[str, str]]` - (display_name, code)
     - `tech_fields: List[Tuple[str, int]]` - (display_name, field_nr)
     - `sectors: List[str]` - sector names
   - And `ReferenceData.load(db)` class method performs all queries
   - And module-level `reference_data` variable holds the instance

## Tasks / Subtasks

- [x] **Task 1: Create ReferenceData dataclass** (AC: 5)
  - [x] 1.1: Define dataclass with countries, tech_fields, sectors attributes
  - [x] 1.2: Add type hints for List[Tuple[...]] types
  - [x] 1.3: Add `load(db)` classmethod stub
  - [x] 1.4: Add module-level `reference_data` variable
  - [x] 1.5: Update `__all__` exports

- [x] **Task 2: Implement country loading** (AC: 1, 2)
  - [x] 2.1: Query `SELECT DISTINCT person_ctry_code FROM tls206_person`
  - [x] 2.2: Create country code to name mapping (ISO or hardcoded common countries)
  - [x] 2.3: Format as (display_name, code) tuples
  - [x] 2.4: Sort alphabetically by display name
  - [x] 2.5: Add sanity check for minimum 50 countries

- [x] **Task 3: Implement technology field loading** (AC: 3, 4)
  - [x] 3.1: Query `SELECT DISTINCT techn_field_nr, techn_field, techn_sector FROM tls901_techn_field_ipc`
  - [x] 3.2: Format as "13 - Medical technology" display names
  - [x] 3.3: Extract distinct sectors list
  - [x] 3.4: Sort fields by field number

- [x] **Task 4: Integrate with initialization** (AC: 1-5)
  - [x] 4.1: Call `ReferenceData.load(db)` after PATSTAT connection
  - [x] 4.2: Store result in module-level `reference_data`
  - [x] 4.3: Update notebook Cell 1 to show "Reference data loaded" status
  - [x] 4.4: Add timing for reference data loading

- [x] **Task 5: Validation** (AC: 1-5)
  - [x] 5.1: Verify at least 50 countries loaded (479 loaded)
  - [x] 5.2: Verify exactly 35 technology fields loaded (35 loaded)
  - [x] 5.3: Verify 5 sectors loaded (5 loaded)
  - [x] 5.4: Verify display names are formatted correctly

## Dev Notes

### Architecture Alignment

- Implements tech-spec AC3: Reference Data Loading
- Uses pattern from tech-spec ReferenceData class definition
- Pre-loading follows ADR-003 (Prevention by Design) - valid options only

### ReferenceData Class Pattern

```python
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class ReferenceData:
    """Cached reference data for dropdowns"""
    countries: List[Tuple[str, str]]      # (display_name, code)
    tech_fields: List[Tuple[str, int]]    # (display_name, field_nr)
    sectors: List[str]                     # Sector names for grouping

    @classmethod
    def load(cls, db) -> 'ReferenceData':
        """Load all reference data from PATSTAT"""
        # Query countries
        # Query tech fields
        # Extract sectors
        return cls(countries=..., tech_fields=..., sectors=...)
```

### PATSTAT Tables

| Table | Query | Purpose |
|-------|-------|---------|
| `tls206_person` | `SELECT DISTINCT person_ctry_code` | Country codes |
| `tls901_techn_field_ipc` | `SELECT DISTINCT techn_field_nr, techn_field, techn_sector` | Tech fields |

### Country Code Mapping

Common approach - hardcode major countries, use code as fallback:
```python
COUNTRY_NAMES = {
    'DE': 'Germany',
    'FR': 'France',
    'GB': 'United Kingdom',
    'US': 'United States',
    'JP': 'Japan',
    'CN': 'China',
    # ... add more as needed
}

def get_country_name(code: str) -> str:
    return COUNTRY_NAMES.get(code, code)
```

### Scope Boundaries

- **IN SCOPE:** Countries, tech fields, sectors loading
- **OUT OF SCOPE:** NUTS regions (loaded dynamically per-country in Epic 2)

### Testing Approach

Manual validation on TIP:
1. After init, check `reference_data.countries` length >= 50
2. Check `reference_data.tech_fields` length == 35
3. Check `reference_data.sectors` length == 5
4. Verify first few countries have proper names

### References

- [Source: docs/sprint-artifacts/tech-spec-epic-1.md#AC3-Reference-Data-Loading]
- [Source: docs/sprint-artifacts/tech-spec-epic-1.md#ReferenceData-Class]
- [Source: docs/epics.md#Story-1.3]
- [Source: docs/architecture.md#ADR-003-Prevention-by-Design]

## Dev Agent Record

### Context Reference

- `docs/sprint-artifacts/stories/1-3-reference-data-loading.context.xml`

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- Implemented all 5 tasks in sequence
- Added COUNTRY_NAMES mapping with 38 major countries
- ReferenceData.load() queries tls206_person and tls901_techn_field_ipc
- Sanity checks: >= 50 countries, == 35 tech fields, == 5 sectors
- Module LOC increased from 229 to 348 (well under 500 threshold)
- Bug fix: Changed `db` to `get_db()` in notebook - import binding issue
- TIP validation: 479 countries, 35 tech fields, 5 sectors loaded in 1.0s

### Completion Notes List

- Added PATSTAT model imports (TLS206_PERSON, TLS901_TECHN_FIELD_IPC)
- Added COUNTRY_NAMES dict with 38 major country code mappings
- Added _get_country_name() helper function
- Added ReferenceData dataclass with countries, tech_fields, sectors attributes
- Added ReferenceData.load(db) classmethod with PATSTAT queries
- Added sanity checks for data validation (50+ countries, 35 fields, 5 sectors)
- Added module-level reference_data variable
- Updated __all__ exports to include ReferenceData and reference_data
- Updated notebook Cell 1 with reference data loading after connection
- Updated README.md with new LOC count (348) and ReferenceData component

### File List

- MODIFIED: `tip4patlibs_core.py` (+119 LOC - ReferenceData class, country mapping)
- MODIFIED: `TIP_for_PATLIBs.ipynb` (Cell 1 updated with reference data loading)
- MODIFIED: `README.md` (LOC count updated, ReferenceData component added)

---

## Changelog

| Date | Author | Change |
|------|--------|--------|
| 2026-01-11 | SM (Bob) | Story drafted from epics.md and tech-spec |
| 2026-01-11 | Dev (Amelia) | Implementation complete - all 5 tasks done, TIP validated |
| 2026-01-11 | Team (Party) | ADR-008: Changed from person_ctry_code to appln_auth (filing jurisdiction) |
| 2026-01-11 | Team (Party) | ADR-009: Removed hardcoded JURISDICTION_NAMES, now queries tls801_country |
| 2026-01-11 | Reviewer (AI) | Senior Developer Review - APPROVED |

---

## Senior Developer Review (AI)

### Reviewer
BMad (AI Code Review)

### Date
2026-01-11

### Outcome
**✅ APPROVE**

All acceptance criteria implemented with evidence. All 22 completed tasks verified. Implementation correctly reflects ADR-008 and ADR-009 architectural changes. TIP validation passed (208 jurisdictions, 35 tech fields, 5 sectors in 1.1s).

### Summary

Story 1.3 implementation underwent architectural evolution during development per ADR-008 (filing jurisdiction) and ADR-009 (no hardcoded data). The implementation is correct, well-architected, and follows all architectural decisions.

### Acceptance Criteria Coverage

| AC | Description | Status | Evidence |
|----|-------------|--------|----------|
| AC1 | Jurisdiction Data Loaded | ✅ IMPLEMENTED | `tip4patlibs_core.py:158-176` |
| AC2 | Names User-Friendly | ✅ IMPLEMENTED | `tip4patlibs_core.py:152-156` |
| AC3 | Technology Fields Loaded | ✅ IMPLEMENTED | `tip4patlibs_core.py:178-201` |
| AC4 | Sectors Loaded | ✅ IMPLEMENTED | `tip4patlibs_core.py:203-208` |
| AC5 | ReferenceData Class | ✅ IMPLEMENTED | `tip4patlibs_core.py:115-210` |

**Summary: 5 of 5 ACs fully implemented**

### Task Completion Validation

| Category | Count | Status |
|----------|-------|--------|
| Task 1 subtasks | 5 | ✅ All verified |
| Task 2 subtasks | 5 | ✅ All verified (evolved per ADR-008/009) |
| Task 3 subtasks | 4 | ✅ All verified |
| Task 4 subtasks | 4 | ✅ All verified |
| Task 5 subtasks | 4 | ✅ All verified |

**Summary: 22 of 22 completed tasks verified, 0 falsely marked**

### Architectural Alignment

- ✅ ADR-002: ORM primary (no raw SQL)
- ✅ ADR-003: Prevention by Design
- ✅ ADR-008: Filing jurisdiction over applicant country
- ✅ ADR-009: No hardcoded reference data
- ✅ Module LOC: 341 lines (under 500 threshold)

### Security Notes

No security concerns.

### Action Items

**Code Changes Required:**
- None

**Advisory Notes:**
- Note: Story ACs reference original approach - consider updating for accuracy
- Note: Diagnostic cell in notebook can be removed before production
