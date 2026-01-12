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

        Executes PATSTAT queries and stores results in analysis_results.
        Shows loading state during execution.

        Args:
            button: The clicked button widget
        """
        global analysis_results

        # Show loading state
        button.description = 'Running...'
        button.disabled = True
        button.icon = 'spinner'

        # Update status message
        if hasattr(self, '_validation_message_widget') and self._validation_message_widget:
            self._validation_message_widget.value = '<span style="color: #17a2b8;">⏳ Querying PATSTAT...</span>'

        try:
            # Initialize PatstatQueries with database connection
            queries = PatstatQueries(get_db())

            # Execute trend query (Story 3.1)
            if hasattr(self, '_validation_message_widget') and self._validation_message_widget:
                self._validation_message_widget.value = '<span style="color: #17a2b8;">⏳ Loading trend data...</span>'

            trend_df = queries.get_trend_data(self.state)
            analysis_results['trend'] = trend_df

            # Execute other queries (stubs for now - Story 3.3)
            if hasattr(self, '_validation_message_widget') and self._validation_message_widget:
                self._validation_message_widget.value = '<span style="color: #17a2b8;">⏳ Loading applicant data...</span>'

            analysis_results['applicants'] = queries.get_top_applicants(self.state)
            analysis_results['tech_breakdown'] = queries.get_tech_breakdown(self.state)
            analysis_results['regional'] = queries.get_regional_distribution(self.state)

            # Show success message
            result_count = len(trend_df) if not trend_df.empty else 0
            if result_count > 0:
                total_apps = trend_df['application_count'].sum() if 'application_count' in trend_df.columns else 0
                if hasattr(self, '_validation_message_widget') and self._validation_message_widget:
                    self._validation_message_widget.value = f'<span style="color: #28a745;">✅ Analysis complete: {result_count} years, {total_apps:,} applications</span>'
            else:
                if hasattr(self, '_validation_message_widget') and self._validation_message_widget:
                    self._validation_message_widget.value = '<span style="color: #ffc107;">⚠️ No patents found for this selection. Try expanding date range or changing filters.</span>'

        except Exception as e:
            # Show error message
            if hasattr(self, '_validation_message_widget') and self._validation_message_widget:
                self._validation_message_widget.value = f'<span style="color: #dc3545;">❌ Query error: {str(e)}</span>'
            print(f"Query execution error: {e}")

        # Reset button state
        button.description = 'Run Analysis'
        button.disabled = False
        button.icon = 'play'

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
