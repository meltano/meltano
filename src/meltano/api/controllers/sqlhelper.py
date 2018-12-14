import logging
import re

import sqlalchemy
from flask import jsonify
from pypika import Query, Order

from .analysishelper import AnalysisHelper
from .aggregate import Aggregate
from .date import Date
from .joinhelper import JoinHelper
from ..app import app, db
from ..models.data import View, DimensionGroup, Join
from ..models.projects import Project
from ..models.settings import Settings


class SqlHelper:
    def parse_sql(self, input):
        placeholders = self.placeholder_match(input)

    def placeholder_match(self, input):
        outer_pattern = r"(\$\{[\w\.]*\})"
        inner_pattern = r"\$\{([\w\.]*)\}"
        outer_results = re.findall(outer_pattern, input)
        inner_results = re.findall(inner_pattern, input)
        return (outer_results, inner_results)

    def get_names(self, things):
        return [thing.name for thing in things]

    def get_sql(self, explore, incoming_json):
        view_name = incoming_json["view"]
        view = View.query.filter(View.name == view_name).first()
        base_table = view.settings["sql_table_name"]
        (schema, table) = base_table.split(".")
        incoming_dimensions = incoming_json["dimensions"]
        incoming_dimension_groups = incoming_json["dimension_groups"]
        incoming_measures = incoming_json["measures"]
        incoming_filters = incoming_json["filters"]
        incoming_joins = incoming_json["joins"]
        incoming_limit = incoming_json.get("limit", 50)
        incoming_order = incoming_json["order"]
        order = None
        if incoming_order:
            if incoming_order["direction"] == "asc":
                order = Order.asc
            else:
                order = Order.desc
        orderby = incoming_order["column"] if incoming_order else None

        # get all timeframes
        timeframes = [t["timeframes"] for t in incoming_dimension_groups]
        # flatten list of timeframes
        timeframes = [y for x in timeframes for y in x]
        dimensions = AnalysisHelper.dimensions_from_names(incoming_dimensions, view)
        measures = AnalysisHelper.measures_from_names(incoming_measures, view)
        dimensions_raw = dimensions
        measures_raw = measures

        table = AnalysisHelper.table(base_table, explore.name)
        joins = [JoinHelper.get_join(j) for j in incoming_joins]
        dimension_groups = self.dimension_groups(
            view_name, incoming_dimension_groups, table
        )
        dimensions = AnalysisHelper.dimensions(dimensions, table)
        dimensions = dimensions + dimension_groups
        measures = AnalysisHelper.measures(measures, table)

        if orderby:
            ordered_by_column = [d for d in dimensions_raw if d.name == orderby]
            if ordered_by_column:
                orderby = self.dimensions(ordered_by_column, table)[0]
            else:
                ordered_by_column = [m for m in measures_raw if m.name == orderby]
                if ordered_by_column:
                    orderby = self.measures(ordered_by_column, table)[0]
                else:
                    raise Exception(
                        "Something is wrong, no dimension or measure column matching the column to sort by."
                    )

        column_headers = self.column_headers(dimensions_raw, measures_raw)
        names = self.get_names(dimensions_raw + measures_raw)
        return {
            "dimensions": dimensions_raw,
            "measures": measures_raw,
            "column_headers": column_headers,
            "names": names,
            "sql": self.get_query(
                from_=table,
                dimensions=dimensions,
                measures=measures,
                limit=incoming_limit,
                joins=joins,
                order=order,
                orderby=orderby,
            ),
        }

    def column_headers(self, dimensions, measures):
        return [d.label for d in dimensions + measures]

    def dimension_groups(self, view_name, dimension_groups, table):
        fields = []
        for dimension_group in dimension_groups:
            dimension_group_queried = (
                DimensionGroup.query.join(View, DimensionGroup.view_id == View.id)
                .filter(View.name == view_name)
                .filter(DimensionGroup.name == dimension_group["name"])
                .first()
            )
            (_table, name) = dimension_group_queried.table_column_name.split(".")
            for timeframe in dimension_group["timeframes"]:
                d = Date(timeframe, table, name)
                fields.append(d.sql)
        return fields

    def get_query(
        self, from_, dimensions, measures, limit, joins=None, order=None, orderby=None
    ):
        select = dimensions + measures
        q = Query.from_(from_)
        if joins:
            region = from_
            entry = joins[0]["table"]
            join_dimensions = joins[0]["dimensions"]
            join_measures = joins[0]["measures"]
            select = select + join_dimensions + join_measures
            dimensions = dimensions + join_dimensions
            q = q.join(joins[0]["table"]).on(
                region.id == entry.region_id and region.id == entry.region_id
            )
        q = q.select(*select).groupby(*dimensions)
        if order:
            q = q.orderby(orderby, order=order)
        q = q.limit(limit)
        return f"{str(q)};"

    def reset_db(self):
        try:
            Settings.__table__.drop(db.engine)
            Project.__table__.drop(db.engine)
            db.drop_all()
        except sqlalchemy.exc.OperationalError as err:
            logging.error("Failed drop database.")
        db.create_all()
        settings = Settings()
        db.session.add(settings)
        db.session.commit()
        return jsonify({"dropped_it": "like_its_hot"})
