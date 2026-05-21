# Story 1.5: Query Execution with Progress

Status: review

## Story

As a **PATLIB staff member**,
I want **to see progress while queries run**,
so that **I know the system is working and can estimate wait time**.

## Acceptance Criteria

### AC1: Execute Button Behavior
**Given** I have configured all required parameters
**When** I click "Execute Query"
**Then** the Execute button disables to prevent double-submission
**And** a progress indicator appears with spinner emoji

### AC2: Progress Updates
**Given** a query is executing
**When** more than 5 seconds have passed
**Then** the progress indicator updates with elapsed time
**And** updates continue every 5 seconds (NFR5)

### AC3: Success Completion
**Given** a query completes successfully
**When** results are ready
**Then** the progress indicator shows success
**And** the results panel activates
**And** execution time is displayed

### AC4: Timeout Handling
**Given** a query exceeds 120 seconds (NFR1)
**When** timeout is reached
**Then** the query is cancelled gracefully
**And** a user-friendly timeout message displays
**And** suggestions for reducing scope are provided

### AC5: Error Handling
**Given** a query fails with an error
**When** the error is caught
**Then** a user-friendly error message displays (FR12)
**And** technical details print below for debugging
**And** the Execute button re-enables

## Tasks / Subtasks

- [x] Task 1: Create QueryExecutor class (AC: 1, 3, 4, 5)
  - [x] 1.1: Create QueryExecutor class in querylib_core.py
  - [x] 1.2: Add `execute(query: QueryMetadata, params: dict)` method
  - [x] 1.3: Implement SQL parameter substitution (@param -> value)
  - [x] 1.4: Execute via PatstatClient.sql_query() (from patstat_client)
  - [x] 1.5: Add timeout handling (120 second limit)
  - [x] 1.6: Return DataFrame on success, raise on error
  - [x] 1.7: Add unit tests for parameter substitution

- [x] Task 2: Create ProgressIndicator widget (AC: 1, 2)
  - [x] 2.1: Create ProgressIndicator class using ipywidgets.HTML
  - [x] 2.2: Implement `start()` method showing spinner
  - [x] 2.3: Implement `update_elapsed(seconds)` method
  - [x] 2.4: Implement `complete(success: bool, message: str)` method
  - [x] 2.5: Use EPO_COLORS for styling (blue for running, green for success, red for error)
  - [x] 2.6: Add unit tests for state transitions

- [x] Task 3: Implement elapsed time tracking (AC: 2)
  - [x] 3.1: Use threading.Timer for periodic updates
  - [x] 3.2: Update progress every 5 seconds (NFR5)
  - [x] 3.3: Format elapsed time as "Running... (Xs)" or "Running... (Xm Ys)"
  - [x] 3.4: Cancel timer when query completes
  - [x] 3.5: Add unit tests for timer behavior

- [x] Task 4: Implement timeout and cancellation (AC: 4)
  - [x] 4.1: Implement 120-second timeout (NFR1)
  - [x] 4.2: Create user-friendly timeout message with suggestions
  - [x] 4.3: Suggestions: "Try narrowing the date range" or "Reduce number of jurisdictions"
  - [x] 4.4: Ensure clean cancellation (no zombie queries)
  - [x] 4.5: Re-enable Execute button after timeout

- [x] Task 5: Implement error handling (AC: 5)
  - [x] 5.1: Catch all exceptions during query execution
  - [x] 5.2: Display user-friendly error using display_error() from Story 1.1
  - [x] 5.3: Log technical details (exception message, traceback)
  - [x] 5.4: Re-enable Execute button after error
  - [x] 5.5: Add unit tests for error handling paths

- [x] Task 6: Wire up Execute button flow (AC: 1-5)
  - [x] 6.1: Create `on_execute_click()` handler
  - [x] 6.2: Validate parameters via ParameterForm.validate()
  - [x] 6.3: If invalid, show validation errors and return
  - [x] 6.4: If valid, disable button and start progress
  - [x] 6.5: Execute query asynchronously (threading)
  - [x] 6.6: On complete, update progress and show results (Story 1.6)
  - [x] 6.7: On error/timeout, show error and re-enable button
  - [x] 6.8: Manual testing of full flow

## Dev Notes

### Critical Architecture Requirements

**Source:** [architecture.md - NFR1, NFR5, NFR6, NFR7]
- NFR1: Standard queries complete within 120 seconds (timeout)
- NFR5: Progress indicators update at least every 5 seconds
- NFR6: Notebooks recover gracefully from interrupted queries
- NFR7: Error messages are user-friendly and suggest next actions

**Source:** [architecture.md - Data Access Boundary]
- All PATSTAT access via `PatstatClient.sql_query()`
- No direct BigQuery client usage

**Source:** [epics.md - Story 1.5 Technical Notes]
- Uses PatstatClient for execution (FR39, FR40)
- Progress indicator pattern from Architecture (ipywidgets HTML)
- Covers FR5, FR11, FR12, FR41
- Handles NFR6 (graceful recovery)

### SQL Parameter Substitution

```python
def substitute_parameters(sql_template: str, params: dict) -> str:
    """
    Replace @param placeholders with actual values.

    Handles:
    - @year_start, @year_end: INT64
    - @jurisdictions: ARRAY<STRING> -> ['EP', 'US'] becomes ('EP', 'US')
    - @tech_field: INT64
    - @text_param: STRING with proper quoting
    """
    result = sql_template

    for param_name, value in params.items():
        placeholder = f"@{param_name}"

        if isinstance(value, list):
            # Convert list to SQL array literal
            quoted = [f"'{v}'" for v in value]
            sql_value = f"({', '.join(quoted)})"
        elif isinstance(value, str):
            # Quote strings
            sql_value = f"'{value}'"
        elif isinstance(value, tuple) and len(value) == 2:
            # Year range - substitute both
            result = result.replace("@year_start", str(value[0]))
            result = result.replace("@year_end", str(value[1]))
            continue
        else:
            sql_value = str(value)

        result = result.replace(placeholder, sql_value)

    return result
```

### Query Execution Pattern

```python
import pandas as pd
import threading
import time

class QueryExecutor:
    TIMEOUT_SECONDS = 120  # NFR1

    def __init__(self, patstat_client):
        self.client = patstat_client

    def execute(self, query: QueryMetadata, params: dict) -> pd.DataFrame:
        """
        Execute query with parameters.

        Args:
            query: QueryMetadata with sql_template
            params: Dict of parameter values

        Returns:
            pandas DataFrame with results

        Raises:
            TimeoutError: If query exceeds 120 seconds
            QueryError: If query fails
        """
        # Substitute parameters
        sql = substitute_parameters(query.sql_template, params)

        # Execute with timeout
        result = [None]
        error = [None]

        def run_query():
            try:
                result[0] = self.client.sql_query(sql)
            except Exception as e:
                error[0] = e

        thread = threading.Thread(target=run_query)
        thread.start()
        thread.join(timeout=self.TIMEOUT_SECONDS)

        if thread.is_alive():
            raise TimeoutError(
                f"Query exceeded {self.TIMEOUT_SECONDS} second timeout. "
                "Try narrowing your search criteria."
            )

        if error[0]:
            raise error[0]

        return result[0]
```

### Progress Indicator Pattern

```python
class ProgressIndicator:
    """Progress indicator with elapsed time tracking."""

    def __init__(self):
        self._widget = widgets.HTML(value="")
        self._start_time = None
        self._timer = None
        self._running = False

    @property
    def widget(self):
        return self._widget

    def start(self, message: str = "Executing query..."):
        """Start progress indicator."""
        self._start_time = time.time()
        self._running = True
        self._update_display(message, "running")
        self._schedule_update()

    def _schedule_update(self):
        """Schedule next elapsed time update."""
        if self._running:
            self._timer = threading.Timer(5.0, self._on_timer)  # NFR5: every 5 seconds
            self._timer.start()

    def _on_timer(self):
        """Update elapsed time display."""
        if self._running:
            elapsed = int(time.time() - self._start_time)
            if elapsed < 60:
                time_str = f"{elapsed}s"
            else:
                time_str = f"{elapsed // 60}m {elapsed % 60}s"
            self._update_display(f"Running... ({time_str})", "running")
            self._schedule_update()

    def complete(self, success: bool, message: str):
        """Mark progress as complete."""
        self._running = False
        if self._timer:
            self._timer.cancel()
        elapsed = int(time.time() - self._start_time)
        status = "success" if success else "error"
        full_message = f"{message} ({elapsed}s)"
        self._update_display(full_message, status)

    def _update_display(self, message: str, status: str):
        """Update the HTML widget display."""
        colors = {
            "running": (EPO_COLORS['primary_blue'], "white", EPO_COLORS['light_gray']),
            "success": (EPO_COLORS['green'], "white", "#E8F5E9"),
            "error": (EPO_COLORS['red'], "white", EPO_COLORS['error_bg']),
        }
        border_color, text_color, bg_color = colors.get(status, colors["running"])

        emoji = {"running": "", "success": "check", "error": "error"}[status]

        self._widget.value = f'''
        <div style="padding: 12px; border-left: 4px solid {border_color};
                    background-color: {bg_color}; margin: 8px 0;">
            <span style="color: {border_color}; font-weight: bold;">
                {message}
            </span>
        </div>
        '''
```

### Error Handling Pattern

From Story 1.1 `display_error()`:

```python
def on_execute_click(b):
    # Validate first
    is_valid, errors = parameter_form.validate()
    if not is_valid:
        for error in errors:
            display_error("Validation Error", error)
        return

    # Disable button
    execute_button.disabled = True
    progress.start("Executing query...")

    try:
        # Execute
        df = executor.execute(selected_query, parameter_form.get_values())
        progress.complete(True, f"Found {len(df)} results")
        display_results(df)  # Story 1.6

    except TimeoutError as e:
        progress.complete(False, "Query timed out")
        display_error(
            "Query Timeout",
            "The query took too long to complete. Please try:\n"
            "- Narrowing the date range\n"
            "- Selecting fewer jurisdictions\n"
            "- Using more specific search criteria",
            details=str(e)
        )

    except Exception as e:
        progress.complete(False, "Query failed")
        display_error(
            "Query Error",
            "Unable to execute the query. Please check your parameters and try again.",
            details=str(e)
        )

    finally:
        execute_button.disabled = False
```

### Timeout Message Template

```python
TIMEOUT_MESSAGE = """
The query exceeded the 120-second time limit.

**Suggestions to reduce query time:**
- Narrow the date range (e.g., last 5 years instead of 20)
- Select fewer jurisdictions
- Use more specific technology field filters
- Try a simpler query first to verify your criteria

If this query is essential, contact your administrator for options.
"""
```

### FRs Covered by This Story

| FR | Description | Implementation |
|----|-------------|----------------|
| FR5 | Users can execute selected query with configured parameters | QueryExecutor.execute() |
| FR11 | System provides progress indicator during execution | ProgressIndicator widget |
| FR12 | System displays user-friendly error messages when queries fail | Error handling + display_error() |
| FR39 | System connects to PATSTAT via PatstatClient | PatstatClient.sql_query() |
| FR40 | System executes queries against BigQuery backend | Via PatstatClient |
| FR41 | System handles query timeouts gracefully | 120s timeout with suggestions |

### NFRs Covered by This Story

| NFR | Description | Implementation |
|-----|-------------|----------------|
| NFR1 | Standard queries complete within 120 seconds | Timeout enforcement |
| NFR5 | Progress indicators update at least every 5 seconds | Timer-based updates |
| NFR6 | Notebooks recover gracefully from interrupted queries | Clean error handling |
| NFR7 | Error messages are user-friendly and suggest next actions | Timeout suggestions |

### Library/Framework Requirements

| Package | Version | Purpose | Pre-installed |
|---------|---------|---------|---------------|
| ipywidgets | latest | Progress widget | Yes (TIP) |
| threading | stdlib | Async execution, timers | Yes |
| time | stdlib | Elapsed time tracking | Yes |
| pandas | latest | Result DataFrames | Yes (TIP) |

### Testing Approach

1. **Unit Tests:**
   - Test SQL parameter substitution (various types)
   - Test ProgressIndicator state transitions
   - Test timeout detection
   - Test error handling paths

2. **Integration Tests:**
   - Mock PatstatClient for controlled testing
   - Test full execute flow with mock

3. **Manual Testing in TIP:**
   - Execute a fast query - verify progress and results
   - Watch progress update every 5 seconds on longer query
   - Test with intentionally invalid SQL - verify error handling
   - (If possible) Test timeout with very large query

### Project Structure Notes

**Files to modify:**
```
tip4patlibs/
├── querylib_core.py                # ADD: QueryExecutor, ProgressIndicator, substitute_parameters
├── TIP_for_PATLIBs_QueryLib_for_PATLIBs.ipynb  # MODIFY: Wire up execution
└── tests/test_query_executor.py    # NEW: Unit tests for execution
```

### Dependencies on Previous Stories

- **Story 1.1:** display_error(), show_progress() patterns, patstat_client
- **Story 1.2:** QueryMetadata with sql_template
- **Story 1.3:** QueryBrowser provides selected query
- **Story 1.4:** ParameterForm.validate() and get_values()

### References

- [Source: _bmad-output/planning-artifacts/architecture.md#Data-Access-Boundary]
- [Source: _bmad-output/planning-artifacts/architecture.md#NFR1-NFR5]
- [Source: _bmad-output/planning-artifacts/epics.md#Story-1.5]
- [Source: _bmad-output/implementation-artifacts/1-1-initialize-querylib-core-module.md#Error-Handling-Pattern]
- [Source: querylib_core.py - patstat_client, display_error]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

None - implementation proceeded without errors.

### Completion Notes List

- Implemented `substitute_parameters()` function handling string, integer, list, and year_range tuple parameters with proper SQL quoting and IN clause formatting
- Created `ProgressIndicator` class with start(), complete(), reset() methods, timer-based elapsed time updates every 5 seconds (NFR5), and EPO-colored styling (blue running, green success, red error)
- Created `QueryExecutor` class with execute() method that substitutes parameters, runs query via PatstatClient in background thread, and enforces 120-second timeout (NFR1)
- Implemented `QueryTimeoutError` exception with user-friendly message including suggestions for reducing query scope
- Updated `create_query_browser()` factory to include ProgressIndicator, QueryExecutor, and full execution flow with on_results callback
- Added results_output Output widget for displaying query results
- Full error handling: validation errors, timeout errors, and query execution errors all display user-friendly messages and re-enable Execute button
- Created comprehensive test suite with 30 tests covering parameter substitution, progress indicator states, timer behavior, executor functionality, and error handling

### File List

_Files created/modified during implementation:_
- [x] `querylib_core.py` - MODIFIED (added QueryExecutor, ProgressIndicator, substitute_parameters, QueryTimeoutError, TIMEOUT_SECONDS, updated create_query_browser with execution flow)
- [x] `tests/test_query_executor.py` - NEW (30 unit tests)

## Change Log

- 2026-02-01: Story 1.5 implementation complete - all 6 tasks implemented with 30 passing tests
