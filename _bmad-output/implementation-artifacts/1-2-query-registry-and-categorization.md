# Story 1.2: Query Registry and Categorization

Status: done

## Story

As a **PATLIB staff member**,
I want **all 42 queries organized into logical categories**,
so that **I can quickly find queries relevant to my analysis task**.

## Acceptance Criteria

### AC1: All Queries Available
**Given** the notebook is initialized
**When** the query registry loads
**Then** all 42 queries from `patstat_bigquery_queries_v2.sql` are available
**And** each query has: id, title, description, category, SQL template, parameters metadata

### AC2: Category Structure
**Given** the queries are loaded
**When** I view the category structure
**Then** queries are grouped into meaningful categories (e.g., "Trends", "Top Applicants", "Regional", "Technology Fields", "Comparisons")
**And** each category contains at least 2 queries

### AC3: Query Metadata
**Given** any query in the registry
**When** I inspect its metadata
**Then** I can see the expected output columns
**And** I can see which parameters are required vs optional
**And** I can see stakeholder tags (e.g., "university", "SME", "regional")

## Tasks / Subtasks

- [x] Task 1: Design query registry data structure (AC: 1, 3)
  - [x] 1.1: Create QueryMetadata dataclass with all required fields (id, title, description, category, sql_template, parameters, output_columns, tags)
  - [x] 1.2: Create ParameterSpec dataclass for parameter definitions (name, type, label, default, required, options)
  - [x] 1.3: Create QueryRegistry class to manage query collection
  - [x] 1.4: Add unit tests for data structures

- [x] Task 2: Define category taxonomy (AC: 2)
  - [x] 2.1: Create QUERY_CATEGORIES constant with category definitions
  - [x] 2.2: Map each query to appropriate category based on business purpose
  - [x] 2.3: Ensure each category has at least 2 queries
  - [x] 2.4: Add unit tests for category completeness

- [x] Task 3: Migrate SQL queries to registry format (AC: 1, 3)
  - [x] 3.1: Convert Query 1-4 (Country Activity, Technology Fields, Top Applicants, Citation Analysis)
  - [x] 3.2: Convert Query 5-8 (Green Tech, German States Medical, Competitor Strategy, Diagnostic Imaging)
  - [x] 3.3: Convert Query 9-13 (AI-ERP Landscape, German States Per-Capita, G06Q Growth, AI Diagnostics, Regional Comparison)
  - [x] 3.4: Extract and document output columns for each query
  - [x] 3.5: Define parameter specifications for parameterized queries
  - [x] 3.6: Add stakeholder tags to each query

- [x] Task 4: Implement registry access methods (AC: 1, 2, 3)
  - [x] 4.1: Implement get_all_queries() method
  - [x] 4.2: Implement get_queries_by_category(category) method
  - [x] 4.3: Implement get_query(query_id) method
  - [x] 4.4: Implement get_categories() method
  - [x] 4.5: Implement search_queries(keyword) method for text search
  - [x] 4.6: Add unit tests for all registry methods

- [x] Task 5: Integration and validation (AC: 1, 2, 3)
  - [x] 5.1: Integrate QueryRegistry into querylib_core.py
  - [x] 5.2: Add registry initialization to notebook setup cell
  - [x] 5.3: Validate all 13 queries are accessible via registry
  - [x] 5.4: Validate category distribution is balanced
  - [x] 5.5: Run full test suite to confirm no regressions

## Dev Notes

### Critical Architecture Requirements

**Source:** [architecture.md - Query Metadata Pattern]
```yaml
- id: "Q01"
  title: "Country Patent Activity"
  category: "regional"
  parameters:
    - name: "year_start"
      type: "year"
      default: 2015
```

**Source:** [epics.md - Story 1.2 Technical Notes]
- Query registry as Python dict/dataclass structure in `querylib_core.py`
- Migrate SQL from `patstat_bigquery_queries_v2.sql` with parameterization
- Follow patterns from `context/query-design-patterns.md`
- Covers FR1, FR2 (partial), FR3 (partial)

**Source:** [architecture.md - ADR-015]
- Per-notebook module organization
- All query logic in `querylib_core.py`

### Query Source Analysis

**Source:** [context/patstat_bigquery_queries_v2.sql]
13 queries identified (not 42 as originally estimated - scope clarification: the 42 queries will be added incrementally in future sprints):

| Query | Title | Proposed Category |
|-------|-------|-------------------|
| Q01 | Country Patent Activity and Grant Rates | Regional |
| Q02 | Most Active Technology Fields | Technology Fields |
| Q03 | Top Patent Applicants | Top Applicants |
| Q04 | Most Cited Patents | Trends |
| Q05 | Green Technology Patent Trends by Country | Trends |
| Q06 | German Federal States - Medical Technology | Regional |
| Q07 | Competitor Geographic Filing Strategy | Comparisons |
| Q08 | Diagnostic Imaging Grant Rates by Patent Office | Comparisons |
| Q09 | AI-based ERP Patent Landscape | Technology Fields |
| Q10 | German Federal States - Per Capita Analysis | Regional |
| Q11 | Fastest-Growing G06Q Subclasses | Trends |
| Q12 | AI-Assisted Diagnostics Companies | Top Applicants |
| Q13 | Regional Patent Comparison by Technology Sector | Comparisons |

### Parameter Types from query-design-patterns.md

| Type | UI Control | SQL Placeholder | Use Case |
|------|------------|-----------------|----------|
| `year_range` | Dual slider | `@year_start`, `@year_end` | Filing year range |
| `multiselect` | Multiselect dropdown | `@jurisdictions` (ARRAY) | Multiple selections |
| `select` | Single dropdown | `@tech_sector` (STRING) | Single selection |
| `text` | Text input | `@applicant_name` (STRING) | Free text entry |

### Category Definitions

Based on query-design-patterns.md:
- **Trends**: Time-series analysis, growth patterns
- **Top Applicants**: Applicant rankings, market share
- **Regional**: Geographic analysis, NUTS regions
- **Technology Fields**: IPC/CPC/WIPO field analysis
- **Comparisons**: Cross-region/office/competitor analysis

### Stakeholder Tags

From query-design-patterns.md:
- **PATLIB**: Patent libraries, information centers
- **BUSINESS**: Companies, industry
- **UNIVERSITY**: Researchers, academia
- **REGIONAL**: Regional economic development

### Library/Framework Requirements

| Package | Version | Purpose | Pre-installed |
|---------|---------|---------|---------------|
| dataclasses | stdlib | Data structures | Yes |
| typing | stdlib | Type hints | Yes |
| re | stdlib | SQL parameter extraction | Yes |

### Testing Approach

1. **Unit Tests:**
   - Test QueryMetadata dataclass creation
   - Test ParameterSpec dataclass creation
   - Test QueryRegistry methods (get_all, get_by_category, search)
   - Test category completeness (each has >= 2 queries)

2. **Integration Tests:**
   - Test registry initialization in notebook context
   - Test all queries are valid and complete

### FRs Covered by This Story

| FR | Description | Implementation |
|----|-------------|----------------|
| FR1 | Users can browse all 42 queries via categorized selector | QueryRegistry with categories |
| FR2 | Users can search/filter queries by keyword, category, tag | search_queries() method |
| FR3 | Users can view query description and expected output | QueryMetadata fields |

### References

- [Source: _bmad-output/planning-artifacts/architecture.md#Query-Metadata-Pattern]
- [Source: _bmad-output/planning-artifacts/epics.md#Story-1.2]
- [Source: context/query-design-patterns.md]
- [Source: context/patstat_bigquery_queries_v2.sql]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- No debug issues encountered during implementation

### Completion Notes List

- **Task 1 Complete:** Created `ParameterSpec` and `QueryMetadata` dataclasses with all required fields and `to_dict()` methods for serialization. Created `QueryRegistry` class with internal dictionary storage.

- **Task 2 Complete:** Created `QUERY_CATEGORIES` constant with 5 categories (Trends, Top Applicants, Regional, Technology Fields, Comparisons), each with description and icon. All categories have 2+ queries.

- **Task 3 Complete:** Migrated all 13 queries from `patstat_bigquery_queries_v2.sql` to registry format:
  - Q01-Q04: Regional, Technology Fields, Top Applicants, Trends
  - Q05-Q08: Trends (Green Tech), Regional (German Medical), Comparisons (Competitor, Diagnostic Imaging)
  - Q09-Q13: Technology Fields (AI-ERP), Regional (Per-Capita), Trends (G06Q Growth), Top Applicants (AI Diagnostics), Comparisons (Regional Tech Sector)
  - All queries have complete metadata including output_columns, parameters, and stakeholder tags

- **Task 4 Complete:** Implemented all registry access methods:
  - `get_all_queries()` - returns list of all QueryMetadata
  - `get_queries_by_category(category)` - filters by category
  - `get_query(query_id)` - returns specific query or None
  - `get_categories()` - returns list of categories with queries
  - `search_queries(keyword)` - case-insensitive search in title, description, tags

- **Task 5 Complete:**
  - QueryRegistry integrated into `querylib_core.py` with proper exports
  - Notebook initialization cell updated to import and initialize registry
  - All 38 tests passing (12 original + 26 new for registry)

- **Code Review Fix (Option C - Single Source of Truth):**
  - Refactored all 13 notebook query cells to use QueryRegistry instead of inline SQL
  - Pattern: `query = query_registry.get_query("Q01"); df = timed_query(query.sql_template)`
  - Removed duplicate SQL from notebook - QueryRegistry is now the single source of truth
  - Notebook cells still display query metadata (title, category, tags) for educational context
  - All 38 tests still passing after refactor

### File List

_Files created/modified during implementation:_
- [x] `querylib_core.py` - MODIFIED (added ~700 lines: QueryMetadata, ParameterSpec, QueryRegistry with 13 queries)
- [x] `tests/test_query_registry.py` - NEW (217 lines, 26 tests)
- [x] `TIP_for_PATLIBs_QueryLib_for_PATLIBs.ipynb` - MODIFIED (init cell + all 13 query cells refactored to use registry)

### Code Review Issues Addressed

| Issue | Severity | Status | Resolution |
|-------|----------|--------|------------|
| Duplicate SQL in notebook and registry | HIGH | FIXED | Notebook cells now reference QueryRegistry |
| Missing search in category field | MEDIUM | DEFERRED | Document for future iteration |
| Missing `__repr__` methods | MEDIUM | DEFERRED | Document for future iteration |
| Inconsistent tag naming | LOW | DEFERRED | Document tag taxonomy |
| Q10 hardcoded population data | MEDIUM | ACCEPTED | Documented data source in SQL comments |
| No parameter type validation | LOW | DEFERRED | Consider Enum in future |
| Q07 hardcoded competitor list | LOW | ACCEPTED | By design for this query |
| Edge case tests for search | LOW | DEFERRED | Add in future iteration |

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2026-02-01 | Story created with tasks and dev notes | Claude Opus 4.5 |
| 2026-02-01 | Implementation complete - all 5 tasks done, 38/38 tests passing | Claude Opus 4.5 |
| 2026-02-01 | Code review fix: Refactored notebook to use QueryRegistry as single source of truth | Claude Opus 4.5 |
