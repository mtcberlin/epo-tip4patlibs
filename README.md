# TIP for PATLIBs

Patent Analysis Training Materials for PATLIB Staff on EPO's Technology Intelligence Platform.

## Executive Summary

**TIP for PATLIBs Phase 2** delivers four production-ready Jupyter notebooks and educational materials for EPO Academy's PATLIB training program as part of the PATLIB2028 roadmap.

**Budget:** 14,000 EUR

### Deliverables

| # | Notebook | Description |
|---|----------|-------------|
| 1 | **Query Library** | 42 parameterized PATSTAT queries with selector UI |
| 2 | **Interactive Demo** | Guided TIP walkthrough for training sessions |
| 3 | **AI Query Builder** | Natural language → PATSTAT SQL generation |
| 4 | **University Analysis** | European university patent portfolio analysis |

**Plus:** Handbook, quick reference guides, 20 hours training delivery, Streamlit app maintenance

### Target Users

- **PATLIB Staff (Entry-Level):** Run queries without coding
- **PATLIB Staff (Multiplicators):** Extend and share customizations
- **University PATLIB Staff:** Analyze university innovation landscapes

### Key Differentiators

- **Learn by doing:** Notebooks are useful from first cell execution
- **TIP-native:** Built for the platform PATLIBs already have access to
- **Transparent code:** Users see Python/SQL but interact via UI controls
- **Dual-purpose:** Training material AND practical tool

## Project Classification

| Attribute | Value |
|-----------|-------|
| Project Type | Jupyter notebook training toolkit |
| Domain | Patent Information (Institutional) |
| Complexity | Medium |
| Context | Brownfield (existing notebooks to refactor) |

## Quick Start

1. Open the desired notebook in TIP's JupyterLab environment
2. Run the first cell (marked "Run this cell first!")
3. Follow the on-screen instructions

## Repository Structure

```
epo-tip4patlibs-bmad/
├── _bmad-output/
│   └── planning-artifacts/
│       ├── product-brief-*.md      # Product Brief
│       └── prd.md                  # Product Requirements Document
├── context/
│   ├── _bmadv4_docs/               # Phase 1 artifacts (reference)
│   ├── index.md                    # Documentation index
│   ├── project-overview.md         # Architecture overview
│   └── *.md                        # Additional context docs
├── TIP_for_PATLIBs.ipynb           # Original notebook (Phase 1)
├── tip4patlibs_core.py             # Core logic module
└── README.md                       # This file
```

## Development

This project follows the BMAD Method for development.

**Planning Artifacts:**
- Product Brief: `_bmad-output/planning-artifacts/product-brief-*.md`
- PRD: `_bmad-output/planning-artifacts/prd.md`

**Context Documentation:**
- See `context/index.md` for full documentation index

## Related Resources

- **Streamlit App:** [patstat.streamlit.app](https://patstat.streamlit.app/) (honeypot/demo)
- **EPO TIP:** Technology Intelligence Platform (requires EPO access)

## License

EPO Internal Use
