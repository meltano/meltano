import logging
import re

import sqlalchemy
from flask import jsonify
from pypika import Query, Order
from .analysis_helper import AnalysisHelper
from .date import Date


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

    def get_sql(self, design, incoming_json):
        table_name = incoming_json["table"]
        table = design["related_table"]

        base_table = table["sql_table_name"]
        incoming_columns = incoming_json["columns"]
        incoming_timeframes = incoming_json["timeframes"]
        incoming_aggregates = incoming_json["aggregates"]
        incoming_filters = incoming_json["filters"]
        incoming_joins = incoming_json["joins"]
        incoming_limit = incoming_json.get("limit", 50)
        incoming_order = incoming_json["order"]

        db_table = AnalysisHelper.db_table(base_table, alias=design["name"])
        timeframes_raw = [
            design.timeframe_periods_for(table, tf) for tf in incoming_timeframes
        ]
        timeframe_periods = [
            AnalysisHelper.periods(timeframe, db_table) for timeframe in timeframes_raw
        ]

        columns_raw = AnalysisHelper.columns_from_names(incoming_columns, table)
        columns = AnalysisHelper.columns(columns_raw, db_table)

        aggregates_raw = AnalysisHelper.aggregates_from_names(
            incoming_aggregates, table
        )
        aggregates = AnalysisHelper.aggregates(aggregates_raw, db_table)

        # add the joins dimension and aggregates
        joins = [design.join_for(j) for j in incoming_joins]
        for j in joins:
            columns_raw += j["columns"]
            aggregates_raw += j["aggregates"]
            timeframes_raw += j["timeframes"]

            columns += AnalysisHelper.columns(j["columns"], j["db_table"])
            aggregates += AnalysisHelper.aggregates(j["aggregates"], j["db_table"])
            timeframe_periods += AnalysisHelper.periods(j["timeframes"], j["db_table"])

        order = None
        orderby = None
        orderby_field = None
        if incoming_order:
            orderby = incoming_order["column"]
            order = Order.asc if incoming_order["direction"] == "asc" else Order.desc

        # order by column
        if orderby:
            try:
                orderby_field = next(
                    AnalysisHelper.field_from_column(c, db_table)
                    for c in columns_raw
                    if c["name"] == orderby
                )
            except StopIteration:
                orderby_field = None
                pass

        # order by aggregate
        if orderby and not orderby_field:
            try:
                orderby_field = next(
                    AnalysisHelper.field_from_aggregate(a, db_table)
                    for a in aggregates_raw
                    if a["name"] == orderby
                )
            except StopIteration:
                orderby_field = None
                raise Exception(
                    "Something is wrong, no dimension or measure column matching the column to sort by."
                )

        orderby = orderby_field
        column_headers = self.column_headers(
            columns_raw, aggregates_raw, timeframes_raw
        )
        names = self.get_names(columns_raw + aggregates_raw)
        return {
            "columns": columns_raw,
            "aggregates": aggregates_raw,
            "column_headers": column_headers,
            "names": names,
            "sql": self.get_query(
                from_=db_table,
                columns=columns,
                aggregates=aggregates,
                periods=timeframe_periods,
                limit=incoming_limit,
                joins=joins,
                orderby=orderby,
                order=order,
            ),
        }

    def column_headers(self, columns, aggregates, timeframes):
        labels = [l["label"] for l in columns + aggregates]
        for timeframe in timeframes:
            labels += timeframe["period_labels"]

        return labels

    def get_query(
        self,
        from_,
        columns,
        aggregates,
        periods,
        limit,
        joins=None,
        order=None,
        orderby=None,
    ):
        select = columns + aggregates + periods
        q = Query.from_(from_)

        for j in joins:
            join_db_table = j["db_table"]
            q = q.join(join_db_table).on(j["on"])

        q = q.select(*select).groupby(*columns, *periods)

        if order:
            q = q.orderby(orderby, order=order)

        q = q.limit(limit)
        return str(q) + ";"

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
