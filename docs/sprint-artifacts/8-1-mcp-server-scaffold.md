# Story 8.1: MCP Server Scaffold

Status: review

## Story

As a **developer using Claude Code**,
I want a **minimal working MCP server for PATSTAT query generation**,
so that **I can discover what context and structure the LLM actually needs**.

## Acceptance Criteria

1. MCP server starts without errors when configured in Claude Code
2. Server exposes at least one tool: `generate_patstat_query`
3. Tool accepts a business question string and returns a response
4. Server loads existing context files from `context/` folder (raw, unprocessed)
5. Basic system prompt instructs LLM to generate BigQuery SQL
6. README.md documents setup and usage

## Tasks / Subtasks

- [x] **Task 1: Project Setup** (AC: 1, 6)
  - [x] Create `mcp-server/` directory structure
  - [x] Initialize Python project with `pyproject.toml`
  - [x] Add `mcp` package dependency
  - [x] Create README.md with setup instructions

- [x] **Task 2: Basic MCP Server** (AC: 1, 2)
  - [x] Create `server.py` with MCP server scaffold
  - [x] Register `generate_query` tool
  - [x] Implement tool handler that returns response with context

- [x] **Task 3: Context Loading** (AC: 4)
  - [x] Load `context/*context*.json` at startup
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

**MCP Server Pattern:**
```python
from mcp.server import Server
from mcp.types import Tool, TextContent

server = Server("patstat-query-generator")

@server.tool()
async def generate_patstat_query(question: str) -> str:
    # Load context, generate response
    pass
```

**Existing Assets:**
- `context/patstat-2026-01-19-context.json` - 28 tables with descriptions
- `context/patstat_global_schema.json` - Full schema (54k tokens)
- `context/QueryLib_for_PATLIBs.ipynb` - 13 validated queries (reference)

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

**What Works:**
- Server starts cleanly in devcontainer
- SSE transport connects without issues
- Context files (29 tables) load correctly at startup
- Tool responds with proper context and prompt structure
- Claude Code successfully integrates with the MCP server

**What Could Be Improved (Future Stories):**
- Tool returns context + prompt; actual SQL generation is delegated to host LLM
- May want to add more sophisticated prompt engineering
- Could add validation of generated SQL
- Consider adding example queries from QueryLib as few-shot examples

### File List

- NEW: `mcp-server/.devcontainer/devcontainer.json`
- NEW: `mcp-server/pyproject.toml`
- NEW: `mcp-server/README.md`
- NEW: `mcp-server/src/query_mcp/__init__.py`
- NEW: `mcp-server/src/query_mcp/config.py`
- NEW: `mcp-server/src/query_mcp/context.py`
- NEW: `mcp-server/src/query_mcp/server.py`
- NEW: `mcp-server/src/query_mcp/tools.py`
- NEW: `mcp-server/src/query_mcp/prompts/default.txt`
- MODIFIED: `README.md` (added comprehensive MCP setup documentation)
- NEW: `.mcp.json` (Claude Code MCP configuration)

