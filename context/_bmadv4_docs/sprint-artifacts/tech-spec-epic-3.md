# Epic Technical Specification: Query Engine

Date: 2026-01-11
Author: BMad
Epic ID: 3
Status: Draft

---

## Overview

Epic 3 implements the query engine layer for TIP for PATLIBs, connecting the user's selection parameters (Epic 2) to PATSTAT database queries that return clean DataFrames for visualization (Epic 4). This epic transforms the AnalysisState selections into efficient SQL queries using the EPO patstat ORM library with SQLAlchemy, handling trend analysis, top applicants ranking, and technology breakdown aggregations.

The PatstatQueries class centralizes all database interactions, following Architecture ADR-002's dual approach: ORM for simple queries and raw SQL for complex aggregations. Query execution includes progress feedback for user transparency.

## Objectives and Scope

### In Scope

- PatstatQueries class with centralized query methods
- Trend query: Applications/inventions by year for line charts
- Top applicants query: Ranked applicants with SQL aggregation
- Progress indicator during query execution
- Error handling and zero-results messaging
- SME filter integration (<100 applications)
- Region filter integration (NUTS codes)

### Out of Scope

- Visualizations (Epic 4)
- Export functionality (Epic 5)
- Query caching (deferred per Architecture)
- Geographic distribution query (simplified to regional bar chart in Epic 4)
- Complex IPC drill-down (future enhancement)

## System Architecture Alignment

### Components Referenced

| Component | Purpose | Source |
|-----------|---------|--------|
| `PatstatQueries` | Query builder class | Architecture - Query Pattern |
| `AnalysisState` | State object for filters | Epic 1 / ADR-006 |
| `PatstatClient` | Database connection | Epic 1 / Story 1.2 |
| `tls201_appln` | Applications table | Architecture - Data Architecture |
| `tls206_person` | Applicants table | Architecture - Data Architecture |
| `tls207_pers_appln` | Person-application link | Architecture - Data Architecture |
| `tls230_appln_techn_field` | Pre-computed tech fields | Architecture - Data Architecture |
| `tls209_appln_ipc` | IPC classifications | Architecture - Data Architecture |

### Architecture Constraints

- **ADR-002**: ORM primary with SQL escape hatch for complex aggregations
- **ADR-003**: Prevention by design - state.is_valid() already validated before queries run
- **ADR-008**: Use `appln_auth` (filing jurisdiction) for country filtering
- **Performance**: Queries must complete within 60 seconds for 5-year spans

## Detailed Design

### Services and Modules

| Component | Responsibility | Inputs | Outputs |
|-----------|----------------|--------|---------|
| `PatstatQueries.__init__(db)` | Initialize with DB session | SQLAlchemy session | Configured instance |
| `PatstatQueries.get_trend_data(state)` | Yearly application/invention counts | AnalysisState | DataFrame[year, application_count, invention_count] |
| `PatstatQueries.get_top_applicants(state, limit)` | Top N applicants ranked | AnalysisState, int | DataFrame[applicant_name, application_count, invention_count, country] |
| `PatstatQueries.get_tech_breakdown(state)` | IPC distribution for treemap | AnalysisState | DataFrame[ipc_class, count] |
| `PatstatQueries.get_regional_distribution(state)` | NUTS region counts | AnalysisState | DataFrame[region, region_label, count] |
| `run_analysis(state, queries)` | Execute all queries with progress | AnalysisState, PatstatQueries | Dict of DataFrames |

### Data Models and Contracts

#### Input: AnalysisState (from Epic 1)

```python
@dataclass
class AnalysisState:
    country: Optional[str]      # appln_auth code (e.g., "DE", "EP")
    region: Optional[str]       # NUTS code (e.g., "DE2")
    tech_mode: str              # "field" or "ipc"
    tech_field: Optional[int]   # WIPO field number 1-35
    ipc_codes: List[str]        # Max 5 IPC codes
    year_start: int             # 2000-2024
    year_end: int               # 2000-2024
    sme_filter: bool            # <100 applications filter
```

#### Output DataFrames

**Trend Data:**
```
| year (int) | application_count (int) | invention_count (int) |
|------------|------------------------|----------------------|
| 2019       | 1234                   | 987                  |
| 2020       | 1456                   | 1102                 |
```

**Top Applicants:**
```
| applicant_name (str) | application_count (int) | invention_count (int) | country (str) |
|---------------------|------------------------|----------------------|---------------|
| SIEMENS AG          | 523                    | 412                  | DE            |
| ROBERT BOSCH GMBH   | 498                    | 387                  | DE            |
```

**Tech Breakdown:**
```
| ipc_class (str) | ipc_label (str) | count (int) |
|-----------------|-----------------|-------------|
| A61B            | Diagnosis...    | 234         |
| A61C            | Dentistry...    | 156         |
```

**Regional Distribution:**
```
| region (str) | region_label (str) | count (int) |
|--------------|-------------------|-------------|
| DE2          | Bayern            | 1234        |
| DE7          | Hessen            | 987         |
```

### APIs and Interfaces

#### PatstatQueries Class

```python
class PatstatQueries:
    """Query builder for PATSTAT database operations."""

    def __init__(self, db):
        """Initialize with PATSTAT database session."""
        self.db = db

    def get_trend_data(self, state: AnalysisState) -> pd.DataFrame:
        """
        Get yearly application and invention counts.

        Returns DataFrame with columns: year, application_count, invention_count
        Grouped by appln_filing_year, ordered ascending.
        """
        ...

    def get_top_applicants(self, state: AnalysisState, limit: int = 10) -> pd.DataFrame:
        """
        Get top N applicants by application count.

        Uses SQL escape hatch for complex aggregation.
        Returns DataFrame with columns: applicant_name, application_count,
                                        invention_count, country
        Ordered by application_count DESC.
        """
        ...

    def get_tech_breakdown(self, state: AnalysisState) -> pd.DataFrame:
        """
        Get IPC class distribution for technology treemap.

        Returns DataFrame with columns: ipc_class, ipc_label, count
        Limited to top 20 IPC classes by count.
        """
        ...

    def get_regional_distribution(self, state: AnalysisState) -> pd.DataFrame:
        """
        Get patent counts by NUTS region.

        Returns DataFrame with columns: region, region_label, count
        Only for applicants with NUTS codes matching country.
        """
        ...
```

#### Query Execution Function

```python
def run_analysis(state: AnalysisState, queries: PatstatQueries) -> Dict[str, pd.DataFrame]:
    """
    Execute all queries with progress feedback.

    Returns dict with keys: 'trend', 'applicants', 'tech_breakdown', 'regional'
    Shows progress via ipywidgets Output widget.
    Handles errors gracefully - returns partial results if some queries fail.
    """
    ...
```

### Workflows and Sequencing

```
User clicks "Run Analysis"
    │
    ▼
state.is_valid() check (already done by button enable/disable)
    │
    ▼
run_analysis(state, queries) called
    │
    ├─► Show progress: "Querying PATSTAT..."
    │
    ├─► Query 1: get_trend_data(state)
    │   └─► Update: "Loading trend data..."
    │
    ├─► Query 2: get_top_applicants(state)
    │   └─► Update: "Loading top applicants..."
    │
    ├─► Query 3: get_tech_breakdown(state)
    │   └─► Update: "Loading technology breakdown..."
    │
    ├─► Query 4: get_regional_distribution(state)
    │   └─► Update: "Loading regional data..."
    │
    ▼
Return results dict to Epic 4 visualization
    │
    ▼
Show: "Analysis complete" or error messages
```

## Non-Functional Requirements

### Performance

| Metric | Target | Measurement |
|--------|--------|-------------|
| Trend query (5 years) | <30 seconds | Time from execution to DataFrame return |
| Top applicants query | <30 seconds | Time from execution to DataFrame return |
| Full analysis (4 queries) | <60 seconds | Total time for run_analysis() |
| Query timeout | 120 seconds | Maximum wait before abort |

**Optimization Strategies:**
- Use pre-computed `tls230_appln_techn_field` for tech field mode (avoids IPC pattern matching)
- Apply country/year filters early in WHERE clause
- Limit results (top 10/25 applicants, top 20 IPC classes)
- Use psn_name for grouping (PATSTAT standardized names)

### Security

- All queries use parameterized SQL (prevent SQL injection)
- Read-only access to PATSTAT (no mutation risk)
- No user credentials handled (TIP platform manages auth)

### Reliability/Availability

- Graceful degradation: If one query fails, others continue
- Connection retry: PatstatClient handles reconnection
- Timeout handling: Long-running queries abort with user message
- Zero results: Return empty DataFrame with proper schema (not None)

### Observability

- Progress messages displayed in Output widget
- Query timing logged (optional, for debugging)
- Error messages include query type that failed
- Data quality warnings for known PATSTAT issues

## Dependencies and Integrations

### Python Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `pandas` | TIP-provided | DataFrame operations |
| `sqlalchemy` | TIP-provided | ORM/SQL execution |
| `epo.tipdata.patstat` | TIP-provided | PATSTAT client and models |
| `ipywidgets` | TIP-provided | Progress display |

### PATSTAT Tables Required

| Table | Columns Used | Rows (approx) |
|-------|--------------|---------------|
| `tls201_appln` | appln_id, appln_auth, appln_filing_year, docdb_family_id | 137M |
| `tls206_person` | person_id, psn_name, person_ctry_code, nuts | 96M |
| `tls207_pers_appln` | appln_id, person_id, applt_seq_nr | 300M |
| `tls230_appln_techn_field` | appln_id, techn_field_nr, weight | 200M |
| `tls209_appln_ipc` | appln_id, ipc_class_symbol | 450M |
| `tls904_nuts` | nuts, nuts_level, nuts_label | 2K |

### Integration Points

- **Input**: AnalysisState from Epic 2 WidgetFactory
- **Output**: DataFrames consumed by Epic 4 ChartBuilder
- **Storage**: Results stored in module-level `analysis_results` dict

## Acceptance Criteria (Authoritative)

### AC1: PatstatQueries Class Initialization
- Given a valid PATSTAT database session
- When PatstatQueries(db) is created
- Then instance stores db reference and is ready for queries

### AC2: Trend Data Query
- Given valid AnalysisState with country, tech_field, year_range
- When get_trend_data(state) is called
- Then returns DataFrame with year, application_count, invention_count columns
- And data is grouped by year, ordered ascending
- And respects all state filters (country, tech_field, years, region, sme_filter)

### AC3: Top Applicants Query
- Given valid AnalysisState
- When get_top_applicants(state, limit=10) is called
- Then returns DataFrame with applicant_name, application_count, invention_count, country
- And data is ordered by application_count DESC
- And limited to specified limit

### AC4: Tech Breakdown Query
- Given valid AnalysisState
- When get_tech_breakdown(state) is called
- Then returns DataFrame with ipc_class, ipc_label, count
- And shows IPC distribution within selected tech field or entered IPC codes

### AC5: Regional Distribution Query
- Given valid AnalysisState with country having NUTS data
- When get_regional_distribution(state) is called
- Then returns DataFrame with region, region_label, count
- And only includes regions matching country's NUTS hierarchy

### AC6: Query Progress Feedback
- Given user clicks Run Analysis
- When queries execute
- Then user sees progress messages ("Querying PATSTAT...", "Loading trend data...", etc.)
- And spinner/loading indicator is visible

### AC7: Query Completion Status
- Given all queries complete successfully
- When results are ready
- Then user sees "Analysis complete" message
- And results are stored for Epic 4 visualization

### AC8: Error Handling
- Given a query fails (timeout, connection error)
- When error occurs
- Then user sees friendly error message
- And other queries continue executing
- And partial results are available

### AC9: Zero Results Handling
- Given query returns no data
- When results displayed
- Then user sees "No patents found for this selection"
- And suggestions for adjusting filters are shown

### AC10: SME Filter Application
- Given state.sme_filter = True
- When queries execute
- Then only applicants with <100 total applications are included

## Traceability Mapping

| AC | Spec Section | Component/API | Test Idea |
|----|--------------|---------------|-----------|
| AC1 | PatstatQueries Class | `__init__(db)` | Create instance, verify db attribute |
| AC2 | get_trend_data | ORM query with GROUP BY | Execute with DE/field13/2019-2023, verify DataFrame schema |
| AC3 | get_top_applicants | SQL escape hatch | Execute, verify top 10 ordered DESC |
| AC4 | get_tech_breakdown | IPC aggregation query | Verify IPC class distribution |
| AC5 | get_regional_distribution | NUTS join query | Execute for DE, verify NUTS regions |
| AC6 | run_analysis | Progress widget | Click Run, observe progress messages |
| AC7 | run_analysis | Completion handling | Run full analysis, verify complete message |
| AC8 | Error handling | try/except blocks | Simulate timeout, verify graceful handling |
| AC9 | Zero results | DataFrame length check | Query obscure combination, verify message |
| AC10 | SME filter | Subquery constraint | Enable SME filter, verify reduced results |

## Risks, Assumptions, Open Questions

### Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Query timeout on large date ranges | Medium | High | Performance tips in Epic 2 pre-warn users; implement timeout |
| PATSTAT connection drops mid-query | Low | Medium | PatstatClient handles reconnection; show retry message |
| SME filter query too slow (subquery) | Medium | Medium | Consider pre-computed SME flag or alternative approach |

### Assumptions

- PATSTAT database is available and responsive on TIP platform
- `psn_name` (standardized names) provides good applicant grouping
- `tls230_appln_techn_field` is complete and accurate for tech field filtering
- TIP environment has sufficient memory for query result DataFrames
- PatstatClient from epo.tipdata.patstat provides stable ORM session

### Open Questions

1. **Q: Should we cache query results?**
   A: Deferred per Architecture. DataFrames persist in memory; no explicit caching for MVP.

2. **Q: How to handle very long applicant names in results?**
   A: Return full names; truncation handled in Epic 4 visualization layer.

3. **Q: Should queries run in parallel?**
   A: Sequential for simplicity. Parallel execution is future enhancement if needed.

## Test Strategy Summary

### Manual Testing on TIP

1. **Happy Path**: Select DE, Field 13 (Medical), 2019-2023, run analysis
   - Verify all 4 queries return data
   - Verify progress messages appear
   - Verify completion message

2. **Edge Cases**:
   - Zero results: Select obscure country/field combination
   - Large range: Select 2000-2024, verify performance tip was shown
   - SME filter: Enable, verify reduced applicant counts
   - Regional: Select DE, verify NUTS regions returned

3. **Error Cases**:
   - Simulated timeout (if possible)
   - Invalid state (should not reach query - button disabled)

### Validation Approach

- Manual testing per project scope (no automated unit tests)
- Compare query results against known PATSTAT data for sanity check
- Verify DataFrame schemas match specification

---

*Generated by BMAD Epic Tech Context Workflow*
*Date: 2026-01-11*
