"""MCP Server entry point."""

import argparse
import asyncio
import logging
import os

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Prompt, PromptMessage, GetPromptResult

from .config import Config
from .context import ContextStore
from .tools import (
    get_tools,
    handle_list_tables,
    handle_get_table_schema,
    handle_search_tables,
    handle_get_table_samples,
)

logger = logging.getLogger(__name__)

# Global state
server = Server("query-mcp")
ctx: ContextStore
cfg: Config


USAGE_PROMPT = """PATSTAT Patent Database Query Helper

I provide schema information for the EPO PATSTAT database to help you generate BigQuery SQL queries.

**Workflow:**
1. Call `list_tables` to see all available tables (28 tables)
2. Identify relevant tables for your query
3. Call `get_table_schema(table_name)` to get column names and types
4. Generate BigQuery SQL using the schema information

**Tips:**
- Use `search_tables(keyword)` to find tables/columns by keyword
- Pay attention to column types (INT64, STRING, DATE) for correct comparisons
- For applicants: use `tls207_pers_appln.applt_seq_nr > 0`
- For inventors: use `tls207_pers_appln.invt_seq_nr > 0`
- Country codes are 2-letter ISO codes (e.g., 'AT' for Austria, 'GB' for UK)

**Common tables:**
- `tls201_appln` - Patent applications (appln_id, appln_filing_year, granted)
- `tls206_person` - Applicants/inventors (person_id, person_name, person_ctry_code)
- `tls207_pers_appln` - Links persons to applications (appln_id, person_id, applt_seq_nr)
"""


@server.list_prompts()
async def list_prompts():
    return [
        Prompt(
            name="usage",
            description="How to use this MCP server to generate PATSTAT BigQuery queries"
        )
    ]


@server.get_prompt()
async def get_prompt(name: str) -> GetPromptResult:
    if name == "usage":
        return GetPromptResult(
            description="PATSTAT query generation guide",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=USAGE_PROMPT)
                )
            ]
        )
    raise ValueError(f"Unknown prompt: {name}")


@server.list_tools()
async def list_tools():
    return get_tools()


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "list_tables":
        return handle_list_tables(ctx)
    elif name == "get_table_schema":
        return handle_get_table_schema(arguments.get("table_name", ""), ctx)
    elif name == "search_tables":
        return handle_search_tables(arguments.get("keyword", ""), ctx)
    elif name == "get_table_samples":
        return handle_get_table_samples(arguments.get("table_name", ""), ctx)
    return [TextContent(type="text", text=f"Unknown tool: {name}")]


def run_stdio() -> None:
    """Run server with stdio transport."""
    async def run():
        async with stdio_server() as (read, write):
            await server.run(read, write, server.create_initialization_options())
    asyncio.run(run())


def run_sse(host: str, port: int) -> None:
    """Run server with SSE transport over HTTP."""
    from mcp.server.sse import SseServerTransport
    import uvicorn

    sse = SseServerTransport("/messages")

    async def handle_sse(scope, receive, send):
        async with sse.connect_sse(scope, receive, send) as streams:
            await server.run(streams[0], streams[1], server.create_initialization_options())

    async def app(scope, receive, send):
        if scope["type"] == "http":
            path = scope["path"]
            if path == "/sse":
                await handle_sse(scope, receive, send)
            elif path == "/messages" and scope["method"] == "POST":
                await sse.handle_post_message(scope, receive, send)
            else:
                await send({"type": "http.response.start", "status": 404, "headers": []})
                await send({"type": "http.response.body", "body": b"Not Found"})

    logger.info(f"Starting SSE server on http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)


# TODO: Add Streamable HTTP transport for Claude.ai web support
# The transport logic is decoupled - just add run_streamable_http() when ready


def main() -> None:
    """Entry point."""
    global cfg, ctx

    parser = argparse.ArgumentParser(description="Query MCP Server")
    parser.add_argument("--sse", action="store_true", help="Run with SSE/HTTP transport")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=int(os.getenv("MCP_PORT", "8080")), help="Port for SSE server (default: 8080)")
    args = parser.parse_args()

    cfg = Config.load()
    logging.basicConfig(level=cfg.log_level)

    # Initialize context store with tables and samples directories
    tables_dir = cfg.context_dir / "tables"
    samples_dir = cfg.context_dir / "samples"
    logger.info(f"Loading tables from: {tables_dir}")
    logger.info(f"Loading samples from: {samples_dir}")
    ctx = ContextStore(tables_dir, samples_dir)

    if args.sse:
        run_sse(args.host, args.port)
    else:
        run_stdio()


if __name__ == "__main__":
    main()
