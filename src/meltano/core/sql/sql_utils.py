from .analysis_helper import AnalysisHelper
from .hyper_dimensional_aggregates_helper import HyperDimensionalAggregatesHelper


class SqlUtils:
    def get_sql(self, design, incoming_json, schema=None):
        table = design["related_table"]
        base_table = table["sql_table_name"]
        db_table = AnalysisHelper.db_table(base_table, alias=design["name"])

        hda_helper = HyperDimensionalAggregatesHelper(design, incoming_json, schema)

        (sql, column_headers, column_names, aggregate_columns) = hda_helper.get_query()

        return {
            "db_table": db_table,
            "aggregates": aggregate_columns,
            "column_headers": column_headers,
            "column_names": column_names,
            "sql": sql,
        }
