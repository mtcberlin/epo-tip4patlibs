# TIP for PATLIBs

Patent analysis training materials and tools for PATLIB staff on EPO's Technology Intelligence Platform (TIP).

## Notebooks

| Notebook | Description |
|----------|-------------|
| **QueryLib** (`TIP_for_PATLIBs_QueryLib.ipynb`) | Parameterized PATSTAT queries with selector UI |
| **Interactive Demo** (`TIP_for_PATLIBs_InteractiveQueryDemo.ipynb`) | Guided TIP walkthrough for training sessions |

### Quick Start

1. Open a notebook in TIP's JupyterLab environment
2. Run the first cell (marked "Run this cell first!")
3. Follow the on-screen instructions

## MCP Server

The `mcp-server/` directory provides an MCP server for AI-assisted PATSTAT query generation. It exposes schema discovery tools (`list_tables`, `get_table_schema`, `search_tables`, `get_table_samples`) that give an LLM the context needed to generate valid BigQuery SQL against the PATSTAT database.

Runs in Docker via DevContainer. Supports SSE and Streamable HTTP transports for use with Claude Code CLI and Claude.ai.

See [mcp-server/README.md](mcp-server/README.md) for setup and configuration.

## Repository Structure

```
epo-tip4patlibs/
├── TIP_for_PATLIBs_QueryLib.ipynb          # Query Library notebook
├── TIP_for_PATLIBs_QueryLib_core.py        # QueryLib core module
├── TIP_for_PATLIBs_QueryLib_queries.py     # Query definitions
├── TIP_for_PATLIBs_InteractiveQueryDemo.ipynb  # Interactive demo notebook
├── tip4patlibs_core.py                     # Shared core logic
├── mcp-server/                             # PATSTAT MCP server
├── tests/                                  # Test suite
└── context/                                # Project documentation & reference
```

## Related Resources

- **Streamlit App:** [patstat.streamlit.app](https://patstat.streamlit.app/)
- **EPO TIP:** Technology Intelligence Platform (requires EPO access)

## License

EPO Internal Use
