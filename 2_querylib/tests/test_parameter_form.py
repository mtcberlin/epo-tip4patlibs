"""
Unit Tests for Parameter Form (Story 1.4)
=========================================
Tests for parameter widget factory, ParameterForm class, validation rules,
and reference data loaders.

Test Categories:
- Task 1.8: Widget factory tests for each parameter type
- Task 2.7: ParameterForm generation and validation tests
- Task 3.5: Validation rule tests
- Task 4.5: Reference data loader tests
"""

import pytest
from unittest.mock import MagicMock, patch
import ipywidgets as widgets

# Import the module under test
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from TIP_for_PATLIBs_QueryLib_core import (
    ParameterSpec,
    QueryMetadata,
    create_parameter_widget,
    ParameterForm,
    get_jurisdiction_options,
    get_wipo_field_options,
    VALIDATION_MESSAGES,
    EPO_COLORS,
)


# =============================================================================
# Task 4.5: Reference Data Loader Tests
# =============================================================================

class TestReferenceDataLoaders:
    """Tests for get_jurisdiction_options and get_wipo_field_options."""

    def test_get_jurisdiction_options_returns_list(self):
        """Test that get_jurisdiction_options returns a list."""
        options = get_jurisdiction_options()
        assert isinstance(options, list)
        assert len(options) > 0

    def test_get_jurisdiction_options_format(self):
        """Test that jurisdiction options are (display_name, code) tuples."""
        options = get_jurisdiction_options()
        for option in options:
            assert isinstance(option, tuple)
            assert len(option) == 2
            display_name, code = option
            assert isinstance(display_name, str)
            assert isinstance(code, str)
            # Code should be 2 letters
            assert len(code) == 2

    def test_get_jurisdiction_options_contains_common_jurisdictions(self):
        """Test that common jurisdictions are included."""
        options = get_jurisdiction_options()
        codes = [code for _, code in options]
        assert 'EP' in codes  # European Patent Office
        assert 'US' in codes  # United States
        assert 'DE' in codes  # Germany
        assert 'JP' in codes  # Japan
        assert 'CN' in codes  # China

    def test_get_jurisdiction_options_cached(self):
        """Test that jurisdiction options are cached."""
        options1 = get_jurisdiction_options()
        options2 = get_jurisdiction_options()
        # Should return same object (cached)
        assert options1 is options2

    def test_get_wipo_field_options_returns_list(self):
        """Test that get_wipo_field_options returns a list."""
        options = get_wipo_field_options()
        assert isinstance(options, list)
        assert len(options) == 35  # WIPO has exactly 35 technology fields

    def test_get_wipo_field_options_format(self):
        """Test that WIPO options are (field_name, field_number) tuples."""
        options = get_wipo_field_options()
        for option in options:
            assert isinstance(option, tuple)
            assert len(option) == 2
            field_name, field_number = option
            assert isinstance(field_name, str)
            assert isinstance(field_number, int)
            assert 1 <= field_number <= 35

    def test_get_wipo_field_options_contains_expected_fields(self):
        """Test that expected WIPO fields are included."""
        options = get_wipo_field_options()
        field_names = [name for name, _ in options]
        assert 'Electrical machinery' in field_names
        assert 'Computer technology' in field_names
        assert 'Biotechnology' in field_names
        assert 'Civil engineering' in field_names

    def test_get_wipo_field_options_cached(self):
        """Test that WIPO field options are cached."""
        options1 = get_wipo_field_options()
        options2 = get_wipo_field_options()
        assert options1 is options2


# =============================================================================
# Task 1.8: Widget Factory Tests
# =============================================================================

class TestCreateParameterWidget:
    """Tests for create_parameter_widget factory function."""

    def test_year_range_creates_int_range_slider(self):
        """Test that year_range type creates IntRangeSlider."""
        spec = ParameterSpec(
            name='years',
            type='year_range',
            label='Year Range',
            default=2015,
            required=True
        )
        widget = create_parameter_widget(spec)
        assert isinstance(widget, widgets.IntRangeSlider)
        assert widget.min == 1980
        assert widget.max == 2024

    def test_year_range_uses_default_start_value(self):
        """Test that year_range uses default as start value."""
        spec = ParameterSpec(
            name='years',
            type='year_range',
            label='Year Range',
            default=2010,
            required=True
        )
        widget = create_parameter_widget(spec)
        assert widget.value[0] == 2010
        assert widget.value[1] == 2024

    def test_year_range_handles_tuple_default(self):
        """Test that year_range handles tuple default value."""
        spec = ParameterSpec(
            name='years',
            type='year_range',
            label='Year Range',
            default=(2000, 2020),
            required=True
        )
        widget = create_parameter_widget(spec)
        assert widget.value == (2000, 2020)

    def test_multiselect_creates_select_multiple(self):
        """Test that multiselect type creates SelectMultiple."""
        spec = ParameterSpec(
            name='countries',
            type='multiselect',
            label='Countries',
            default=['EP', 'US'],
            required=True,
            options=[('European (EP)', 'EP'), ('United States (US)', 'US'), ('Germany (DE)', 'DE')]
        )
        widget = create_parameter_widget(spec)
        assert isinstance(widget, widgets.SelectMultiple)

    def test_multiselect_uses_jurisdiction_options_when_none_provided(self):
        """Test that multiselect uses jurisdiction options as fallback."""
        spec = ParameterSpec(
            name='countries',
            type='multiselect',
            label='Countries',
            default=[],
            required=True,
            options=None
        )
        widget = create_parameter_widget(spec)
        assert isinstance(widget, widgets.SelectMultiple)
        # Should have jurisdiction options loaded
        assert len(widget.options) > 0

    def test_select_creates_dropdown(self):
        """Test that select type creates Dropdown."""
        spec = ParameterSpec(
            name='category',
            type='select',
            label='Category',
            default='A',
            required=True,
            options=[('Option A', 'A'), ('Option B', 'B')]
        )
        widget = create_parameter_widget(spec)
        assert isinstance(widget, widgets.Dropdown)

    def test_text_creates_text_input(self):
        """Test that text type creates Text widget."""
        spec = ParameterSpec(
            name='ipc_code',
            type='text',
            label='IPC Code',
            default='H01L',
            required=False
        )
        widget = create_parameter_widget(spec)
        assert isinstance(widget, widgets.Text)
        assert widget.value == 'H01L'

    def test_text_has_placeholder(self):
        """Test that text widget has appropriate placeholder."""
        spec = ParameterSpec(
            name='ipc_code',
            type='text',
            label='IPC Code',
            default='',
            required=False
        )
        widget = create_parameter_widget(spec)
        assert 'ipc code' in widget.placeholder.lower()

    def test_slider_creates_int_slider(self):
        """Test that slider type creates IntSlider."""
        spec = ParameterSpec(
            name='top_n',
            type='slider',
            label='Top N',
            default=10,
            required=True
        )
        widget = create_parameter_widget(spec)
        assert isinstance(widget, widgets.IntSlider)
        assert widget.value == 10
        assert widget.min == 1
        assert widget.max == 100

    def test_unknown_type_falls_back_to_text(self):
        """Test that unknown parameter type falls back to Text widget."""
        spec = ParameterSpec(
            name='unknown',
            type='unknown_type',
            label='Unknown',
            default='test',
            required=False
        )
        widget = create_parameter_widget(spec)
        assert isinstance(widget, widgets.Text)


# =============================================================================
# Task 2.7: ParameterForm Tests
# =============================================================================

class TestParameterForm:
    """Tests for ParameterForm class."""

    @pytest.fixture
    def sample_query_with_params(self):
        """Create a sample QueryMetadata with parameters."""
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
                ),
                ParameterSpec(
                    name='country',
                    type='text',
                    label='Country',
                    default='DE',
                    required=False
                ),
            ],
            output_columns=[],
            tags=['test']
        )

    @pytest.fixture
    def query_without_params(self):
        """Create a sample QueryMetadata without parameters."""
        return QueryMetadata(
            id='TEST02',
            title='No Params Query',
            description='A query without parameters',
            category='Test',
            sql_template='SELECT COUNT(*) FROM table',
            parameters=[],
            output_columns=[],
            tags=['test']
        )

    def test_form_initializes_empty(self):
        """Test that ParameterForm can be initialized without query."""
        form = ParameterForm()
        assert form._query is None
        assert form.execute_button.disabled is True

    def test_form_initializes_with_query(self, sample_query_with_params):
        """Test that ParameterForm initializes with query."""
        form = ParameterForm(sample_query_with_params)
        assert form._query is not None
        assert form.execute_button.disabled is False
        assert len(form._widgets) == 2

    def test_form_update_with_query(self, sample_query_with_params):
        """Test that form can be updated with new query."""
        form = ParameterForm()
        form.update(sample_query_with_params)
        assert form._query is not None
        assert len(form._widgets) == 2

    def test_form_update_with_none_clears_form(self, sample_query_with_params):
        """Test that updating with None clears the form."""
        form = ParameterForm(sample_query_with_params)
        form.update(None)
        assert form._query is None
        assert len(form._widgets) == 0
        assert form.execute_button.disabled is True

    def test_form_without_params_shows_message(self, query_without_params):
        """Test that query without params shows appropriate message."""
        form = ParameterForm(query_without_params)
        assert form.execute_button.disabled is False
        # Form container should have "No parameters required" message
        assert len(form._form_container.children) > 0

    def test_get_values_returns_dict(self, sample_query_with_params):
        """Test that get_values returns parameter values as dict."""
        form = ParameterForm(sample_query_with_params)
        values = form.get_values()
        assert isinstance(values, dict)
        assert 'year_range' in values
        assert 'country' in values

    def test_get_values_returns_correct_types(self, sample_query_with_params):
        """Test that get_values returns correct value types."""
        form = ParameterForm(sample_query_with_params)
        values = form.get_values()
        # year_range should be tuple
        assert isinstance(values['year_range'], tuple)
        # text should be string
        assert isinstance(values['country'], str)

    def test_validate_returns_tuple(self, sample_query_with_params):
        """Test that validate returns (bool, list) tuple."""
        form = ParameterForm(sample_query_with_params)
        result = form.validate()
        assert isinstance(result, tuple)
        assert len(result) == 2
        is_valid, errors = result
        assert isinstance(is_valid, bool)
        assert isinstance(errors, list)

    def test_validate_passes_for_valid_form(self, sample_query_with_params):
        """Test that validation passes for properly filled form."""
        form = ParameterForm(sample_query_with_params)
        is_valid, errors = form.validate()
        assert is_valid is True
        assert len(errors) == 0

    def test_highlight_invalid_adds_border(self, sample_query_with_params):
        """Test that highlight_invalid adds red border to widget."""
        form = ParameterForm(sample_query_with_params)
        form.highlight_invalid('year_range')
        widget = form._widgets['year_range']
        assert EPO_COLORS['red'] in widget.layout.border


# =============================================================================
# Task 3.5: Validation Rule Tests
# =============================================================================

class TestValidationRules:
    """Tests for parameter validation rules."""

    @pytest.fixture
    def form_with_required_text(self):
        """Create form with required text parameter."""
        query = QueryMetadata(
            id='TEST',
            title='Test',
            description='Test',
            category='Test',
            sql_template='SELECT * WHERE code = @code',
            parameters=[
                ParameterSpec(
                    name='code',
                    type='text',
                    label='Code',
                    default='',
                    required=True
                )
            ],
            output_columns=[],
            tags=[]
        )
        return ParameterForm(query)

    @pytest.fixture
    def form_with_year_range(self):
        """Create form with year_range parameter."""
        query = QueryMetadata(
            id='TEST',
            title='Test',
            description='Test',
            category='Test',
            sql_template='SELECT * WHERE year >= @start',
            parameters=[
                ParameterSpec(
                    name='years',
                    type='year_range',
                    label='Year Range',
                    default=2015,
                    required=True
                )
            ],
            output_columns=[],
            tags=[]
        )
        return ParameterForm(query)

    @pytest.fixture
    def form_with_required_multiselect(self):
        """Create form with required multiselect parameter."""
        query = QueryMetadata(
            id='TEST',
            title='Test',
            description='Test',
            category='Test',
            sql_template='SELECT * WHERE country IN (@countries)',
            parameters=[
                ParameterSpec(
                    name='countries',
                    type='multiselect',
                    label='Countries',
                    default=[],
                    required=True,
                    options=[('EP', 'EP'), ('US', 'US'), ('DE', 'DE')]
                )
            ],
            output_columns=[],
            tags=[]
        )
        return ParameterForm(query)

    def test_required_empty_text_fails_validation(self, form_with_required_text):
        """Test that empty required text field fails validation."""
        # Widget should have empty value by default
        form_with_required_text._widgets['code'].value = ''
        is_valid, errors = form_with_required_text.validate()
        assert is_valid is False
        assert len(errors) == 1
        assert 'required' in errors[0].lower()

    def test_required_filled_text_passes_validation(self, form_with_required_text):
        """Test that filled required text field passes validation."""
        form_with_required_text._widgets['code'].value = 'H01L'
        is_valid, errors = form_with_required_text.validate()
        assert is_valid is True
        assert len(errors) == 0

    def test_year_range_widget_prevents_invalid_range(self, form_with_year_range):
        """Test that IntRangeSlider widget itself prevents start > end.

        The ipywidgets IntRangeSlider validates at the widget level that
        lower <= upper, so invalid ranges cannot be set programmatically.
        This is correct behavior - validation happens at the UI level.
        """
        import traitlets
        # Attempting to set start > end should raise TraitError
        with pytest.raises(traitlets.TraitError):
            form_with_year_range._widgets['years'].value = (2020, 2010)

    def test_year_range_valid_passes(self, form_with_year_range):
        """Test that valid year range passes validation."""
        form_with_year_range._widgets['years'].value = (2010, 2020)
        is_valid, errors = form_with_year_range.validate()
        assert is_valid is True

    def test_required_empty_multiselect_fails(self, form_with_required_multiselect):
        """Test that empty required multiselect fails validation."""
        form_with_required_multiselect._widgets['countries'].value = ()
        is_valid, errors = form_with_required_multiselect.validate()
        assert is_valid is False
        assert len(errors) >= 1

    def test_required_multiselect_with_selection_passes(self, form_with_required_multiselect):
        """Test that multiselect with selection passes validation."""
        form_with_required_multiselect._widgets['countries'].value = ('EP',)
        is_valid, errors = form_with_required_multiselect.validate()
        assert is_valid is True

    def test_validation_messages_exist(self):
        """Test that all expected validation message templates exist."""
        assert 'required' in VALIDATION_MESSAGES
        assert 'year_range_invalid' in VALIDATION_MESSAGES
        assert 'year_out_of_bounds' in VALIDATION_MESSAGES
        assert 'empty_multiselect' in VALIDATION_MESSAGES

    def test_validation_messages_have_label_placeholder(self):
        """Test that validation messages have {label} placeholder."""
        for key, msg in VALIDATION_MESSAGES.items():
            assert '{label}' in msg, f"Message '{key}' missing {{label}} placeholder"


# =============================================================================
# Integration Tests
# =============================================================================

class TestParameterFormIntegration:
    """Integration tests for ParameterForm with QueryMetadata."""

    def test_form_works_with_real_query_structure(self):
        """Test form works with query structure matching TIP_for_PATLIBs_QueryLib_queries.py."""
        query = QueryMetadata(
            id='Q01',
            title='Patent Applications by Year',
            description='Analyze patent application trends over time',
            category='Trends',
            sql_template='''
                SELECT filing_year, COUNT(*) as count
                FROM tls201_appln
                WHERE filing_year BETWEEN @start_year AND @end_year
                AND appln_auth = @authority
                GROUP BY filing_year
            ''',
            parameters=[
                ParameterSpec(
                    name='year_range',
                    type='year_range',
                    label='Filing Years',
                    default=2015,
                    required=True
                ),
                ParameterSpec(
                    name='authority',
                    type='select',
                    label='Patent Authority',
                    default='EP',
                    required=True,
                    options=[('EP', 'EP'), ('US', 'US'), ('DE', 'DE')]
                ),
                ParameterSpec(
                    name='top_n',
                    type='slider',
                    label='Top N Results',
                    default=20,
                    required=False
                ),
            ],
            output_columns=['filing_year', 'count'],
            tags=['PATLIB', 'TRENDS']
        )

        form = ParameterForm(query)

        # Verify all widgets created
        assert len(form._widgets) == 3
        assert 'year_range' in form._widgets
        assert 'authority' in form._widgets
        assert 'top_n' in form._widgets

        # Verify widget types
        assert isinstance(form._widgets['year_range'], widgets.IntRangeSlider)
        assert isinstance(form._widgets['authority'], widgets.Dropdown)
        assert isinstance(form._widgets['top_n'], widgets.IntSlider)

        # Verify validation works
        is_valid, errors = form.validate()
        assert is_valid is True

        # Verify get_values works
        values = form.get_values()
        assert 'year_range' in values
        assert 'authority' in values
        assert 'top_n' in values


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
