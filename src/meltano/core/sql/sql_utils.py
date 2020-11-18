from .analysis_helper import AnalysisHelper
from .base import MeltanoQuery


class SqlUtils:
    def get_sql(self, design, incoming_json, schema=None):
        query = MeltanoQuery(
            definition=incoming_json, design_helper=design, schema=schema
        )

        (sql, query_properties, aggregate_columns) = query.get_query()

        return {
            "aggregates": aggregate_columns,
            "query_properties": query_properties,
            "sql": sql,
        }
