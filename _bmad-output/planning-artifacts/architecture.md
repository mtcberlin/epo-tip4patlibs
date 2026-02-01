---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8]
status: complete
completedAt: '2026-02-01'
inputDocuments:
  - _bmad-output/planning-artifacts/prd.md
  - _bmad-output/planning-artifacts/product-brief-epo-tip4patlibs-bmad-2026-02-01.md
  - context/project-overview.md
  - context/query-design-patterns.md
  - context/what-worked-well.md
  - context/_bmadv4_docs/architecture.md
workflowType: 'architecture'
project_name: 'epo-tip4patlibs-bmad'
user_name: 'Arne'
date: '2026-02-01'
---

# Architecture Decision Document

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

## Project Context Analysis

### Architecture Scope

**Phase 2 extends Phase 1 architecture** - no fundamental changes to core patterns. The Phase 1 architecture document (`context/_bmadv4_docs/architecture.md`) remains the authoritative reference for:

- Notebook structure (hybrid: notebook + Python module)
- State management (AnalysisState pattern)
- Widget framework (ipywidgets - validated in ADR-007)
- Query patterns (ORM primary + SQL escape hatch)
- Visualization (Plotly with EPO colors)
- Export (CSV semicolon UTF-8 BOM, PNG)

### Phase 2 Extensions

| Extension | Purpose | Architectural Impact |
|-----------|---------|---------------------|
| **Claude API Integration** | AI Query Builder notebook | New API key config; structured prompt/response parsing |
| **University Reference Data** | University Analysis notebook | New data source (list of European universities with metadata) |
| **Expanded IPC/CPC Data** | Custom classification entry | Query TLS209/TLS224 tables for validation |

### Requirements Overview

**Functional Requirements (46 total):**

| Category | FRs | Scope |
|----------|-----|-------|
| Query Library | FR1-FR12 | Query selector, parameters, execution, export |
| Interactive Demo | FR13-FR17 | Guided walkthrough, training-ready |
| AI Query Builder | FR18-FR24 | Natural language → SQL, validation, save |
| University Analysis | FR25-FR32 | University selector, portfolio analysis, comparisons |
| Common Features | FR33-FR38 | Consistent patterns across all notebooks |
| Data Access | FR39-FR42 | PatstatClient, BigQuery, error handling |
| Educational Materials | FR43-FR46 | Handbook, quick guides, training materials |

**Non-Functional Requirements (20 total):**

| Category | Key NFRs | Implication |
|----------|----------|-------------|
| Performance | NFR1-5 | Queries < 120s, UI < 1s response, progress indicators |
| Reliability | NFR6-9 | Graceful error recovery, user-friendly messages |
| Integration | NFR10-13 | TIP-native, PatstatClient only, no external network |
| Maintainability | NFR14-17 | Modular code, readable SQL, centralized config |
| Usability | NFR18-20 | Non-technical users, plain language, trainer-independent |

### Technical Constraints

| Constraint | Source | Impact |
|------------|--------|--------|
| TIP JupyterLab only | NFR10 | No standalone apps, Jupyter-native UI |
| PatstatClient required | NFR11 | All data via `epo.tipdata.patstat` |
| BigQuery SQL dialect | NFR11 | SQL syntax must be BigQuery-compatible |
| Pre-installed packages only | TIP environment | ipywidgets, pandas, plotly available; verify others |
| No external network | TIP environment | Claude API requires special handling (see ADR) |

### Cross-Cutting Concerns

1. **Consistent UI Patterns** - All 4 notebooks use same widget patterns (FR33-38)
2. **Error Handling** - User-friendly messages, no tracebacks (FR35, NFR7)
3. **Export Functionality** - CSV and PNG in all notebooks (FR7-8, FR31)
4. **Self-Documenting** - Each notebook is didactic and trainer-independent (FR37, NFR20)
5. **Reference Data** - Query PATSTAT tables, no hardcoding (ADR-009)

### Complexity Assessment

| Factor | Rating | Notes |
|--------|--------|-------|
| Overall Complexity | **Medium** | Brownfield with established patterns |
| Technical Domain | Jupyter + Data Analytics | Familiar stack |
| Integration Points | **Low** | Single data source (PatstatClient) + Claude API |
| New Capabilities | **Incremental** | Extensions to proven patterns |
| Risk Areas | Claude API in TIP, University data sourcing | Require spikes |

## Technology Foundation

### Platform: EPO Technology Intelligence Platform (TIP)

The technology stack is determined by the TIP JupyterLab environment. This is a brownfield extension - no starter template selection needed.

### Established Stack (from Phase 1)

| Component | Technology | Pre-installed |
|-----------|------------|---------------|
| Runtime | Python 3.x | Yes (TIP) |
| Data Access | PatstatClient (epo.tipdata.patstat) | Yes (TIP) |
| UI Widgets | ipywidgets | Yes (TIP) |
| Visualization | Plotly | Yes (TIP) |
| Data Processing | pandas | Yes (TIP) |

### Phase 2 Dependencies (pip install required)

| Package | Notebook | Purpose |
|---------|----------|---------|
| `anthropic` | AI Query Builder | Claude API client |
| TBD | Track during implementation | Additional needs discovered |

### Dependency Check Pattern

Each notebook's initialization cell includes install-if-needed logic:

```python
# Install dependencies if needed
try:
    import anthropic
except ImportError:
    !pip install anthropic
    import anthropic

from epo.tipdata.patstat import PatstatClient
patstat = PatstatClient()
db = patstat.orm_session()
```

This ensures notebooks work on fresh TIP sessions without manual setup. Dependencies are tracked during implementation and added to initialization cells as discovered.

## Core Architectural Decisions

### Decision Summary

| # | Decision | Choice | Rationale |
|---|----------|--------|-----------|
| 1 | Claude API Integration | Direct API call from module, `.env` for key | Simple, portable, proven pattern |
| 2 | University Data Source | Static CSV file bundled with notebook | Easy pandas import, no external dependencies |
| 3 | Module Organization | Per-notebook modules | Independent notebooks, proven Phase 1 pattern |

### ADR-013: Claude API Integration Pattern

**Context:** AI Query Builder notebook needs Claude API for natural language → SQL generation.

**Decision:** Direct API call from notebook module using `anthropic` package. API key stored in `.env` file.

**Pattern:**
```python
# In ai_query_builder_core.py
import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
```

**Consequences:**
- User must provide `.env` file with `ANTHROPIC_API_KEY`
- Notebook initialization checks for key and provides helpful error if missing
- Same pattern as Streamlit app - proven and portable

### ADR-014: University Reference Data

**Context:** University Analysis notebook needs European university list with metadata.

**Decision:** Static CSV file bundled with notebook. Loaded via pandas.

**Pattern:**
```python
# In university_analysis_core.py
import pandas as pd
universities_df = pd.read_csv("european_universities.csv")
```

**Data Schema (minimum):**

| Column | Type | Description |
|--------|------|-------------|
| name | str | University name |
| country | str | Country code |
| city | str | City |
| type | str | Technical/General/etc. |

**Consequences:**
- No external network calls needed
- Easy to update by replacing CSV file
- Can expand schema as needs emerge

### ADR-015: Per-Notebook Module Organization

**Context:** Phase 2 has 4 notebooks. Need to decide on code sharing strategy.

**Decision:** Each notebook has its own module, following Phase 1 pattern.

**Structure:**
```
tip4patlibs/
├── QueryLib_for_PATLIBs.ipynb
├── query_lib_core.py
├── InteractiveDemo_for_PATLIBs.ipynb
├── interactive_demo_core.py
├── AIQueryBuilder_for_PATLIBs.ipynb
├── ai_query_builder_core.py
├── UniversityAnalysis_for_PATLIBs.ipynb
├── university_analysis_core.py
└── european_universities.csv
```

**Consequences:**
- Notebooks are fully independent and portable
- Some code duplication (utility functions) is acceptable
- Can extract shared utilities to common module later if duplication becomes excessive

## Implementation Patterns & Consistency Rules

### Established Patterns (from Phase 1)

| Pattern | Convention | Source |
|---------|------------|--------|
| Python naming | snake_case (PEP 8) | Standard |
| File naming | snake_case (`*_core.py`) | Phase 1 |
| Widget framework | ipywidgets | ADR-007 |
| Colors | EPO_COLORS palette | Phase 1 |
| Export format | CSV semicolon, UTF-8 BOM | Phase 1 |
| State management | AnalysisState dataclass | ADR-006 |
| SQL dialect | BigQuery | TIP Platform |
| Reference data | Query TLS8xx, no hardcoding | ADR-009 |

### Error Handling Pattern

User-friendly errors for non-technical users (FR35, NFR7):

```python
def run_query(state):
    try:
        # query execution
    except Exception as e:
        display(HTML(f"""
            <div style="color: #C8102E; padding: 10px; border: 1px solid #C8102E;">
                <b>Query Error</b><br>
                Unable to execute query. Please check your parameters and try again.
            </div>
        """))
        # Log technical error for debugging (visible in notebook output)
        print(f"Technical details: {e}")
```

### Progress Indicator Pattern

```python
from IPython.display import display, clear_output
import ipywidgets as widgets

progress = widgets.HTML(value="⏳ Running query...")
display(progress)
# ... execute query ...
progress.value = "✅ Complete!"
```

### File Organization Pattern

```
tip4patlibs/
├── QueryLib_for_PATLIBs.ipynb
├── query_lib_core.py
├── AIQueryBuilder_for_PATLIBs.ipynb
├── ai_query_builder_core.py
├── UniversityAnalysis_for_PATLIBs.ipynb
├── university_analysis_core.py
├── InteractiveDemo_for_PATLIBs.ipynb
├── interactive_demo_core.py
├── data/
│   └── european_universities.csv
└── .env                              # User provides (not committed)
```

### Query Metadata Pattern (Query Library)

YAML format for query definitions:

```yaml
- id: "Q01"
  title: "Country Patent Activity"
  category: "regional"
  parameters:
    - name: "year_start"
      type: "year"
      default: 2015
```

### Enforcement Guidelines

**All AI Agents MUST:**
- Follow snake_case naming for Python files, functions, and variables
- Use ipywidgets (not ipyvuetify) for UI controls
- Query PATSTAT reference tables instead of hardcoding values
- Display user-friendly error messages (no raw tracebacks)
- Use EPO_COLORS palette for visualizations

## Project Structure & Boundaries

### Complete Project Directory Structure

```
tip4patlibs/
├── README.md                              # Project overview and setup instructions
├── .env.example                           # Template for environment variables
├── .gitignore                             # Git ignore rules (.env, __pycache__, etc.)
│
├── data/
│   └── european_universities.csv          # Static university reference data
│
├── QueryLib_for_PATLIBs.ipynb             # Query Library notebook (FR1-FR12)
├── query_lib_core.py                      # Query Library module
│   ├── QueryRegistry                      # Load/manage query definitions
│   ├── QueryBuilder                       # Parameter substitution
│   ├── ParameterForm                      # ipywidgets form generator
│   └── Exporter                           # CSV/Excel export
│
├── queries/
│   ├── queries.yaml                       # Query metadata registry
│   ├── Q01_country_activity.sql           # Individual SQL templates
│   ├── Q02_tech_fields.sql
│   └── ... (42 queries)
│
├── InteractiveDemo_for_PATLIBs.ipynb      # Interactive Demo notebook (FR13-FR17)
├── interactive_demo_core.py               # Demo module (minimal - mostly markdown cells)
│
├── AIQueryBuilder_for_PATLIBs.ipynb       # AI Query Builder notebook (FR18-FR24)
├── ai_query_builder_core.py               # AI Query Builder module
│   ├── ClaudeClient                       # Anthropic API wrapper
│   ├── PromptBuilder                      # System prompt + user input
│   ├── SQLValidator                       # Basic SQL validation
│   └── QuerySaver                         # Save to session favorites
│
├── UniversityAnalysis_for_PATLIBs.ipynb   # University Analysis notebook (FR25-FR32)
└── university_analysis_core.py            # University Analysis module
    ├── UniversityLoader                   # Load CSV, provide selectors
    ├── PortfolioQueries                   # PATSTAT queries for universities
    └── ComparisonBuilder                  # Multi-university comparison
```

### Requirements to Structure Mapping

| FRs | Notebook | Module | Key Components |
|-----|----------|--------|----------------|
| FR1-FR12 | QueryLib | query_lib_core.py | QueryRegistry, ParameterForm |
| FR13-FR17 | InteractiveDemo | interactive_demo_core.py | Minimal (guided cells) |
| FR18-FR24 | AIQueryBuilder | ai_query_builder_core.py | ClaudeClient, PromptBuilder |
| FR25-FR32 | UniversityAnalysis | university_analysis_core.py | UniversityLoader, PortfolioQueries |
| FR33-FR38 | All | All modules | Consistent patterns (ipywidgets, error handling) |
| FR39-FR42 | All | All modules | PatstatClient usage |

### Architectural Boundaries

**Data Access Boundary:**
- All PATSTAT access via `PatstatClient.sql_query()`
- No direct BigQuery client usage
- University data via pandas CSV read

**API Boundary:**
- Claude API isolated in `ai_query_builder_core.py`
- API key via `.env` file only

**Module Boundary:**
- Each notebook imports only its own `*_core.py` module
- No cross-module dependencies
- Shared patterns duplicated (acceptable for independence)

## Architecture Validation Results

### Coherence Validation ✅

**Decision Compatibility:** All technology choices (Python, PatstatClient, ipywidgets, Plotly, anthropic) are compatible and work together without conflicts.

**Pattern Consistency:** All implementation patterns follow Python/Jupyter conventions and support the architectural decisions.

**Structure Alignment:** Per-notebook module organization supports all decisions and enables independent development.

### Requirements Coverage Validation ✅

| FR Category | Coverage | Implementation |
|-------------|----------|----------------|
| FR1-FR12 (Query Library) | ✅ | query_lib_core.py, queries/ folder |
| FR13-FR17 (Interactive Demo) | ✅ | interactive_demo_core.py |
| FR18-FR24 (AI Query Builder) | ✅ | ai_query_builder_core.py + Claude API |
| FR25-FR32 (University Analysis) | ✅ | university_analysis_core.py + CSV data |
| FR33-FR38 (Common Features) | ✅ | Consistent patterns across all modules |
| FR39-FR42 (Data Access) | ✅ | PatstatClient usage pattern |
| FR43-FR46 (Educational Materials) | ⚪ | Documentation deliverable (not architectural) |

**NFR Coverage:** All 20 non-functional requirements addressed through patterns (performance, reliability, integration, maintainability, usability).

### Implementation Readiness ✅

**Decision Completeness:** All critical decisions documented with ADR-001 through ADR-015.

**Structure Completeness:** Complete project directory structure defined with all files and components.

**Pattern Completeness:** All implementation patterns documented with examples.

### Architecture Completeness Checklist

- [x] Project context analyzed (Phase 2 extends Phase 1)
- [x] Technology foundation established (TIP platform + extensions)
- [x] Core decisions documented (ADR-013, ADR-014, ADR-015)
- [x] Implementation patterns defined (error handling, progress, file organization)
- [x] Project structure mapped to requirements
- [x] Architectural boundaries defined
- [x] Validation complete

### Architecture Readiness Assessment

**Overall Status:** ✅ READY FOR IMPLEMENTATION

**Confidence Level:** High - brownfield extension with proven Phase 1 patterns

**Key Strengths:**
- Extends proven Phase 1 architecture (12 existing ADRs)
- Clear per-notebook module separation
- No complex external dependencies (only Claude API)
- Consistent patterns across all notebooks

**First Implementation Priority:**
1. Create epics and stories from PRD
2. Set up sprint planning
3. Begin with Query Library notebook (highest training value)

