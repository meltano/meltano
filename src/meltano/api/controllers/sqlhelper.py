import logging
import re

import sqlalchemy
from flask import jsonify
from pypika import Query, Order

from .analysishelper import AnalysisHelper
from .date import Date
from .joinhelper import JoinHelper


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
        return [thing["name"] for thing in things]

    def get_sql(self, explore, incoming_json):
        table_name = incoming_json["table"]
        table = explore["related_table"]

        base_table = table["sql_table_name"]
        incoming_columns = incoming_json["columns"]
        incoming_column_groups = incoming_json["column_groups"]
        incoming_aggregates = incoming_json["aggregates"]
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
        timeframes = [t["timeframes"] for t in incoming_column_groups]
        # flatten list of timeframes
        timeframes = [y for x in timeframes for y in x]
        columns = AnalysisHelper.columns_from_names(incoming_columns, table)
        aggregates = AnalysisHelper.aggregates_from_names(incoming_aggregates, table)
        columns_raw = columns
        aggregates_raw = aggregates

        table = AnalysisHelper.table(base_table, explore["name"])
        joins = [JoinHelper.get_join(j) for j in incoming_joins]
        column_groups = self.column_groups(
            table_name, incoming_column_groups, table
        )
        columns = AnalysisHelper.columns(columns, table)
        columns = columns + column_groups
        aggregates = AnalysisHelper.aggregates(aggregates, table)

        if orderby:
            ordered_by_column = [d for d in columns_raw if d.name == orderby]
            if ordered_by_column:
                orderby = self.columns(ordered_by_column, table)[0]
            else:
                ordered_by_column = [m for m in aggregates_raw if m.name == orderby]
                if ordered_by_column:
                    orderby = self.aggregates(ordered_by_column, table)[0]
                else:
                    raise Exception(
                        "Something is wrong, no column or aggregate column matching the column to sort by."
                    )

        column_headers = self.column_headers(columns_raw, aggregates_raw)
        names = self.get_names(columns_raw + aggregates_raw)
        return {
            "columns": columns_raw,
            "aggregates": aggregates_raw,
            "column_headers": column_headers,
            "names": names,
            "sql": self.get_query(
                from_=table,
                columns=columns,
                aggregates=aggregates,
                limit=incoming_limit,
                joins=joins,
                order=order,
                orderby=orderby,
            ),
        }

    def column_headers(self, columns, aggregates):
        return [d["label"] for d in columns + aggregates]

    def column_groups(self, table_name, column_groups, table):
        fields = []
        for column_group in column_groups:
            column_group_queried = (
                ColumnGroup.query.join(Table, ColumnGroup.table_id == Table.id)
                .filter(Table.name == table_name)
                .filter(ColumnGroup.name == column_group["name"])
                .first()
            )
            (_table, name) = column_group_queried.table_column_name.split(".")
            for timeframe in column_group["timeframes"]:
                d = Date(timeframe, table, name)
                fields.append(d.sql)
        return fields

    def get_query(
        self, from_, columns, aggregates, limit, joins=None, order=None, orderby=None
    ):
        select = columns + aggregates
        q = Query.from_(from_)
        if joins:
            region = from_
            entry = joins[0]["table"]
            join_columns = joins[0]["columns"]
            join_aggregates = joins[0]["aggregates"]
            select = select + join_columns + join_aggregates
            columns = columns + join_columns
            q = q.join(joins[0]["table"]).on(
                region.id == entry.region_id and region.id == entry.region_id
            )
        q = q.select(*select).groupby(*columns)
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
