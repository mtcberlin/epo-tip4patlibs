"""
QueryLib Core Module
====================
Core functions for the Query Library notebook.
Provides initialization, status display, and error handling.

This module follows ADR-015: Each notebook has its own *_core.py module.

Architecture Requirements:
- UI framework: ipywidgets (ADR-007)
- Data access: PatstatClient only (NFR11)
- Error messages: User-friendly, no tracebacks (FR35, NFR7)
- Colors: EPO_COLORS palette (Phase 1)

Author: BMad
Version: 0.1.0
"""

from typing import Tuple, Optional, Any

# IPython and widgets for display
import ipywidgets as widgets
from IPython.display import display, HTML

# PATSTAT connection
from epo.tipdata.patstat import PatstatClient

# =============================================================================
# Module-level Connection State
# =============================================================================

patstat_client: Optional[PatstatClient] = None
db: Optional[Any] = None  # SQLAlchemy Session

# =============================================================================
# EPO Brand Colors (from existing tip4patlibs_core.py)
# =============================================================================

EPO_COLORS = {
    'primary_blue': '#003399',
    'secondary_blue': '#0055A5',
    'light_blue': '#66B3FF',
    'orange': '#FF6600',
    'green': '#009933',
    'red': '#C8102E',
    'gray': '#666666',
    'light_gray': '#F5F5F5',
    'error_bg': '#FFF5F5',  # Light red background for errors
}

# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    'init_patstat',
    'display_status',
    'display_error',
    'show_progress',
    'patstat_client',
    'db',
    'EPO_COLORS',
]


# =============================================================================
# PATSTAT Connection Management
# =============================================================================

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
        >>> client, session = init_patstat()
        >>> print(session)  # Access the session
    """
    global patstat_client, db
    try:
        patstat_client = PatstatClient(env='PROD')
        db = patstat_client.orm()
        return patstat_client, db
    except Exception as e:
        raise ConnectionError(f"Could not connect to PATSTAT: {e}") from e


# =============================================================================
# Status Display Helpers (FR34, FR35)
# =============================================================================

def display_status(message: str, success: bool = True) -> None:
    """
    Display status message with emoji indicator.

    Shows a styled status message with green checkmark (success) or
    red X (failure) emoji. Uses EPO brand colors for styling.

    Args:
        message: The status message to display
        success: True for success (green), False for failure (red)

    Example:
        >>> display_status("Connection established", success=True)
        >>> display_status("Query failed", success=False)
    """
    emoji = "✅" if success else "❌"
    color = EPO_COLORS['green'] if success else EPO_COLORS['red']

    html_content = f"""
    <div style="padding: 10px; border-left: 4px solid {color}; background-color: {EPO_COLORS['light_gray']}; margin: 5px 0;">
        <span style="font-size: 1.2em;">{emoji}</span>
        <span style="color: {color}; font-weight: bold; margin-left: 8px;">{message}</span>
    </div>
    """
    display(HTML(html_content))


def display_error(title: str, message: str, details: Optional[str] = None) -> None:
    """
    Display user-friendly error with optional technical details.

    Shows a red-styled error box with helpful message for users.
    Technical details are printed below for troubleshooting but
    kept separate from the user-facing message.

    Args:
        title: Short error title (e.g., "Connection Error")
        message: User-friendly description with suggested actions
        details: Optional technical details for debugging

    Example:
        >>> display_error(
        ...     "Connection Error",
        ...     "Unable to connect to PATSTAT. Please check your network.",
        ...     details="TimeoutError: Connection timed out after 30s"
        ... )
    """
    html_content = f"""
    <div style="color: {EPO_COLORS['red']}; padding: 15px; border: 1px solid {EPO_COLORS['red']};
                border-radius: 4px; background-color: {EPO_COLORS['error_bg']}; margin: 10px 0;">
        <b style="font-size: 1.1em;">❌ {title}</b><br><br>
        {message}
    </div>
    """
    display(HTML(html_content))

    # Technical details printed below for debugging (visible in notebook output)
    if details:
        print(f"\nTechnical details: {details}")


def show_progress(message: str = "Loading...") -> widgets.HTML:
    """
    Create and display a progress indicator.

    Returns the widget so caller can update its value when the
    operation completes.

    Args:
        message: Initial progress message (default: "Loading...")

    Returns:
        widgets.HTML: The progress widget for later updates

    Example:
        >>> progress = show_progress("Connecting to PATSTAT...")
        >>> # ... do work ...
        >>> progress.value = "✅ Connected!"
    """
    progress = widgets.HTML(
        value=f"""
        <div style="padding: 10px; background-color: {EPO_COLORS['light_gray']};
                    border-left: 4px solid {EPO_COLORS['primary_blue']};">
            <span style="font-size: 1.2em;">⏳</span>
            <span style="color: {EPO_COLORS['primary_blue']}; margin-left: 8px;">{message}</span>
        </div>
        """
    )
    display(progress)
    return progress
