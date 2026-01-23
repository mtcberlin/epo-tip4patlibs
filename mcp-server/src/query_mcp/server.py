"""MCP Server entry point."""

import argparse
import asyncio
import logging
import os

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent

from .config import Config
from .context import ContextStore
from .tools import get_tools, handle_generate_query

logger = logging.getLogger(__name__)

# Global state
server = Server("query-mcp")
ctx = ContextStore()
cfg: Config


@server.list_tools()
async def list_tools():
    return get_tools()


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "generate_query":
        return handle_generate_query(arguments.get("question", ""), ctx, cfg.prompt_file)
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


def main() -> None:
    """Entry point."""
    global cfg

    parser = argparse.ArgumentParser(description="Query MCP Server")
    parser.add_argument("--sse", action="store_true", help="Run with SSE/HTTP transport")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=int(os.getenv("MCP_PORT", "8080")), help="Port for SSE server (default: 8080)")
    args = parser.parse_args()

    cfg = Config.load()
    logging.basicConfig(level=cfg.log_level)
    logger.info(f"Loading context from: {cfg.context_dir}")
    ctx.load(cfg.context_dir)

    if args.sse:
        run_sse(args.host, args.port)
    else:
        run_stdio()


if __name__ == "__main__":
    main()
