"""
Tests for querylib_core module.

Tests Story 1.1 acceptance criteria:
- AC1: Successful initialization
- AC2: Connection failure handling
- AC3: Idempotent reinitialization

Note: Full integration tests require TIP environment.
These are unit tests for module structure and error handling.
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestQueryLibCoreModuleStructure(unittest.TestCase):
    """Test module structure and exports (AC1: module loaded)."""

    def test_module_imports(self):
        """Module should import without errors."""
        import querylib_core
        self.assertIsNotNone(querylib_core)

    def test_module_exports(self):
        """Module should export all required functions."""
        import querylib_core
        required_exports = [
            'init_patstat',
            'display_status',
            'display_error',
            'show_progress',
            'patstat_client',
            'db',
            'EPO_COLORS',
        ]
        for export in required_exports:
            self.assertIn(export, querylib_core.__all__,
                          f"'{export}' should be in __all__")
            self.assertTrue(hasattr(querylib_core, export),
                            f"'{export}' should be accessible from module")

    def test_epo_colors_defined(self):
        """EPO_COLORS should contain required brand colors."""
        from querylib_core import EPO_COLORS
        required_colors = ['primary_blue', 'green', 'red', 'light_gray']
        for color in required_colors:
            self.assertIn(color, EPO_COLORS,
                          f"EPO_COLORS should contain '{color}'")

    def test_module_level_state_initialized_to_none(self):
        """Module-level state should start as None (idempotent)."""
        # Reload module to test initial state
        import importlib
        import querylib_core
        importlib.reload(querylib_core)

        # After reload, should be None (not connected)
        self.assertIsNone(querylib_core.patstat_client,
                          "patstat_client should be None after module reload")
        self.assertIsNone(querylib_core.db,
                          "db should be None after module reload")


class TestInitPatstat(unittest.TestCase):
    """Test init_patstat function (AC1, AC2, AC3)."""

    @patch('querylib_core.PatstatClient')
    def test_init_patstat_success(self, mock_client_class):
        """AC1: Successful initialization returns client and session."""
        import querylib_core

        # Setup mock
        mock_client = MagicMock()
        mock_session = MagicMock()
        mock_client.orm.return_value = mock_session
        mock_client_class.return_value = mock_client

        # Call init
        client, session = querylib_core.init_patstat()

        # Verify
        mock_client_class.assert_called_once_with(env='PROD')
        mock_client.orm.assert_called_once()
        self.assertEqual(client, mock_client)
        self.assertEqual(session, mock_session)

        # Verify module-level state updated
        self.assertEqual(querylib_core.patstat_client, mock_client)
        self.assertEqual(querylib_core.db, mock_session)

    @patch('querylib_core.PatstatClient')
    def test_init_patstat_failure_raises_connection_error(self, mock_client_class):
        """AC2: Connection failure raises ConnectionError."""
        import querylib_core

        # Setup mock to raise exception
        mock_client_class.side_effect = Exception("Network error")

        # Should raise ConnectionError
        with self.assertRaises(ConnectionError) as context:
            querylib_core.init_patstat()

        self.assertIn("PATSTAT", str(context.exception))
        self.assertIn("Network error", str(context.exception))

    @patch('querylib_core.PatstatClient')
    def test_init_patstat_idempotent(self, mock_client_class):
        """AC3: Re-running init should work without errors."""
        import querylib_core

        # Setup mock
        mock_client = MagicMock()
        mock_session = MagicMock()
        mock_client.orm.return_value = mock_session
        mock_client_class.return_value = mock_client

        # Call twice
        querylib_core.init_patstat()
        querylib_core.init_patstat()

        # Should be called twice (fresh connection each time)
        self.assertEqual(mock_client_class.call_count, 2)


class TestDisplayFunctions(unittest.TestCase):
    """Test display helper functions (AC1, AC2)."""

    @patch('querylib_core.display')
    def test_display_status_success(self, mock_display):
        """AC1: display_status shows success emoji."""
        from querylib_core import display_status

        display_status("Test message", success=True)

        mock_display.assert_called_once()
        # Check HTML contains success emoji (access .data for HTML content)
        html_arg = mock_display.call_args[0][0]
        html_content = html_arg.data if hasattr(html_arg, 'data') else str(html_arg)
        self.assertIn('✅', html_content)

    @patch('querylib_core.display')
    def test_display_status_failure(self, mock_display):
        """AC2: display_status shows failure emoji."""
        from querylib_core import display_status

        display_status("Test message", success=False)

        mock_display.assert_called_once()
        # Check HTML contains failure emoji (access .data for HTML content)
        html_arg = mock_display.call_args[0][0]
        html_content = html_arg.data if hasattr(html_arg, 'data') else str(html_arg)
        self.assertIn('❌', html_content)

    @patch('querylib_core.display')
    @patch('builtins.print')
    def test_display_error_shows_user_friendly_message(self, mock_print, mock_display):
        """AC2: display_error shows user-friendly message."""
        from querylib_core import display_error

        display_error(
            "Connection Error",
            "Please check your network",
            details="TimeoutError: connection timed out"
        )

        # Should display HTML with title and message (access .data for HTML content)
        mock_display.assert_called_once()
        html_arg = mock_display.call_args[0][0]
        html_content = html_arg.data if hasattr(html_arg, 'data') else str(html_arg)
        self.assertIn("Connection Error", html_content)
        self.assertIn("Please check your network", html_content)

        # Technical details should be printed separately
        mock_print.assert_called_once()
        print_arg = mock_print.call_args[0][0]
        self.assertIn("TimeoutError", print_arg)

    @patch('querylib_core.display')
    @patch('builtins.print')
    def test_display_error_without_details(self, mock_print, mock_display):
        """AC2: display_error works without optional details parameter."""
        from querylib_core import display_error

        display_error("Connection Error", "Please check your network")

        # Should display HTML with title and message
        mock_display.assert_called_once()
        html_arg = mock_display.call_args[0][0]
        html_content = html_arg.data if hasattr(html_arg, 'data') else str(html_arg)
        self.assertIn("Connection Error", html_content)
        self.assertIn("Please check your network", html_content)

        # Technical details should NOT be printed when not provided
        mock_print.assert_not_called()

    @patch('querylib_core.display')
    def test_show_progress_returns_widget(self, mock_display):
        """AC1: show_progress returns updatable widget."""
        from querylib_core import show_progress
        import ipywidgets as widgets

        progress = show_progress("Loading...")

        # Should return HTML widget
        self.assertIsInstance(progress, widgets.HTML)

        # Should have been displayed
        mock_display.assert_called_once()

        # Should be updatable
        progress.value = "✅ Done!"
        self.assertIn("Done", progress.value)


if __name__ == '__main__':
    unittest.main()
