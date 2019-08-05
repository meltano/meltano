from .analysis_helper import AnalysisHelper
from .base import MeltanoQuery


class SqlUtils:
    def get_sql(self, design, incoming_json, schema=None):
        query = MeltanoQuery(
            definition=incoming_json, design_helper=design, schema=schema
        )

        (sql, query_attributes, aggregate_columns) = query.get_query()

        return {
            "aggregates": aggregate_columns,
            "query_attributes": query_attributes,
            "sql": sql,
        }
