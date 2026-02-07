"""MCP tool definitions for patent database queries."""

import json
from pathlib import Path

from mcp.types import TextContent, Tool

from .context import ContextStore


def get_tools() -> list[Tool]:
    """Return list of available tools."""
    return [
        Tool(
            name="list_tables",
            description="List all available database tables with their descriptions. Use this first to understand what data is available. Optionally filter by platform ('bigquery' or 'tip').",
            inputSchema={
                "type": "object",
                "properties": {
                    "platform": {
                        "type": "string",
                        "description": "Filter tables by platform availability: 'bigquery' (BigQuery direct) or 'tip' (Technology Intelligence Platform). Omit to list all tables.",
                        "enum": ["bigquery", "tip"]
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_table_schema",
            description="Get detailed schema for a specific table including all columns and their descriptions. Use after list_tables to get column details for relevant tables.",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Name of the table to get schema for (e.g., 'tls201_appln')"
                    }
                },
                "required": ["table_name"]
            }
        ),
        Tool(
            name="search_tables",
            description="Search for tables and columns matching a keyword. Useful when you're not sure which tables contain the data you need.",
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "Keyword to search for in table/column names and descriptions"
                    }
                },
                "required": ["keyword"]
            }
        ),
        Tool(
            name="get_table_samples",
            description="Get sample data rows for a specific table. Useful to understand actual data format and values.",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Name of the table to get sample data for (e.g., 'tls201_appln')"
                    }
                },
                "required": ["table_name"]
            }
        ),
    ]


def handle_list_tables(ctx: ContextStore, platform: str | None = None) -> list[TextContent]:
    """Handle list_tables tool call."""
    tables = ctx.list_tables(platform=platform)

    if not tables:
        filter_msg = f" for platform '{platform}'" if platform else ""
        return [TextContent(type="text", text=f"No tables found{filter_msg}.")]

    # Format as readable list
    filter_label = f" (platform: {platform})" if platform else ""
    lines = [f"**Available Tables ({len(tables)}){filter_label}:**\n"]
    for t in tables:
        avail = ", ".join(t["availability"])
        lines.append(f"- **{t['table_name']}** [{avail}]: {t['description']}")

    return [TextContent(type="text", text="\n".join(lines))]


def handle_get_table_schema(table_name: str, ctx: ContextStore) -> list[TextContent]:
    """Handle get_table_schema tool call."""
    schema = ctx.get_table_schema(table_name)

    if not schema:
        return [TextContent(
            type="text",
            text=f"Table '{table_name}' not found. Use list_tables to see available tables."
        )]

    # Format schema as readable output
    availability = schema.get("availability", ["bigquery", "tip"])
    avail_str = ", ".join(availability)
    lines = [
        f"**Table: {schema['table_name']}** [{avail_str}]",
        f"_{schema.get('description', 'No description')}_\n",
        "**Columns:**"
    ]

    for col in schema.get("columns", []):
        col_type = col.get("type", "")
        type_str = f" ({col_type})" if col_type else ""
        lines.append(f"- **{col['name']}**{type_str}: {col.get('description', 'No description')}")

    # Include common joins if present
    if schema.get("common_joins"):
        lines.append("\n**Common Joins:**")
        for join in schema["common_joins"]:
            lines.append(f"- {join}")

    # Include example filters if present
    if schema.get("example_filters"):
        lines.append("\n**Example Filters:**")
        for filter_ex in schema["example_filters"]:
            lines.append(f"- `{filter_ex}`")

    return [TextContent(type="text", text="\n".join(lines))]


def handle_search_tables(keyword: str, ctx: ContextStore) -> list[TextContent]:
    """Handle search_tables tool call."""
    results = ctx.search_tables(keyword)

    if not results:
        return [TextContent(
            type="text",
            text=f"No tables or columns found matching '{keyword}'."
        )]

    lines = [f"**Search Results for '{keyword}':**\n"]

    for result in results:
        lines.append(f"**{result['table_name']}**: {result['description']}")

        # Group matches
        table_matches = [m for m in result["matches"] if m["match_type"] == "table"]
        col_matches = [m for m in result["matches"] if m["match_type"] == "column"]

        if col_matches:
            cols = ", ".join(m["column"] for m in col_matches)
            lines.append(f"  Matching columns: {cols}")

        lines.append("")

    return [TextContent(type="text", text="\n".join(lines))]


def handle_get_table_samples(table_name: str, ctx: ContextStore) -> list[TextContent]:
    """Handle get_table_samples tool call."""
    samples = ctx.get_table_samples(table_name)

    if not samples:
        return [TextContent(
            type="text",
            text=f"No sample data found for table '{table_name}'."
        )]

    lines = [
        f"**Sample Data: {samples['table_name']}**",
        f"_{samples.get('row_count', 0)} sample rows_\n",
        "**Columns:** " + ", ".join(samples.get("columns", [])),
        "\n**Sample Rows:**"
    ]

    # Format rows as a simple table
    for i, row in enumerate(samples.get("rows", [])[:5], 1):  # Limit to 5 rows
        lines.append(f"\n_Row {i}:_")
        # Row is a dict, iterate over columns to maintain order
        for col in samples.get("columns", []):
            val = row.get(col) if isinstance(row, dict) else None
            val_str = str(val) if val is not None else "NULL"
            # Truncate long values
            if len(val_str) > 50:
                val_str = val_str[:47] + "..."
            lines.append(f"  {col}: {val_str}")

    if samples.get("row_count", 0) > 5:
        lines.append(f"\n_... and {samples['row_count'] - 5} more rows_")

    return [TextContent(type="text", text="\n".join(lines))]
