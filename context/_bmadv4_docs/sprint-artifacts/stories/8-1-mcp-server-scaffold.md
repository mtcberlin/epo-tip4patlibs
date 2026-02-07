# Story 8.1: MCP Server Scaffold

Status: complete

## Story

As a **developer using Claude Code**,
I want a **minimal working MCP server for PATSTAT query generation**,
so that **I can discover what context and structure the LLM actually needs**.

## Acceptance Criteria

1. MCP server starts without errors when configured in Claude Code
2. Server exposes schema discovery tools: `list_tables`, `get_table_schema`, `search_tables`, `get_table_samples`
3. Tools provide sufficient context for LLM to generate valid BigQuery SQL
4. Server loads table definitions from extensible `data/tables/` directory (one JSON per table)
5. Server loads sample data from extensible `data/samples/` directory (one JSON per table)
6. Adding new tables requires only adding JSON files (no code changes)
7. README.md documents setup and usage

## Tasks / Subtasks

- [x] **Task 1: Project Setup** (AC: 1, 6)
  - [x] Create `mcp-server/` directory structure
  - [x] Initialize Python project with `pyproject.toml`
  - [x] Add `mcp` package dependency
  - [x] Create README.md with setup instructions

- [x] **Task 2: Basic MCP Server** (AC: 1, 2)
  - [x] Create `server.py` with MCP server scaffold
  - [x] Register `generate_query` tool (initial approach)
  - [x] Implement tool handler that returns response with context

- [x] **Task 3: Context Loading** (AC: 4)
  - [x] Load `context/*context*.json` at startup (initial approach)
  - [x] Load `context/*schema*.json` at startup
  - [x] Store context in ContextStore class

- [x] **Task 4: System Prompt** (AC: 5)
  - [x] Create configurable prompt template (`prompts/default.txt`)
  - [x] Instruct LLM to generate BigQuery SQL (no `public.` prefix)
  - [x] Support custom prompt via PROMPT_FILE env var

- [x] **Task 5: Integration Test** (AC: 1, 2, 3)
  - [x] Configure MCP server in Claude Code settings
  - [x] Verify server appears in available tools
  - [x] Test with simple business question
  - [x] Document what works and what doesn't

- [x] **Task 6: Multi-Tool Refactor** (AC: 2, 3, 4, 5)
  - [x] Split monolithic context into per-table JSON files in `data/tables/`
  - [x] Implement `list_tables` tool - returns all table names + descriptions
  - [x] Implement `get_table_schema` tool - returns columns for specific table
  - [x] Implement `search_tables` tool - keyword search across tables/columns
  - [x] Update ContextStore to lazy-load from tables directory
  - [x] Test agentic workflow: list → identify → get schema → generate SQL

- [x] **Task 7: Column Type Accuracy** (AC: 3)
  - [x] Merge types from `patstat_global_schema.json` into table JSON files
  - [x] Types mapped: INTEGER→INT64, VARCHAR→STRING, DATE→DATE, FLOAT→FLOAT64
  - [x] Verified: SQL generated from clean folder uses correct type comparisons

- [x] **Task 8: Sample Data Tool** (AC: 2, 5)
  - [x] Extract sample data from `patstat_global_schema.json` into `data/samples/` directory
  - [x] Create 28 per-table sample JSON files (10 rows each)
  - [x] Implement `get_table_samples` tool - returns sample rows for a table
  - [x] Verified: Sample data helps understand actual data values and formats

## Dev Notes

### Approach: Discovery-Driven

This is Story 1 of a discovery-driven epic. The goal is to BUILD FIRST, then learn what context structure the LLM actually needs.

**Do NOT over-engineer:**
- Load raw context files as-is
- Minimal system prompt
- No validation, no fancy formatting
- Just get it working

**What we'll learn:**
- Does the LLM generate valid queries?
- Is 54k tokens of schema too much?
- What context is missing?
- What format works best?

These learnings feed into Stories 8-2, 8-3, 8-4.

### Technical Reference

**Multi-Tool MCP Pattern (Current):**
```python
# Four tools for agentic schema discovery:
# 1. list_tables - overview of all tables
# 2. get_table_schema(table_name) - column details with types
# 3. search_tables(keyword) - find relevant tables
# 4. get_table_samples(table_name) - sample data rows

# Agent workflow:
# User: "Austrian applicants in 2021"
# Agent: list_tables() → identify tls201_appln, tls206_person, tls207_pers_appln
# Agent: get_table_schema("tls201_appln") → appln_id (INT64), appln_filing_year (INT64), ...
# Agent: get_table_schema("tls207_pers_appln") → applt_seq_nr (INT64), invt_seq_nr (INT64), ...
# Agent: get_table_samples("tls207_pers_appln") → see applt_seq_nr=1 means applicant
# Agent: Generate SQL using ONLY MCP-provided context
```

**Extensible Table Format:**
```json
// data/tables/tls201_appln.json
{
  "table_name": "tls201_appln",
  "description": "Core patent application table...",
  "columns": [
    {"name": "appln_id", "type": "INT64", "description": "Unique identifier..."},
    {"name": "appln_filing_year", "type": "INT64", "description": "Year of filing..."}
  ]
}
```

**Data Assets:**
- `data/tables/*.json` - 28 per-table schema files with columns and types (extensible)
- `data/samples/*.json` - 28 per-table sample data files with 10 rows each (extensible)
- `data/patstat-2026-01-19-context.json` - Original combined context (archived)
- `data/patstat_global_schema.json` - Full schema with types and samples (source of truth)

### References

- [Source: docs/sprint-artifacts/tech-spec-epic-8.md#APIs-and-Interfaces]
- [Source: docs/architecture.md#Phase-2-Architecture-Extension]
- [Source: docs/PRD.md#Feature-MCP-Server]

## Dev Agent Record

### Context Reference

<!-- Path(s) to story context XML will be added here by context workflow -->

### Agent Model Used

### Debug Log References

### Completion Notes List

**2026-01-23 - Task 5 Integration Test Complete**
- MCP server verified working via SSE transport on localhost:8080
- `.mcp.json` configuration tested and functional
- `generate_query` tool successfully returns context (29 tables) and prompt structure
- Tool design: provides structured context for host LLM to generate SQL
- Updated root README.md with comprehensive MCP setup instructions including Docker requirements

**2026-01-23 - Task 6 Multi-Tool Refactor Complete**
- Refactored from single `generate_query` tool to three schema discovery tools
- Split `patstat-2026-01-19-context.json` into 29 individual table JSON files in `data/tables/`
- New tools enable agentic workflow:
  1. `list_tables` → overview of all 29 tables with descriptions
  2. `get_table_schema(table_name)` → full column details for specific table
  3. `search_tables(keyword)` → find tables/columns matching keyword
- Extensible design: add new tables by dropping JSON files (no code changes)
- Successfully tested end-to-end: "Austrian applicants in 2021" query generated using ONLY MCP tool outputs

**What Works:**
- Server starts cleanly in devcontainer
- SSE transport connects without issues
- All three tools return properly formatted responses
- LLM can discover schema iteratively and generate valid SQL structure
- Claude Code successfully integrates with the MCP server

**2026-01-23 - Task 7 Column Types Fixed**
- Merged types from `patstat_global_schema.json` into all table JSON files
- Type mapping: INTEGER→INT64, VARCHAR→STRING, DATE→DATE, FLOAT→FLOAT64
- 26 files updated with correct types
- `nuts_zip` skipped (not in global schema, custom table)

**2026-01-23 - Task 8 Sample Data Tool Complete**
- Extracted sample data from `patstat_global_schema.json` into `data/samples/` directory
- Created 28 per-table sample JSON files (10 rows each)
- Implemented `get_table_samples` tool for inspecting actual data values
- Sample data helps LLM understand: `applt_seq_nr=1` means applicant, `invt_seq_nr=1` means inventor
- Added MCP usage prompt (though Claude Code doesn't expose prompts in UI yet)

**What Works:**
- All 4 tools functional: `list_tables`, `get_table_schema`, `search_tables`, `get_table_samples`
- Schema has correct BigQuery types (INT64, STRING, DATE)
- Sample data available for all 28 tables
- Tested from clean folder (`~/mcp-test/`) - generated working SQL using only MCP context
- MCP is fully self-contained - no project file access needed

**What Could Be Improved (Future Stories):**
- Add common join hints to table JSONs
- Add example queries from QueryLib as few-shot examples
- Consider SQL validation before returning to user
- Add `nuts_zip` to global schema or document separately

### File List

- NEW: `mcp-server/.devcontainer/devcontainer.json`
- NEW: `mcp-server/pyproject.toml`
- NEW: `mcp-server/README.md`
- NEW: `mcp-server/src/query_mcp/__init__.py`
- NEW: `mcp-server/src/query_mcp/config.py`
- MODIFIED: `mcp-server/src/query_mcp/context.py` (multi-tool pattern with tables + samples)
- MODIFIED: `mcp-server/src/query_mcp/server.py` (4 tools + usage prompt)
- MODIFIED: `mcp-server/src/query_mcp/tools.py` (list_tables, get_table_schema, search_tables, get_table_samples)
- NEW: `mcp-server/src/query_mcp/prompts/default.txt`
- MODIFIED: `README.md` (added comprehensive MCP setup documentation)
- NEW: `.mcp.json` (Claude Code MCP configuration)
- NEW: `mcp-server/.mcp.json.example` (example config with setup instructions)
- NEW: `mcp-server/MCP_Query_Test.ipynb` (test notebook for running MCP-generated SQL)
- NEW: `mcp-server/data/tables/*.json` (28 per-table schema files with types)
- NEW: `mcp-server/data/samples/*.json` (28 per-table sample data files)

