"""MCP tool definitions."""

from pathlib import Path

from mcp.types import TextContent, Tool

from .context import ContextStore

# Fallback prompt if no file configured
FALLBACK_PROMPT = """Generate BigQuery SQL for the question.

TABLES:
{tables}
"""


def get_tools() -> list[Tool]:
    """Return list of available tools."""
    return [
        Tool(
            name="generate_query",
            description="Generate a BigQuery SQL query from a business question",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The business question to answer"
                    }
                },
                "required": ["question"]
            }
        )
    ]


def build_prompt(ctx: ContextStore, prompt_file: Path | None = None) -> str:
    """Build system prompt with context."""
    if prompt_file and prompt_file.exists():
        template = prompt_file.read_text()
    else:
        template = FALLBACK_PROMPT

    # Format table list
    tables_text = "\n".join(
        f"- {t.get('table_name', '').replace('public.', '')}: {t.get('table_description', '')}"
        for t in ctx.tables
    )

    return template.format(tables=tables_text)


def handle_generate_query(question: str, ctx: ContextStore, prompt_file: Path | None = None) -> list[TextContent]:
    """Handle generate_query tool call."""
    prompt = build_prompt(ctx, prompt_file)

    response = f"""**Question:** {question}

**Context:** {len(ctx.tables)} tables loaded

{prompt}

---
Generate SQL for the question above.
"""
    return [TextContent(type="text", text=response)]
