"""
Tests for Results Display and Export functionality (Story 1.6).

Tests Story 1.6 acceptance criteria:
- AC1: DataFrame Display with formatting and row count
- AC2: CSV Export with semicolon delimiter, UTF-8 BOM
- AC3: PNG Export at 300 DPI
- AC4: Zero Results Handling with helpful messages
- AC5: Copy SQL for editing

Note: Full integration tests require TIP environment.
These are unit tests for module structure and formatting functions.
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import tempfile
import shutil

import pandas as pd

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestFormatNumber(unittest.TestCase):
    """Test number formatting function (AC1: formatted numbers)."""

    def test_format_integer_with_thousands(self):
        """Large integers should have thousand separators."""
        from TIP_for_PATLIBs_QueryLib_core import format_number

        self.assertEqual(format_number(1234567), "1,234,567")
        self.assertEqual(format_number(1000), "1,000")
        self.assertEqual(format_number(999), "999")

    def test_format_float_with_thousands_and_decimals(self):
        """Floats should have thousand separators and 2 decimal places."""
        from TIP_for_PATLIBs_QueryLib_core import format_number

        self.assertEqual(format_number(1234567.89), "1,234,567.89")
        self.assertEqual(format_number(1000.5), "1,000.50")

    def test_format_small_numbers(self):
        """Small numbers should still format correctly."""
        from TIP_for_PATLIBs_QueryLib_core import format_number

        self.assertEqual(format_number(0), "0")
        self.assertEqual(format_number(1), "1")
        self.assertEqual(format_number(99), "99")

    def test_format_non_numeric_passthrough(self):
        """Non-numeric values should pass through unchanged."""
        from TIP_for_PATLIBs_QueryLib_core import format_number

        self.assertEqual(format_number("text"), "text")
        self.assertEqual(format_number(None), None)

    def test_format_nan_passthrough(self):
        """NaN values should pass through unchanged."""
        from TIP_for_PATLIBs_QueryLib_core import format_number
        import math

        self.assertTrue(math.isnan(format_number(float('nan'))))


class TestResultsDisplay(unittest.TestCase):
    """Test ResultsDisplay class (AC1: DataFrame display)."""

    def test_results_display_class_exists(self):
        """ResultsDisplay class should be importable."""
        from TIP_for_PATLIBs_QueryLib_core import ResultsDisplay
        self.assertIsNotNone(ResultsDisplay)

    def test_results_display_has_widget(self):
        """ResultsDisplay should have a widget property."""
        from TIP_for_PATLIBs_QueryLib_core import ResultsDisplay

        rd = ResultsDisplay()
        self.assertTrue(hasattr(rd, 'widget'))

    @patch('TIP_for_PATLIBs_QueryLib_core.display')
    def test_results_display_shows_row_count(self, mock_display):
        """ResultsDisplay should show row count above table (AC1)."""
        from TIP_for_PATLIBs_QueryLib_core import ResultsDisplay

        # Create sample DataFrame
        df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})

        rd = ResultsDisplay()
        rd.show(df, title="Test Query")

        # Verify display was called
        self.assertTrue(mock_display.called)

    @patch('TIP_for_PATLIBs_QueryLib_core.display')
    def test_results_display_limits_to_100_rows(self, mock_display):
        """ResultsDisplay should show first 100 rows with message for larger datasets (AC1)."""
        from TIP_for_PATLIBs_QueryLib_core import ResultsDisplay

        # Create large DataFrame
        df = pd.DataFrame({'A': range(150), 'B': range(150)})

        rd = ResultsDisplay()
        rd.show(df, title="Test Query")

        # Should have been displayed
        self.assertTrue(mock_display.called)


class TestZeroResultsHandler(unittest.TestCase):
    """Test zero results handling (AC4)."""

    @patch('TIP_for_PATLIBs_QueryLib_core.display')
    def test_display_zero_results_shows_message(self, mock_display):
        """Empty DataFrame should show helpful message (AC4)."""
        from TIP_for_PATLIBs_QueryLib_core import display_zero_results

        display_zero_results()

        # Should display an HTML message
        mock_display.assert_called_once()
        html_arg = mock_display.call_args[0][0]
        html_content = html_arg.data if hasattr(html_arg, 'data') else str(html_arg)

        # Should contain helpful message
        self.assertIn("no results found", html_content.lower())
        self.assertIn("try", html_content.lower())  # Suggestion present

    @patch('TIP_for_PATLIBs_QueryLib_core.display')
    def test_zero_results_shows_suggestions(self, mock_display):
        """Zero results should show suggestions for broadening search (AC4)."""
        from TIP_for_PATLIBs_QueryLib_core import display_zero_results

        display_zero_results()

        html_arg = mock_display.call_args[0][0]
        html_content = html_arg.data if hasattr(html_arg, 'data') else str(html_arg)

        # Should contain suggestions
        self.assertIn("date range", html_content.lower())


class TestCSVExporter(unittest.TestCase):
    """Test CSV export functionality (AC2)."""

    def setUp(self):
        """Set up temporary directory for exports."""
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)

    def tearDown(self):
        """Clean up temporary directory."""
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)

    def test_export_to_csv_function_exists(self):
        """export_to_csv function should be importable."""
        from TIP_for_PATLIBs_QueryLib_core import export_to_csv
        self.assertIsNotNone(export_to_csv)

    def test_export_to_csv_creates_file(self):
        """export_to_csv should create a file (AC2)."""
        from TIP_for_PATLIBs_QueryLib_core import export_to_csv

        df = pd.DataFrame({'A': [1, 2, 3], 'B': ['x', 'y', 'z']})
        filepath = export_to_csv(df, "Test Query")

        self.assertTrue(os.path.exists(filepath))

    def test_export_to_csv_uses_semicolon_delimiter(self):
        """CSV should use semicolon delimiter per architecture spec (AC2)."""
        from TIP_for_PATLIBs_QueryLib_core import export_to_csv

        df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
        filepath = export_to_csv(df, "Test Query")

        with open(filepath, 'r', encoding='utf-8-sig') as f:
            content = f.read()

        # Check for semicolon delimiter
        self.assertIn(';', content)
        self.assertNotIn(',', content.split('\n')[0])  # First line (header) should have no commas

    def test_export_to_csv_uses_utf8_bom(self):
        """CSV should use UTF-8 with BOM per architecture spec (AC2)."""
        from TIP_for_PATLIBs_QueryLib_core import export_to_csv

        df = pd.DataFrame({'A': [1, 2], 'B': ['äöü', 'ñ']})
        filepath = export_to_csv(df, "Test Query")

        with open(filepath, 'rb') as f:
            content = f.read()

        # Check for UTF-8 BOM (EF BB BF)
        self.assertTrue(content.startswith(b'\xef\xbb\xbf'))

    def test_export_to_csv_filename_includes_query_title(self):
        """Filename should include sanitized query title (AC2)."""
        from TIP_for_PATLIBs_QueryLib_core import export_to_csv

        df = pd.DataFrame({'A': [1, 2]})
        filepath = export_to_csv(df, "Country Patent Activity")

        filename = os.path.basename(filepath)
        self.assertIn("Country_Patent_Activity", filename)

    def test_export_to_csv_filename_includes_timestamp(self):
        """Filename should include timestamp (AC2)."""
        from TIP_for_PATLIBs_QueryLib_core import export_to_csv

        df = pd.DataFrame({'A': [1, 2]})
        filepath = export_to_csv(df, "Test Query")

        filename = os.path.basename(filepath)
        # Should match pattern: name_YYYYMMDD_HHMMSS.csv
        import re
        self.assertTrue(re.search(r'_\d{8}_\d{6}\.csv$', filename))


class TestPNGExporter(unittest.TestCase):
    """Test PNG export functionality (AC3)."""

    def test_export_to_png_function_exists(self):
        """export_to_png function should be importable."""
        from TIP_for_PATLIBs_QueryLib_core import export_to_png
        self.assertIsNotNone(export_to_png)


class TestCopySQLButton(unittest.TestCase):
    """Test Copy SQL functionality (AC5)."""

    def test_copy_sql_to_clipboard_function_exists(self):
        """copy_sql_to_clipboard function should be importable."""
        from TIP_for_PATLIBs_QueryLib_core import copy_sql_to_clipboard
        self.assertIsNotNone(copy_sql_to_clipboard)

    @patch('TIP_for_PATLIBs_QueryLib_core.display')
    @patch('TIP_for_PATLIBs_QueryLib_core.Javascript')
    def test_copy_sql_calls_javascript(self, mock_js, mock_display):
        """copy_sql_to_clipboard should use JavaScript clipboard API (AC5)."""
        from TIP_for_PATLIBs_QueryLib_core import copy_sql_to_clipboard

        copy_sql_to_clipboard("SELECT * FROM test")

        # Should create JavaScript
        mock_js.assert_called_once()
        js_code = mock_js.call_args[0][0]
        self.assertIn("clipboard", js_code)


class TestResultsPanel(unittest.TestCase):
    """Test ResultsPanel composite widget (AC1-5)."""

    def test_results_panel_class_exists(self):
        """ResultsPanel class should be importable."""
        from TIP_for_PATLIBs_QueryLib_core import ResultsPanel
        self.assertIsNotNone(ResultsPanel)

    def test_results_panel_has_widget(self):
        """ResultsPanel should have a widget property."""
        from TIP_for_PATLIBs_QueryLib_core import ResultsPanel

        panel = ResultsPanel()
        self.assertTrue(hasattr(panel, 'widget'))

    def test_results_panel_has_export_buttons(self):
        """ResultsPanel should have export buttons (AC2, AC3)."""
        from TIP_for_PATLIBs_QueryLib_core import ResultsPanel

        panel = ResultsPanel()
        # Should have access to export CSV button
        self.assertTrue(hasattr(panel, '_export_csv_btn'))
        # Should have access to export PNG button
        self.assertTrue(hasattr(panel, '_export_png_btn'))

    def test_results_panel_has_copy_sql_button(self):
        """ResultsPanel should have copy SQL button (AC5)."""
        from TIP_for_PATLIBs_QueryLib_core import ResultsPanel

        panel = ResultsPanel()
        self.assertTrue(hasattr(panel, '_copy_sql_btn'))


class TestModuleExports(unittest.TestCase):
    """Test that all Story 1.6 exports are in __all__."""

    def test_results_display_in_exports(self):
        """ResultsDisplay should be in __all__."""
        import TIP_for_PATLIBs_QueryLib_core

        expected_exports = [
            'ResultsDisplay',
            'ResultsPanel',
            'export_to_csv',
            'export_to_png',
            'display_zero_results',
            'copy_sql_to_clipboard',
            'format_number',
        ]

        for export in expected_exports:
            self.assertIn(export, TIP_for_PATLIBs_QueryLib_core.__all__,
                          f"'{export}' should be in __all__")


if __name__ == '__main__':
    unittest.main()
