# Architecture: TIP for PATLIBs

## Executive Summary

**TIP for PATLIBs** is a Jupyter notebook application that enables PATLIB staff to perform sophisticated patent analysis on the EPO Technology Intelligence Platform (TIP) without programming skills.

The architecture prioritizes:
- **Simplicity**: No-code UI via ipywidgets, complexity hidden in Python module
- **Transparency**: Users see their query parameters summarized before execution
- **Reliability**: Prevention by design - widgets constrain input to valid, tested ranges
- **Performance**: Pre-computed PATSTAT tables (tls230) + ORM queries with SQL escape hatch

**Target Environment**: EPO TIP JupyterLab
**Delivery**: Single notebook + supporting Python module
**Primary Users**: PATLIB staff (non-programmers)

---

## Decision Summary

| Category | Decision | Rationale |
|----------|----------|-----------|
| **Notebook Structure** | Hybrid: `notebook.ipynb` + `tip4patlibs_core.py` | Balance simplicity with maintainability; split to lib/ folder if >500 LOC |
| **Query Architecture** | ORM primary + SQL escape hatch | ORM for type safety, raw SQL for complex aggregations |
| **State Management** | State class with `summary()` | Clean source of truth + user transparency |
| **Input Handling** | Prevention by design | Widgets constrain to valid ranges; no error handling needed |
| **Widget Layout** | Progressive cells | Guided flow for non-technical users |
| **Visualizations** | Plotly with EPO colors | Bar/Line/Treemap; Top 10/25 applicants |
| **Export** | CSV (semicolon, UTF-8 BOM) + PNG | European standard, Excel-friendly |
| **Progress Feedback** | Simple spinner + performance tips | User pre-informed by dynamic tip labels |
| **Configuration** | In module | Sensible defaults, not user-configurable |
| **Caching** | None (MVP) | Deferred; DataFrames persist in memory |
| **Documentation** | Minimal inline | Self-explanatory UI + brief intro cell |

---

## Project Structure

```
tip4patlibs/
├── TIP_for_PATLIBs.ipynb          # User-facing notebook (progressive cells)
├── tip4patlibs_core.py            # Core logic module (<500 LOC target)
│   ├── AnalysisState              # State management class
│   ├── PatstatQueries             # Query builders (ORM + SQL)
│   ├── Widgets                    # UI component factories
│   ├── Charts                     # Plotly visualization builders
│   └── Export                     # CSV/PNG export functions
└── README.md                      # Brief setup instructions
```

**If >500 LOC, split to:**

```
tip4patlibs/
├── TIP_for_PATLIBs.ipynb
├── lib/
│   ├── __init__.py
│   ├── state.py                   # AnalysisState class
│   ├── queries.py                 # PATSTAT query builders
│   ├── widgets.py                 # UI components
│   ├── charts.py                  # Plotly visualizations
│   └── export.py                  # CSV/PNG export
└── README.md
```

---

## Notebook Cell Structure

```
Cell 1: Setup
├── "▶️ Run this cell first!"
├── Imports and initialization
├── PatstatClient connection
└── Load reference data (countries, tech fields)

Cell 2: Country & Region Selection
├── Country dropdown (person_ctry_code values)
├── Region dropdown (cascading NUTS from tls904)
└── Updates state.country, state.region

Cell 3: Technology Selection
├── Mode toggle: "Tech Field" / "Custom IPC/CPC"
├── If Tech Field: Dropdown of 35 WIPO fields
├── If Custom: Text input (max 5 IPC/CPC codes)
└── Updates state.tech_mode, state.tech_field, state.ipc_codes

Cell 4: Date Range & Options
├── Year range slider (2000-2024)
├── Performance tip label (dynamic: "⚡ Fast" / "🐢 Slow")
├── SME filter checkbox (<100 applications)
└── Updates state.year_start, state.year_end, state.sme_filter

Cell 5: Review & Run
├── Display state.summary() - transparent query preview
├── "Run Analysis" button
└── Validation (all required fields filled)

Cell 6: Results & Export
├── Output area for visualizations
├── Trend chart (Line)
├── Top applicants chart (Horizontal Bar)
├── Technology breakdown (Treemap)
├── Export buttons: CSV | PNG
└── Download links
```

---

## Technology Stack Details

### Core Technologies

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Platform** | EPO TIP | - | Hosting environment |
| **Notebook** | JupyterLab | TIP-provided | User interface |
| **Language** | Python | 3.x (TIP) | Core logic |
| **Data Access** | epo.tipdata.patstat | TIP-provided | PATSTAT ORM |
| **ORM** | SQLAlchemy | TIP-provided | Query building |
| **Data Processing** | Pandas | TIP-provided | DataFrame operations |
| **Visualization** | Plotly | TIP-provided | Interactive charts |
| **UI Widgets** | ipywidgets | TIP-provided | No-code controls |

### PATSTAT Tables Used

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `tls201_appln` | Applications | appln_id, appln_auth, appln_filing_year, docdb_family_id |
| `tls206_person` | Applicants/Inventors | person_id, psn_name, person_ctry_code, nuts, nuts_level |
| `tls207_pers_appln` | Person-Application link | appln_id, person_id, applt_seq_nr, invt_seq_nr |
| `tls230_appln_techn_field` | Pre-computed tech fields | appln_id, techn_field_nr, weight |
| `tls901_techn_field_ipc` | Tech field reference | techn_field_nr, techn_sector, techn_field |
| `tls904_nuts` | NUTS reference | nuts, nuts_level, nuts_label |
| `tls209_appln_ipc` | IPC classifications | appln_id, ipc_class_symbol |
| `tls224_appln_cpc` | CPC classifications | appln_id, cpc_class_symbol |

---

## Implementation Patterns

### State Management Pattern

```python
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class AnalysisState:
    """Single source of truth for user selections"""
    country: Optional[str] = None
    region: Optional[str] = None
    tech_mode: str = "field"              # "field" or "ipc"
    tech_field: Optional[int] = None      # WIPO field number (1-35)
    ipc_codes: List[str] = field(default_factory=list)  # Max 5
    year_start: int = 2019
    year_end: int = 2023
    sme_filter: bool = False              # <100 applications

    def summary(self) -> str:
        """Human-readable query summary for user transparency"""
        lines = [
            f"📍 Country: {self.country or 'Not selected'}",
            f"🗺️  Region: {self.region or 'All regions'}",
        ]
        if self.tech_mode == "field":
            lines.append(f"🔬 Technology: Field {self.tech_field}")
        else:
            lines.append(f"🔬 IPC/CPC: {', '.join(self.ipc_codes)}")
        lines.append(f"📅 Period: {self.year_start}-{self.year_end}")
        if self.sme_filter:
            lines.append("🏢 SME Focus: Yes (<100 applications)")
        return "\n".join(lines)

    def is_valid(self) -> tuple[bool, str]:
        """Check if state is ready for query execution"""
        if not self.country:
            return False, "Please select a country"
        if self.tech_mode == "field" and not self.tech_field:
            return False, "Please select a technology field"
        if self.tech_mode == "ipc" and len(self.ipc_codes) == 0:
            return False, "Please enter at least one IPC/CPC code"
        return True, "Ready"
```

### Query Pattern (ORM Primary)

```python
from epo.tipdata.patstat import PatstatClient
from epo.tipdata.patstat.database.models import (
    TLS201_APPLN, TLS206_PERSON, TLS207_PERS_APPLN,
    TLS230_APPLN_TECHN_FIELD, TLS901_TECHN_FIELD_IPC
)
from sqlalchemy import func, and_

class PatstatQueries:
    """Query builders - ORM primary, SQL escape hatch for complex aggregations"""

    def __init__(self, db):
        self.db = db

    def get_applications_by_tech_field(self, state: AnalysisState):
        """ORM query for tech field mode"""
        return self.db.query(
            TLS201_APPLN.appln_id,
            TLS201_APPLN.appln_filing_year,
            TLS201_APPLN.docdb_family_id
        ).join(
            TLS230_APPLN_TECHN_FIELD,
            TLS201_APPLN.appln_id == TLS230_APPLN_TECHN_FIELD.appln_id
        ).join(
            TLS207_PERS_APPLN,
            TLS201_APPLN.appln_id == TLS207_PERS_APPLN.appln_id
        ).join(
            TLS206_PERSON,
            TLS207_PERS_APPLN.person_id == TLS206_PERSON.person_id
        ).filter(
            and_(
                TLS230_APPLN_TECHN_FIELD.techn_field_nr == state.tech_field,
                TLS206_PERSON.person_ctry_code == state.country,
                TLS201_APPLN.appln_filing_year.between(state.year_start, state.year_end),
                TLS207_PERS_APPLN.applt_seq_nr > 0  # Applicants only
            )
        )

    def get_top_applicants(self, state: AnalysisState, limit: int = 10):
        """SQL escape hatch for complex aggregation"""
        sql = """
            SELECT
                p.psn_name as applicant_name,
                COUNT(DISTINCT a.appln_id) as application_count,
                COUNT(DISTINCT a.docdb_family_id) as invention_count
            FROM tls201_appln a
            JOIN tls207_pers_appln pa ON a.appln_id = pa.appln_id
            JOIN tls206_person p ON pa.person_id = p.person_id
            JOIN tls230_appln_techn_field tf ON a.appln_id = tf.appln_id
            WHERE
                tf.techn_field_nr = :tech_field
                AND p.person_ctry_code = :country
                AND a.appln_filing_year BETWEEN :year_start AND :year_end
                AND pa.applt_seq_nr > 0
                {sme_filter}
            GROUP BY p.psn_name
            ORDER BY application_count DESC
            LIMIT :limit
        """

        sme_clause = ""
        if state.sme_filter:
            sme_clause = """
                AND p.psn_name IN (
                    SELECT psn_name FROM tls206_person
                    GROUP BY psn_name
                    HAVING COUNT(*) < 100
                )
            """

        return self.db.execute(
            sql.format(sme_filter=sme_clause),
            {
                "tech_field": state.tech_field,
                "country": state.country,
                "year_start": state.year_start,
                "year_end": state.year_end,
                "limit": limit
            }
        )
```

### Widget Factory Pattern

```python
import ipywidgets as widgets
from IPython.display import display

class WidgetFactory:
    """Creates pre-configured widgets with valid options only"""

    def __init__(self, reference_data):
        self.ref = reference_data  # Preloaded from PATSTAT

    def country_dropdown(self, on_change=None):
        """Country selection - constrained to valid values"""
        w = widgets.Dropdown(
            options=[('Select country...', None)] + self.ref.countries,
            description='Country:',
            style={'description_width': '100px'}
        )
        if on_change:
            w.observe(on_change, names='value')
        return w

    def region_dropdown(self, country_code: str, on_change=None):
        """Region selection - cascades from country"""
        regions = self.ref.get_regions_for_country(country_code)
        w = widgets.Dropdown(
            options=[('All regions', None)] + regions,
            description='Region:',
            style={'description_width': '100px'}
        )
        if on_change:
            w.observe(on_change, names='value')
        return w

    def year_range_slider(self, on_change=None):
        """Year range with performance tip"""
        w = widgets.IntRangeSlider(
            value=[2019, 2023],
            min=2000,
            max=2024,
            step=1,
            description='Years:',
            style={'description_width': '100px'}
        )
        if on_change:
            w.observe(on_change, names='value')
        return w

    def performance_tip(self, year_range_widget):
        """Dynamic performance tip based on year span"""
        tip = widgets.HTML(value="⚡ Fast query (~10 sec)")

        def update(change):
            span = change['new'][1] - change['new'][0]
            if span <= 5:
                tip.value = "⚡ Fast query (~10 sec)"
            elif span <= 10:
                tip.value = "⏱️ Medium query (~30 sec)"
            else:
                tip.value = "🐢 Large query (~2 min)"

        year_range_widget.observe(update, names='value')
        return tip
```

### Visualization Pattern

```python
import plotly.express as px
import plotly.graph_objects as go

# EPO brand colors
EPO_COLORS = {
    'primary': '#C8102E',      # EPO Red
    'secondary': '#6D6E71',    # EPO Gray
    'light': '#F5F5F5',        # Light background
    'dark': '#1D1D1B',         # Dark text
}

EPO_PALETTE = ['#C8102E', '#6D6E71', '#A6093D', '#8B8D8E', '#D4495B', '#B0B1B3']

class ChartBuilder:
    """Plotly chart builders with EPO styling"""

    @staticmethod
    def trend_line(df, x='year', y='count', title='Patent Applications Over Time'):
        """Line chart for temporal trends"""
        fig = px.line(
            df, x=x, y=y,
            title=title,
            color_discrete_sequence=[EPO_COLORS['primary']]
        )
        fig.update_layout(
            font_family="Arial",
            title_font_size=16,
            xaxis_title="Year",
            yaxis_title="Applications"
        )
        return fig

    @staticmethod
    def top_applicants_bar(df, x='count', y='applicant', title='Top Applicants', limit=10):
        """Horizontal bar chart for rankings"""
        df_top = df.head(limit)
        fig = px.bar(
            df_top, x=x, y=y,
            orientation='h',
            title=title,
            color_discrete_sequence=[EPO_COLORS['primary']]
        )
        fig.update_layout(
            font_family="Arial",
            title_font_size=16,
            yaxis={'categoryorder': 'total ascending'},
            xaxis_title="Applications",
            yaxis_title=""
        )
        return fig

    @staticmethod
    def tech_treemap(df, path=['sector', 'field'], values='count', title='Technology Breakdown'):
        """Treemap for technology distribution"""
        fig = px.treemap(
            df, path=path, values=values,
            title=title,
            color_discrete_sequence=EPO_PALETTE
        )
        fig.update_layout(
            font_family="Arial",
            title_font_size=16
        )
        return fig
```

### Export Pattern

```python
import pandas as pd
from pathlib import Path
from datetime import datetime

class Exporter:
    """CSV and PNG export with consistent naming"""

    @staticmethod
    def generate_filename(state: AnalysisState, extension: str) -> str:
        """Generate descriptive filename"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        tech = f"field{state.tech_field}" if state.tech_mode == "field" else "ipc"
        return f"tip4patlibs_{state.country}_{tech}_{state.year_start}-{state.year_end}_{timestamp}.{extension}"

    @staticmethod
    def to_csv(df: pd.DataFrame, state: AnalysisState) -> str:
        """Export DataFrame to CSV (European format)"""
        filename = Exporter.generate_filename(state, 'csv')
        df.to_csv(
            filename,
            index=False,
            sep=';',                    # European standard
            encoding='utf-8-sig',       # UTF-8 with BOM for Excel
        )
        return filename

    @staticmethod
    def to_png(fig, state: AnalysisState, chart_name: str) -> str:
        """Export Plotly figure to PNG"""
        filename = Exporter.generate_filename(state, 'png').replace('.png', f'_{chart_name}.png')
        fig.write_image(filename, scale=2)  # 2x for high DPI
        return filename
```

---

## Data Architecture

### Key Relationships

```
┌─────────────────┐
│  tls201_appln   │  Main applications table
│  (137M rows)    │
└────────┬────────┘
         │ appln_id
         │
    ┌────┴─────────────────────┬─────────────────────────┐
    │                          │                         │
    ▼                          ▼                         ▼
┌─────────────────┐    ┌─────────────────┐     ┌─────────────────┐
│ tls207_pers_appln│    │tls230_appln_    │     │ tls209_appln_ipc│
│ (person link)   │    │techn_field      │     │ (IPC codes)     │
└────────┬────────┘    │ (pre-computed)  │     └─────────────────┘
         │             └─────────────────┘
         │ person_id
         ▼
┌─────────────────┐
│  tls206_person  │  Contains: psn_name, person_ctry_code, nuts
│  (96M rows)     │
└─────────────────┘

Reference Tables:
┌─────────────────┐     ┌─────────────────┐
│tls901_techn_    │     │  tls904_nuts    │
│field_ipc (771)  │     │  (2,056 rows)   │
│ 35 WIPO fields  │     │  NUTS reference │
└─────────────────┘     └─────────────────┘
```

### Key Filters

| Filter | Table | Column | Notes |
|--------|-------|--------|-------|
| Applicants only | tls207_pers_appln | `applt_seq_nr > 0` | Excludes inventors |
| Country | tls206_person | `person_ctry_code` | Applicant's country |
| Region | tls206_person | `nuts` | NUTS code |
| Tech field | tls230_appln_techn_field | `techn_field_nr` | 1-35 |
| Year | tls201_appln | `appln_filing_year` | Integer |
| Family | tls201_appln | `docdb_family_id` | For counting inventions |

### Patent Family Counting

Two ways to count:
- **Applications (filings)**: `COUNT(appln_id)` - same invention counted multiple times across jurisdictions
- **Inventions (families)**: `COUNT(DISTINCT docdb_family_id)` - one per patent family

Default to **applications** but show both where relevant.

---

## Performance Considerations

### Query Optimization

| Strategy | Implementation |
|----------|----------------|
| **Use pre-computed tables** | `tls230_appln_techn_field` instead of IPC pattern matching |
| **Filter early** | Apply country/year filters before joins |
| **Limit results** | Top 10/25 applicants, not unlimited |
| **Avoid SELECT *** | Specify needed columns only |
| **Use psn_name** | Standardized names for better grouping |

### Expected Query Times

| Query Scope | Expected Time |
|-------------|---------------|
| Single country, 5 years, 1 tech field | ~10 sec |
| Single country, 10 years, 1 tech field | ~30 sec |
| Single country, 20 years, 1 tech field | ~2 min |
| With SME filter | +20% time |

### User Feedback

- Dynamic performance tip before query runs
- Simple spinner during execution
- User is pre-informed, no surprises

---

## Security Architecture

**N/A for this project.**

- TIP platform handles authentication
- PATSTAT is read-only
- No user data stored
- No API exposed

---

## Deployment Architecture

**Target**: EPO Technology Intelligence Platform (TIP)

```
┌─────────────────────────────────────────┐
│            EPO TIP Platform             │
│  ┌───────────────────────────────────┐  │
│  │         JupyterLab                │  │
│  │  ┌─────────────────────────────┐  │  │
│  │  │   TIP_for_PATLIBs.ipynb    │  │  │
│  │  │   tip4patlibs_core.py      │  │  │
│  │  └─────────────────────────────┘  │  │
│  └───────────────────────────────────┘  │
│                   │                      │
│                   ▼                      │
│  ┌───────────────────────────────────┐  │
│  │      PATSTAT BigQuery             │  │
│  │      (via epo.tipdata.patstat)    │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

**Distribution**:
- Share notebook + module via TIP file system
- Or package as .zip for download
- No pip install required (uses TIP-provided libraries)

---

## Development Environment

### Prerequisites

- Access to EPO TIP platform
- TIP JupyterLab environment
- No local setup required (all dependencies on TIP)

### For Local Development (optional)

```bash
# Not required - develop directly on TIP
# But if needed for testing:
pip install pandas plotly ipywidgets
# Note: epo.tipdata.patstat only available on TIP
```

### Setup Commands (on TIP)

```bash
# Clone or upload project files
# No installation needed - just open notebook

# Verify environment
python -c "from epo.tipdata.patstat import PatstatClient; print('OK')"
```

---

## Architecture Decision Records (ADRs)

### ADR-001: Hybrid Notebook Structure

**Context**: Need balance between simplicity (single file) and maintainability.

**Decision**: Start with notebook + single Python module. Split to lib/ folder if exceeding 500 LOC.

**Consequences**: Easy to share, code is testable, can grow if needed.

---

### ADR-002: ORM Primary with SQL Escape Hatch

**Context**: Need type-safe queries but also support complex aggregations.

**Decision**: Use SQLAlchemy ORM for standard queries; raw SQL for complex GROUP BY / window functions.

**Consequences**: Best of both worlds. Two patterns to maintain but clear separation.

---

### ADR-003: Prevention by Design

**Context**: Non-technical users could create invalid queries.

**Decision**: Widgets constrain input to valid, tested ranges. No error handling for invalid input because invalid input is impossible.

**Consequences**: No try/catch complexity. Pre-loaded options guarantee valid queries.

---

### ADR-004: Tech Field Dual Mode

**Context**: WIPO 35 fields efficient but unfamiliar; IPC/CPC familiar but complex.

**Decision**: Support both modes via toggle. Tech field dropdown uses tls230 (fast). Custom IPC/CPC uses tls209/tls224 (flexible).

**Consequences**: Power users get IPC. Casual users get predefined fields. Backend handles both.

---

### ADR-005: Applicant Country for Regional Analysis [SUPERSEDED by ADR-008]

**Context**: Could filter by filing jurisdiction or applicant location.

**Decision**: ~~Use applicant's country (`person_ctry_code`) and NUTS region from `tls206_person`.~~

**Status**: SUPERSEDED by ADR-008. The `person_ctry_code` field in TLS206 has data quality issues and doesn't match user intent.

**Consequences**: ~~Shows where innovation originates, not where patents are filed. SME filter added to address HQ filing bias.~~

---

### ADR-006: State Class with Summary

**Context**: Need to manage user selections and show transparency.

**Decision**: Single `AnalysisState` dataclass with `summary()` method for user-facing query preview.

**Consequences**: Clean state management. Users see exactly what they're querying before execution.

---

### ADR-007: UI Framework Selection

**Context**: TIP platform provides both `ipywidgets` (standard Jupyter widgets) and `ipyvuetify` (Material Design components). Need to choose primary UI framework for all user-facing controls.

**Status**: DECIDED (2026-01-11) - Spike completed in Story 2.1.

**Spike Results** (Story 2.1):

| Criterion | ipywidgets | ipyvuetify | Notes |
|-----------|------------|------------|-------|
| Visual Polish | 3/5 | 4/5 | ipyvuetify looks nicer (Material Design) |
| Code Complexity | 5/5 | 4/5 | ipywidgets simpler API |
| Responsiveness | 4/5 | 4/5 | Both adequate |
| Layout Control | 4/5 | 3/5 | VBox/HBox reliable |
| **Rendering** | 5/5 | 2/5 | **DEAL BREAKER**: ipyvuetify floating labels clipped |

**Critical Finding**: ipyvuetify's Material Design floating labels do not render correctly in TIP's Jupyter environment. The label text ("Jurisdiction") gets clipped at the top of the widget container. This is a fundamental UX issue that cannot be easily fixed.

**Decision**: Use **ipywidgets** for all selection interface components.

**Rationale**:
1. ipyvuetify IS available on TIP (confirmed)
2. BUT: Label rendering bug makes ipyvuetify unsuitable for production
3. ipywidgets renders cleanly and reliably across all TIP containers
4. Simpler API reduces maintenance burden
5. Adequate for MVP requirements

**Consequences**:
- All Epic 2 widgets use ipywidgets.Dropdown, ipywidgets.IntRangeSlider, etc.
- Basic styling but functional and reliable
- Consider CSS enhancements in future if polish needed

---

### ADR-008: Filing Jurisdiction over Applicant Country

**Context**: Story 1.3 initially loaded country data from `TLS206_PERSON.person_ctry_code` (applicant's residence). Testing revealed 479 "countries" due to data quality issues in TLS206 (historical codes, organization codes, missing data). More importantly, PATLIB users want "patents filed IN Germany" not "patents BY German applicants."

**Decision**: Use `TLS201_APPLN.appln_auth` (filing jurisdiction/patent office) instead of `TLS206_PERSON.person_ctry_code` for country filtering.

**Rationale**:
1. **User intent**: "Select Germany" means "patents filed at DPMA" not "patents from German applicants"
2. **Data quality**: `appln_auth` is always populated and reliable; `person_ctry_code` has gaps and inconsistencies
3. **Clean values**: ~50 patent office codes vs 479 messy country codes
4. **Industry standard**: Patent analysis typically filters by filing jurisdiction first

**Consequences**:
- Supersedes ADR-005
- Country dropdown shows patent offices (EP, US, DE, JP, CN, etc.) with friendly names
- Regional filtering (NUTS) deferred or removed - NUTS codes relate to applicant location, not filing jurisdiction
- SME filter remains viable (based on applicant filing history)

**Reference**: PATSTAT training documentation `TLS206_PERSON.html` - person_ctry_code reliability issues.

---

### ADR-009: No Hardcoded Reference Data

**Context**: During Story 1.3 implementation, country/jurisdiction names were hardcoded in a Python dict (`JURISDICTION_NAMES`) instead of querying PATSTAT's lookup table `tls801_country`. This creates maintenance burden, risks stale data, and violates single source of truth.

**Decision**: Never hardcode reference data when PATSTAT provides lookup tables (TLS8xx series). Always query the authoritative source.

**Enforcement**:
- Any hardcoded mapping requires explicit approval from Architect (Winston) or Product Owner (BMad)
- Approval must include documented justification
- Story checklist item: "Verify no hardcoded reference data - check TLS8xx tables"

**Lookup Tables Available**:
| Table | Purpose |
|-------|---------|
| `tls801_country` | Country/jurisdiction codes and names (242 rows) |
| `tls901_techn_field_ipc` | Technology fields and sectors |
| `tls902_ipc_nace2` | IPC to NACE mapping |

**Consequences**:
- Self-healing: New jurisdictions automatically appear
- Single source of truth: PATSTAT is authoritative
- No maintenance: No code changes needed when data changes

---

_Generated by BMAD Architecture Workflow_
_Date: 2026-01-12_
_Architect: Winston_
_For: BMad_
