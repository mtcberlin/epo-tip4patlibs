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
from typing import List, Optional, Tuple

# Heavy imports - kept in module, not notebook
import pandas as pd
import plotly.express as px
import ipywidgets as widgets

# Module exports - controls what `from tip4patlibs_core import *` exposes
__all__ = [
    'AnalysisState',
    'PatstatQueries',
    'WidgetFactory',
    'ChartBuilder',
    'Exporter',
]


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
        # Placeholder implementation - will be enhanced in Story 1.4
        lines = [
            f"Country: {self.country or 'Not selected'}",
            f"Region: {self.region or 'All regions'}",
        ]
        if self.tech_mode == "field":
            lines.append(f"Technology: Field {self.tech_field or 'Not selected'}")
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
        # Placeholder implementation - will be enhanced in Story 1.4
        return (False, "Not implemented")


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
