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

    def get_dimensions(join, table, table):
        dimensions = AnalysisHelper.dimensions_from_names(join["dimensions"], table)
        return AnalysisHelper.dimensions(dimensions, table)

    def get_table(join):
        return {}
