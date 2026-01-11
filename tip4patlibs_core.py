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
from epo.tipdata.patstat.database.models import TLS201_APPLN, TLS801_COUNTRY, TLS901_TECHN_FIELD_IPC, TLS904_NUTS

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
    'load_regions_for_jurisdiction',
    'patstat_client',
    'db',
    'reference_data',
    'state',
    'widget_factory',
]

# =============================================================================
# PATSTAT Connection Management
# =============================================================================

# Module-level connection (initialized by init_patstat())
patstat_client: Optional[PatstatClient] = None
db: Optional[Any] = None  # SQLAlchemy Session

# Module-level reference data (initialized after PATSTAT connection)
reference_data: Optional['ReferenceData'] = None

# Module-level state and widget factory (initialized in notebook after reference data load)
state: Optional['AnalysisState'] = None
widget_factory: Optional['WidgetFactory'] = None


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


def load_regions_for_jurisdiction(session, jurisdiction_code: str) -> List[Tuple[str, str]]:
    """
    Load NUTS regions for a jurisdiction.

    Queries tls904_nuts table for regions within the given jurisdiction.
    Returns regions at NUTS level 1 only (federal states/large regions).

    Args:
        session: SQLAlchemy session from PatstatClient.orm()
        jurisdiction_code: Two-letter jurisdiction code (e.g., "DE", "FR")

    Returns:
        List of (display_name, nuts_code) tuples sorted by display name.
        Returns empty list if no NUTS data for jurisdiction.

    Example:
        >>> regions = load_regions_for_jurisdiction(db, "DE")
        >>> print(regions[:3])
        [('Baden-Württemberg', 'DE1'), ('Bavaria', 'DE2'), ...]
    """
    if not jurisdiction_code:
        return []

    rows = session.query(
        TLS904_NUTS.nuts_label,
        TLS904_NUTS.nuts
    ).filter(
        TLS904_NUTS.nuts.like(f"{jurisdiction_code}%"),
        TLS904_NUTS.nuts_level == 1  # Level 1 only (federal states/large regions)
    ).distinct().order_by(TLS904_NUTS.nuts_label).all()

    return [(label, code) for label, code in rows if label and code]


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

    Creates ipywidgets components (ADR-007: ipywidgets chosen over ipyvuetify
    due to label rendering issues) with valid options loaded from reference data.

    Follows ADR-003 (Prevention by Design): widgets constrain input to valid,
    tested ranges loaded from ReferenceData.

    Attributes:
        ref: ReferenceData instance with dropdown options
        state: AnalysisState instance to update on selection
        _region_dropdown: Internal reference for cascade refresh (Story 2.2)
    """

    def __init__(self, reference_data: ReferenceData, state: AnalysisState):
        """
        Initialize WidgetFactory with reference data and state.

        Args:
            reference_data: ReferenceData instance with jurisdiction, tech field options
            state: AnalysisState instance to update when user makes selections
        """
        self.ref = reference_data
        self.state = state
        self._region_dropdown = None  # For cascade refresh (Story 2.2)
        self._region_helper = None    # Helper text for NUTS availability

    def jurisdiction_dropdown(self) -> widgets.Dropdown:
        """
        Create jurisdiction selection dropdown.

        Returns a dropdown populated with all patent offices from
        ReferenceData.jurisdictions (ADR-008: filing jurisdiction).

        Returns:
            widgets.Dropdown: Configured dropdown with observe callback

        Example:
            >>> factory = WidgetFactory(reference_data, state)
            >>> dropdown = factory.jurisdiction_dropdown()
            >>> display(dropdown)
        """
        # Build options: placeholder + all jurisdictions sorted alphabetically
        options = [('Select jurisdiction...', None)] + self.ref.jurisdictions

        dropdown = widgets.Dropdown(
            options=options,
            value=None,
            description='Jurisdiction:',
            style={'description_width': '100px'},
            layout=widgets.Layout(width='350px')
        )

        # Register callback to update state on selection change
        dropdown.observe(self._on_jurisdiction_change, names='value')

        return dropdown

    def region_dropdown(self) -> widgets.Dropdown:
        """
        Create region selection dropdown.

        Returns a dropdown for NUTS region selection. Initially shows
        "All regions" only. Populated dynamically when jurisdiction changes.

        Returns:
            widgets.Dropdown: Configured dropdown with observe callback

        Example:
            >>> factory = WidgetFactory(reference_data, state)
            >>> dropdown = factory.region_dropdown()
            >>> display(dropdown)
        """
        dropdown = widgets.Dropdown(
            options=[('All regions', None)],
            value=None,
            description='Region:',
            style={'description_width': '100px'},
            layout=widgets.Layout(width='350px'),
            disabled=True  # Disabled until jurisdiction selected
        )

        # Store reference for cascade refresh
        self._region_dropdown = dropdown

        # Register callback to update state on selection change
        dropdown.observe(self._on_region_change, names='value')

        return dropdown

    def region_helper_text(self) -> widgets.HTML:
        """
        Create helper text widget for region availability.

        Shows message when jurisdiction has no NUTS data.

        Returns:
            widgets.HTML: Helper text widget
        """
        helper = widgets.HTML(value='')
        self._region_helper = helper
        return helper

    def _on_jurisdiction_change(self, change):
        """
        Callback when jurisdiction selection changes.

        Updates state.country and triggers region dropdown refresh.

        Args:
            change: ipywidgets change dict with 'new' value
        """
        self.state.country = change['new']
        # Trigger region dropdown refresh
        if self._region_dropdown is not None:
            self._refresh_region_dropdown()

    def _on_region_change(self, change):
        """
        Callback when region selection changes.

        Updates state.region with selected NUTS code.

        Args:
            change: ipywidgets change dict with 'new' value
        """
        self.state.region = change['new']

    def _refresh_region_dropdown(self):
        """
        Refresh region dropdown based on selected jurisdiction.

        Queries NUTS regions for the selected jurisdiction and updates
        the dropdown options. Shows helper text if no NUTS data available.
        """
        if self._region_dropdown is None:
            return

        jurisdiction = self.state.country

        if not jurisdiction:
            # No jurisdiction selected - disable region dropdown
            self._region_dropdown.options = [('All regions', None)]
            self._region_dropdown.value = None
            self._region_dropdown.disabled = True
            if self._region_helper:
                self._region_helper.value = ''
            return

        # Query NUTS regions for this jurisdiction
        try:
            regions = load_regions_for_jurisdiction(get_db(), jurisdiction)
        except Exception:
            regions = []

        if regions:
            # Has NUTS data - enable and populate dropdown
            self._region_dropdown.options = [('All regions', None)] + regions
            self._region_dropdown.value = None
            self._region_dropdown.disabled = False
            if self._region_helper:
                self._region_helper.value = ''
        else:
            # No NUTS data - show only "All regions" with helper text
            self._region_dropdown.options = [('All regions', None)]
            self._region_dropdown.value = None
            self._region_dropdown.disabled = True
            if self._region_helper:
                self._region_helper.value = '<i style="color: #666;">Regional data not available for this jurisdiction</i>'

        # Reset state.region on jurisdiction change
        self.state.region = None


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
