import logging
import re
import os
from pathlib import Path
from collections import OrderedDict

import sqlalchemy
from flask import jsonify
from pypika import Query, Order
from .analysis_helper import AnalysisHelper
from .settings_helper import SettingsHelper
from meltano.core.project import Project
from .m5oc_file import M5ocFile
from .date import Date

meltano_model_path = Path(os.getcwd(), "model")


class ConnectionNotFound(Exception):
    def __init__(self, connection_name: str):
        self.connection_name = connection_name
        super().__init__("{connection_name} is missing.")


class SqlHelper:
    def parse_sql(self, input):
        placeholders = self.placeholder_match(input)

    def placeholder_match(self, input):
        outer_pattern = r"(\$\{[\w\.]*\})"
        inner_pattern = r"\$\{([\w\.]*)\}"
        outer_results = re.findall(outer_pattern, input)
        inner_results = re.findall(inner_pattern, input)
        return (outer_results, inner_results)

    def get_aliases_from_aggregates(self, aggregates, db_table):
        return [
            AnalysisHelper.field_from_aggregate(a, db_table).alias for a in aggregates
        ]

    def get_names(self, things):
        return [thing["name"] for thing in things]

    def get_m5oc_model(self, model_name):
        m5oc_file = Path(meltano_model_path).joinpath(f"{model_name}.model.m5oc")
        with m5oc_file.open() as f:
            m5oc = M5ocFile.load(f)
        return m5oc

    def get_db_engine(self, connection_name):
        project = Project.find()
        settings_helper = SettingsHelper()
        connections = settings_helper.get_connections()["settings"]["connections"]

        try:
            connection = next(
                connection
                for connection in connections
                if connection["name"] == connection_name
            )

            if connection["dialect"] == "postgresql":
                psql_params = ["username", "password", "host", "port", "database"]
                user, pw, host, port, db = [connection[param] for param in psql_params]
                connection_url = f"postgresql+psycopg2://{user}:{pw}@{host}:{port}/{db}"
            elif connection["dialect"] == "sqlite":
                db_path = project.root.joinpath(connection["path"])
                connection_url = f"sqlite:///{db_path}"

            return sqlalchemy.create_engine(connection_url)

            raise ConnectionNotFound(connection_name)
        except StopIteration:
            raise ConnectionNotFound(connection_name)

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
        join_order = []
        for j in joins:
            columns_raw += j["columns"]
            aggregates_raw += j["aggregates"]
            timeframes_raw += j["timeframes"]

            columns += AnalysisHelper.columns(j["columns"], j["db_table"])
            aggregates += AnalysisHelper.aggregates(j["aggregates"], j["db_table"])
            timeframe_periods += AnalysisHelper.periods(j["timeframes"], j["db_table"])
            if j.get("columns") or j.get("aggregates") or j.get("timeframes"):
              join_deps = design.joins_for_table(j["name"])
              for i in range(0, len(join_deps)):
                if len(join_order) < i + 1:
                  join_order.append(set())
                join_order[i].add(join_deps[i])

        # flatten
        join_order = [name for joins in join_order for name in joins]

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
            "db_table": db_table,
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
                join_order=join_order,
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
        join_order=None,
        order=None,
        orderby=None,
    ):
        select = columns + aggregates + periods
        q = Query.from_(from_)
        sorted_joins = filter(lambda j: j["name"] in join_order, joins)
        sorted_joins = sorted(sorted_joins, key=lambda j: join_order.index(j["name"]))
        for j in sorted_joins:

            join_db_table = j["db_table"]
            q = q.join(join_db_table).on(j["on"])

        q = q.select(*select).groupby(*columns, *periods)

        if order:
            q = q.orderby(orderby, order=order)

        q = q.limit(limit)
        return str(q) + ";"

    def get_query_results(self, connection_name, sql):
        engine = self.get_db_engine(connection_name)
        results = engine.execute(sql)
        results = [OrderedDict(row) for row in results]
        return results

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
''