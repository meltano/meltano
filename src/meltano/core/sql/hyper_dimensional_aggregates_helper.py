from typing import Dict, Tuple
from pypika import functions as fn
from pypika import AliasedQuery, Query, Order, Table, Field

from .design_helper import DesignHelper
from .base import MeltanoDesign, MeltanoQuery


class HyperDimensionalAggregatesHelper:
    def __init__(
        self, design_helper: DesignHelper, incoming_json: Dict, schema: str = None
    ) -> None:
        self.design_helper = design_helper
        self.incoming_json = incoming_json
        self.query = MeltanoQuery(
            definition=incoming_json, design_helper=design_helper, schema=schema
        )

    def needs_hda(self) -> bool:
        has_join_columns = next(
            filter(lambda x: len(x.get("columns", [])), self.incoming_json["joins"]),
            None,
        )

        has_join_aggregates = next(
            filter(lambda x: len(x.get("aggregates", [])), self.incoming_json["joins"]),
            None,
        )
        has_base_table_aggregate = len(self.incoming_json.get("aggregates", []))

        if not has_join_columns and not has_join_aggregates:
            return False
        else:
            return has_base_table_aggregate or has_join_aggregates

    def get_query(self) -> Tuple:
        """
        Build the HDA SQL query for this Query definition.

        Returns a Tuple (sql, column_headers, column_names)
        - sql: A string with the hda_query as a SQL:1999 compatible query
        - (column_names, column_headers): The column names and headers of
           the final result in the same order as the one defined by the HDA query
        """
        return self.query.hda_query()
