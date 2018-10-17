from enum import Enum

from .substitution import Substitution
from ..models.data import View, Dimension


class JoinType(Enum):
    left_join = "left"
    inner_join = "inner"
    full_outer_join = "full_outer"
    cross_join = "cross"


class Join:
    def __init__(self, join, view, table):
        self.table = table
        self.view = view
        join_type = self.get_join_type(join)
        join_sql = self.join_sql(join, table)
        self.sql = " ".join([join_type.value, join_sql])

    def get_join_type(self, join):
        if not "type" in join.settings:
            return JoinType.left_join
        else:
            type_of_join = join.settings["type"].lower()
            if type_of_join == JoinType.inner_join.value:
                return JoinType.inner_join
            elif type_of_join == JoinType.full_outer_join.value:
                return JoinType.full_outer_join
            elif type_of_join == JoinType.cross_join.value:
                return JoinType.cross_join

    def join_sql(self, join, table):
        sql = join.settings["sql_on"]
        results = Substitution.placeholder_match(sql)
        related_view = View.query.filter(View.name == join.name).first()

        def dimension_actual_name(result):
            (joined_view, joined_dimension) = result.split(".")
            queried_view = self.view
            if queried_view.name != joined_view:
                queried_view = related_view
            _dimensions = Dimension.query.filter(
                Dimension.name == joined_dimension
            ).all()
            queried_dimension = (
                Dimension.query.join(View, Dimension.view_id == View.id)
                .filter(Dimension.name == joined_dimension)
                .filter(View.id == queried_view.id)
                .first()
            )

            return queried_dimension.table_column_name

        inner_results = list(map(dimension_actual_name, results.inner))

        Substitution.variable_replace(results)

        for i, result in enumerate(results.outer):
            sql = sql.replace(result, inner_results[i])
        table_name = related_view.settings["sql_table_name"]
        return f"{table_name} AS {join.name} ON {sql}"
