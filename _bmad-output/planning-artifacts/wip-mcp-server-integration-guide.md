# WIP: Integrating the PATSTAT MCP Server into Another Project

> **Purpose:** Step-by-step instructions for an AI agent (or developer) to copy and
> integrate the `query-mcp` MCP server from the `epo-tip4patlibs` repo into a
> different project.
>
> **Source repo:** `epo-tip4patlibs` (branch `develop`)

---

## 1. What This MCP Server Does

A lightweight, metadata-only MCP server that exposes PATSTAT database schema
information via 4 tools. It does **not** execute SQL — it gives an LLM enough
context to *generate* valid BigQuery SQL.

**30 tables total:**
- 28 standard PATSTAT tables (available on both BigQuery and TIP platform)
- 2 custom hierarchy tables, BigQuery-only:
  - `tls_ipc_hierarchy` — 79,833 IPC classification entries
  - `tls_cpc_hierarchy` — 254,249 CPC classification entries

```

User question  →  LLM calls MCP tools  →  Gets schema + samples  →  Generates SQL
```

### Exposed Tools

| Tool | Input | Output |
|------|-------|--------|
| `list_tables` | `platform?` (bigquery / tip) | All table names + descriptions |
| `get_table_schema` | `table_name` | Columns with types & descriptions |
| `search_tables` | `keyword` | Tables/columns matching the keyword |
| `get_table_samples` | `table_name` | Up to 10 real data rows |

### Transport Modes

| Flag | Endpoints | Best for |
|------|-----------|----------|
| *(none)* | stdio | Direct subprocess pipe |
| `--sse` | `/sse` + `/messages` | Claude Code CLI (`"type": "sse"`) |
| `--streamable-http` | `/mcp` | Claude Code CLI (`"type": "http"`) + Claude.ai web |
| `--http` | all of the above | One port, all clients |

---

## 2. Files to Copy

Copy the **entire** `mcp-server/` directory from the source repo. Here is what's
inside and what each piece does:

```
mcp-server/
├── src/query_mcp/              # Python package (the server)
│   ├── __init__.py             # Version string
│   ├── server.py               # Entry point: transports, MCP handlers, CLI args
│   ├── tools.py                # Tool definitions + response formatters
│   ├── config.py               # Config loader (JSON file → env vars → defaults)
│   └── context.py              # ContextStore: loads JSON schemas, lazy caching
│
├── data/
│   ├── tables/                 # 30 table schema JSONs (the knowledge base)
│   │   ├── tls201_appln.json
│   │   ├── tls206_person.json
│   │   └── ... (30 files total)
│   └── samples/                # 30 sample-data JSONs (10 rows each)
│       ├── tls201_appln.json
│       └── ... (30 files total)
│
├── config/
│   └── query-mcp.json          # Server config (context_dir, log_level)
│
├── .devcontainer/
│   └── devcontainer.json       # VS Code DevContainer (Python 3.12 + Node)
│
├── pyproject.toml              # Dependencies & entry point
├── Dockerfile                  # Production image
├── .mcp.json.example           # Example client config for Claude Code
└── README.md                   # Full documentation
```

### Minimum Copy (If You Want Lean)

If you only need the server running locally (no Docker, no DevContainer):

```
mcp-server/
├── src/query_mcp/   (all 5 files)
├── data/            (tables/ and samples/ directories — all JSON files)
├── config/query-mcp.json
└── pyproject.toml
```

---

## 3. Dependencies

### Runtime

| Package | Version | Purpose |
|---------|---------|---------|
| Python | >= 3.10 | Runtime |
| `mcp` | >= 1.8.0, < 1.26.0 | MCP protocol SDK |
| `starlette` | >= 0.27.0 | ASGI framework (HTTP transports) |
| `uvicorn` | >= 0.24.0 | ASGI server |

### Build System

Uses **hatchling**. Defined in `pyproject.toml`:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/query_mcp"]
```

### Install

```bash
cd mcp-server
pip install -e .          # Editable install (dev)
# or
pip install .             # Standard install
```

This registers the `query-mcp` CLI command.

---

## 4. Configuration

### Config File: `config/query-mcp.json`

```json
{
  "context_dir": "./data",
  "log_level": "INFO"
}
```

- `context_dir` — path to the directory containing `tables/` and `samples/` subdirs
- `log_level` — Python log level (DEBUG, INFO, WARNING, ERROR)

### Config Resolution Order

1. `QUERY_MCP_CONFIG` env var → path to JSON config file
2. `config/query-mcp.json` in the working directory
3. Environment variable fallbacks: `CONTEXT_DIR`, `LOG_LEVEL`

### No Secrets Required

The server reads only local JSON files. No API keys, no database credentials,
no `.env` file needed.

---

## 5. How to Run

### Option A: Local Install

```bash
cd mcp-server
pip install -e .

# Pick a transport:
query-mcp                                  # stdio (default)
query-mcp --sse --port 8080               # SSE only
query-mcp --streamable-http --port 8080   # Streamable HTTP only
query-mcp --http --port 8080              # Both SSE + Streamable HTTP
```

### Option B: Docker

```bash
cd mcp-server
docker build -t query-mcp .
docker run -p 8080:8080 query-mcp    # Runs --http by default
```

### Option C: DevContainer

1. Open `mcp-server/` in VS Code
2. "Reopen in Container" when prompted
3. Dependencies auto-install via `pip install -e '.[dev]'`
4. Run `query-mcp --http --port 8080` in the container terminal

---

## 6. Connect Claude Code CLI to the Server

Create a `.mcp.json` file **in the root of the target project** (not inside
`mcp-server/`):

### SSE Transport

```json
{
  "mcpServers": {
    "PATSTAT": {
      "type": "sse",
      "url": "http://localhost:8080/sse"
    }
  }
}
```

### Streamable HTTP Transport

```json
{
  "mcpServers": {
    "PATSTAT": {
      "type": "http",
      "url": "http://localhost:8080/mcp"
    }
  }
}
```

After creating the file, restart Claude Code or run `/mcp` to reconnect.
The 4 schema tools should appear.

---

## 7. Connect Claude.ai Web

1. Start server with `--streamable-http` or `--http`
2. Expose via tunnel: `ngrok http 8080` (on host, not in container)
3. In Claude.ai: **Settings > Connectors > Add custom connector**
4. Enter: `https://<your-ngrok-id>.ngrok-free.app/mcp`

---

## 8. Architecture at a Glance

```
┌──────────────────────────────────────────────────┐
│  mcp-server/                                     │
│                                                  │
│  pyproject.toml ──→ pip install ──→ `query-mcp`  │
│                                                  │
│  server.py                                       │
│    ├─ CLI arg parsing (transport mode, port)      │
│    ├─ Config.load()  ← config/query-mcp.json     │
│    ├─ ContextStore(tables_dir, samples_dir)       │
│    └─ MCP handlers:                              │
│         list_prompts / get_prompt                 │
│         list_tools   / call_tool ──→ tools.py    │
│                                                  │
│  context.py                                      │
│    └─ ContextStore                               │
│         ├─ Lazy-loads all data/tables/*.json      │
│         ├─ Lazy-loads data/samples/*.json         │
│         └─ Methods: list_tables, get_table_schema │
│                     search_tables, get_table_samp │
│                                                  │
│  tools.py                                        │
│    ├─ get_tools() → Tool definitions             │
│    └─ handle_* functions → Formatted responses    │
│                                                  │
│  data/tables/*.json   ← Schema knowledge base    │
│  data/samples/*.json  ← Sample rows              │
└──────────────────────────────────────────────────┘
```

---

## 9. Extending with New Tables

No code changes needed. Just drop files:

1. Add `data/tables/<table_name>.json`:

```json
{
  "table_name": "my_new_table",
  "availability": ["bigquery"],
  "description": "What this table contains...",
  "columns": [
    { "name": "id", "type": "INT64", "description": "Primary key" },
    { "name": "value", "type": "STRING", "description": "Some value" }
  ],
  "common_joins": ["JOIN other_table ON ..."],
  "example_filters": ["WHERE value = 'something'"]
}
```

2. Optionally add `data/samples/<table_name>.json`:

```json
{
  "table_name": "my_new_table",
  "columns": ["id", "value"],
  "rows": [
    { "id": "1", "value": "foo" },
    { "id": "2", "value": "bar" }
  ],
  "row_count": 2
}
```

3. Restart the server. Done.

---

## 10. Checklist for the Implementing Agent

- [ ] Copy `mcp-server/` directory into target project
- [ ] Verify Python >= 3.10 is available
- [ ] Run `pip install -e .` from inside `mcp-server/`
- [ ] Confirm `query-mcp --help` works
- [ ] Start server: `query-mcp --http --port 8080`
- [ ] Create `.mcp.json` in the target project root (see section 6)
- [ ] Restart Claude Code and verify 4 tools appear via `/mcp`
- [ ] Test: ask Claude to `list_tables` — should return 30 tables
- [ ] (Optional) Add `.mcp.json` to `.gitignore` if it contains local-only config
- [ ] (Optional) Set up Docker for production deployment (see section 5B)

---

## 11. Gotchas & Notes

- The server must be **running** before Claude Code can use its tools — it's a live HTTP service, not a static config.
- `config/query-mcp.json` uses `"context_dir": "./data"` — this is **relative to the working directory** where you run `query-mcp`. Make sure you run it from inside `mcp-server/`.
- The DevContainer mounts a `../context` directory from the parent repo. In a new project, you can ignore this or update the mount path in `.devcontainer/devcontainer.json`.
- `uv.lock` is present but not required — standard `pip install` works fine.
- The server name in `server.py` is hardcoded as `"query-mcp"`. Change it if you want a different name in MCP tool listings.
