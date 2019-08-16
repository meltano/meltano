import pytest
import json
import os
import shutil
from pathlib import Path
from os.path import join

from support.payload_builder import PayloadBuilder
from meltano.core.compiler.project_compiler import ProjectCompiler
from meltano.core.sql.sql_utils import SqlUtils
from meltano.core.sql.analysis_helper import AnalysisHelper
from meltano.core.sql.date import Date
from meltano.core.project import Project
from meltano.core.m5o.m5o_file_parser import MeltanoAnalysisFileParser
from meltano.core.m5o.m5oc_file import M5ocFile
from meltano.core.sql.base import (
    MeltanoDesign,
    MeltanoTable,
    MeltanoColumn,
    MeltanoAggregate,
    MeltanoQuery,
    ParseError,
)


@pytest.fixture(scope="class")
def setup_test_models(project, request):
    # Find where the subfolder with the tmp models is by using request.fspath
    #  as we switch to another directory for tests (check test_dir session fixture)
    models_dir = request.fspath.join("..").join("models/")

    # And copy everything to the model/ directory of the test Project
    project_models_dir = project.root_dir("model")

    test_models = os.listdir(models_dir)
    for file_name in test_models:
        full_file_name = os.path.join(models_dir, file_name)
        if os.path.isfile(full_file_name):
            shutil.copy(full_file_name, project_models_dir)


@pytest.fixture(scope="class")
def gitflix(project, setup_test_models):
    # Compile the test files and make sure that the proper m5oc file was generated
    ProjectCompiler(project).compile()

    # Load the m5oc file for gitflix
    m5oc_file = project.root_dir("model", "gitflix.topic.m5oc")
    return M5ocFile.load(m5oc_file)


class TestQueryGeneration:
    @pytest.fixture
    def users(self):
        return (
            PayloadBuilder("users_design")
            .columns("gender")
            .aggregates("count", "avg_age", "sum_clv")
            .columns("day", "month", "year", join="streams_join")
            .aggregates("count", "sum_minutes", "count_days", join="streams_join")
            .columns("tv_series", join="episodes_join")
            .aggregates("count", "avg_rating", join="episodes_join")
        )

    @pytest.fixture
    def streams(self):
        return (
            PayloadBuilder("streams_design")
            .columns("day", "month", "year")
            .aggregates("count", "sum_minutes", "count_days")
            .columns("gender", join="users_join")
            .aggregates("count", "avg_age", "sum_clv", join="users_join")
            .columns("tv_series", join="episodes_join")
            .aggregates("count", "avg_rating", join="episodes_join")
        )

    @pytest.fixture
    def no_join_with_filters(self):
        return (
            PayloadBuilder("users_design")
            .columns("name")
            .aggregates("count", "avg_age", "sum_clv")
            .column_filter("users_design", "name", "is_not_null", "")
            .column_filter("users_design", "name", "like", "%yannis%")
            .column_filter("users_design", "gender", "is_null", "")
            .aggregate_filter("users_design", "count", "equal_to", 10)
            .aggregate_filter("users_design", "avg_age", "greater_than", 20)
            .aggregate_filter("users_design", "avg_age", "less_than", 40)
            .aggregate_filter("users_design", "sum_clv", "greater_or_equal_than", 100)
            .aggregate_filter("users_design", "sum_clv", "less_or_equal_than", 500)
            .order_by("users_design", "name", "asc")
            .order_by("users_design", "avg_age", "desc")
            .order_by("users_design", "sum_clv", "")
        )

    @pytest.fixture
    def join_with_filters(self):
        return (
            PayloadBuilder("users_design")
            .columns("gender")
            .aggregates("count", "avg_age", "sum_clv")
            .columns("day", "month", "year", join="streams_join")
            .aggregates("count", "sum_minutes", "count_days", join="streams_join")
            .columns("tv_series", join="episodes_join")
            .aggregates("count", "avg_rating", join="episodes_join")
            .column_filter("users_design", "gender", "equal_to", "male")
            .column_filter("streams_join", "year", "greater_or_equal_than", "2017")
            .column_filter("episodes_join", "tv_series", "like", "Marvel")
            .column_filter("episodes_join", "title", "like", "%Wolverine%")
            .aggregate_filter("users_design", "sum_clv", "less_than", 50)
            .aggregate_filter("episodes_join", "avg_rating", "greater_than", 8)
            .order_by("users_design", "gender", "asc")
            .order_by("users_design", "avg_age", "asc")
            .order_by("streams_join", "year", "desc")
            .order_by("streams_join", "sum_minutes", "desc")
            .order_by("episodes_join", "tv_series", "")
            .order_by("episodes_join", "avg_rating", "")
        )

    def test_compile_and_load_m5o_files(self, project, gitflix):
        design = MeltanoDesign(definition=gitflix.design("users_design").design)

        assert design.name == "users_design"
        assert len(design.tables()) == 3
        assert len(design.joins()) == 2

    def test_meltano_base_classes(self, gitflix):
        design = MeltanoDesign(definition=gitflix.design("users_design").design)

        assert design.name == "users_design"
        assert len(design.tables()) == 3
        assert len(design.joins()) == 2

        table = design.find_table("streams_join")
        assert table.name == "streams_table"

        join = design.get_join("episodes_join")
        assert join.name == "episodes_join"
        assert join.related_table["name"] == "episodes_table"

        # Test Meltano Tables and Columns
        assert "id" in [c.column_name() for c in table.primary_keys()]
        assert "streams.month" in [c.alias() for c in table.columns()]

        assert len(table.columns()) == 6
        new_c = MeltanoColumn(table)
        new_c.copy_metadata(table.get_column("month"))
        new_c.name = "quarter"
        table.add_column(new_c)
        assert len(table.columns()) == 7
        assert table.get_column("quarter").type == table.get_column("month").type

        # Test Meltano Tables and Aggregates
        assert "minutes" in [a.column_name() for a in table.aggregates()]
        assert "streams.id" in [a.column_alias() for a in table.aggregates()]
        assert "streams.sum_minutes" in [a.alias() for a in table.aggregates()]
        assert "streams.count_days" in [a.alias() for a in table.aggregates()]

        assert len(table.aggregates()) == 3
        new_a = MeltanoAggregate(table)
        new_a.name = "avg_price"
        new_a.type = "avg"
        new_a.label = "AVG Price"
        new_a.description = "Average Price"
        new_a.sql = "{{table}}.price"
        table.add_aggregate(new_a)
        assert len(table.aggregates()) == 4

    def test_meltano_query(self, users, gitflix):
        # Test parsing a json payload using a Design generated from a m5oc file
        #  and generating a proper MeltanoQuery Object
        q = MeltanoQuery(
            definition=users.payload, design_helper=gitflix.design("users_design")
        )

        assert q.design.name == "users_design"
        assert len(q.tables) == 3
        assert len(q.join_order) == 3
        assert q.join_order[2]["table"] == "episodes_table"

        # Test generating an HDA query
        (sql, query_attributes, aggregate_columns) = q.get_query()
        assert any(
            attr["attribute_label"] == "Average Age" for attr in query_attributes
        )
        assert any(attr["attribute_name"] == "sum_minutes" for attr in query_attributes)
        assert "users.sum_clv" in aggregate_columns

        assert "WITH base_join AS (SELECT" in sql
        assert "base_streams_table AS (SELECT DISTINCT" in sql
        assert "users_table_stats AS (" in sql
        assert 'COALESCE(AVG("episodes.rating"),0)' in sql
        assert 'COALESCE(COUNT("users.id"),0)' in sql
        assert 'COALESCE(SUM("users.clv"),0)' in sql
        assert 'SELECT * FROM "result"' in sql
        assert 'JOIN "streams"' in sql
        assert 'JOIN "episodes"' in sql

        # Check that the attribute used both as a column and as an aggregate
        # 1. Only appears once in the select clause of the base query
        # 2. Properly appears as an aggregate
        assert sql.count('"streams"."day" "streams.day"') == 1
        assert 'COALESCE(COUNT("streams.day"),0)' in sql

    def test_meltano_disjointed_query(self, streams, gitflix):
        # Test parsing a json payload using a Design generated from a m5oc file
        #  and generating a proper MeltanoQuery Object
        q = MeltanoQuery(
            definition=streams.payload, design_helper=gitflix.design("streams_design")
        )

        assert q.design.name == "streams_design"
        assert len(q.tables) == 3
        assert len(q.join_order) == 3
        assert q.join_order[2]["table"] == "episodes_table"

        # Test generating an HDA query
        (sql, query_attributes, aggregate_columns) = q.get_query()

        assert any(
            attr["attribute_label"] == "Average Age" for attr in query_attributes
        )
        assert any(attr["attribute_name"] == "sum_minutes" for attr in query_attributes)
        assert "users.sum_clv" in aggregate_columns

        assert "WITH base_join AS (SELECT" in sql
        assert "base_streams_table AS (SELECT DISTINCT" in sql
        assert "users_table_stats AS (" in sql
        assert 'COALESCE(AVG("episodes.rating"),0)' in sql
        assert 'COALESCE(COUNT("users.id"),0)' in sql
        assert 'COALESCE(SUM("users.clv"),0)' in sql
        assert 'SELECT * FROM "result"' in sql
        assert 'JOIN "users"' in sql
        assert 'JOIN "episodes"' in sql

        # Check that the attribute used both as a column and as an aggregate
        # 1. Only appears once in the select clause of the base query
        # 2. Properly appears as an aggregate
        assert sql.count('"streams"."day" "streams.day"') == 1
        assert 'COALESCE(COUNT("streams.day"),0)' in sql

    def test_meltano_no_join_query_filters(self, no_join_with_filters, gitflix):
        # Test a no-join query with filters
        q = MeltanoQuery(
            definition=no_join_with_filters.payload,
            design_helper=gitflix.design("users_design"),
        )

        # Test generating an HDA query
        (sql, query_attributes, aggregate_columns) = q.get_query()

        # There should be one where clause and 1 having clause
        assert sql.count("WHERE") == 1
        assert sql.count("HAVING") == 1

        # Check that all the WHERE filters were added correctly
        assert 'NOT "users"."name" IS NULL' in sql
        assert '"users"."name" LIKE \'%yannis%\'' in sql
        assert '"users"."gender" IS NULL' in sql

        # Check that all the HAVING filters were added correctly
        assert 'COALESCE(SUM("users"."clv"),0)>=100' in sql
        assert 'COALESCE(SUM("users"."clv"),0)<=500' in sql
        assert 'COALESCE(COUNT("users"."id"),0)=10' in sql
        assert 'COALESCE(AVG("users"."age"),0)>20' in sql
        assert 'COALESCE(AVG("users"."age"),0)<40' in sql

        # Check that the correct order by clauses have been generated
        assert (
            'ORDER BY "users.name" ASC,"users.avg_age" DESC,"users.sum_clv" ASC' in sql
        )

    def test_meltano_hda_query_filters(self, join_with_filters, gitflix):
        # Test an HDA query with filters
        q = MeltanoQuery(
            definition=join_with_filters.payload,
            design_helper=gitflix.design("users_design"),
        )

        # Test generating an HDA query
        (sql, query_attributes, aggregate_columns) = q.get_query()

        # There should be one where clause and 2 having clauses
        assert sql.count("WHERE") == 1
        assert sql.count("HAVING") == 2

        # Check that all the WHERE filters were added correctly
        assert '"users"."gender"=\'male\'' in sql
        assert '"streams"."year">=\'2017\'' in sql
        assert '"episodes"."tv_series" LIKE \'Marvel\'' in sql
        assert '"episodes"."title" LIKE \'%Wolverine%\'' in sql

        # Check that all the HAVING filters were added correctly
        assert 'HAVING COALESCE(SUM("users.clv"),0)<50' in sql
        assert 'HAVING COALESCE(AVG("episodes.rating"),0)>8' in sql

        # Check that the correct order by clauses have been generated
        #  and that they are in the correct order
        order_by_clause = (
            'ORDER BY "result"."users.gender" ASC,'
            '"result"."users.avg_age" ASC,'
            '"result"."streams.year" DESC,'
            '"result"."streams.sum_minutes" DESC,'
            '"result"."episodes.tv_series" ASC,'
            '"result"."episodes.avg_rating" ASC'
        )
        assert order_by_clause in sql

    def test_meltano_invalid_filters(self, gitflix):
        # Test for wrong expression
        bad_payload = (
            PayloadBuilder("users_design")
            .columns("gender")
            .aggregates("count", "avg_age", "sum_clv")
            .column_filter("users_design", "gender", "WRONG_EXPRESSION_TYPE", "male")
        )

        with pytest.raises(NotImplementedError) as e:
            assert MeltanoQuery(
                definition=bad_payload.payload,
                design_helper=gitflix.design("users_design"),
            )

        assert "Unknown filter expression: WRONG_EXPRESSION_TYPE" in str(e.value)

        # Test for wrong value
        bad_payload = (
            PayloadBuilder("users_design")
            .columns("gender")
            .aggregates("count", "avg_age", "sum_clv")
            .aggregate_filter("users_design", "sum_clv", "equal_to", None)
        )

        with pytest.raises(ParseError) as e:
            assert MeltanoQuery(
                definition=bad_payload.payload,
                design_helper=gitflix.design("users_design"),
            )

        assert "Filter expression: equal_to needs a non-empty value." in str(e.value)

        # Test for table not defined in design
        bad_payload = (
            PayloadBuilder("users_design")
            .columns("gender")
            .aggregates("count", "avg_age", "sum_clv")
            .column_filter("UNAVAILABLE_SOURCE", "gender", "equal_to", "male")
        )

        with pytest.raises(ParseError) as e:
            assert MeltanoQuery(
                definition=bad_payload.payload,
                design_helper=gitflix.design("users_design"),
            )

        assert "UNAVAILABLE_SOURCE not found in design users_design" in str(e.value)

        # Test for column not defined in design
        bad_payload = (
            PayloadBuilder("users_design")
            .columns("gender")
            .aggregates("count", "avg_age", "sum_clv")
            .column_filter("users_design", "UNAVAILABLE_COLUMN", "equal_to", "male")
        )

        with pytest.raises(ParseError) as e:
            assert MeltanoQuery(
                definition=bad_payload.payload,
                design_helper=gitflix.design("users_design"),
            )

        assert "Requested column users_table.UNAVAILABLE_COLUMN" in str(e.value)

        # Test for aggregate not defined in design
        bad_payload = (
            PayloadBuilder("users_design")
            .columns("gender")
            .aggregates("count", "avg_age", "sum_clv")
            .aggregate_filter("users_design", "UNAVAILABLE_AGGREGATE", "less_than", 50)
        )

        with pytest.raises(ParseError) as e:
            assert MeltanoQuery(
                definition=bad_payload.payload,
                design_helper=gitflix.design("users_design"),
            )

        assert "Requested column users_table.UNAVAILABLE_AGGREGATE" in str(e.value)
