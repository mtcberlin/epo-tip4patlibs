# Query MCP Server

MCP server for AI-powered SQL query generation from natural language.

## Quick Start (Docker - Recommended)

The server **must be running** before Claude Code can use its tools.

```bash
cd mcp-server
devcontainer up --workspace-folder .
```

This starts the server on port 8080 with SSE transport. The container runs in the background.

To stop: `docker stop <container-id>` (find ID with `docker ps`)

## Claude Code Configuration

Add to your project's `.mcp.json` file (create in project root if needed):

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

**Verify the setup:**
1. Ensure the Docker container is running (`docker ps` should show the mcp-server)
2. Restart Claude Code to pick up the MCP configuration
3. The `generate_query` tool should now be available

## Local Installation (Alternative)

```bash
# Install
pip install -e .

# Or with dev dependencies
pip install -e '.[dev]'

# Run with SSE transport
query-mcp --sse --port 8080
```

## Configuration

Create `query-mcp.json` in working directory:

```json
{
  "context_dir": "../context",
  "prompt_file": null,
  "log_level": "INFO"
}
```

Or use env var `QUERY_MCP_CONFIG=/path/to/config.json`

Fallback: individual env vars (`CONTEXT_DIR`, `PROMPT_FILE`, `LOG_LEVEL`)

## Endpoints

- `GET /sse` - SSE connection endpoint (for Claude Code)
- `POST /messages` - Message endpoint

## Custom Prompts

Create a text file with `{tables}` placeholder:

```text
You are a SQL expert.

TABLES:
{tables}

Generate BigQuery SQL.
```

Set `PROMPT_FILE=/path/to/prompt.txt`
