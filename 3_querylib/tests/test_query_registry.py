"""
Tests for Query Registry and Categorization (Story 1.2)

Tests the QueryMetadata, ParameterSpec, and QueryRegistry classes
that manage the query collection for the Query Library notebook.
"""

import unittest
from typing import List

# Import classes under test
from TIP_for_PATLIBs_QueryLib_core import (
    QueryMetadata,
    ParameterSpec,
    QueryRegistry,
    QUERY_CATEGORIES,
)


class TestParameterSpec(unittest.TestCase):
    """Test ParameterSpec dataclass."""

    def test_create_required_parameter(self):
        """Test creating a required parameter specification."""
        param = ParameterSpec(
            name="year_start",
            type="year",
            label="Start Year",
            default=2015,
            required=True,
        )
        self.assertEqual(param.name, "year_start")
        self.assertEqual(param.type, "year")
        self.assertEqual(param.label, "Start Year")
        self.assertEqual(param.default, 2015)
        self.assertTrue(param.required)
        self.assertIsNone(param.options)

    def test_create_optional_parameter_with_options(self):
        """Test creating an optional parameter with dropdown options."""
        param = ParameterSpec(
            name="jurisdiction",
            type="select",
            label="Patent Office",
            default="EP",
            required=False,
            options=["EP", "US", "CN", "DE"],
        )
        self.assertEqual(param.name, "jurisdiction")
        self.assertEqual(param.type, "select")
        self.assertFalse(param.required)
        self.assertEqual(param.options, ["EP", "US", "CN", "DE"])

    def test_parameter_to_dict(self):
        """Test converting parameter to dictionary."""
        param = ParameterSpec(
            name="top_n",
            type="slider",
            label="Number of Results",
            default=20,
            required=True,
        )
        param_dict = param.to_dict()
        self.assertIsInstance(param_dict, dict)
        self.assertEqual(param_dict["name"], "top_n")
        self.assertEqual(param_dict["type"], "slider")


class TestQueryMetadata(unittest.TestCase):
    """Test QueryMetadata dataclass."""

    def test_create_query_metadata(self):
        """Test creating complete query metadata."""
        query = QueryMetadata(
            id="Q01",
            title="Country Patent Activity",
            description="Analyzes patent filing activity by country.",
            category="Regional",
            sql_template="SELECT country, COUNT(*) FROM patents WHERE year >= @year_start GROUP BY country",
            parameters=[
                ParameterSpec("year_start", "year", "Start Year", 2015, True),
            ],
            output_columns=["country", "patent_count"],
            tags=["PATLIB", "REGIONAL"],
        )
        self.assertEqual(query.id, "Q01")
        self.assertEqual(query.title, "Country Patent Activity")
        self.assertEqual(query.category, "Regional")
        self.assertEqual(len(query.parameters), 1)
        self.assertEqual(query.output_columns, ["country", "patent_count"])
        self.assertIn("PATLIB", query.tags)

    def test_query_without_parameters(self):
        """Test creating query without parameters (static query)."""
        query = QueryMetadata(
            id="Q00",
            title="Database Statistics",
            description="Overview of PATSTAT database.",
            category="Trends",
            sql_template="SELECT COUNT(*) FROM tls201_appln",
            parameters=[],
            output_columns=["total_count"],
            tags=["PATLIB"],
        )
        self.assertEqual(query.parameters, [])

    def test_query_to_dict(self):
        """Test converting query metadata to dictionary."""
        query = QueryMetadata(
            id="Q02",
            title="Technology Fields",
            description="Most active technology fields.",
            category="Technology Fields",
            sql_template="SELECT field, COUNT(*) FROM tech GROUP BY field",
            parameters=[],
            output_columns=["field", "count"],
            tags=["BUSINESS"],
        )
        query_dict = query.to_dict()
        self.assertIsInstance(query_dict, dict)
        self.assertEqual(query_dict["id"], "Q02")
        self.assertEqual(query_dict["category"], "Technology Fields")


class TestQueryCategories(unittest.TestCase):
    """Test QUERY_CATEGORIES constant."""

    def test_categories_exist(self):
        """Test that required categories are defined."""
        required_categories = [
            "Trends",
            "Competitors",
            "Regional",
            "Technology",
        ]
        for category in required_categories:
            self.assertIn(category, QUERY_CATEGORIES,
                f"Category '{category}' not found in QUERY_CATEGORIES")

    def test_categories_have_descriptions(self):
        """Test that each category has a description."""
        for category, info in QUERY_CATEGORIES.items():
            self.assertIn("description", info,
                f"Category '{category}' missing description")
            self.assertIsInstance(info["description"], str)


class TestQueryRegistry(unittest.TestCase):
    """Test QueryRegistry class."""

    def setUp(self):
        """Set up registry for tests."""
        self.registry = QueryRegistry()

    def test_registry_initialization(self):
        """Test that registry initializes with queries."""
        self.assertIsNotNone(self.registry)
        queries = self.registry.get_all_queries()
        self.assertIsInstance(queries, list)
        self.assertGreater(len(queries), 0, "Registry should have at least one query")

    def test_get_all_queries_returns_query_metadata(self):
        """Test that get_all_queries returns QueryMetadata instances."""
        queries = self.registry.get_all_queries()
        for query in queries:
            self.assertIsInstance(query, QueryMetadata)

    def test_get_query_by_id(self):
        """Test retrieving a specific query by ID."""
        query = self.registry.get_query("Q01")
        self.assertIsNotNone(query)
        self.assertEqual(query.id, "Q01")
        self.assertIsInstance(query, QueryMetadata)

    def test_get_nonexistent_query_returns_none(self):
        """Test that getting nonexistent query returns None."""
        query = self.registry.get_query("QXXX_INVALID")
        self.assertIsNone(query)

    def test_get_queries_by_category(self):
        """Test retrieving queries by category."""
        regional_queries = self.registry.get_queries_by_category("Regional")
        self.assertIsInstance(regional_queries, list)
        for query in regional_queries:
            self.assertEqual(query.category, "Regional")

    def test_get_categories(self):
        """Test retrieving list of categories."""
        categories = self.registry.get_categories()
        self.assertIsInstance(categories, list)
        self.assertIn("Regional", categories)
        self.assertIn("Trends", categories)

    def test_search_queries_by_keyword(self):
        """Test searching queries by keyword in title/description."""
        results = self.registry.search_queries("patent")
        self.assertIsInstance(results, list)
        # At least some queries should mention "patent"
        self.assertGreater(len(results), 0)

    def test_search_queries_case_insensitive(self):
        """Test that search is case-insensitive."""
        results_lower = self.registry.search_queries("country")
        results_upper = self.registry.search_queries("COUNTRY")
        # Both searches should return same results
        self.assertEqual(len(results_lower), len(results_upper))

    def test_search_queries_by_tag(self):
        """Test searching queries by tag."""
        results = self.registry.search_queries("PATLIB")
        self.assertIsInstance(results, list)
        for query in results:
            self.assertIn("PATLIB", query.tags)

    def test_each_category_has_minimum_queries(self):
        """Test that each category has at least 2 queries (AC2)."""
        categories = self.registry.get_categories()
        for category in categories:
            queries = self.registry.get_queries_by_category(category)
            self.assertGreaterEqual(len(queries), 2,
                f"Category '{category}' has fewer than 2 queries")

    def test_all_queries_have_required_fields(self):
        """Test that all queries have required metadata fields (AC3)."""
        queries = self.registry.get_all_queries()
        for query in queries:
            self.assertIsNotNone(query.id, f"Query missing id")
            self.assertIsNotNone(query.title, f"Query {query.id} missing title")
            self.assertIsNotNone(query.description, f"Query {query.id} missing description")
            self.assertIsNotNone(query.category, f"Query {query.id} missing category")
            self.assertIsNotNone(query.sql_template, f"Query {query.id} missing sql_template")
            self.assertIsNotNone(query.output_columns, f"Query {query.id} missing output_columns")
            self.assertIsNotNone(query.tags, f"Query {query.id} missing tags")
            self.assertIsInstance(query.parameters, list, f"Query {query.id} parameters not a list")

    def test_query_count_matches_expected(self):
        """Test that registry has expected number of queries (42 from TIP_for_PATLIBs_QueryLib_queries.py)."""
        queries = self.registry.get_all_queries()
        self.assertEqual(len(queries), 42,
            f"Expected 42 queries, found {len(queries)}")


class TestQueryRegistryIntegration(unittest.TestCase):
    """Integration tests for QueryRegistry with actual query data from TIP_for_PATLIBs_QueryLib_queries.py."""

    def setUp(self):
        """Set up registry for tests."""
        self.registry = QueryRegistry()

    def test_q01_database_statistics_exists(self):
        """Test Q01: Database Statistics query exists with correct metadata."""
        query = self.registry.get_query("Q01")
        self.assertIsNotNone(query)
        self.assertEqual(query.category, "Trends")
        self.assertIn("PATLIB", query.tags)

    def test_q02_patent_offices_exists(self):
        """Test Q02: Patent Offices query exists in Regional category."""
        query = self.registry.get_query("Q02")
        self.assertIsNotNone(query)
        self.assertEqual(query.category, "Regional")

    def test_q03_application_trends_exists(self):
        """Test Q03: Application Trends query exists."""
        query = self.registry.get_query("Q03")
        self.assertIsNotNone(query)
        self.assertEqual(query.category, "Trends")

    def test_q04_technology_classes_exists(self):
        """Test Q04: Technology Classes query exists."""
        query = self.registry.get_query("Q04")
        self.assertIsNotNone(query)
        self.assertEqual(query.category, "Technology")

    def test_q06_country_leaders_exists(self):
        """Test Q06: Country Leaders query exists in Competitors."""
        query = self.registry.get_query("Q06")
        self.assertIsNotNone(query)
        self.assertEqual(query.category, "Competitors")

    def test_regional_category_has_queries(self):
        """Test Regional category has multiple queries including Q02."""
        regional = self.registry.get_queries_by_category("Regional")
        ids = [q.id for q in regional]
        self.assertIn("Q02", ids)
        self.assertGreaterEqual(len(ids), 2, "Regional category should have at least 2 queries")


if __name__ == "__main__":
    unittest.main()
