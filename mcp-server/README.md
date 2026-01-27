# Query MCP Server

MCP server providing PATSTAT database schema discovery tools for AI-powered BigQuery SQL generation.

## Tools

The server exposes 4 tools for agentic schema discovery:

| Tool | Description |
|------|-------------|
| `list_tables` | List all 28 available tables with descriptions |
| `get_table_schema` | Get column details (name, type, description) for a specific table |
| `search_tables` | Search for tables/columns by keyword |
| `get_table_samples` | Get sample data rows for a specific table |

**Agentic Workflow:**
1. `list_tables()` → overview of all tables
2. Identify relevant tables for the query
3. `get_table_schema(table_name)` → column details with BigQuery types
4. `get_table_samples(table_name)` → understand actual data values
5. Generate SQL using ONLY MCP-provided context

## Quick Start (Docker)

The server **must be running** before Claude Code or Claude.ai can use its tools.

```bash
cd mcp-server
# Open in VS Code and "Reopen in Container"
# Then in container terminal:
query-mcp --sse --port 8080            # SSE only (Claude Code CLI)
query-mcp --streamable-http --port 8080 # Streamable HTTP only (Claude Code CLI + Claude.ai web)
query-mcp --http --port 8080            # Both SSE + Streamable HTTP on one port
```

Or use VS Code tasks: `Start MCP Server (SSE only)` / `Start MCP Server (Streamable HTTP only)` / `Start MCP Server (SSE + Streamable HTTP)`

## Transport Options

| Transport | Flag | Endpoints | Use with |
|-----------|------|-----------|----------|
| stdio | _(default)_ | — | Direct pipe (e.g. subprocess) |
| SSE | `--sse` | `/sse` + `/messages` | Claude Code CLI (`"type": "sse"`) |
| Streamable HTTP | `--streamable-http` | `/mcp` | Claude Code CLI (`"type": "http"`) + Claude.ai web |
| Combined | `--http` | `/sse` + `/messages` + `/mcp` | All clients on one port |

## Claude Code CLI Configuration

Copy `.mcp.json.example` to your project root as `.mcp.json`:

```json
{
  "mcpServers": {
    "query-mcp": {
      "type": "sse",
      "url": "http://localhost:8080/sse"
    }
  }
}
```

Or with Streamable HTTP:

```json
{
  "mcpServers": {
    "query-mcp": {
      "type": "http",
      "url": "http://localhost:8080/mcp"
    }
  }
}
```

## Claude.ai Web Configuration

Claude.ai requires a publicly accessible HTTPS URL, so you need a tunnel (e.g. ngrok):

1. Start the server with `--streamable-http` or `--http` inside the dev container
2. Run `ngrok http 8080` on your **host machine** (not in the container)
3. In Claude.ai: **Settings > Connectors > Add custom connector**
4. Enter the ngrok URL with `/mcp` path, e.g. `https://abc123.ngrok-free.app/mcp`

**Verify the setup:**
1. Ensure the server is running
2. For Claude Code CLI: restart or run `/mcp` to reconnect
3. For Claude.ai: check the connector status in Settings
4. The 4 schema discovery tools should now be available

## Data Structure

```
data/
├── tables/          # 28 per-table schema files (extensible)
│   ├── tls201_appln.json
│   ├── tls206_person.json
│   └── ...
└── samples/         # 28 per-table sample data files (10 rows each)
    ├── tls201_appln.json
    ├── tls206_person.json
    └── ...
```

**Extensible:** Add new tables by dropping JSON files - no code changes required.

**Table JSON format:**
```json
{
  "table_name": "tls201_appln",
  "description": "Core patent application table...",
  "columns": [
    {"name": "appln_id", "type": "INT64", "description": "Unique identifier..."},
    {"name": "appln_filing_year", "type": "INT64", "description": "Year of filing..."}
  ]
}
```

**Sample JSON format:**
```json
{
  "table_name": "tls201_appln",
  "columns": ["appln_id", "appln_filing_year", ...],
  "rows": [{"appln_id": "123", "appln_filing_year": "2021", ...}],
  "row_count": 10
}
```

## Local Installation

```bash
pip install -e .

# Run with SSE transport
query-mcp --sse --port 8080

# Run with Streamable HTTP transport
query-mcp --streamable-http --port 8080

# Run with both SSE + Streamable HTTP
query-mcp --http --port 8080
```

## Configuration

Create `query-mcp.json` in working directory:

```json
{
  "context_dir": "data",
  "log_level": "INFO"
}
```

Or use env vars: `CONTEXT_DIR`, `LOG_LEVEL`

## Endpoints

**SSE mode** (`--sse`):
- `GET /sse` - SSE connection endpoint
- `POST /messages` - Message endpoint

**Streamable HTTP mode** (`--streamable-http`):
- `POST /mcp` - Streamable HTTP endpoint (session-managed)

**Combined mode** (`--http`):
- All of the above on a single port
