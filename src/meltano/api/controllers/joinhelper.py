from enum import Enum

from .analysishelper import AnalysisHelper
from ..models.data import View, Join


class JoinType(Enum):
    left_join = "left"
    inner_join = "inner"
    full_outer_join = "full_outer"
    cross_join = "cross"


class JoinHelper:
    @staticmethod
    def get_join(join):
        view = JoinHelper.get_view(join)
        table = AnalysisHelper.table(view.settings["sql_table_name"], view.name)
        dimensions = JoinHelper.get_dimensions(join, view, table)
        # TODO finish this implementation with measures
        measures = []
        join = Join.query.filter(Join.name == join["name"]).first()
        return {
            "view": view,
            "dimensions": dimensions,
            "measures": measures,
            "table": table,
            "on": join.settings["sql_on"],
            "join": join,
        }

    def get_dimensions(join, view, table):
        dimensions = AnalysisHelper.dimensions_from_names(join["dimensions"], view)
        return AnalysisHelper.dimensions(dimensions, table)

    def get_view(join):
        return View.query.filter(View.name == join["name"]).first()
