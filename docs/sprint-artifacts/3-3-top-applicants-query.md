# Story 3.3: Top Applicants Query

Status: ready-for-dev

## Story

As a **PATLIB user**,
I want **to see who files the most patents in my selection**,
so that **I can identify key players in the technology field**.

## Acceptance Criteria

1. **AC1: Method Implementation**
   - Given PatstatQueries class
   - When `get_top_applicants(state, limit=10)` is called
   - Then returns DataFrame with applicant rankings
   - And method signature matches: `def get_top_applicants(self, state: AnalysisState, limit: int = 10) -> pd.DataFrame`

2. **AC2: DataFrame Schema**
   - Given top applicants query completes
   - When DataFrame is returned
   - Then it has columns:
     - `applicant_name` (str): psn_name from tls206_person
     - `application_count` (int): Number of applications
     - `invention_count` (int): Unique docdb_family_id count
     - `country` (str): Applicant's person_ctry_code
   - And results ordered by application_count DESC

3. **AC3: SQL Escape Hatch Pattern**
   - Given complex aggregation required
   - When query is built
   - Then uses raw SQL via execute_sql() or text() (ADR-002)
   - And query handles GROUP BY with multiple aggregations efficiently

4. **AC4: Limit Parameter**
   - Given `limit` parameter is provided
   - When query executes
   - Then returns at most `limit` rows
   - And default limit is 10
   - And limit options support 10 or 25

5. **AC5: Tech Field Mode Support**
   - Given `state.tech_mode == "field"`
   - When query executes
   - Then joins tls230_appln_techn_field for tech field filtering
   - And filters by `techn_field_nr = state.tech_field`

6. **AC6: IPC Mode Support**
   - Given `state.tech_mode == "ipc"`
   - When query executes
   - Then joins tls209_appln_ipc for IPC filtering
   - And applies LIKE pattern for each IPC code

7. **AC7: Region Filter Support**
   - Given `state.region` is set
   - When query executes
   - Then filters applicants by NUTS region
   - And only counts applications from applicants in that region

8. **AC8: SME Filter Support**
   - Given `state.sme_filter == True`
   - When query executes
   - Then excludes applicants with >=100 total applications
   - And uses subquery or CTE for efficiency

9. **AC9: Name Quality Handling**
   - Given PATSTAT applicant names vary in quality
   - When results are returned
   - Then uses `psn_name` (standardized name) for grouping
   - And handles NULL names gracefully (exclude or label)

10. **AC10: Error Handling**
    - Given query encounters an error
    - When error occurs
    - Then returns empty DataFrame with correct schema
    - And logs error message

## Tasks / Subtasks

- [ ] **Task 1: Implement get_top_applicants() method** (AC: 1, 2, 3)
  - [ ] 1.1: Replace stub with full implementation in PatstatQueries
  - [ ] 1.2: Build raw SQL query with proper joins
  - [ ] 1.3: Add parameterized query for SQL injection prevention
  - [ ] 1.4: Convert results to DataFrame with correct schema

- [ ] **Task 2: Implement query filters** (AC: 5, 6, 7, 8)
  - [ ] 2.1: Add tech field mode filter (tls230 join)
  - [ ] 2.2: Add IPC mode filter (tls209 join)
  - [ ] 2.3: Add region filter (NUTS LIKE pattern)
  - [ ] 2.4: Add SME filter (subquery for <100 applications)

- [ ] **Task 3: Implement limit and ordering** (AC: 4)
  - [ ] 3.1: Add ORDER BY application_count DESC
  - [ ] 3.2: Add LIMIT clause with parameter
  - [ ] 3.3: Test with limit=10 and limit=25

- [ ] **Task 4: Handle name quality** (AC: 9)
  - [ ] 4.1: Use psn_name for grouping
  - [ ] 4.2: Filter out NULL or empty names
  - [ ] 4.3: Test with various applicant types

- [ ] **Task 5: Add error handling** (AC: 10)
  - [ ] 5.1: Wrap execution in try/except
  - [ ] 5.2: Return empty DataFrame on error
  - [ ] 5.3: Log error details for debugging

- [ ] **Task 6: Integration with UI** (AC: 1-10)
  - [ ] 6.1: Update _on_run_click() to call get_top_applicants()
  - [ ] 6.2: Store results in analysis_results['applicants']
  - [ ] 6.3: Add progress message during execution

- [ ] **Task 7: Validation** (AC: 1-10)
  - [ ] 7.1: Test with DE + Field 13 + 2019-2023
  - [ ] 7.2: Verify top applicants list is reasonable
  - [ ] 7.3: Compare with known German patent leaders
  - [ ] 7.4: Test IPC mode with A61B

## Dev Notes

### Architecture Alignment

From Architecture ADR-002: This query uses the SQL escape hatch pattern because:
- Complex GROUP BY with multiple aggregations
- Need to optimize join order for performance
- Raw SQL gives better control over query plan

### Query Pattern from Tech Spec

```sql
SELECT
    p.psn_name as applicant_name,
    p.person_ctry_code as country,
    COUNT(DISTINCT a.appln_id) as application_count,
    COUNT(DISTINCT a.docdb_family_id) as invention_count
FROM tls201_appln a
JOIN tls207_pers_appln pa ON a.appln_id = pa.appln_id
JOIN tls206_person p ON pa.person_id = p.person_id
JOIN tls230_appln_techn_field tf ON a.appln_id = tf.appln_id  -- or tls209 for IPC
WHERE a.appln_auth = :country
  AND tf.techn_field_nr = :tech_field
  AND a.appln_filing_year BETWEEN :year_start AND :year_end
  AND pa.applt_seq_nr > 0  -- applicants only
  AND p.psn_name IS NOT NULL
GROUP BY p.psn_name, p.person_ctry_code
ORDER BY application_count DESC
LIMIT :limit
```

### SME Filter Pattern

```sql
-- Subquery to identify SME applicants (< 100 total applications)
AND pa.person_id IN (
    SELECT person_id
    FROM tls207_pers_appln
    GROUP BY person_id
    HAVING COUNT(appln_id) < 100
)
```

### PATSTAT Notes

- `psn_name` = PATSTAT Standardized Name (best for grouping)
- `person_ctry_code` = Applicant country (may differ from filing jurisdiction)
- `applt_seq_nr > 0` filters to applicants only (excludes inventors)
- Consider performance: index on (appln_auth, appln_filing_year)

### References

- [Source: docs/sprint-artifacts/tech-spec-epic-3.md#AC3-Top-Applicants-Query]
- [Source: docs/epics.md#Story-3.3]
- [Source: docs/architecture.md#ADR-002]
- [Source: docs/architecture.md#SQL-Pattern]

---

## Changelog

| Date | Author | Change |
|------|--------|--------|
| 2026-01-12 | SM (Bob) | Story drafted from epics.md and tech-spec-epic-3.md |
