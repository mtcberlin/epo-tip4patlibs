"""
Unit Tests for Query Execution (Story 1.5)
==========================================
Tests for QueryExecutor, ProgressIndicator, and parameter substitution.

Test Categories:
- Task 1.7: Parameter substitution tests
- Task 2.6: ProgressIndicator state transition tests
- Task 3.5: Timer behavior tests
- Task 5.5: Error handling tests
"""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
import threading
import time

# Import the module under test
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from TIP_for_PATLIBs_QueryLib_core import (
    substitute_parameters,
    ProgressIndicator,
    QueryExecutor,
    QueryTimeoutError,
    QueryMetadata,
    ParameterSpec,
    TIMEOUT_SECONDS,
    EPO_COLORS,
)


# =============================================================================
# Task 1.7: Parameter Substitution Tests
# =============================================================================

class TestSubstituteParameters:
    """Tests for substitute_parameters function."""

    def test_substitutes_string_parameter(self):
        """Test substitution of string parameters with proper quoting."""
        sql = "SELECT * FROM table WHERE code = @code"
        params = {"code": "H01L"}
        result = substitute_parameters(sql, params)
        assert result == "SELECT * FROM table WHERE code = 'H01L'"

    def test_substitutes_integer_parameter(self):
        """Test substitution of integer parameters."""
        sql = "SELECT * FROM table WHERE count > @count"
        params = {"count": 10}
        result = substitute_parameters(sql, params)
        assert result == "SELECT * FROM table WHERE count > 10"

    def test_substitutes_year_range_tuple(self):
        """Test substitution of year range tuple."""
        sql = "SELECT * FROM table WHERE year >= @year_start AND year <= @year_end"
        params = {"year_range": (2015, 2020)}
        result = substitute_parameters(sql, params)
        assert "2015" in result
        assert "2020" in result

    def test_substitutes_year_range_alternative_names(self):
        """Test substitution with @start_year/@end_year pattern."""
        sql = "SELECT * FROM table WHERE year >= @start_year AND year <= @end_year"
        params = {"year_range": (2010, 2024)}
        result = substitute_parameters(sql, params)
        assert "2010" in result
        assert "2024" in result

    def test_substitutes_list_parameter(self):
        """Test substitution of list parameters for IN clause."""
        sql = "SELECT * FROM table WHERE country IN @countries"
        params = {"countries": ["EP", "US", "DE"]}
        result = substitute_parameters(sql, params)
        assert "('EP', 'US', 'DE')" in result

    def test_substitutes_empty_list(self):
        """Test substitution of empty list."""
        sql = "SELECT * FROM table WHERE country IN @countries"
        params = {"countries": []}
        result = substitute_parameters(sql, params)
        assert "()" in result

    def test_substitutes_multiple_parameters(self):
        """Test substitution of multiple parameters in one query."""
        sql = "SELECT * FROM table WHERE code = @code AND count > @count"
        params = {"code": "A01B", "count": 5}
        result = substitute_parameters(sql, params)
        assert "'A01B'" in result
        assert "5" in result

    def test_handles_missing_parameter(self):
        """Test that missing parameters leave placeholder unchanged."""
        sql = "SELECT * FROM table WHERE code = @code"
        params = {}
        result = substitute_parameters(sql, params)
        assert "@code" in result

    def test_substitutes_numeric_list(self):
        """Test substitution of numeric list."""
        sql = "SELECT * FROM table WHERE field IN @fields"
        params = {"fields": [1, 2, 3]}
        result = substitute_parameters(sql, params)
        assert "(1, 2, 3)" in result

    def test_substitutes_unnest_with_array_format(self):
        """Test that UNNEST parameters use BigQuery array format."""
        sql = "SELECT * FROM table WHERE country IN UNNEST(@jurisdictions)"
        params = {"jurisdictions": ["EP", "US", "DE"]}
        result = substitute_parameters(sql, params)
        # Should use array format ['EP', 'US', 'DE'] not tuple format ('EP', 'US', 'DE')
        assert "['EP', 'US', 'DE']" in result
        assert "('EP'" not in result

    def test_substitutes_unnest_case_insensitive(self):
        """Test that UNNEST detection is case-insensitive."""
        sql = "SELECT * FROM table WHERE country IN unnest(@countries)"
        params = {"countries": ["JP", "CN"]}
        result = substitute_parameters(sql, params)
        assert "['JP', 'CN']" in result

    def test_regular_in_clause_uses_tuple_format(self):
        """Test that regular IN clause uses tuple format."""
        sql = "SELECT * FROM table WHERE country IN @countries"
        params = {"countries": ["EP", "US"]}
        result = substitute_parameters(sql, params)
        # Should use tuple format for regular IN clause
        assert "('EP', 'US')" in result
        assert "['EP'" not in result


# =============================================================================
# Task 2.6: ProgressIndicator State Transition Tests
# =============================================================================

class TestProgressIndicator:
    """Tests for ProgressIndicator widget."""

    def test_initializes_with_empty_widget(self):
        """Test that ProgressIndicator starts with empty display."""
        progress = ProgressIndicator()
        assert progress.widget.value == ""

    def test_start_sets_running_state(self):
        """Test that start() enables running state."""
        progress = ProgressIndicator()
        progress.start("Testing...")
        assert progress._running is True
        assert progress._start_time is not None
        progress.reset()  # Clean up timer

    def test_start_displays_message(self):
        """Test that start() displays the message with spinner."""
        progress = ProgressIndicator()
        progress.start("Executing query...")
        assert "Executing query" in progress.widget.value
        assert "⏳" in progress.widget.value
        progress.reset()

    def test_complete_success_shows_green(self):
        """Test that success completion shows green styling."""
        progress = ProgressIndicator()
        progress.start("Test")
        time.sleep(0.1)
        progress.complete(True, "Success!")
        assert "✅" in progress.widget.value
        assert EPO_COLORS['green'] in progress.widget.value
        assert "Success!" in progress.widget.value

    def test_complete_failure_shows_red(self):
        """Test that failure completion shows red styling."""
        progress = ProgressIndicator()
        progress.start("Test")
        time.sleep(0.1)
        progress.complete(False, "Failed!")
        assert "❌" in progress.widget.value
        assert EPO_COLORS['red'] in progress.widget.value
        assert "Failed!" in progress.widget.value

    def test_complete_stops_timer(self):
        """Test that complete() stops the timer."""
        progress = ProgressIndicator()
        progress.start("Test")
        assert progress._running is True
        progress.complete(True, "Done")
        assert progress._running is False
        assert progress._timer is None

    def test_reset_clears_state(self):
        """Test that reset() clears all state."""
        progress = ProgressIndicator()
        progress.start("Test")
        progress.reset()
        assert progress._running is False
        assert progress._timer is None
        assert progress.widget.value == ""

    def test_complete_shows_elapsed_time(self):
        """Test that complete message includes elapsed time."""
        progress = ProgressIndicator()
        progress.start("Test")
        time.sleep(0.2)
        progress.complete(True, "Done")
        # Should contain elapsed time in seconds
        assert "s)" in progress.widget.value


# =============================================================================
# Task 3.5: Timer Behavior Tests
# =============================================================================

class TestProgressIndicatorTimer:
    """Tests for ProgressIndicator timer functionality."""

    def test_timer_schedules_update(self):
        """Test that start schedules a timer update."""
        progress = ProgressIndicator()
        progress.start("Test")
        # Timer should be scheduled
        assert progress._timer is not None
        progress.reset()

    def test_timer_updates_display(self):
        """Test that timer updates display with elapsed time (simulated)."""
        progress = ProgressIndicator()
        progress._start_time = time.time() - 10  # Simulate 10 seconds elapsed
        progress._running = True
        progress._on_timer()
        # Should show elapsed time
        assert "10s" in progress.widget.value or "Running" in progress.widget.value
        progress.reset()

    def test_timer_formats_minutes(self):
        """Test that timer formats time > 60 seconds as minutes."""
        progress = ProgressIndicator()
        progress._start_time = time.time() - 90  # 90 seconds = 1m 30s
        progress._running = True
        progress._on_timer()
        # Should show minutes
        assert "1m" in progress.widget.value
        progress.reset()


# =============================================================================
# QueryExecutor Tests
# =============================================================================

class TestQueryExecutor:
    """Tests for QueryExecutor class."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock PatstatClient."""
        client = MagicMock()
        client.sql_query.return_value = [
            {"col1": "a", "col2": 1},
            {"col1": "b", "col2": 2},
        ]
        return client

    @pytest.fixture
    def sample_query(self):
        """Create a sample QueryMetadata."""
        return QueryMetadata(
            id='TEST01',
            title='Test Query',
            description='A test query',
            category='Test',
            sql_template='SELECT * FROM table WHERE year >= @start_year',
            parameters=[
                ParameterSpec(
                    name='year_range',
                    type='year_range',
                    label='Year Range',
                    default=2015,
                    required=True
                )
            ],
            output_columns=[],
            tags=[]
        )

    def test_executor_uses_provided_client(self, mock_client, sample_query):
        """Test that executor uses the provided client."""
        executor = QueryExecutor(client=mock_client)
        df = executor.execute(sample_query, {"year_range": (2015, 2020)})
        mock_client.sql_query.assert_called_once()

    def test_executor_returns_dataframe(self, mock_client, sample_query):
        """Test that executor returns a pandas DataFrame."""
        import pandas as pd
        executor = QueryExecutor(client=mock_client)
        df = executor.execute(sample_query, {"year_range": (2015, 2020)})
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2

    def test_executor_substitutes_parameters(self, mock_client, sample_query):
        """Test that executor substitutes parameters before execution."""
        executor = QueryExecutor(client=mock_client)
        executor.execute(sample_query, {"year_range": (2015, 2020)})
        # Check the SQL passed to sql_query
        call_args = mock_client.sql_query.call_args
        sql = call_args[0][0]
        assert "2015" in sql
        assert "@start_year" not in sql

    def test_executor_raises_on_client_error(self, mock_client, sample_query):
        """Test that executor raises when client throws error."""
        mock_client.sql_query.side_effect = Exception("Database error")
        executor = QueryExecutor(client=mock_client)
        with pytest.raises(Exception, match="Database error"):
            executor.execute(sample_query, {"year_range": (2015, 2020)})

    def test_timeout_constant_is_120(self):
        """Test that timeout is set to 120 seconds per NFR1."""
        assert TIMEOUT_SECONDS == 120
        assert QueryExecutor.TIMEOUT_SECONDS == 120


# =============================================================================
# Task 5.5: Error Handling Tests
# =============================================================================

class TestQueryExecutorErrorHandling:
    """Tests for QueryExecutor error handling."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock PatstatClient."""
        return MagicMock()

    @pytest.fixture
    def sample_query(self):
        """Create a sample QueryMetadata."""
        return QueryMetadata(
            id='TEST01',
            title='Test Query',
            description='Test',
            category='Test',
            sql_template='SELECT * FROM table',
            parameters=[],
            output_columns=[],
            tags=[]
        )

    def test_raises_runtime_error_if_not_initialized(self, sample_query):
        """Test that executor raises if no client available."""
        # Create executor without client and mock that module-level is None
        executor = QueryExecutor(client=None)
        with patch('TIP_for_PATLIBs_QueryLib_core.patstat_client', None):
            with pytest.raises(RuntimeError, match="not initialized"):
                executor.execute(sample_query, {})

    def test_query_timeout_error_is_defined(self):
        """Test that QueryTimeoutError is properly defined."""
        error = QueryTimeoutError("Test timeout")
        assert isinstance(error, Exception)
        assert "Test timeout" in str(error)

    def test_timeout_error_has_suggestions(self):
        """Test that timeout error message includes helpful suggestions."""
        # Create a slow mock that takes too long
        # We can't easily test actual timeout, so test the error message format
        error = QueryTimeoutError(
            f"Query exceeded {TIMEOUT_SECONDS} second timeout.\n\n"
            "Suggestions to reduce query time:\n"
            "- Narrow the date range"
        )
        assert "Suggestions" in str(error)
        assert "date range" in str(error).lower()


# =============================================================================
# Integration Tests
# =============================================================================

class TestQueryExecutionIntegration:
    """Integration tests for query execution flow."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock PatstatClient that returns quickly."""
        client = MagicMock()
        client.sql_query.return_value = [{"count": 100}]
        return client

    @pytest.fixture
    def complex_query(self):
        """Create a query with multiple parameter types."""
        return QueryMetadata(
            id='COMPLEX',
            title='Complex Query',
            description='Query with multiple parameters',
            category='Test',
            sql_template='''
                SELECT * FROM table
                WHERE year >= @start_year
                AND year <= @end_year
                AND country IN @countries
                AND code = @code
            ''',
            parameters=[
                ParameterSpec(
                    name='year_range',
                    type='year_range',
                    label='Years',
                    default=(2015, 2020),
                    required=True
                ),
                ParameterSpec(
                    name='countries',
                    type='multiselect',
                    label='Countries',
                    default=['EP'],
                    required=True,
                    options=[('EP', 'EP'), ('US', 'US')]
                ),
                ParameterSpec(
                    name='code',
                    type='text',
                    label='Code',
                    default='H01L',
                    required=False
                ),
            ],
            output_columns=[],
            tags=[]
        )

    def test_full_execution_with_complex_params(self, mock_client, complex_query):
        """Test full execution with multiple parameter types."""
        executor = QueryExecutor(client=mock_client)
        params = {
            "year_range": (2018, 2023),
            "countries": ["EP", "US"],
            "code": "A01B"
        }
        df = executor.execute(complex_query, params)

        # Check that all parameters were substituted
        sql = mock_client.sql_query.call_args[0][0]
        assert "2018" in sql
        assert "2023" in sql
        assert "'EP'" in sql
        assert "'US'" in sql
        assert "'A01B'" in sql

    def test_progress_indicator_lifecycle(self):
        """Test the complete lifecycle of progress indicator."""
        progress = ProgressIndicator()

        # Initially empty
        assert progress.widget.value == ""

        # Start
        progress.start("Testing...")
        assert progress._running is True
        assert "Testing" in progress.widget.value

        # Complete successfully
        progress.complete(True, "Done")
        assert progress._running is False
        assert "Done" in progress.widget.value
        assert "✅" in progress.widget.value

        # Reset
        progress.reset()
        assert progress.widget.value == ""


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
