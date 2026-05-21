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
import plotly.graph_objects as go
import ipywidgets as widgets

# PATSTAT connection and models
from epo.tipdata.patstat import PatstatClient
from epo.tipdata.patstat.database.models import (
    TLS201_APPLN, TLS206_PERSON, TLS207_PERS_APPLN,
    TLS209_APPLN_IPC, TLS230_APPLN_TECHN_FIELD,
    TLS801_COUNTRY, TLS901_TECHN_FIELD_IPC, TLS904_NUTS
)
from sqlalchemy import func, and_, or_
from sqlalchemy.orm import Session

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
    'analysis_results',
    'display_results',
    'EPO_COLORS',
    'EPO_PALETTE',
    'EPO_LAYOUT',
    'truncate_name',
    'create_export_buttons',
    'export_all_charts',
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

# Module-level analysis results (populated by PatstatQueries, consumed by ChartBuilder)
# Keys: 'trend', 'applicants', 'tech_breakdown', 'regional'
analysis_results: dict = {}


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
            f"📍 Country: {self.country or 'Not selected'}",
            f"🗺️ Region: {self.region or 'All regions'}",
        ]
        if self.tech_mode == "field":
            tech_display = f"Field {self.tech_field}" if self.tech_field else "Not selected"
            lines.append(f"🔬 Technology: {tech_display}")
        else:
            codes = ', '.join(self.ipc_codes) if self.ipc_codes else 'None entered'
            lines.append(f"🔬 IPC/CPC: {codes}")
        lines.append(f"📅 Period: {self.year_start}-{self.year_end}")
        if self.sme_filter:
            lines.append("🏢 SME Focus: Yes (<100 applications)")
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

    Architecture: ADR-002 ORM primary with SQL escape hatch
    - get_trend_data: ORM (straightforward aggregation)
    - get_top_applicants: SQL escape hatch (complex GROUP BY) - Story 3.3

    Attributes:
        db: SQLAlchemy session from PatstatClient.orm()

    Example:
        >>> queries = PatstatQueries(get_db())
        >>> trend_df = queries.get_trend_data(state)
    """

    # Empty DataFrame schemas for error returns (AC8)
    TREND_SCHEMA = {'year': pd.Series(dtype='int64'),
                    'application_count': pd.Series(dtype='int64'),
                    'invention_count': pd.Series(dtype='int64')}

    APPLICANTS_SCHEMA = {'applicant_name': pd.Series(dtype='str'),
                         'application_count': pd.Series(dtype='int64'),
                         'invention_count': pd.Series(dtype='int64'),
                         'country': pd.Series(dtype='str')}

    TECH_BREAKDOWN_SCHEMA = {'ipc_class': pd.Series(dtype='str'),
                             'ipc_label': pd.Series(dtype='str'),
                             'count': pd.Series(dtype='int64')}

    REGIONAL_SCHEMA = {'region': pd.Series(dtype='str'),
                       'region_label': pd.Series(dtype='str'),
                       'count': pd.Series(dtype='int64')}

    def __init__(self, db: Session) -> None:
        """
        Initialize with PATSTAT database connection.

        Args:
            db: SQLAlchemy session from PatstatClient.orm()
        """
        self.db = db

    def _empty_trend_df(self) -> pd.DataFrame:
        """Return empty DataFrame with trend schema."""
        return pd.DataFrame(self.TREND_SCHEMA)

    def _empty_applicants_df(self) -> pd.DataFrame:
        """Return empty DataFrame with applicants schema."""
        return pd.DataFrame(self.APPLICANTS_SCHEMA)

    def _empty_tech_breakdown_df(self) -> pd.DataFrame:
        """Return empty DataFrame with tech breakdown schema."""
        return pd.DataFrame(self.TECH_BREAKDOWN_SCHEMA)

    def _empty_regional_df(self) -> pd.DataFrame:
        """Return empty DataFrame with regional schema."""
        return pd.DataFrame(self.REGIONAL_SCHEMA)

    def get_trend_data(self, state: 'AnalysisState', debug: bool = False) -> pd.DataFrame:
        """
        Get yearly application and invention counts.

        Implements AC3, AC4, AC5, AC6, AC7.

        Args:
            state: AnalysisState with filter parameters
            debug: If True, prints the compiled SQL query for transparency

        Returns:
            DataFrame with columns: year, application_count, invention_count
            Grouped by appln_filing_year, ordered ascending.

        Architecture:
            - Uses ORM query (ADR-002)
            - Filters by appln_auth (ADR-008)
            - Respects tech_mode, region, sme_filter

        Example:
            >>> queries = PatstatQueries(get_db())
            >>> df = queries.get_trend_data(state, debug=True)  # Shows SQL
        """
        try:
            # Build base query with aggregations
            if state.tech_mode == 'field' and state.tech_field is not None:
                # Tech Field mode - use tls230_appln_techn_field (AC4)
                query = self.db.query(
                    TLS201_APPLN.appln_filing_year.label('year'),
                    func.count(TLS201_APPLN.appln_id).label('application_count'),
                    func.count(func.distinct(TLS201_APPLN.docdb_family_id)).label('invention_count')
                ).join(
                    TLS230_APPLN_TECHN_FIELD,
                    TLS201_APPLN.appln_id == TLS230_APPLN_TECHN_FIELD.appln_id
                ).join(
                    TLS207_PERS_APPLN,
                    TLS201_APPLN.appln_id == TLS207_PERS_APPLN.appln_id
                )

                # Build filter conditions
                filters = [
                    TLS201_APPLN.appln_auth == state.country,
                    TLS230_APPLN_TECHN_FIELD.techn_field_nr == state.tech_field,
                    TLS201_APPLN.appln_filing_year.between(state.year_start, state.year_end),
                    TLS207_PERS_APPLN.applt_seq_nr > 0  # Applicants only
                ]

                # Add region filter if set (AC6)
                if state.region is not None:
                    query = query.join(
                        TLS206_PERSON,
                        TLS207_PERS_APPLN.person_id == TLS206_PERSON.person_id
                    )
                    filters.append(TLS206_PERSON.nuts.like(f"{state.region}%"))

                # Add SME filter if set (AC7)
                if state.sme_filter:
                    # Subquery for applicants with <100 total applications
                    sme_subquery = self.db.query(
                        TLS207_PERS_APPLN.person_id
                    ).group_by(
                        TLS207_PERS_APPLN.person_id
                    ).having(
                        func.count(TLS207_PERS_APPLN.appln_id) < 100
                    ).subquery()

                    query = query.filter(TLS207_PERS_APPLN.person_id.in_(sme_subquery))

                query = query.filter(and_(*filters))

            else:
                # IPC mode - use tls209_appln_ipc (AC5)
                query = self.db.query(
                    TLS201_APPLN.appln_filing_year.label('year'),
                    func.count(TLS201_APPLN.appln_id).label('application_count'),
                    func.count(func.distinct(TLS201_APPLN.docdb_family_id)).label('invention_count')
                ).join(
                    TLS209_APPLN_IPC,
                    TLS201_APPLN.appln_id == TLS209_APPLN_IPC.appln_id
                ).join(
                    TLS207_PERS_APPLN,
                    TLS201_APPLN.appln_id == TLS207_PERS_APPLN.appln_id
                )

                # Build IPC LIKE conditions
                ipc_conditions = [TLS209_APPLN_IPC.ipc_class_symbol.like(f"{code}%")
                                  for code in state.ipc_codes]

                filters = [
                    TLS201_APPLN.appln_auth == state.country,
                    or_(*ipc_conditions),  # Match any of the IPC codes
                    TLS201_APPLN.appln_filing_year.between(state.year_start, state.year_end),
                    TLS207_PERS_APPLN.applt_seq_nr > 0
                ]

                # Add region filter if set (AC6)
                if state.region is not None:
                    query = query.join(
                        TLS206_PERSON,
                        TLS207_PERS_APPLN.person_id == TLS206_PERSON.person_id
                    )
                    filters.append(TLS206_PERSON.nuts.like(f"{state.region}%"))

                # Add SME filter if set (AC7)
                if state.sme_filter:
                    sme_subquery = self.db.query(
                        TLS207_PERS_APPLN.person_id
                    ).group_by(
                        TLS207_PERS_APPLN.person_id
                    ).having(
                        func.count(TLS207_PERS_APPLN.appln_id) < 100
                    ).subquery()

                    query = query.filter(TLS207_PERS_APPLN.person_id.in_(sme_subquery))

                query = query.filter(and_(*filters))

            # Apply grouping and ordering
            query = query.group_by(
                TLS201_APPLN.appln_filing_year
            ).order_by(
                TLS201_APPLN.appln_filing_year
            )

            # Debug mode - print compiled SQL for transparency (recommended by Architect)
            if debug:
                try:
                    compiled = query.statement.compile(
                        dialect=self.db.bind.dialect,
                        compile_kwargs={"literal_binds": True}
                    )
                    print("=" * 60)
                    print("DEBUG: Compiled SQL Query")
                    print("=" * 60)
                    print(str(compiled))
                    print("=" * 60)
                except Exception as debug_err:
                    print(f"DEBUG: Could not compile SQL with literal binds: {debug_err}")
                    print(f"DEBUG: Query statement: {query.statement}")

            # Execute and convert to DataFrame
            df = pd.read_sql(query.statement, self.db.bind)
            return df

        except Exception as e:
            print(f"Error executing trend query: {e}")
            return self._empty_trend_df()

    def get_top_applicants(self, state: 'AnalysisState', limit: int = 10, debug: bool = False) -> pd.DataFrame:
        """
        Get top N applicants by application count.

        Uses SQL escape hatch pattern (ADR-002) for complex aggregation.

        Args:
            state: AnalysisState with filter parameters
            limit: Maximum number of applicants to return (default 10, supports 10 or 25)
            debug: If True, prints the SQL query for transparency

        Returns:
            DataFrame with columns: applicant_name, application_count,
                                    invention_count, country
            Ordered by application_count DESC.

        Architecture:
            - Uses raw SQL (ADR-002) for complex GROUP BY
            - Filters by appln_auth (ADR-008)
            - Uses psn_name for standardized name grouping
            - Filters applt_seq_nr > 0 for applicants only
        """
        from sqlalchemy import text

        try:
            # Build base query parts
            # Tech field mode: join tls230_appln_techn_field
            # IPC mode: join tls209_appln_ipc
            if state.tech_mode == 'field' and state.tech_field is not None:
                tech_join = "JOIN tls230_appln_techn_field tf ON a.appln_id = tf.appln_id"
                tech_filter = "AND tf.techn_field_nr = :tech_field"
                params = {
                    'country': state.country,
                    'tech_field': state.tech_field,
                    'year_start': state.year_start,
                    'year_end': state.year_end,
                    'limit': limit
                }
            else:
                # IPC mode - build LIKE conditions for each code
                tech_join = "JOIN tls209_appln_ipc ipc ON a.appln_id = ipc.appln_id"
                # Build OR condition for multiple IPC codes
                ipc_conditions = " OR ".join([f"ipc.ipc_class_symbol LIKE :ipc_{i}" for i in range(len(state.ipc_codes))])
                tech_filter = f"AND ({ipc_conditions})" if ipc_conditions else ""
                params = {
                    'country': state.country,
                    'year_start': state.year_start,
                    'year_end': state.year_end,
                    'limit': limit
                }
                # Add IPC parameters
                for i, code in enumerate(state.ipc_codes):
                    params[f'ipc_{i}'] = f"{code}%"

            # Region filter (AC7)
            region_join = ""
            region_filter = ""
            if state.region is not None:
                # Need to filter by applicant's NUTS region
                region_filter = "AND p.nuts LIKE :region"
                params['region'] = f"{state.region}%"

            # SME filter (AC8) - subquery for applicants with <100 total applications
            sme_filter = ""
            if state.sme_filter:
                sme_filter = """
                AND pa.person_id IN (
                    SELECT person_id
                    FROM tls207_pers_appln
                    GROUP BY person_id
                    HAVING COUNT(appln_id) < 100
                )"""

            # Build the complete SQL query
            sql = f"""
                SELECT
                    p.psn_name as applicant_name,
                    p.person_ctry_code as country,
                    COUNT(DISTINCT a.appln_id) as application_count,
                    COUNT(DISTINCT a.docdb_family_id) as invention_count
                FROM tls201_appln a
                JOIN tls207_pers_appln pa ON a.appln_id = pa.appln_id
                JOIN tls206_person p ON pa.person_id = p.person_id
                {tech_join}
                WHERE a.appln_auth = :country
                  AND a.appln_filing_year BETWEEN :year_start AND :year_end
                  AND pa.applt_seq_nr > 0
                  AND p.psn_name IS NOT NULL
                  AND p.psn_name != ''
                  {tech_filter}
                  {region_filter}
                  {sme_filter}
                GROUP BY p.psn_name, p.person_ctry_code
                ORDER BY application_count DESC
                LIMIT :limit
            """

            # Debug mode - print SQL for transparency
            if debug:
                print("=" * 60)
                print("DEBUG: Top Applicants SQL Query")
                print("=" * 60)
                print(sql)
                print("Parameters:", params)
                print("=" * 60)

            # Execute query and convert to DataFrame
            result = self.db.execute(text(sql), params)
            df = pd.DataFrame(result.fetchall(), columns=['applicant_name', 'country', 'application_count', 'invention_count'])

            # Reorder columns to match schema spec (AC2)
            df = df[['applicant_name', 'application_count', 'invention_count', 'country']]

            return df

        except Exception as e:
            print(f"Error executing top applicants query: {e}")
            return self._empty_applicants_df()

    def get_tech_breakdown(self, state: 'AnalysisState') -> pd.DataFrame:
        """
        Get IPC class distribution for technology treemap.

        Full implementation in Story 3.3.

        Args:
            state: AnalysisState with filter parameters

        Returns:
            DataFrame with columns: ipc_class, ipc_label, count
            Limited to top 20 IPC classes by count.
        """
        # Stub - full implementation in Story 3.3
        return self._empty_tech_breakdown_df()

    def get_regional_distribution(self, state: 'AnalysisState') -> pd.DataFrame:
        """
        Get patent counts by NUTS region.

        Full implementation in Story 3.3.

        Args:
            state: AnalysisState with filter parameters

        Returns:
            DataFrame with columns: region, region_label, count
            Only for applicants with NUTS codes matching country.
        """
        # Stub - full implementation in Story 3.3
        return self._empty_regional_df()


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

        # Store reference for reset functionality (Story 2.6)
        self._jurisdiction_dropdown_widget = dropdown

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
        # Update review panel (Story 2.6)
        self._update_summary_panel()
        self._update_run_button_state()

    def _on_region_change(self, change):
        """
        Callback when region selection changes.

        Updates state.region with selected NUTS code.

        Args:
            change: ipywidgets change dict with 'new' value
        """
        self.state.region = change['new']
        # Update review panel (Story 2.6)
        self._update_summary_panel()
        self._update_run_button_state()

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

    def tech_field_dropdown(self) -> widgets.Dropdown:
        """
        Create technology field selection dropdown.

        Returns a dropdown populated with all 35 WIPO technology fields
        grouped by sector (Electrical, Instruments, Chemistry, Mechanical, Other).

        Returns:
            widgets.Dropdown: Configured dropdown with observe callback

        Example:
            >>> factory = WidgetFactory(reference_data, state)
            >>> dropdown = factory.tech_field_dropdown()
            >>> display(dropdown)
        """
        # Build grouped options with sector headers
        options = [('Select technology field...', None)]

        # Sector definitions: (sector_name, field_number_range)
        sectors = [
            ('Electrical engineering', range(1, 9)),
            ('Instruments', range(9, 14)),
            ('Chemistry', range(14, 24)),
            ('Mechanical engineering', range(24, 33)),
            ('Other fields', range(33, 36)),
        ]

        # Create lookup dict from tech_fields: {field_nr: display_name}
        field_lookup = {nr: name for name, nr in self.ref.tech_fields}

        for sector_name, field_range in sectors:
            # Add sector header as disabled separator
            options.append((f'── {sector_name} ──', -1))
            # Add fields in this sector
            for nr in field_range:
                if nr in field_lookup:
                    options.append((field_lookup[nr], nr))

        dropdown = widgets.Dropdown(
            options=options,
            value=None,
            description='Technology:',
            style={'description_width': '100px'},
            layout=widgets.Layout(width='400px')
        )

        # Register callback to update state on selection change
        dropdown.observe(self._on_tech_field_change, names='value')

        return dropdown

    def _on_tech_field_change(self, change):
        """
        Callback when technology field selection changes.

        Updates state.tech_field and sets state.tech_mode to "field".
        Ignores sector header selections (value == -1).

        Args:
            change: ipywidgets change dict with 'new' value
        """
        new_value = change['new']
        # Ignore sector headers (value == -1) and placeholder (value == None)
        if new_value is not None and new_value != -1:
            self.state.tech_field = new_value
            self.state.tech_mode = "field"
            # Update review panel (Story 2.6)
            self._update_summary_panel()
            self._update_run_button_state()

    # ========== Story 2.4: Custom IPC/CPC Entry (Dual Mode) ==========

    def tech_mode_toggle(self) -> widgets.RadioButtons:
        """
        Create mode toggle between Tech Field and Custom IPC/CPC modes.

        Returns a RadioButtons widget that allows users to switch between
        selecting from predefined WIPO technology fields or entering
        custom IPC/CPC codes.

        Returns:
            widgets.RadioButtons: Configured toggle with observe callback

        Example:
            >>> factory = WidgetFactory(reference_data, state)
            >>> toggle = factory.tech_mode_toggle()
            >>> display(toggle)
        """
        toggle = widgets.RadioButtons(
            options=['Tech Field', 'Custom IPC/CPC'],
            value='Tech Field',
            description='Mode:',
            style={'description_width': '100px'},
            layout=widgets.Layout(width='300px')
        )
        toggle.observe(self._on_tech_mode_change, names='value')
        return toggle

    def ipc_input(self) -> widgets.Text:
        """
        Create text input for custom IPC/CPC codes.

        Returns a text input widget for entering comma-separated IPC codes.
        Valid format: A-H section + 2 digit class + optional subclass letter
        (e.g., A61B, H01L, G06F).

        Returns:
            widgets.Text: Configured text input with observe callback

        Example:
            >>> factory = WidgetFactory(reference_data, state)
            >>> ipc = factory.ipc_input()
            >>> display(ipc)
        """
        text = widgets.Text(
            placeholder='A61B, H01L, ...',
            description='IPC Codes:',
            style={'description_width': '100px'},
            layout=widgets.Layout(width='400px')
        )
        text.observe(self._on_ipc_input_change, names='value')
        return text

    def ipc_helper_text(self) -> widgets.HTML:
        """
        Create helper text widget for IPC input.

        Returns:
            widgets.HTML: Helper text with IPC format guidance
        """
        return widgets.HTML(
            value='<i style="color: #666;">Enter up to 5 IPC main groups (e.g., A61B, H01L)</i>'
        )

    def ipc_validation_feedback(self) -> widgets.HTML:
        """
        Create validation feedback widget for IPC input.

        Initially empty, updated by _on_ipc_input_change callback.

        Returns:
            widgets.HTML: Validation feedback display
        """
        return widgets.HTML(value='')

    def _validate_ipc_codes(self, input_text: str) -> tuple:
        """
        Validate IPC codes from user input.

        Parses comma-separated IPC codes and validates each against
        the pattern: Section (A-H) + Class (2 digits) + optional Subclass (letter).

        Args:
            input_text: Comma-separated IPC codes string

        Returns:
            tuple: (valid_codes: List[str], is_valid: bool, message: str)
                - valid_codes: List of validated IPC codes (max 5)
                - is_valid: True if at least one valid code found
                - message: Validation feedback message
        """
        import re

        if not input_text or not input_text.strip():
            return ([], False, '')

        # IPC pattern: Section (A-H) + Class (2 digits) + optional Subclass (A-Z)
        pattern = re.compile(r'^[A-H]\d{2}[A-Z]?$')

        # Parse and normalize codes
        codes = [c.strip().upper() for c in input_text.split(',') if c.strip()]

        # Validate each code
        valid_codes = [c for c in codes if pattern.match(c)]
        invalid_codes = [c for c in codes if not pattern.match(c)]

        # Enforce max 5 codes
        truncated = len(valid_codes) > 5
        valid_codes = valid_codes[:5]

        # Build message
        if not codes:
            return ([], False, '')
        elif invalid_codes and not valid_codes:
            return ([], False, '<span style="color: red;">✗ Invalid format</span>')
        elif invalid_codes:
            return (valid_codes, True,
                    f'<span style="color: orange;">⚠ {len(valid_codes)} valid, {len(invalid_codes)} invalid</span>')
        elif truncated:
            return (valid_codes, True,
                    '<span style="color: orange;">⚠ Maximum 5 codes (showing first 5)</span>')
        else:
            return (valid_codes, True,
                    f'<span style="color: green;">✓ Valid ({len(valid_codes)} code{"s" if len(valid_codes) > 1 else ""})</span>')

    def _on_ipc_input_change(self, change):
        """
        Callback when IPC input text changes.

        Validates input and updates state.ipc_codes with valid codes.
        Updates validation feedback widget if registered.

        Args:
            change: ipywidgets change dict with 'new' value
        """
        input_text = change['new']
        valid_codes, is_valid, message = self._validate_ipc_codes(input_text)

        if is_valid:
            self.state.ipc_codes = valid_codes
            self.state.tech_mode = "ipc"
        else:
            self.state.ipc_codes = []

        # Update feedback widget if registered
        if hasattr(self, '_ipc_feedback_widget') and self._ipc_feedback_widget:
            self._ipc_feedback_widget.value = message

        # Update review panel (Story 2.6)
        self._update_summary_panel()
        self._update_run_button_state()

    def _on_tech_mode_change(self, change):
        """
        Callback when tech mode toggle changes.

        Toggles visibility between tech field dropdown and IPC input.
        Clears the inactive mode's state to prevent conflicts.

        Args:
            change: ipywidgets change dict with 'new' value
        """
        new_mode = change['new']

        if new_mode == 'Custom IPC/CPC':
            # Show IPC input, hide dropdown
            if hasattr(self, '_tech_dropdown_widget') and self._tech_dropdown_widget:
                self._tech_dropdown_widget.layout.display = 'none'
            if hasattr(self, '_ipc_input_widget') and self._ipc_input_widget:
                self._ipc_input_widget.layout.display = ''
            if hasattr(self, '_ipc_helper_widget') and self._ipc_helper_widget:
                self._ipc_helper_widget.layout.display = ''
            if hasattr(self, '_ipc_feedback_widget') and self._ipc_feedback_widget:
                self._ipc_feedback_widget.layout.display = ''

            self.state.tech_mode = 'ipc'
            self.state.tech_field = None  # Clear field selection
        else:
            # Show dropdown, hide IPC input
            if hasattr(self, '_tech_dropdown_widget') and self._tech_dropdown_widget:
                self._tech_dropdown_widget.layout.display = ''
            if hasattr(self, '_ipc_input_widget') and self._ipc_input_widget:
                self._ipc_input_widget.layout.display = 'none'
            if hasattr(self, '_ipc_helper_widget') and self._ipc_helper_widget:
                self._ipc_helper_widget.layout.display = 'none'
            if hasattr(self, '_ipc_feedback_widget') and self._ipc_feedback_widget:
                self._ipc_feedback_widget.layout.display = 'none'

            self.state.tech_mode = 'field'
            self.state.ipc_codes = []  # Clear IPC codes

        # Update review panel (Story 2.6)
        self._update_summary_panel()
        self._update_run_button_state()

    def create_technology_section(self) -> widgets.VBox:
        """
        Create complete technology selection section with mode toggle.

        Creates and registers all widgets needed for dual-mode technology
        selection (Tech Field dropdown or Custom IPC/CPC input).

        Returns:
            widgets.VBox: Complete technology section layout

        Example:
            >>> factory = WidgetFactory(reference_data, state)
            >>> tech_section = factory.create_technology_section()
            >>> display(tech_section)
        """
        # Create widgets and store references for callbacks
        self._tech_mode_toggle_widget = self.tech_mode_toggle()

        self._tech_dropdown_widget = self.tech_field_dropdown()
        self._ipc_input_widget = self.ipc_input()
        self._ipc_helper_widget = self.ipc_helper_text()
        self._ipc_feedback_widget = self.ipc_validation_feedback()

        # Initially hide IPC widgets (Tech Field is default)
        self._ipc_input_widget.layout.display = 'none'
        self._ipc_helper_widget.layout.display = 'none'
        self._ipc_feedback_widget.layout.display = 'none'

        # Build layout
        return widgets.VBox([
            widgets.HTML('<b>Technology</b>'),
            self._tech_mode_toggle_widget,
            self._tech_dropdown_widget,
            self._ipc_input_widget,
            self._ipc_helper_widget,
            self._ipc_feedback_widget
        ])

    # ========== Story 2.5: Date Range Selection ==========

    def year_range_slider(self) -> widgets.IntRangeSlider:
        """
        Create year range slider for date filtering.

        Returns an IntRangeSlider widget with range 2000-2024 and
        default value [2019, 2023]. Updates state.year_start and
        state.year_end on change.

        Returns:
            widgets.IntRangeSlider: Configured slider with observe callback

        Example:
            >>> factory = WidgetFactory(reference_data, state)
            >>> slider = factory.year_range_slider()
            >>> display(slider)
        """
        slider = widgets.IntRangeSlider(
            value=[self.state.year_start, self.state.year_end],
            min=2000,
            max=2024,
            step=1,
            description='Years:',
            style={'description_width': '100px'},
            layout=widgets.Layout(width='400px'),
            continuous_update=False  # Update only on release for better performance
        )
        slider.observe(self._on_year_range_change, names='value')
        return slider

    def performance_tip(self) -> widgets.HTML:
        """
        Create performance tip widget for date range.

        Displays dynamic performance estimate based on year span:
        - ≤5 years: "Fast query (~10 sec)"
        - 6-10 years: "Medium query (~30 sec)"
        - >10 years: "Large query (~2 min)"

        Returns:
            widgets.HTML: Performance tip display widget

        Example:
            >>> factory = WidgetFactory(reference_data, state)
            >>> tip = factory.performance_tip()
            >>> display(tip)
        """
        # Calculate initial span from state defaults
        year_span = self.state.year_end - self.state.year_start + 1
        initial_tip = self._get_performance_tip_text(year_span)
        return widgets.HTML(value=initial_tip)

    def _get_performance_tip_text(self, year_span: int) -> str:
        """
        Get performance tip text based on year span.

        Args:
            year_span: Number of years in the selected range

        Returns:
            str: Formatted HTML tip text with emoji
        """
        if year_span <= 5:
            return '<span style="color: #28a745;">⚡ Fast query (~10 sec)</span>'
        elif year_span <= 10:
            return '<span style="color: #ffc107;">⏱️ Medium query (~30 sec)</span>'
        else:
            return '<span style="color: #dc3545;">🐢 Large query (~2 min)</span>'

    def _update_performance_tip(self, year_span: int):
        """
        Update performance tip widget with new span value.

        Called by _on_year_range_change when slider value changes.

        Args:
            year_span: Number of years in the selected range
        """
        if hasattr(self, '_performance_tip_widget') and self._performance_tip_widget:
            self._performance_tip_widget.value = self._get_performance_tip_text(year_span)

    def _on_year_range_change(self, change):
        """
        Callback when year range slider changes.

        Updates state.year_start and state.year_end, then refreshes
        the performance tip display.

        Args:
            change: ipywidgets change dict with 'new' value tuple
        """
        new_range = change['new']
        self.state.year_start = new_range[0]
        self.state.year_end = new_range[1]

        # Calculate span and update performance tip
        year_span = new_range[1] - new_range[0] + 1
        self._update_performance_tip(year_span)

        # Update review panel (Story 2.6)
        self._update_summary_panel()
        self._update_run_button_state()

    def create_date_range_section(self) -> widgets.VBox:
        """
        Create complete date range selection section.

        Creates and registers all widgets needed for date range
        selection including IntRangeSlider and performance tip.

        Returns:
            widgets.VBox: Complete date range section layout

        Example:
            >>> factory = WidgetFactory(reference_data, state)
            >>> date_section = factory.create_date_range_section()
            >>> display(date_section)
        """
        # Create widgets and store references for callbacks
        self._year_range_slider_widget = self.year_range_slider()
        self._performance_tip_widget = self.performance_tip()

        # Build layout
        return widgets.VBox([
            widgets.HTML('<b>Date Range</b>'),
            self._year_range_slider_widget,
            self._performance_tip_widget
        ])

    # ========== Story 2.6: Options & Review Panel ==========

    def summary_panel(self) -> widgets.HTML:
        """
        Create summary panel displaying current selections.

        Returns an HTML widget showing state.summary() with emoji
        formatting. Updates dynamically via _update_summary_panel().

        Returns:
            widgets.HTML: Summary display widget

        Example:
            >>> factory = WidgetFactory(reference_data, state)
            >>> panel = factory.summary_panel()
            >>> display(panel)
        """
        summary_text = self.state.summary().replace('\n', '<br>')
        return widgets.HTML(
            value=f'<div style="background: #f8f9fa; padding: 10px; border-radius: 5px; border-left: 3px solid #007bff;">{summary_text}</div>'
        )

    def _update_summary_panel(self):
        """
        Update summary panel with current state.

        Called by all selection callbacks to refresh the display
        whenever user makes a selection change.
        """
        if hasattr(self, '_summary_panel_widget') and self._summary_panel_widget:
            summary_text = self.state.summary().replace('\n', '<br>')
            self._summary_panel_widget.value = f'<div style="background: #f8f9fa; padding: 10px; border-radius: 5px; border-left: 3px solid #007bff;">{summary_text}</div>'

    def sme_checkbox(self) -> widgets.Checkbox:
        """
        Create SME filter checkbox.

        Returns a checkbox for filtering to SME applicants (those with
        fewer than 100 total applications). Updates state.sme_filter.

        Returns:
            widgets.Checkbox: SME filter checkbox widget

        Example:
            >>> factory = WidgetFactory(reference_data, state)
            >>> checkbox = factory.sme_checkbox()
            >>> display(checkbox)
        """
        checkbox = widgets.Checkbox(
            value=False,
            description='Focus on SMEs (<100 applications)',
            indent=False,
            layout=widgets.Layout(width='300px')
        )
        checkbox.observe(self._on_sme_change, names='value')
        return checkbox

    def _on_sme_change(self, change):
        """
        Callback when SME checkbox changes.

        Updates state.sme_filter and refreshes summary panel.

        Args:
            change: ipywidgets change dict with 'new' value
        """
        self.state.sme_filter = change['new']
        self._update_summary_panel()
        self._update_run_button_state()

    def reset_button(self) -> widgets.Button:
        """
        Create Reset button to clear all selections.

        Returns a button styled as secondary (default gray) that
        resets all selections to defaults when clicked.

        Returns:
            widgets.Button: Reset button widget

        Example:
            >>> factory = WidgetFactory(reference_data, state)
            >>> button = factory.reset_button()
            >>> display(button)
        """
        button = widgets.Button(
            description='Reset',
            button_style='',  # Default gray style
            icon='refresh',
            layout=widgets.Layout(width='100px')
        )
        button.on_click(self._on_reset_click)
        return button

    def _on_reset_click(self, button):
        """
        Callback when Reset button is clicked.

        Re-initializes AnalysisState and resets all widgets to defaults.

        Args:
            button: The clicked button widget (unused)
        """
        # Re-initialize state to defaults
        self.state.country = None
        self.state.region = None
        self.state.tech_mode = "field"
        self.state.tech_field = None
        self.state.ipc_codes = []
        self.state.year_start = 2019
        self.state.year_end = 2023
        self.state.sme_filter = False

        # Reset jurisdiction dropdown
        if hasattr(self, '_jurisdiction_dropdown_widget') and self._jurisdiction_dropdown_widget:
            self._jurisdiction_dropdown_widget.value = None

        # Reset region dropdown
        if self._region_dropdown is not None:
            self._region_dropdown.options = [('All regions', None)]
            self._region_dropdown.value = None
            self._region_dropdown.disabled = True
            if self._region_helper:
                self._region_helper.value = ''

        # Reset tech dropdown
        if hasattr(self, '_tech_dropdown_widget') and self._tech_dropdown_widget:
            self._tech_dropdown_widget.value = None
            self._tech_dropdown_widget.layout.display = ''

        # Reset IPC input
        if hasattr(self, '_ipc_input_widget') and self._ipc_input_widget:
            self._ipc_input_widget.value = ''
            self._ipc_input_widget.layout.display = 'none'
        if hasattr(self, '_ipc_helper_widget') and self._ipc_helper_widget:
            self._ipc_helper_widget.layout.display = 'none'
        if hasattr(self, '_ipc_feedback_widget') and self._ipc_feedback_widget:
            self._ipc_feedback_widget.value = ''
            self._ipc_feedback_widget.layout.display = 'none'

        # Reset tech mode toggle
        if hasattr(self, '_tech_mode_toggle_widget') and self._tech_mode_toggle_widget:
            self._tech_mode_toggle_widget.value = 'Tech Field'

        # Reset year range slider
        if hasattr(self, '_year_range_slider_widget') and self._year_range_slider_widget:
            self._year_range_slider_widget.value = [2019, 2023]

        # Reset SME checkbox
        if hasattr(self, '_sme_checkbox_widget') and self._sme_checkbox_widget:
            self._sme_checkbox_widget.value = False

        # Update performance tip
        self._update_performance_tip(5)  # 5 year span for default [2019, 2023]

        # Update review panel
        self._update_summary_panel()
        self._update_run_button_state()

    def run_button(self) -> widgets.Button:
        """
        Create Run Analysis button.

        Returns a prominently styled green button for triggering query
        execution. Disabled until state.is_valid() returns True.

        Returns:
            widgets.Button: Run Analysis button widget

        Example:
            >>> factory = WidgetFactory(reference_data, state)
            >>> button = factory.run_button()
            >>> display(button)
        """
        button = widgets.Button(
            description='Run Analysis',
            button_style='success',  # Green style
            icon='play',
            layout=widgets.Layout(width='150px')
        )
        button.on_click(self._on_run_click)
        return button

    def _on_run_click(self, button):
        """
        Callback when Run Analysis button is clicked.

        Executes PATSTAT queries sequentially and stores results in analysis_results.
        Shows loading state and progress messages during execution.
        Handles individual query failures gracefully (partial results).
        Displays total execution time on completion.

        Args:
            button: The clicked button widget

        Story 3.4: Query Execution & Progress
        - AC1: Loading indicator (button disabled, spinner)
        - AC2: Progress messages per query
        - AC3: Sequential query execution
        - AC4: Completion message with timing
        - AC5: Per-query error handling
        - AC6: Zero results handling
        - AC7: Results storage in analysis_results
        - AC8: Query timing
        """
        import time
        global analysis_results

        # Show loading state (AC1)
        button.description = 'Running...'
        button.disabled = True
        button.icon = 'spinner'

        # Track execution time (AC8)
        total_start = time.time()
        query_errors = []

        # Helper to update progress message
        def update_progress(message, style="info"):
            if hasattr(self, '_validation_message_widget') and self._validation_message_widget:
                colors = {"info": "#17a2b8", "success": "#28a745", "warning": "#ffc107", "error": "#dc3545"}
                color = colors.get(style, "#17a2b8")
                self._validation_message_widget.value = f'<span style="color: {color};">{message}</span>'

        # Update initial status message (AC2)
        update_progress("⏳ Querying PATSTAT...")

        # Initialize PatstatQueries with database connection
        queries = PatstatQueries(get_db())

        # Query 1: Trend data (AC3 - sequential execution)
        update_progress("⏳ Loading trend data...")
        try:
            trend_df = queries.get_trend_data(self.state)
            analysis_results['trend'] = trend_df
        except Exception as e:
            print(f"Could not load trend data: {e}")
            query_errors.append("trend data")
            analysis_results['trend'] = queries._empty_trend_df()

        # Query 2: Top applicants (AC3)
        update_progress("⏳ Loading top applicants...")
        try:
            analysis_results['applicants'] = queries.get_top_applicants(self.state, limit=25)
        except Exception as e:
            print(f"Could not load applicants: {e}")
            query_errors.append("applicants")
            analysis_results['applicants'] = queries._empty_applicants_df()

        # Query 3: Tech breakdown (AC3)
        update_progress("⏳ Loading technology breakdown...")
        try:
            analysis_results['tech_breakdown'] = queries.get_tech_breakdown(self.state)
        except Exception as e:
            print(f"Could not load tech breakdown: {e}")
            query_errors.append("tech breakdown")
            analysis_results['tech_breakdown'] = queries._empty_tech_breakdown_df()

        # Query 4: Regional distribution - only if region set (AC3)
        if self.state.region is not None:
            update_progress("⏳ Loading regional data...")
            try:
                analysis_results['regional'] = queries.get_regional_distribution(self.state)
            except Exception as e:
                print(f"Could not load regional data: {e}")
                query_errors.append("regional data")
                analysis_results['regional'] = queries._empty_regional_df()
        else:
            # No region selected - get empty regional data
            analysis_results['regional'] = queries.get_regional_distribution(self.state)

        # Calculate total execution time (AC8)
        total_time = time.time() - total_start

        # Determine completion message (AC4, AC5, AC6)
        trend_df = analysis_results.get('trend', pd.DataFrame())
        result_count = len(trend_df) if not trend_df.empty else 0

        if query_errors:
            # AC5: Partial results with error indication
            error_list = ", ".join(query_errors)
            if result_count > 0:
                total_apps = trend_df['application_count'].sum() if 'application_count' in trend_df.columns else 0
                update_progress(
                    f"⚠️ Analysis complete with errors ({total_time:.1f}s): {result_count} years, {total_apps:,} apps. Could not load: {error_list}",
                    "warning"
                )
            else:
                update_progress(f"⚠️ Partial results ({total_time:.1f}s). Could not load: {error_list}", "warning")
        elif result_count > 0:
            # AC4: Full success
            total_apps = trend_df['application_count'].sum() if 'application_count' in trend_df.columns else 0
            update_progress(f"✅ Analysis complete ({total_time:.1f}s): {result_count} years, {total_apps:,} applications", "success")
        else:
            # AC6: Zero results
            update_progress(
                f"⚠️ No patents found ({total_time:.1f}s). Try expanding date range or changing filters.",
                "warning"
            )

        # Reset button state (AC4)
        button.description = 'Run Analysis'
        button.disabled = False
        button.icon = 'play'

        # Display charts (Story 4.1: Trend Line Chart)
        if result_count > 0 or not query_errors:
            # Use output widget if registered, otherwise create inline
            output_widget = getattr(self, '_chart_output_widget', None)
            display_results(analysis_results, self.state, output_widget)

    def _update_run_button_state(self):
        """
        Update Run button enabled/disabled state based on validation.

        Checks state.is_valid() and updates button disabled property
        and validation message display.
        """
        if not hasattr(self, '_run_button_widget') or not self._run_button_widget:
            return

        is_valid, message = self.state.is_valid()

        if is_valid:
            self._run_button_widget.disabled = False
            if hasattr(self, '_validation_message_widget') and self._validation_message_widget:
                self._validation_message_widget.value = ''
        else:
            self._run_button_widget.disabled = True
            if hasattr(self, '_validation_message_widget') and self._validation_message_widget:
                self._validation_message_widget.value = f'<span style="color: #dc3545;">⚠️ {message}</span>'

    def validation_message(self) -> widgets.HTML:
        """
        Create validation message widget.

        Displays validation errors when state.is_valid() returns False.
        Hidden when state is valid.

        Returns:
            widgets.HTML: Validation message widget

        Example:
            >>> factory = WidgetFactory(reference_data, state)
            >>> msg = factory.validation_message()
            >>> display(msg)
        """
        # Initialize with current validation state
        is_valid, message = self.state.is_valid()
        if is_valid:
            initial_value = ''
        else:
            initial_value = f'<span style="color: #dc3545;">⚠️ {message}</span>'

        return widgets.HTML(value=initial_value)

    def create_review_section(self) -> widgets.VBox:
        """
        Create complete review and run section.

        Creates and registers all widgets needed for the Options & Review
        panel: summary panel, SME checkbox, Reset button, Run button,
        and validation message.

        Returns:
            widgets.VBox: Complete review section layout

        Example:
            >>> factory = WidgetFactory(reference_data, state)
            >>> review_section = factory.create_review_section()
            >>> display(review_section)
        """
        # Create widgets and store references for callbacks
        self._summary_panel_widget = self.summary_panel()
        self._sme_checkbox_widget = self.sme_checkbox()
        self._reset_button_widget = self.reset_button()
        self._run_button_widget = self.run_button()
        self._validation_message_widget = self.validation_message()

        # Update initial run button state
        self._update_run_button_state()

        # Button row: Reset | Run Analysis
        button_row = widgets.HBox([
            self._reset_button_widget,
            widgets.HTML(value='&nbsp;&nbsp;'),  # Spacer
            self._run_button_widget
        ])

        # Build layout
        return widgets.VBox([
            widgets.HTML('<b>Review & Run</b>'),
            self._summary_panel_widget,
            self._sme_checkbox_widget,
            button_row,
            self._validation_message_widget
        ])

    def chart_output(self) -> widgets.Output:
        """
        Create Output widget for chart display.

        Returns an Output widget that will be used by display_results()
        to render charts after query execution.

        Returns:
            widgets.Output: Output widget for charts

        Example:
            >>> factory = WidgetFactory(reference_data, state)
            >>> chart_area = factory.chart_output()
            >>> display(chart_area)
        """
        output = widgets.Output()
        self._chart_output_widget = output
        return output


# =============================================================================
# EPO Brand Constants (Story 4.1)
# =============================================================================

EPO_COLORS = {
    'primary': '#C8102E',      # EPO Red
    'secondary': '#6D6E71',    # EPO Gray
    'light': '#F5F5F5',        # Light background
    'dark': '#1D1D1B',         # Dark text
}

EPO_PALETTE = ['#C8102E', '#6D6E71', '#A6093D', '#8B8D8E', '#D4495B', '#B0B1B3']

EPO_LAYOUT = {
    'font_family': 'Arial',
    'title_font_size': 16,
    'paper_bgcolor': 'white',
    'plot_bgcolor': 'white',
}


def truncate_name(name: str, max_length: int = 30) -> str:
    """
    Truncate long names for chart display.

    Args:
        name: Original name string
        max_length: Maximum length before truncation (default 30)

    Returns:
        str: Truncated name with "..." if over max_length, otherwise original

    Example:
        >>> truncate_name("SIEMENS HEALTHCARE DIAGNOSTICS GMBH")
        "SIEMENS HEALTHCARE DIAGNOS..."
    """
    if name and len(name) > max_length:
        return name[:max_length - 3] + "..."
    return name or ""


class ChartBuilder:
    """
    Builder for Plotly visualizations with EPO styling.

    Creates interactive charts for patent analysis results:
    - Trend line charts (trend_line)
    - Top applicants bar charts (top_applicants_bar) - Story 4.2
    - Regional distribution charts (regional_bar) - Story 4.3
    - Technology breakdown treemaps (tech_treemap) - Story 4.4

    All methods are static and return go.Figure objects configured with
    EPO brand styling (colors, fonts) and interactivity (hover, zoom/pan).
    """

    @staticmethod
    def _get_tech_field_name(tech_field: Optional[int]) -> str:
        """
        Get human-readable technology field name from field number.

        Args:
            tech_field: WIPO technology field number (1-35)

        Returns:
            str: Field name (e.g., "Medical technology") or "Custom IPC" if None
        """
        if tech_field is None:
            return "Custom IPC"

        # Look up from reference_data if available
        if reference_data is not None:
            for display_name, field_nr in reference_data.tech_fields:
                if field_nr == tech_field:
                    # Extract just the name part (remove "13 - " prefix)
                    parts = display_name.split(' - ', 1)
                    return parts[1] if len(parts) > 1 else display_name
        return f"Field {tech_field}"

    @staticmethod
    def trend_line(df: pd.DataFrame, state: 'AnalysisState') -> go.Figure:
        """
        Create line chart for patent applications over time.

        Implements AC1-AC8 of Story 4.1:
        - AC1: Line chart with X=years, Y=application count
        - AC2: Dual lines (applications solid, inventions dashed)
        - AC3: EPO brand styling
        - AC4: Dynamic title from state
        - AC5: Interactive hover with year and counts
        - AC6: Zoom/pan enabled
        - AC7: Empty data handling (returns None, caller shows message)
        - AC8: Single year shows point with marker

        Args:
            df: DataFrame with columns [year, application_count, invention_count]
            state: AnalysisState for title generation

        Returns:
            go.Figure: Configured Plotly figure, or None if df is empty
        """
        # AC7: Handle empty DataFrame
        if df is None or df.empty:
            return None

        # Get tech field name for title (AC4)
        tech_name = ChartBuilder._get_tech_field_name(state.tech_field)

        # Build dynamic title (AC4)
        title = f"Patent Applications: {state.country} - {tech_name} ({state.year_start}-{state.year_end})"

        # Create figure with dual traces (AC1, AC2)
        fig = go.Figure()

        # AC8: Determine if single point (show marker)
        show_markers = len(df) == 1

        # Applications line - solid, EPO Red (AC2, AC3)
        fig.add_trace(go.Scatter(
            x=df['year'],
            y=df['application_count'],
            name='Applications',
            mode='lines+markers' if show_markers else 'lines',
            line=dict(color=EPO_COLORS['primary'], width=2),
            marker=dict(size=8) if show_markers else None,
            hovertemplate='<b>%{x}</b><br>Applications: %{y:,}<extra></extra>'
        ))

        # Inventions line - dashed, EPO Gray (AC2)
        fig.add_trace(go.Scatter(
            x=df['year'],
            y=df['invention_count'],
            name='Inventions (families)',
            mode='lines+markers' if show_markers else 'lines',
            line=dict(color=EPO_COLORS['secondary'], width=2, dash='dash'),
            marker=dict(size=8) if show_markers else None,
            hovertemplate='<b>%{x}</b><br>Inventions: %{y:,}<extra></extra>'
        ))

        # Apply EPO layout styling (AC3)
        fig.update_layout(
            title=dict(
                text=title,
                font=dict(family=EPO_LAYOUT['font_family'], size=EPO_LAYOUT['title_font_size'])
            ),
            font=dict(family=EPO_LAYOUT['font_family']),
            paper_bgcolor=EPO_LAYOUT['paper_bgcolor'],
            plot_bgcolor=EPO_LAYOUT['plot_bgcolor'],
            xaxis=dict(
                title='Year',
                tickmode='linear',
                dtick=1,
                gridcolor='#E5E5E5',
                linecolor='#E5E5E5'
            ),
            yaxis=dict(
                title='Count',
                gridcolor='#E5E5E5',
                linecolor='#E5E5E5'
            ),
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='right',
                x=1
            ),
            hovermode='x unified',
            margin=dict(l=60, r=30, t=80, b=60)
        )

        # AC6: Enable zoom/pan (default behavior, ensure modebar visible)
        fig.update_layout(
            modebar=dict(
                orientation='v',
                bgcolor='rgba(255,255,255,0.7)'
            )
        )

        return fig

    @staticmethod
    def top_applicants_bar(df: pd.DataFrame, state: 'AnalysisState', limit: int = 10) -> go.Figure:
        """
        Create horizontal bar chart for top applicants.

        Implements AC1-AC8 of Story 4.2:
        - AC1: Horizontal bar chart with Y=applicant names, X=application count
        - AC2: Bars ordered with largest at top
        - AC3: Names truncated to 30 chars, full name in hover
        - AC4: Dynamic title from state and limit
        - AC5: Hover shows full name, counts, country
        - AC7: EPO Red bar color, Arial font
        - AC8: Empty data handling (returns None)

        Args:
            df: DataFrame with columns [applicant_name, application_count, invention_count, country]
            state: AnalysisState for title generation
            limit: Number of applicants to show (default 10, supports 10 or 25)

        Returns:
            go.Figure: Configured Plotly figure, or None if df is empty
        """
        # AC8: Handle empty DataFrame
        if df is None or df.empty:
            return None

        # Get top N applicants (DataFrame should already be sorted DESC)
        df_top = df.head(limit).copy()

        # AC3: Truncate names for display, keep full names for hover
        df_top['display_name'] = df_top['applicant_name'].apply(truncate_name)

        # Get tech field name for title (AC4)
        tech_name = ChartBuilder._get_tech_field_name(state.tech_field)

        # Build dynamic title (AC4)
        title = f"Top {limit} Applicants: {state.country} - {tech_name}"

        # Create horizontal bar chart (AC1)
        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=df_top['application_count'],
            y=df_top['display_name'],
            orientation='h',
            marker_color=EPO_COLORS['primary'],
            # AC5: Hover data with full details
            customdata=df_top[['applicant_name', 'invention_count', 'country']].values,
            hovertemplate=(
                '<b>%{customdata[0]}</b><br>'
                'Applications: %{x:,}<br>'
                'Inventions: %{customdata[1]:,}<br>'
                'Country: %{customdata[2]}'
                '<extra></extra>'
            )
        ))

        # AC2: Order with largest at top (reverse order since bar chart draws bottom-up)
        fig.update_layout(
            yaxis=dict(
                categoryorder='total ascending',  # Largest at top
                title='',
                tickfont=dict(size=11)
            )
        )

        # Apply EPO layout styling (AC7)
        fig.update_layout(
            title=dict(
                text=title,
                font=dict(family=EPO_LAYOUT['font_family'], size=EPO_LAYOUT['title_font_size'])
            ),
            font=dict(family=EPO_LAYOUT['font_family']),
            paper_bgcolor=EPO_LAYOUT['paper_bgcolor'],
            plot_bgcolor=EPO_LAYOUT['plot_bgcolor'],
            xaxis=dict(
                title='Applications',
                gridcolor='#E5E5E5',
                linecolor='#E5E5E5'
            ),
            margin=dict(l=200, r=30, t=80, b=60),  # Extra left margin for names
            height=max(400, limit * 25 + 150)  # Dynamic height based on limit
        )

        return fig

    @staticmethod
    def regional_bar(df: pd.DataFrame, state: 'AnalysisState') -> go.Figure:
        """
        Create vertical bar chart for regional distribution.

        Implements AC1-AC8 of Story 4.3:
        - AC1: Vertical bar chart with X=region labels, Y=application count
        - AC2: Bars ordered by count descending (highest on left)
        - AC3: Limited to top 10 regions
        - AC4: Dynamic title from state
        - AC5: Hover shows region label, NUTS code, count
        - AC6: EPO Red bar color, Arial font
        - AC7/AC8: Empty data handling (returns None)

        Args:
            df: DataFrame with columns [region, region_label, count]
            state: AnalysisState for title generation

        Returns:
            go.Figure: Configured Plotly figure, or None if df is empty or has <=1 regions
        """
        # AC7/AC8: Handle empty or single-region DataFrame
        if df is None or df.empty or len(df) <= 1:
            return None

        # AC3: Limit to top 10 regions, sorted by count descending (AC2)
        df_top = df.nlargest(10, 'count').copy()

        # Get tech field name for title (AC4)
        tech_name = ChartBuilder._get_tech_field_name(state.tech_field)

        # Build dynamic title (AC4)
        title = f"Regional Distribution: {state.country} - {tech_name}"

        # Create vertical bar chart (AC1)
        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=df_top['region_label'],
            y=df_top['count'],
            marker_color=EPO_COLORS['primary'],
            # AC5: Hover data with NUTS code and count
            customdata=df_top[['region']].values,
            hovertemplate=(
                '<b>%{x}</b><br>'
                'NUTS Code: %{customdata[0]}<br>'
                'Applications: %{y:,}'
                '<extra></extra>'
            )
        ))

        # Apply EPO layout styling (AC6)
        fig.update_layout(
            title=dict(
                text=title,
                font=dict(family=EPO_LAYOUT['font_family'], size=EPO_LAYOUT['title_font_size'])
            ),
            font=dict(family=EPO_LAYOUT['font_family']),
            paper_bgcolor=EPO_LAYOUT['paper_bgcolor'],
            plot_bgcolor=EPO_LAYOUT['plot_bgcolor'],
            xaxis=dict(
                title='Region',
                tickangle=-45,
                gridcolor='#E5E5E5',
                linecolor='#E5E5E5'
            ),
            yaxis=dict(
                title='Applications',
                gridcolor='#E5E5E5',
                linecolor='#E5E5E5'
            ),
            margin=dict(l=60, r=30, t=80, b=120)  # Extra bottom margin for rotated labels
        )

        return fig

    @staticmethod
    def tech_treemap(df: pd.DataFrame, state: 'AnalysisState') -> go.Figure:
        """
        Create treemap for technology (IPC class) breakdown.

        Implements AC1-AC8 of Story 4.4:
        - AC1: Treemap with boxes sized by count
        - AC2: Proportional box sizing
        - AC3: Labels show IPC class and count
        - AC4: Dynamic title from state
        - AC5: Hover shows IPC class, label, count, percentage
        - AC6: EPO color palette for visual distinction
        - AC7: Limited to top 20 IPC classes
        - AC8: Empty data handling (returns None)

        Args:
            df: DataFrame with columns [ipc_class, ipc_label, count]
            state: AnalysisState for title generation

        Returns:
            go.Figure: Configured Plotly figure, or None if df is empty
        """
        # AC8: Handle empty DataFrame
        if df is None or df.empty:
            return None

        # AC7: Limit to top 20 IPC classes
        df_top = df.nlargest(20, 'count').copy()

        # Calculate percentage for hover (AC5)
        total = df_top['count'].sum()
        df_top['percentage'] = (df_top['count'] / total * 100).round(1)

        # Build dynamic title (AC4)
        title = f"Technology Breakdown: {state.country} ({state.year_start}-{state.year_end})"

        # Create treemap (AC1, AC2)
        fig = px.treemap(
            df_top,
            path=['ipc_class'],
            values='count',
            color_discrete_sequence=EPO_PALETTE,
            custom_data=['ipc_label', 'percentage']
        )

        # AC3: Configure text labels and AC5: hover template
        fig.update_traces(
            textinfo='label+value',
            texttemplate='<b>%{label}</b><br>%{value:,}',
            hovertemplate=(
                '<b>%{label}</b><br>'
                '%{customdata[0]}<br>'
                'Count: %{value:,}<br>'
                'Share: %{customdata[1]:.1f}%'
                '<extra></extra>'
            )
        )

        # Apply EPO layout styling (AC6)
        fig.update_layout(
            title=dict(
                text=title,
                font=dict(family=EPO_LAYOUT['font_family'], size=EPO_LAYOUT['title_font_size'])
            ),
            font=dict(family=EPO_LAYOUT['font_family']),
            paper_bgcolor=EPO_LAYOUT['paper_bgcolor'],
            margin=dict(l=20, r=20, t=60, b=20)
        )

        return fig


def display_results(results: dict, state: 'AnalysisState', output_widget: Optional[widgets.Output] = None) -> None:
    """
    Render charts in output area based on analysis results.

    Implements empty data handling for all chart types.
    Called by _on_run_click() after queries complete.

    Args:
        results: Dict with keys 'trend', 'applicants', 'tech_breakdown', 'regional'
                 Each value is a DataFrame (may be empty)
        state: AnalysisState for chart configuration
        output_widget: Optional Output widget to render into (creates new if None)

    Story 4.1: Trend line chart
    Story 4.2: Top applicants bar chart with toggle
    Stories 4.3-4.4: Regional and technology charts
    """
    from IPython.display import display, clear_output

    # Use provided output widget or create new one
    if output_widget is None:
        output_widget = widgets.Output()
        display(output_widget)

    with output_widget:
        clear_output(wait=True)

        # Check for zero results first (Story 5.3)
        if _is_zero_results(results):
            zero_msg = handle_zero_results(state)
            display(zero_msg)
            return  # Don't render charts or export buttons

        # Track if any charts were rendered and collect figures for PNG export
        charts_rendered = 0
        figures = {}  # Collect figures for PNG export

        # Trend line chart (Story 4.1)
        trend_df = results.get('trend')
        if trend_df is not None and not trend_df.empty:
            fig = ChartBuilder.trend_line(trend_df, state)
            if fig is not None:
                fig.show()
                figures['trend'] = fig
                charts_rendered += 1
        else:
            print("📊 No trend data available for this selection")

        # Top Applicants bar chart (Story 4.2)
        applicants_df = results.get('applicants')
        if applicants_df is not None and not applicants_df.empty:
            # Create output widget for applicants chart (allows re-render on toggle)
            applicants_output = widgets.Output()

            # AC6: Create Top 10/25 toggle dropdown
            limit_dropdown = widgets.Dropdown(
                options=[('Top 10', 10), ('Top 25', 25)],
                value=10,
                description='Show:',
                style={'description_width': '50px'},
                layout=widgets.Layout(width='150px')
            )

            # Store current figure for PNG export (updated on toggle)
            current_applicants_fig = [None]  # Use list to allow mutation in closure

            def render_applicants_chart(limit):
                """Render applicants chart with given limit."""
                with applicants_output:
                    clear_output(wait=True)
                    fig = ChartBuilder.top_applicants_bar(applicants_df, state, limit=limit)
                    if fig is not None:
                        fig.show()
                        current_applicants_fig[0] = fig

            def on_limit_change(change):
                """Callback when limit toggle changes."""
                render_applicants_chart(change['new'])

            limit_dropdown.observe(on_limit_change, names='value')

            # Display toggle and chart
            print("")  # Spacer
            display(limit_dropdown)
            display(applicants_output)

            # Initial render
            render_applicants_chart(10)
            figures['applicants'] = current_applicants_fig[0]
            charts_rendered += 1
        else:
            print("📊 No applicant data available for this selection")

        # Regional Distribution chart (Story 4.3)
        regional_df = results.get('regional')
        if regional_df is not None and not regional_df.empty and len(regional_df) > 1:
            fig = ChartBuilder.regional_bar(regional_df, state)
            if fig is not None:
                print("")  # Spacer
                fig.show()
                figures['regional'] = fig
                charts_rendered += 1
        else:
            print("📊 Regional breakdown not available for this selection")

        # Technology Breakdown treemap (Story 4.4)
        tech_df = results.get('tech_breakdown')
        if tech_df is not None and not tech_df.empty:
            fig = ChartBuilder.tech_treemap(tech_df, state)
            if fig is not None:
                print("")  # Spacer
                fig.show()
                figures['tech_breakdown'] = fig
                charts_rendered += 1
        else:
            print("📊 No technology breakdown available for this selection")

        if charts_rendered == 0:
            print("\n⚠️ No charts could be rendered. Try adjusting your filters.")

        # Export buttons (Story 5.1, 5.2)
        # Only show if we have any data to export
        has_data = any([
            results.get('trend') is not None and not results.get('trend').empty,
            results.get('applicants') is not None and not results.get('applicants').empty
        ])
        if has_data:
            export_ui = create_export_buttons(results, state, figures)
            display(export_ui)

            # Data quality warning (Story 5.3) - collapsed by default
            warning = data_quality_warning()
            display(warning)


class Exporter:
    """
    Export utilities for CSV and PNG output.

    Handles:
    - CSV export with European formatting (semicolon delimiter, UTF-8 BOM)
    - PNG export for Plotly charts (Story 5.2)
    - Descriptive filename generation

    All methods are static. Files are written to current working directory.
    """

    @staticmethod
    def generate_filename(state: 'AnalysisState', extension: str, chart_name: str = None) -> str:
        """
        Generate descriptive filename based on analysis parameters.

        Args:
            state: AnalysisState with country, tech_field/ipc_codes, year range
            extension: File extension ('csv' or 'png')
            chart_name: Optional chart identifier for PNG exports

        Returns:
            Filename string (not full path)

        Example:
            >>> Exporter.generate_filename(state, 'csv')
            'tip4patlibs_DE_field13_2019-2023_20260112_1430.csv'
        """
        from datetime import datetime

        # Country code
        country = state.country or 'XX'

        # Tech component: field{nr} or ipc
        if state.tech_mode == 'field' and state.tech_field:
            tech = f"field{state.tech_field}"
        elif state.tech_mode == 'ipc':
            tech = "ipc"
        else:
            tech = "all"

        # Year range
        year_start = state.year_start or 2019
        year_end = state.year_end or 2023
        years = f"{year_start}-{year_end}"

        # Timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")

        # Build filename
        parts = ['tip4patlibs', country, tech, years, timestamp]
        if chart_name:
            parts.append(chart_name)

        return '_'.join(parts) + f'.{extension}'

    @staticmethod
    def to_csv(results: dict, state: 'AnalysisState') -> str:
        """
        Export analysis results to CSV with European formatting.

        Combines trend and applicants DataFrames into a single CSV file
        with section headers for clarity.

        Args:
            results: Dict with 'trend' and 'applicants' DataFrames
            state: AnalysisState for filename generation

        Returns:
            Full path to exported file

        Format:
            - Separator: semicolon (;)
            - Encoding: UTF-8 with BOM (utf-8-sig)
            - No index column

        Raises:
            Exception: If export fails (caught by caller for user message)
        """
        from pathlib import Path
        import io

        filename = Exporter.generate_filename(state, 'csv')
        filepath = Path.cwd() / filename

        # Build combined CSV content
        lines = []

        # Section 1: Trend data
        trend_df = results.get('trend')
        if trend_df is not None and not trend_df.empty:
            lines.append("# Trend Data (Applications over Time)")
            # Get CSV string from DataFrame
            csv_content = trend_df.to_csv(index=False, sep=';', encoding='utf-8')
            lines.append(csv_content.strip())
            lines.append("")  # Blank line separator

        # Section 2: Top Applicants
        applicants_df = results.get('applicants')
        if applicants_df is not None and not applicants_df.empty:
            lines.append("# Top Applicants")
            csv_content = applicants_df.to_csv(index=False, sep=';', encoding='utf-8')
            lines.append(csv_content.strip())

        # Write with UTF-8 BOM for Excel compatibility
        content = '\n'.join(lines)
        with open(filepath, 'w', encoding='utf-8-sig') as f:
            f.write(content)

        return str(filepath)

    @staticmethod
    def to_png(fig: 'go.Figure', state: 'AnalysisState', chart_name: str) -> str:
        """
        Export Plotly figure to PNG with high resolution.

        Args:
            fig: Plotly Figure object
            state: AnalysisState for filename generation
            chart_name: Chart identifier ('trend', 'applicants', etc.)

        Returns:
            Full path to exported file

        Raises:
            Exception: If kaleido not available or export fails
        """
        from pathlib import Path

        filename = Exporter.generate_filename(state, 'png', chart_name)
        filepath = Path.cwd() / filename

        # Export at 2x scale for high DPI
        fig.write_image(str(filepath), scale=2, format='png')

        return str(filepath)


def _is_zero_results(results: dict) -> bool:
    """
    Check if all primary DataFrames are empty (zero results).

    Args:
        results: Dict with 'trend' and 'applicants' DataFrames

    Returns:
        bool: True if both trend and applicants are empty
    """
    trend_empty = results.get('trend') is None or results.get('trend').empty
    applicants_empty = results.get('applicants') is None or results.get('applicants').empty
    return trend_empty and applicants_empty


def _generate_suggestions(state: 'AnalysisState') -> list:
    """
    Generate actionable suggestions based on current filter state.

    Args:
        state: AnalysisState with current filter settings

    Returns:
        List of suggestion strings
    """
    suggestions = []

    # Check date range (AC3)
    if state.year_start and state.year_end:
        year_span = state.year_end - state.year_start + 1
        if year_span <= 3:
            suggestions.append(f"Try expanding the date range (currently {year_span} years)")

    # Check SME filter (AC4)
    if state.sme_filter:
        suggestions.append("Try disabling the SME filter")

    # Check region (AC5)
    if state.region is not None:
        suggestions.append("Try selecting 'All regions'")

    # Check IPC mode (AC6)
    if state.tech_mode == 'ipc':
        suggestions.append("Try using a WIPO Technology Field instead of custom IPC codes")

    return suggestions


def handle_zero_results(state: 'AnalysisState') -> widgets.VBox:
    """
    Create a helpful message when query returns no results.

    Implements AC1-AC6 of Story 5.3:
    - Clear message about no results
    - Shows current filter summary
    - Provides actionable suggestions

    Args:
        state: AnalysisState with current filter settings

    Returns:
        widgets.VBox with message and suggestions
    """
    # Generate suggestions based on state
    suggestions = _generate_suggestions(state)

    # Build suggestion list HTML
    suggestions_html = ""
    if suggestions:
        suggestions_html = "<ul style='margin: 10px 0; padding-left: 20px;'>"
        for suggestion in suggestions:
            suggestions_html += f"<li>{suggestion}</li>"
        suggestions_html += "</ul>"

    # Build filter summary
    summary_parts = []
    if state.country:
        summary_parts.append(f"Country: {state.country}")
    if state.tech_mode == 'field' and state.tech_field:
        summary_parts.append(f"Technology Field: {state.tech_field}")
    elif state.tech_mode == 'ipc' and state.ipc_codes:
        summary_parts.append(f"IPC Codes: {', '.join(state.ipc_codes[:3])}...")
    if state.year_start and state.year_end:
        summary_parts.append(f"Years: {state.year_start}-{state.year_end}")
    if state.region:
        summary_parts.append(f"Region: {state.region}")
    if state.sme_filter:
        summary_parts.append("SME Filter: Enabled")

    filter_summary = " | ".join(summary_parts) if summary_parts else "No filters selected"

    # Build the message widget
    message_html = f'''
    <div style="background: #fff3cd; border: 1px solid #ffc107; border-radius: 5px; padding: 15px; margin: 10px 0;">
        <h4 style="margin: 0 0 10px 0; color: #856404;">
            📭 No patents found for this selection
        </h4>
        <p style="margin: 5px 0; color: #856404; font-size: 0.9em;">
            <b>Current filters:</b> {filter_summary}
        </p>
        {f'<p style="margin: 10px 0 5px 0; color: #856404;"><b>Suggestions to try:</b></p>{suggestions_html}' if suggestions else ''}
    </div>
    '''

    return widgets.VBox([widgets.HTML(value=message_html)])


def data_quality_warning() -> widgets.Accordion:
    """
    Create a collapsible data quality warning section.

    Implements AC7-AC10 of Story 5.3:
    - Explains PATSTAT data limitations
    - Collapsed by default
    - Non-intrusive styling

    Returns:
        widgets.Accordion with data quality notes (collapsed)
    """
    content_html = '''
    <div style="font-size: 0.9em; color: #666; padding: 10px;">
        <ul style="margin: 0; padding-left: 20px;">
            <li><b>Applicant names:</b> The same organization may appear multiple times
                under different name variations (e.g., "SIEMENS AG" vs "SIEMENS AKTIENGESELLSCHAFT")</li>
            <li><b>Regional data:</b> NUTS region data coverage varies by country.
                Some countries may have limited or no regional attribution.</li>
            <li><b>Classifications:</b> Older patents (pre-2000) may have incomplete
                IPC/CPC classification data.</li>
        </ul>
    </div>
    '''

    content = widgets.HTML(value=content_html)

    accordion = widgets.Accordion(children=[content])
    accordion.set_title(0, 'ℹ️ Data Quality Notes')
    accordion.selected_index = None  # Collapsed by default

    return accordion


def _check_kaleido_available() -> bool:
    """
    Check if kaleido package is available for PNG export.

    Returns:
        bool: True if kaleido is installed and importable
    """
    try:
        import kaleido
        return True
    except ImportError:
        return False


def export_all_charts(figures: dict, state: 'AnalysisState') -> list:
    """
    Export all available charts as PNG files.

    Args:
        figures: Dict of chart_name -> go.Figure
        state: AnalysisState for filename generation

    Returns:
        List of exported filepaths

    Raises:
        Exception: If kaleido not available or export fails
    """
    if not _check_kaleido_available():
        raise ImportError("PNG export requires the kaleido package")

    exported_files = []
    for chart_name, fig in figures.items():
        if fig is not None:
            filepath = Exporter.to_png(fig, state, chart_name)
            exported_files.append(filepath)

    return exported_files


def create_export_buttons(results: dict, state: 'AnalysisState', figures: dict = None) -> widgets.VBox:
    """
    Create export buttons for CSV and PNG downloads.

    Args:
        results: Dict of DataFrames from analysis
        state: AnalysisState for filename generation
        figures: Dict of chart_name -> go.Figure for PNG export (optional)

    Returns:
        VBox containing export buttons and status message area
    """
    from IPython.display import display, clear_output

    # Status message area
    status_output = widgets.Output()

    # CSV Export button
    csv_button = widgets.Button(
        description='Export CSV',
        icon='download',
        button_style='info',
        tooltip='Export data as CSV (semicolon delimiter for Excel)'
    )

    def on_csv_export(b):
        """Handle CSV export button click."""
        with status_output:
            clear_output(wait=True)
            try:
                filepath = Exporter.to_csv(results, state)
                print(f"✅ Exported to: {filepath}")
            except Exception as e:
                print(f"❌ Export failed: {str(e)}")

    csv_button.on_click(on_csv_export)

    # PNG Export button
    png_button = widgets.Button(
        description='Export Charts (PNG)',
        icon='image',
        button_style='info',
        tooltip='Export charts as high-resolution PNG images'
    )

    def on_png_export(b):
        """Handle PNG export button click."""
        with status_output:
            clear_output(wait=True)
            if figures is None or len(figures) == 0:
                print("⚠️ No charts available to export")
                return

            if not _check_kaleido_available():
                print("⚠️ PNG export requires the kaleido package")
                print("")
                print("Alternative: Use your browser's screenshot function")
                print("  • Mac: Cmd+Shift+4")
                print("  • Windows: Win+Shift+S")
                return

            try:
                exported = export_all_charts(figures, state)
                print(f"✅ Exported {len(exported)} charts:")
                for filepath in exported:
                    print(f"   • {filepath}")
            except Exception as e:
                print(f"❌ PNG export failed: {str(e)}")

    png_button.on_click(on_png_export)

    # Layout: buttons in a row, status below
    button_row = widgets.HBox([csv_button, png_button], layout=widgets.Layout(gap='10px'))

    return widgets.VBox([
        widgets.HTML('<hr style="margin: 20px 0 10px 0;">'),
        widgets.HTML('<b>Export Options</b>'),
        button_row,
        status_output
    ])
