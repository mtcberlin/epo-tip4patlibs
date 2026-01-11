"""
TIP for PATLIBs - Core Module
=============================

Core logic module for the TIP for PATLIBs Jupyter notebook application.
Enables PATLIB staff to perform patent analysis on EPO's Technology Intelligence Platform.

This module contains:
- AnalysisState: State management dataclass for user selections
- PatstatQueries: Query builder for PATSTAT database (placeholder)
- WidgetFactory: UI component factories (placeholder)
- ChartBuilder: Plotly visualization builders (placeholder)
- Exporter: CSV/PNG export utilities (placeholder)

Architecture: ADR-001 Hybrid Structure
- Single module file (<500 LOC target)
- Split to lib/ folder if exceeding 500 LOC

Author: BMad
Version: 0.1.0
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Any

# Heavy imports - kept in module, not notebook
import pandas as pd
import plotly.express as px
import ipywidgets as widgets

# PATSTAT connection and models
from epo.tipdata.patstat import PatstatClient
from epo.tipdata.patstat.database.models import TLS201_APPLN, TLS801_COUNTRY, TLS901_TECHN_FIELD_IPC

# Module exports - controls what `from tip4patlibs_core import *` exposes
__all__ = [
    'AnalysisState',
    'ReferenceData',
    'PatstatQueries',
    'WidgetFactory',
    'ChartBuilder',
    'Exporter',
    'init_patstat',
    'get_db',
    'patstat_client',
    'db',
    'reference_data',
]

# =============================================================================
# PATSTAT Connection Management
# =============================================================================

# Module-level connection (initialized by init_patstat())
patstat_client: Optional[PatstatClient] = None
db: Optional[Any] = None  # SQLAlchemy Session

# Module-level reference data (initialized after PATSTAT connection)
reference_data: Optional['ReferenceData'] = None


def init_patstat() -> Tuple[PatstatClient, Any]:
    """
    Initialize PATSTAT connection.

    Establishes connection to PATSTAT database via EPO's PatstatClient.
    Stores the client and ORM session in module-level variables for
    access by subsequent notebook cells.

    Returns:
        tuple: (PatstatClient, SQLAlchemy session) on success

    Raises:
        ConnectionError: If PATSTAT is unavailable

    Example:
        >>> init_patstat()
        >>> print(db)  # Access the session
    """
    global patstat_client, db
    try:
        patstat_client = PatstatClient(env='PROD')
        db = patstat_client.orm()
        return patstat_client, db
    except Exception as e:
        raise ConnectionError(f"Could not connect to PATSTAT: {e}") from e


def get_db() -> Any:
    """
    Get the active database session.

    Returns:
        SQLAlchemy Session: The active PATSTAT database session

    Raises:
        RuntimeError: If PATSTAT has not been initialized

    Example:
        >>> session = get_db()
        >>> result = session.query(TLS201_APPLN).limit(1).first()
    """
    if db is None:
        raise RuntimeError("PATSTAT not initialized. Run init_patstat() first.")
    return db


# =============================================================================
# Reference Data Management
# =============================================================================

# ADR-009: No hardcoded reference data - query tls801_country for names


@dataclass
class ReferenceData:
    """
    Cached reference data for dropdown options.

    Pre-loaded at startup to ensure instant response when users
    interact with filter controls. Follows ADR-003 (Prevention by Design).

    Attributes:
        jurisdictions: List of (display_name, code) tuples for patent offices
                       ADR-008: Uses appln_auth from TLS201, not person_ctry_code
        tech_fields: List of (display_name, field_nr) tuples for WIPO 35 fields
        sectors: List of sector names for grouping technology fields
    """
    jurisdictions: List[Tuple[str, str]]  # (display_name, code) - patent offices
    tech_fields: List[Tuple[str, int]]    # (display_name, field_nr)
    sectors: List[str]                     # Sector names for grouping

    @classmethod
    def load(cls, session) -> 'ReferenceData':
        """
        Load all reference data from PATSTAT.

        Queries distinct values from PATSTAT tables:
        - tls201_appln.appln_auth for filing jurisdictions (ADR-008)
        - tls901_techn_field_ipc for technology fields and sectors

        Args:
            session: SQLAlchemy session from PatstatClient.orm()

        Returns:
            ReferenceData: Populated instance with all dropdown options

        Raises:
            ValueError: If sanity checks fail (< 20 jurisdictions, != 35 tech fields)
        """
        # ADR-009: Load country/jurisdiction names from tls801_country (no hardcoded data)
        country_names_rows = session.query(
            TLS801_COUNTRY.ctry_code,
            TLS801_COUNTRY.st3_name
        ).all()
        country_name_lookup = {row[0]: row[1] for row in country_names_rows if row[0]}

        # Load jurisdictions from tls201_appln (ADR-008: filing jurisdiction, not applicant country)
        jurisdiction_codes = session.query(
            TLS201_APPLN.appln_auth
        ).distinct().all()

        jurisdictions = []
        for (code,) in jurisdiction_codes:
            if code and code.strip():  # Skip empty/null codes
                code_clean = code.strip()
                # Use tls801_country name, fall back to code if not found
                display_name = country_name_lookup.get(code_clean, code_clean)
                jurisdictions.append((display_name, code_clean))

        # Sort alphabetically by display name
        jurisdictions.sort(key=lambda x: x[0])

        # Sanity check: at least 20 jurisdictions (major patent offices)
        if len(jurisdictions) < 20:
            raise ValueError(f"Expected >= 20 jurisdictions, got {len(jurisdictions)}")

        # Load technology fields from tls901_techn_field_ipc
        tech_rows = session.query(
            TLS901_TECHN_FIELD_IPC.techn_field_nr,
            TLS901_TECHN_FIELD_IPC.techn_field,
            TLS901_TECHN_FIELD_IPC.techn_sector
        ).distinct().all()

        # Build tech fields list: "13 - Medical technology"
        tech_fields_dict = {}
        sectors_set = set()

        for field_nr, field_name, sector in tech_rows:
            if field_nr is not None and field_name:
                display_name = f"{field_nr} - {field_name}"
                tech_fields_dict[field_nr] = display_name
            if sector:
                sectors_set.add(sector)

        # Convert to sorted list of tuples
        tech_fields = [(name, nr) for nr, name in sorted(tech_fields_dict.items())]

        # Sanity check: exactly 35 technology fields
        if len(tech_fields) != 35:
            raise ValueError(f"Expected 35 tech fields, got {len(tech_fields)}")

        # Sectors as sorted list
        sectors = sorted(sectors_set)

        # Sanity check: exactly 5 sectors
        if len(sectors) != 5:
            raise ValueError(f"Expected 5 sectors, got {len(sectors)}")

        return cls(jurisdictions=jurisdictions, tech_fields=tech_fields, sectors=sectors)


@dataclass
class AnalysisState:
    """
    Single source of truth for user selections.

    Manages all filter criteria for patent analysis queries.
    Used by widgets to store selections and by queries to build filters.

    Attributes:
        country: ISO country code (e.g., "DE" for Germany)
        region: NUTS code for regional filtering (e.g., "DE2" for Bavaria)
        tech_mode: Technology selection mode - "field" (WIPO 35) or "ipc" (custom codes)
        tech_field: WIPO technology field number (1-35) when tech_mode="field"
        ipc_codes: List of IPC/CPC codes (max 5) when tech_mode="ipc"
        year_start: Start year for date range filter
        year_end: End year for date range filter
        sme_filter: If True, filter to applicants with <100 total applications
    """
    country: Optional[str] = None
    region: Optional[str] = None
    tech_mode: str = "field"
    tech_field: Optional[int] = None
    ipc_codes: List[str] = field(default_factory=list)
    year_start: int = 2019
    year_end: int = 2023
    sme_filter: bool = False

    def summary(self) -> str:
        """
        Human-readable summary of current selections.

        Returns formatted string with emoji indicators for display
        in the Review & Run panel before query execution.

        Returns:
            str: Formatted multi-line summary of all selections
        """
        lines = [
            f"Country: {self.country or 'Not selected'}",
            f"Region: {self.region or 'All regions'}",
        ]
        if self.tech_mode == "field":
            tech_display = f"Field {self.tech_field}" if self.tech_field else "Not selected"
            lines.append(f"Technology: {tech_display}")
        else:
            codes = ', '.join(self.ipc_codes) if self.ipc_codes else 'None entered'
            lines.append(f"IPC/CPC: {codes}")
        lines.append(f"Period: {self.year_start}-{self.year_end}")
        if self.sme_filter:
            lines.append("SME Focus: Yes (<100 applications)")
        return "\n".join(lines)

    def is_valid(self) -> Tuple[bool, str]:
        """
        Validate that required fields are set for query execution.

        Checks:
        - Country must be selected
        - Either tech_field (field mode) or ipc_codes (ipc mode) must be set

        Returns:
            Tuple[bool, str]: (is_valid, message)
                - (True, "Ready") if all required fields are set
                - (False, "error message") describing what's missing
        """
        # Check country is selected
        if self.country is None:
            return (False, "Please select a country")

        # Check technology selection based on mode
        if self.tech_mode == "field":
            if self.tech_field is None:
                return (False, "Please select a technology field")
        else:  # ipc mode
            if not self.ipc_codes:
                return (False, "Please enter at least one IPC/CPC code")

        return (True, "Ready")


class PatstatQueries:
    """
    Query builder for PATSTAT database operations.

    Provides methods to build and execute queries against PATSTAT
    using the EPO patstat library and SQLAlchemy ORM.

    Placeholder - full implementation in Epic 3.
    """

    def __init__(self, db):
        """
        Initialize with PATSTAT database connection.

        Args:
            db: SQLAlchemy session from PatstatClient.orm()
        """
        self.db = db


class WidgetFactory:
    """
    Factory for creating pre-configured UI widgets.

    Creates ipywidgets (or ipyvuetify - pending ADR-007) components
    with valid options loaded from reference data.

    Placeholder - full implementation in Epic 2.
    """
    pass


class ChartBuilder:
    """
    Builder for Plotly visualizations with EPO styling.

    Creates interactive charts for patent analysis results:
    - Trend line charts
    - Top applicants bar charts
    - Technology breakdown treemaps
    - Regional distribution charts

    Placeholder - full implementation in Epic 4.
    """
    pass


class Exporter:
    """
    Export utilities for CSV and PNG output.

    Handles:
    - CSV export with European formatting (semicolon delimiter, UTF-8 BOM)
    - PNG export for Plotly charts
    - Descriptive filename generation

    Placeholder - full implementation in Epic 5.
    """
    pass
