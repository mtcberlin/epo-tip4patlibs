# Story 8.1: MCP Server Scaffold

Status: ready-for-dev

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

- [ ] **Task 1: Project Setup** (AC: 1, 6)
  - [ ] Create `mcp-server/` directory structure
  - [ ] Initialize Python project with `pyproject.toml`
  - [ ] Add `mcp` package dependency
  - [ ] Create README.md with setup instructions

- [ ] **Task 2: Basic MCP Server** (AC: 1, 2)
  - [ ] Create `server.py` with MCP server scaffold
  - [ ] Register `generate_patstat_query` tool
  - [ ] Implement tool handler that returns placeholder response

- [ ] **Task 3: Context Loading** (AC: 4)
  - [ ] Load `context/patstat-2026-01-19-context.json` at startup
  - [ ] Load `context/patstat_global_schema.json` at startup
  - [ ] Store context in memory for tool access

- [ ] **Task 4: System Prompt** (AC: 5)
  - [ ] Create system prompt that includes loaded context
  - [ ] Instruct LLM to generate BigQuery SQL (no `public.` prefix)
  - [ ] Include basic query patterns from existing knowledge

- [ ] **Task 5: Integration Test** (AC: 1, 2, 3)
  - [ ] Configure MCP server in Claude Code settings
  - [ ] Verify server appears in available tools
  - [ ] Test with simple business question
  - [ ] Document what works and what doesn't

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

### File List

