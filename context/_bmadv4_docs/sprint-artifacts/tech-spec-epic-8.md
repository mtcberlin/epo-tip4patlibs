# Epic Technical Specification: MCP Server Preparation

Date: 2026-01-23
Author: BMad
Epic ID: 8
Status: Draft

---

## Overview

Epic 8 prepares the context package required for building an MCP (Model Context Protocol) server that enables AI-powered PATSTAT query generation. This epic creates the foundation for an AI assistant that can convert natural language business questions into validated BigQuery SQL queries against the PATSTAT database.

The MCP server will serve as an internal tool for rapidly expanding the Query Library (Epic 6-7, prototype-exists) and as a marketing differentiator demonstrating AI capability in the patent analytics domain.

**PRD Reference:** Phase 2 Extension - Feature: MCP Server (lines 593-631)
**Architecture Reference:** Phase 2 Architecture Extension - MCP Server Architecture (lines 946-987)

## Objectives and Scope

### In Scope

- Clean existing context JSON for BigQuery compatibility (remove `public.` prefix)
- Create summarized schema optimized for LLM context window (~10k tokens from 54k)
- Document PATSTAT table relationships (FK diagram, common JOIN patterns)
- Extract validated queries from QueryLib as few-shot examples for LLM prompting
- Implement basic MCP server with query generation capability

### Out of Scope

- Production deployment of MCP server (this is a preparation/prototype epic)
- Integration with external systems beyond local Claude Code usage
- User authentication for MCP server (internal tool only)
- Query Library UI modifications (Epic 6-7 scope)
- Real-time PATSTAT connection from MCP (generates queries only, validation done manually in TIP)

## System Architecture Alignment

This epic implements the "MCP Context Package Design" from the Phase 2 Architecture:

```
mcp_context/
├── patstat_context.json       # Business descriptions (28 tables) - Story 8.1
├── patstat_schema_summary.md  # Condensed schema (~10k tokens) - Story 8.2
├── table_relations.md         # FK diagram, common JOINs - Story 8.3
├── query_examples.json        # Validated queries as few-shot examples - Story 8.4
└── bigquery_notes.md          # BigQuery-specific syntax - Story 8.3 (combined)
```

**Architecture Decisions Referenced:**
- ADR-010: SQL Parameter Substitution Without Injection Protection
- ADR-011: Rely on BigQuery Session Caching
- ADR-012: Separate SQL Template Files

## Detailed Design

### Services and Modules

| Component | Responsibility | Inputs | Outputs |
|-----------|----------------|--------|---------|
| Context Cleaner (8.1) | Remove `public.` prefix from table names | `patstat-2026-01-19-context.json` | `mcp_context/patstat_context.json` |
| Schema Summarizer (8.2) | Compress schema to LLM-friendly format | `patstat_global_schema.json` (54k tokens) | `mcp_context/patstat_schema_summary.md` (~10k tokens) |
| Relationship Documenter (8.3) | Document FK relationships and JOIN patterns | PATSTAT documentation, existing queries | `mcp_context/table_relations.md`, `mcp_context/bigquery_notes.md` |
| Query Extractor (8.4) | Extract validated queries as examples | `context/QueryLib_for_PATLIBs.ipynb` | `mcp_context/query_examples.json` |
| MCP Server (8.5) | Serve context to Claude, generate queries | All context files | Query + description responses |

### Data Models and Contracts

#### Context JSON Schema (Story 8.1 Output)

```json
{
  "table_name": "tls201_appln",  // No public. prefix
  "table_description": "Patent applications - Main table...",
  "columns": [
    {
      "column_name": "appln_id",
      "column_description": "Unique identifier for each patent application"
    }
  ]
}
```

#### Query Example Schema (Story 8.4 Output)

```json
{
  "id": "Q01",
  "title": "Country Patent Activity & Grant Rates",
  "business_question": "Which countries have the highest patent application activity since 2015, and what are their grant rates?",
  "stakeholder": "Strategic Planning / Market Intelligence",
  "sql": "SELECT p.person_ctry_code, COUNT(DISTINCT a.appln_id) AS patent_count...",
  "parameters": [
    {"name": "year_from", "type": "year", "default": 2015},
    {"name": "min_patents", "type": "numeric", "default": 100}
  ],
  "output_columns": ["person_ctry_code", "patent_count", "granted_count", "grant_rate"],
  "execution_time_seconds": 0.55,
  "typical_rows": 20
}
```

### APIs and Interfaces

#### MCP Server Tools (Story 8.5)

The MCP server will expose tools following the MCP specification:

| Tool | Description | Parameters | Returns |
|------|-------------|------------|---------|
| `generate_patstat_query` | Generate SQL from business question | `question: string`, `parameters?: object` | `{sql: string, description: string, confidence: string}` |
| `list_available_tables` | List PATSTAT tables with descriptions | None | `{tables: TableInfo[]}` |
| `get_table_schema` | Get detailed schema for a table | `table_name: string` | `{columns: ColumnInfo[], relationships: string[]}` |
| `validate_sql_syntax` | Basic SQL syntax validation | `sql: string` | `{valid: boolean, errors?: string[]}` |

### Workflows and Sequencing

```
Story 8.1: Clean Context JSON
    │
    ├── Read patstat-2026-01-19-context.json
    ├── Remove "public." prefix from all table_name fields
    └── Write to mcp_context/patstat_context.json
         │
         ▼
Story 8.2: Create Schema Summary
    │
    ├── Read patstat_global_schema.json (54k tokens)
    ├── Extract: table names, key columns, row counts
    ├── Prioritize: most-used tables (tls201, tls206, tls207, tls230)
    ├── Summarize column descriptions
    └── Write to mcp_context/patstat_schema_summary.md (~10k tokens)
         │
         ▼
Story 8.3: Document Relationships
    │
    ├── Analyze FK relationships from schema
    ├── Document common JOIN patterns from QueryLib
    ├── Create FK diagram (text/mermaid)
    ├── Document BigQuery-specific syntax notes
    └── Write to mcp_context/table_relations.md, bigquery_notes.md
         │
         ▼
Story 8.4: Extract Query Examples
    │
    ├── Parse QueryLib_for_PATLIBs.ipynb
    ├── Extract 13 validated queries with metadata
    ├── Format as JSON for few-shot prompting
    └── Write to mcp_context/query_examples.json
         │
         ▼
Story 8.5: MCP Server Implementation
    │
    ├── Create MCP server scaffold
    ├── Load all context files at startup
    ├── Implement generate_patstat_query tool
    ├── Add system prompt with context
    └── Test with sample business questions
```

## Non-Functional Requirements

### Performance

| Metric | Target | Source |
|--------|--------|--------|
| Context loading time | < 2 seconds | MCP server startup |
| Query generation response | < 10 seconds | Tool invocation |
| Schema summary size | ~10k tokens | LLM context efficiency |
| Context JSON size | < 50KB | Efficient loading |

### Security

- MCP server runs locally only (no network exposure)
- No credentials stored in context files
- PATSTAT data is read-only, no injection risk (per ADR-010)
- Context files contain schema only, no actual patent data

### Reliability

- MCP server gracefully handles missing context files
- Invalid business questions return helpful error messages
- Generated queries include confidence indicator (high/medium/low)

### Observability

- MCP server logs query generation requests
- Track which context files are loaded successfully
- Log generation time for performance monitoring

## Dependencies and Integrations

### Input Dependencies

| Dependency | Location | Purpose |
|------------|----------|---------|
| patstat-2026-01-19-context.json | context/ | Business descriptions for 28 tables |
| patstat_global_schema.json | context/ | Full technical schema (54k tokens) |
| QueryLib_for_PATLIBs.ipynb | context/ | 13 validated queries as examples |
| patstat_bigquery_queries_v2.sql | context/ | Additional SQL reference |

### Technology Dependencies

| Component | Version | Purpose |
|-----------|---------|---------|
| Python | 3.10+ | MCP server runtime |
| mcp | latest | MCP protocol implementation |
| Claude Code | current | MCP client for testing |

### Integration Points

- **Claude Code**: Primary client for MCP server during development
- **TIP Environment**: Manual validation of generated queries (not automated)
- **Query Library**: Generated queries feed into Epic 6-7 (if formalized)

## Acceptance Criteria (Authoritative)

### Story 8.1: Clean Context JSON for BigQuery

1. **AC-8.1.1**: All `public.` prefixes removed from `table_name` fields in output JSON
2. **AC-8.1.2**: Output file created at `mcp_context/patstat_context.json`
3. **AC-8.1.3**: JSON structure preserved (same schema, just cleaned table names)
4. **AC-8.1.4**: All 28 tables present in output file

### Story 8.2: Create Schema Summary for LLM

1. **AC-8.2.1**: Schema summary is ≤ 12,000 tokens (measurable via tokenizer)
2. **AC-8.2.2**: All 28 tables listed with descriptions
3. **AC-8.2.3**: Key columns documented for top 10 most-used tables
4. **AC-8.2.4**: Row counts included for scale context
5. **AC-8.2.5**: Output file created at `mcp_context/patstat_schema_summary.md`

### Story 8.3: Document Table Relationships

1. **AC-8.3.1**: FK relationships documented for all major joins
2. **AC-8.3.2**: At least 10 common JOIN patterns documented with examples
3. **AC-8.3.3**: Mermaid diagram showing core table relationships
4. **AC-8.3.4**: BigQuery syntax notes cover: date functions, string functions, aggregations
5. **AC-8.3.5**: Output files at `mcp_context/table_relations.md` and `mcp_context/bigquery_notes.md`

### Story 8.4: Extract Validated Queries as Examples

1. **AC-8.4.1**: All 13 queries from QueryLib extracted
2. **AC-8.4.2**: Each query includes: id, title, business_question, sql, parameters, output_columns
3. **AC-8.4.3**: Execution times documented for performance context
4. **AC-8.4.4**: JSON format suitable for LLM few-shot prompting
5. **AC-8.4.5**: Output file at `mcp_context/query_examples.json`

### Story 8.5: MCP Server Implementation

1. **AC-8.5.1**: MCP server starts without errors
2. **AC-8.5.2**: `generate_patstat_query` tool generates valid BigQuery SQL for simple business questions
3. **AC-8.5.3**: Generated queries follow patterns from query_examples.json
4. **AC-8.5.4**: Server returns confidence indicator (high/medium/low) with each query
5. **AC-8.5.5**: Server can be used from Claude Code via MCP integration
6. **AC-8.5.6**: README.md documents setup and usage

## Traceability Mapping

| AC | Spec Section | Component | Test Approach |
|----|--------------|-----------|---------------|
| AC-8.1.1 | Data Models | Context Cleaner | Grep for "public." in output |
| AC-8.1.2 | Services | Context Cleaner | File existence check |
| AC-8.2.1 | NFR Performance | Schema Summarizer | Token count verification |
| AC-8.2.2 | Services | Schema Summarizer | Table count in output |
| AC-8.3.1 | Detailed Design | Relationship Documenter | Manual review |
| AC-8.3.3 | Detailed Design | Relationship Documenter | Mermaid render test |
| AC-8.4.1 | Data Models | Query Extractor | JSON array length = 13 |
| AC-8.5.2 | APIs | MCP Server | Generate query for known question |
| AC-8.5.5 | Integration | MCP Server | Claude Code connection test |

## Risks, Assumptions, Open Questions

### Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Schema summary too large for LLM context | Medium | High | Iterative compression, prioritize key tables |
| Generated queries have syntax errors | High | Medium | Include few-shot examples, add validation tool |
| MCP protocol changes | Low | Medium | Pin mcp package version |
| QueryLib queries don't cover all patterns | Medium | Low | Document gaps, expand examples over time |

### Assumptions

- **A1**: Claude Code supports MCP server integration (verified)
- **A2**: 10k tokens is sufficient for effective query generation
- **A3**: 13 example queries provide adequate few-shot coverage
- **A4**: BigQuery SQL syntax is consistent with validated queries

### Open Questions

- **Q1**: Should MCP server validate generated SQL against BigQuery syntax? (Recommendation: Yes, basic validation)
- **Q2**: How to handle ambiguous business questions? (Recommendation: Return multiple query options with confidence)
- **Q3**: Should we include negative examples (queries that don't work)? (Recommendation: Not for MVP)

## Test Strategy Summary

### Test Levels

| Level | Scope | Approach |
|-------|-------|----------|
| Unit | Individual transformations | Python assertions |
| Integration | MCP server + context files | End-to-end tool calls |
| Acceptance | Business question → valid query | Manual validation in TIP |

### Key Test Cases

1. **Context Cleaning**: Verify no `public.` prefix in output, all 28 tables present
2. **Schema Summary**: Token count ≤ 12k, all tables represented
3. **Query Extraction**: 13 queries extracted, JSON valid, parameters captured
4. **MCP Server**:
   - Start server, verify no errors
   - Call `generate_patstat_query` with Q01 business question
   - Verify generated SQL matches expected pattern
   - Call from Claude Code, verify tool appears

### Validation in TIP

Generated queries must be manually validated in TIP environment:
1. Copy generated SQL to TIP JupyterLab
2. Execute via `patstat.sql_query(query, use_legacy_sql=False)`
3. Verify results are reasonable
4. Document any corrections needed

---

_Generated by BMAD Epic Tech Context Workflow_
_Date: 2026-01-23_
