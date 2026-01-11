# TIP for PATLIBs

Patent Analysis Tool for PATLIB Staff on EPO's Technology Intelligence Platform.

## Overview

TIP for PATLIBs is a ready-to-use Jupyter notebook application that enables PATLIB staff to perform sophisticated patent analysis without programming skills. It provides no-code UI controls (dropdowns, buttons, sliders) that make TIP's powerful PATSTAT backend accessible to entry-level users.

## Quick Start

1. Open `TIP_for_PATLIBs.ipynb` in JupyterLab
2. Run the first cell (marked "Run this cell first!")
3. Follow the on-screen instructions

## File Structure

```
tip4patlibs/
├── TIP_for_PATLIBs.ipynb      # User-facing notebook
├── tip4patlibs_core.py        # Core logic module (168 LOC)
└── README.md                  # This file
```

## Module Structure

The `tip4patlibs_core.py` module contains:

| Component | Purpose | Status |
|-----------|---------|--------|
| `init_patstat()` | Initialize PATSTAT connection | Implemented |
| `get_db()` | Get active database session | Implemented |
| `AnalysisState` | State management for user selections | Implemented |
| `PatstatQueries` | PATSTAT query builder | Placeholder |
| `WidgetFactory` | UI component factories | Placeholder |
| `ChartBuilder` | Plotly visualization builders | Placeholder |
| `Exporter` | CSV/PNG export utilities | Placeholder |

## Code Organization

**Current LOC:** 229 lines

**Split Threshold:** If the module exceeds 500 LOC, it will be split into separate files under a `lib/` folder:

```
lib/
├── __init__.py
├── state.py          # AnalysisState class
├── queries.py        # PATSTAT query builders
├── widgets.py        # UI components
├── charts.py         # Plotly visualizations
└── export.py         # CSV/PNG export
```

## Development

This project follows the BMAD Method for development. See `docs/` folder for:
- PRD (Product Requirements Document)
- Architecture decisions
- Epic and story breakdowns
- Sprint status tracking

## License

EPO Internal Use
