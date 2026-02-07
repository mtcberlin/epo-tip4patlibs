"""
Tests for Query Browser Widget (Story 1.3)

Tests the QueryBrowser, QueryPreview, and SQLViewer widget classes
that provide the visual interface for browsing and selecting queries.
"""

import unittest
from unittest.mock import MagicMock, patch
import re
import threading
import time

# Import classes under test
from TIP_for_PATLIBs_QueryLib_core import (
    QueryRegistry,
    QueryMetadata,
    ParameterSpec,
    EPO_COLORS,
)


class TestQueryBrowserInitialization(unittest.TestCase):
    """Test QueryBrowser widget initialization (Task 1.1, 1.7)."""

    def setUp(self):
        """Set up registry for tests."""
        self.registry = QueryRegistry()

    def test_query_browser_import(self):
        """Test that QueryBrowser can be imported from TIP_for_PATLIBs_QueryLib_core."""
        from TIP_for_PATLIBs_QueryLib_core import QueryBrowser
        self.assertIsNotNone(QueryBrowser)

    def test_query_browser_initialization(self):
        """Test QueryBrowser initializes with a registry."""
        from TIP_for_PATLIBs_QueryLib_core import QueryBrowser
        browser = QueryBrowser(self.registry)
        self.assertIsNotNone(browser)
        self.assertEqual(browser._registry, self.registry)

    def test_query_browser_has_category_dropdown(self):
        """Test QueryBrowser has category dropdown widget (Task 1.2)."""
        from TIP_for_PATLIBs_QueryLib_core import QueryBrowser
        browser = QueryBrowser(self.registry)
        self.assertIsNotNone(browser.category_dropdown)
        # Should have "All Categories" plus actual categories
        self.assertIn("All Categories", browser.category_dropdown.options)

    def test_query_browser_has_search_input(self):
        """Test QueryBrowser has search text input (Task 1.3)."""
        from TIP_for_PATLIBs_QueryLib_core import QueryBrowser
        browser = QueryBrowser(self.registry)
        self.assertIsNotNone(browser.search_input)
        self.assertEqual(browser.search_input.placeholder, "Search queries...")

    def test_query_browser_has_query_list(self):
        """Test QueryBrowser has query list output area (Task 1.4)."""
        from TIP_for_PATLIBs_QueryLib_core import QueryBrowser
        browser = QueryBrowser(self.registry)
        self.assertIsNotNone(browser.query_list)


class TestCategoryFiltering(unittest.TestCase):
    """Test category filtering functionality (Task 1.5)."""

    def setUp(self):
        """Set up registry and browser for tests."""
        self.registry = QueryRegistry()
        from TIP_for_PATLIBs_QueryLib_core import QueryBrowser
        self.browser = QueryBrowser(self.registry)

    def test_all_categories_shows_all_queries(self):
        """Test 'All Categories' selection shows all queries."""
        self.browser.category_dropdown.value = "All Categories"
        self.browser._on_category_change({'new': 'All Categories'})

        # Query list should contain all queries
        all_queries = self.registry.get_all_queries()
        self.assertEqual(len(self.browser._current_queries), len(all_queries))

    def test_category_filter_shows_only_category_queries(self):
        """Test selecting a category filters to only that category."""
        self.browser._on_category_change({'new': 'Regional'})

        # All displayed queries should be in Regional category
        for query in self.browser._current_queries:
            self.assertEqual(query.category, 'Regional')

    def test_category_filter_updates_query_list(self):
        """Test category filter updates the query list options."""
        initial_options = len(self.browser.query_list.options)

        # Filter to a specific category
        self.browser._on_category_change({'new': 'Regional'})
        regional_queries = self.registry.get_queries_by_category('Regional')

        # Query list should now show only regional queries
        self.assertEqual(len(self.browser.query_list.options), len(regional_queries))


class TestSearchFunctionality(unittest.TestCase):
    """Test search functionality with debouncing (Task 1.6)."""

    def setUp(self):
        """Set up registry and browser for tests."""
        self.registry = QueryRegistry()
        from TIP_for_PATLIBs_QueryLib_core import QueryBrowser
        self.browser = QueryBrowser(self.registry)

    def test_search_filters_by_title(self):
        """Test search filters queries by title."""
        # Execute search directly (bypassing debounce)
        self.browser._execute_search("country")

        # All results should contain "country" in title or description or tags
        for query in self.browser._current_queries:
            contains_keyword = (
                "country" in query.title.lower() or
                "country" in query.description.lower() or
                any("country" in tag.lower() for tag in query.tags)
            )
            self.assertTrue(contains_keyword,
                f"Query {query.id} doesn't contain 'country'")

    def test_search_filters_by_description(self):
        """Test search filters queries by description."""
        self.browser._execute_search("patent")

        # Should find queries mentioning "patent"
        self.assertGreater(len(self.browser._current_queries), 0)

    def test_search_respects_category_filter(self):
        """Test search respects current category filter."""
        # Set category to Regional first
        self.browser.category_dropdown.value = "Regional"
        self.browser._on_category_change({'new': 'Regional'})

        # Now search
        self.browser._execute_search("patent")

        # All results should be in Regional category
        for query in self.browser._current_queries:
            self.assertEqual(query.category, 'Regional')

    def test_search_debounce_delay_exists(self):
        """Test search has debounce delay configured."""
        from TIP_for_PATLIBs_QueryLib_core import QueryBrowser
        browser = QueryBrowser(self.registry)
        self.assertEqual(browser._search_delay, 0.3)  # 300ms

    def test_empty_search_shows_all_queries(self):
        """Test empty search shows all queries in current category."""
        self.browser._execute_search("")

        all_queries = self.registry.get_all_queries()
        self.assertEqual(len(self.browser._current_queries), len(all_queries))


class TestQueryPreviewWidget(unittest.TestCase):
    """Test QueryPreview widget (Task 2)."""

    def setUp(self):
        """Set up test data."""
        self.registry = QueryRegistry()
        self.sample_query = self.registry.get_query("Q01")

    def test_query_preview_import(self):
        """Test that QueryPreview can be imported."""
        from TIP_for_PATLIBs_QueryLib_core import QueryPreview
        self.assertIsNotNone(QueryPreview)

    def test_query_preview_initialization(self):
        """Test QueryPreview initializes correctly."""
        from TIP_for_PATLIBs_QueryLib_core import QueryPreview
        preview = QueryPreview()
        self.assertIsNotNone(preview)

    def test_query_preview_shows_title(self):
        """Test QueryPreview displays query title (Task 2.2)."""
        from TIP_for_PATLIBs_QueryLib_core import QueryPreview
        preview = QueryPreview()
        preview.update(self.sample_query)

        # Title should be in the HTML content
        self.assertIn(self.sample_query.title, preview.title_html.value)

    def test_query_preview_shows_category_badge(self):
        """Test QueryPreview displays category badge (Task 2.2)."""
        from TIP_for_PATLIBs_QueryLib_core import QueryPreview
        preview = QueryPreview()
        preview.update(self.sample_query)

        # Category should appear in title HTML
        self.assertIn(self.sample_query.category, preview.title_html.value)

    def test_query_preview_shows_description(self):
        """Test QueryPreview displays description (Task 2.2)."""
        from TIP_for_PATLIBs_QueryLib_core import QueryPreview
        preview = QueryPreview()
        preview.update(self.sample_query)

        # Description should be in description HTML
        self.assertIn(self.sample_query.description[:50], preview.description_html.value)

    def test_query_preview_shows_tags(self):
        """Test QueryPreview displays tags (Task 2.2)."""
        from TIP_for_PATLIBs_QueryLib_core import QueryPreview
        preview = QueryPreview()
        preview.update(self.sample_query)

        # At least one tag should appear
        if self.sample_query.tags:
            self.assertIn(self.sample_query.tags[0], preview.tags_html.value)

    def test_query_preview_has_view_sql_button(self):
        """Test QueryPreview has View SQL button (Task 2.5)."""
        from TIP_for_PATLIBs_QueryLib_core import QueryPreview
        preview = QueryPreview()
        self.assertIsNotNone(preview.view_sql_button)
        self.assertEqual(preview.view_sql_button.description, "View SQL")

    def test_view_sql_button_initially_disabled(self):
        """Test View SQL button is initially disabled (Task 2.5)."""
        from TIP_for_PATLIBs_QueryLib_core import QueryPreview
        preview = QueryPreview()
        self.assertTrue(preview.view_sql_button.disabled)

    def test_view_sql_button_enabled_after_selection(self):
        """Test View SQL button enabled after query selection (Task 2.6)."""
        from TIP_for_PATLIBs_QueryLib_core import QueryPreview
        preview = QueryPreview()
        preview.update(self.sample_query)
        self.assertFalse(preview.view_sql_button.disabled)


class TestSQLViewerWidget(unittest.TestCase):
    """Test SQLViewer widget (Task 3)."""

    def test_sql_viewer_import(self):
        """Test that SQLViewer can be imported."""
        from TIP_for_PATLIBs_QueryLib_core import SQLViewer
        self.assertIsNotNone(SQLViewer)

    def test_sql_viewer_initialization(self):
        """Test SQLViewer initializes correctly (Task 3.1)."""
        from TIP_for_PATLIBs_QueryLib_core import SQLViewer
        viewer = SQLViewer()
        self.assertIsNotNone(viewer)

    def test_sql_viewer_displays_sql(self):
        """Test SQLViewer displays SQL content (Task 3.2)."""
        from TIP_for_PATLIBs_QueryLib_core import SQLViewer
        viewer = SQLViewer()

        test_sql = "SELECT * FROM table WHERE year >= @year_start"
        viewer.show_sql(test_sql)

        # SQL should be in the content
        self.assertIn("SELECT", viewer.sql_content.value)

    def test_sql_viewer_preserves_indentation(self):
        """Test SQLViewer preserves SQL indentation (Task 3.2)."""
        from TIP_for_PATLIBs_QueryLib_core import SQLViewer
        viewer = SQLViewer()

        test_sql = """SELECT
    column1,
    column2
FROM table"""
        viewer.show_sql(test_sql)

        # Check that formatting is preserved (via <pre> tag)
        self.assertIn("<pre", viewer.sql_content.value)


class TestSQLParameterHighlighting(unittest.TestCase):
    """Test SQL parameter highlighting (Task 3.3)."""

    def test_highlight_parameters_function(self):
        """Test highlight_parameters function exists."""
        from TIP_for_PATLIBs_QueryLib_core import highlight_parameters
        self.assertIsNotNone(highlight_parameters)

    def test_highlight_single_parameter(self):
        """Test highlighting a single @parameter."""
        from TIP_for_PATLIBs_QueryLib_core import highlight_parameters

        sql = "SELECT * FROM table WHERE year >= @year_start"
        highlighted = highlight_parameters(sql)

        # Should contain a span with the parameter
        self.assertIn("@year_start", highlighted)
        self.assertIn("<span", highlighted)
        self.assertIn(EPO_COLORS['orange'], highlighted)

    def test_highlight_multiple_parameters(self):
        """Test highlighting multiple @parameters."""
        from TIP_for_PATLIBs_QueryLib_core import highlight_parameters

        sql = "SELECT * FROM table WHERE year >= @start_year AND year <= @end_year"
        highlighted = highlight_parameters(sql)

        # Both parameters should be highlighted
        self.assertIn("@start_year", highlighted)
        self.assertIn("@end_year", highlighted)

    def test_no_highlight_when_no_parameters(self):
        """Test no highlighting when no parameters present."""
        from TIP_for_PATLIBs_QueryLib_core import highlight_parameters

        sql = "SELECT COUNT(*) FROM table"
        highlighted = highlight_parameters(sql)

        # Should not contain span for parameters
        self.assertNotIn("<span", highlighted)

    def test_highlight_preserves_sql_structure(self):
        """Test highlighting preserves SQL structure."""
        from TIP_for_PATLIBs_QueryLib_core import highlight_parameters

        sql = "SELECT column FROM table WHERE id = @id"
        highlighted = highlight_parameters(sql)

        # Original SQL keywords should still be present
        self.assertIn("SELECT", highlighted)
        self.assertIn("FROM", highlighted)
        self.assertIn("WHERE", highlighted)


class TestBrowserWidgetComposition(unittest.TestCase):
    """Test full browser widget composition (Task 4)."""

    def setUp(self):
        """Set up registry for tests."""
        self.registry = QueryRegistry()

    def test_create_query_browser_factory(self):
        """Test create_query_browser factory function (Task 4.1)."""
        from TIP_for_PATLIBs_QueryLib_core import create_query_browser

        browser_widget = create_query_browser(self.registry)
        self.assertIsNotNone(browser_widget)

    def test_browser_widget_is_vbox(self):
        """Test browser is composed as VBox (Task 4.2)."""
        from TIP_for_PATLIBs_QueryLib_core import create_query_browser
        import ipywidgets as widgets

        browser_widget = create_query_browser(self.registry)
        self.assertIsInstance(browser_widget, widgets.VBox)

    def test_browser_uses_epo_colors(self):
        """Test browser uses EPO_COLORS palette (Task 4.3)."""
        from TIP_for_PATLIBs_QueryLib_core import create_query_browser

        browser_widget = create_query_browser(self.registry)

        # The header should use EPO primary blue
        header_html = browser_widget.children[0].value
        self.assertIn(EPO_COLORS['primary_blue'], header_html)

    def test_browser_exports_selected_query(self):
        """Test browser exports selected query (Task 4.5)."""
        from TIP_for_PATLIBs_QueryLib_core import QueryBrowser

        browser = QueryBrowser(self.registry)

        # Initially no selection
        self.assertIsNone(browser.selected_query)

        # After selection, should have selected query
        queries = self.registry.get_all_queries()
        if queries:
            browser._on_query_select({'new': queries[0].id})
            self.assertIsNotNone(browser.selected_query)


class TestBrowserIntegration(unittest.TestCase):
    """Integration tests for full browser functionality."""

    def setUp(self):
        """Set up registry and browser for tests."""
        self.registry = QueryRegistry()

    def test_browse_all_42_queries(self):
        """Test that all 42 queries are browsable (Task 5.4)."""
        from TIP_for_PATLIBs_QueryLib_core import QueryBrowser

        browser = QueryBrowser(self.registry)

        # All queries should be available
        all_queries = self.registry.get_all_queries()
        self.assertEqual(len(all_queries), 42)

        # Query list should show all of them
        browser._on_category_change({'new': 'All Categories'})
        self.assertEqual(len(browser._current_queries), 42)

    def test_full_workflow_browse_search_select(self):
        """Test full workflow: browse, search, select, view SQL."""
        from TIP_for_PATLIBs_QueryLib_core import QueryBrowser, QueryPreview, SQLViewer

        # Create widgets
        browser = QueryBrowser(self.registry)
        preview = QueryPreview()
        sql_viewer = SQLViewer()

        # 1. Browse categories
        self.assertIn("Regional", browser.category_dropdown.options)

        # 2. Filter to category
        browser._on_category_change({'new': 'Regional'})
        regional_count = len(browser._current_queries)
        self.assertGreater(regional_count, 0)

        # 3. Select a query
        if browser._current_queries:
            query = browser._current_queries[0]
            browser._on_query_select({'new': query.id})
            self.assertEqual(browser.selected_query, query)

            # 4. Update preview
            preview.update(query)
            self.assertIn(query.title, preview.title_html.value)

            # 5. View SQL
            sql_viewer.show_sql(query.sql_template)
            self.assertIn("SELECT", sql_viewer.sql_content.value)


if __name__ == "__main__":
    unittest.main()
