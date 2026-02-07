# MCP Server Extension: IPC/CPC Search Tools for PATSTAT

## Summary

Extend the existing PATSTAT BigQuery MCP server with SQL query execution and dedicated classification search tools. Upload the IPC hierarchy database as a new reference table to enable technology keyword search.

## Work Order

### Part 1: BigQuery Upload (prerequisite)
1. Upload IPC SQLite database (`patent-classification-2025.db`) to BigQuery as `tls_ipc_hierarchy` using the provided upload script
2. Generate `symbol_patstat` (PATSTAT space-padded format) and `title_full` (concatenated ancestor chain) columns during upload
3. Verify JOINs to `tls209_appln_ipc.ipc_class_symbol` work via `symbol_patstat`
4. Run the 4 provided test queries to validate

### Part 2: MCP Tools (in priority order)
1. **`run_query`** — Execute read-only SQL against PATSTAT with safeguards (dry_run, byte limit, row limit, dataset scoping)
2. **`search_ipc_by_technology`** — Keyword search against `tls_ipc_hierarchy.title_full` with level filter. The killer feature.
3. **`search_by_ipc`** — Search by IPC code with automatic whitespace normalization, main-only filter, authority filter
4. **`search_by_cpc`** — Same as IPC but with application/family level switch (tls224 vs tls225)
5. **`resolve_ipc`** — Hierarchy navigation: children, ancestors, English titles for a given code
6. **`get_tech_field`** — Map IPC codes or applications to WIPO/Schmoch technology fields

### Conversion Functions
- 4 Python functions for converting between zero-padded, PATSTAT space-padded, and short symbol formats
- Verified against all 79,039 subgroup-level IPC entries with zero errors
- Provided in the spec, ready to integrate

## Expected Result

- `tls_ipc_hierarchy` table live in BigQuery with 79,833 rows, `symbol_patstat` and `title_full` columns populated
- 6 new MCP tools available, each returning JSON with `query_used` field for transparency
- Technology keyword search returning results with +135% to +610% better recall than naive `title_en` search (verified benchmarks in spec)
- All tool parameters, generated SQL, return formats, and test queries documented in `mcp-patstat-extension-spec.md`
