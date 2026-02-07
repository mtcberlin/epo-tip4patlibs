# Ticket 2: MCP Server – Add IPC/CPC Search Tools

**Depends on:** Ticket 1 (BigQuery Upload)

## Summary

Add 6 new tools to the PATSTAT BigQuery MCP server: SQL query execution and 5 dedicated classification search tools.

## Work Order

Implement in priority order:

1. **`run_query`** – Read-only SQL execution with safeguards (dry_run, byte limit, row limit)
2. **`search_ipc_by_technology`** – Keyword search against `title_full`, the killer feature (+135% to +610% recall vs naive search)
3. **`search_by_ipc`** – IPC code search with automatic whitespace normalization
4. **`search_by_cpc`** – CPC search with application-level (tls224) vs family-level (tls225) switch
5. **`resolve_ipc`** – Hierarchy navigation: children, ancestors, English titles
6. **`get_tech_field`** – Map IPC to WIPO/Schmoch technology fields

## Deliverable

6 MCP tools, each returning JSON with `query_used` field for transparency. All parameters, SQL templates, return formats, and test queries documented in spec.

## Spec

`mcp-patstat-extension-spec.md`, Sections "Tool 1–4" and "MCP Tool Update/Search"
