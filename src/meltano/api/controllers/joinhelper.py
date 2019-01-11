from enum import Enum

from .analysishelper import AnalysisHelper


class JoinType(Enum):
    left_join = "left"
    inner_join = "inner"
    full_outer_join = "full_outer"
    cross_join = "cross"


class JoinHelper:
    @staticmethod
    def get_join(join):
        return {"get_join": "get_join"}

    def get_dimensions(join, table, table_todo):
        # TODO table_todo renamed due to terminology refactor. Unsure if we'll need these JoinHelper methods as Micaël is working on joins (173-joins-in-meltano-with-pypika)
        dimensions = AnalysisHelper.dimensions_from_names(join["dimensions"], table)
        return AnalysisHelper.dimensions(dimensions, table_todo)

    def get_table(join):
        return {}
