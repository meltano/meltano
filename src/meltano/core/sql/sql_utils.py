import re

from pypika import Query, Order

from .analysis_helper import AnalysisHelper
from .hyper_dimensional_aggregates_helper import HyperDimensionalAggregatesHelper
from .date import Date


class SqlUtils:
    def get_aliases_from_aggregates(self, aggregates, db_table):
        return [
            AnalysisHelper.field_from_aggregate(a, db_table).alias for a in aggregates
        ]

    def get_names(self, things):
        return [thing["name"] for thing in things]

    def get_sql(self, design, incoming_json, schema=None):
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
        column_names = self.get_names(columns_raw + aggregates_raw)

        hda_helper = HyperDimensionalAggregatesHelper(design, incoming_json, schema)
        if hda_helper.needs_hda():
            (
                sql,
                column_headers,
                column_names,
                aggregate_columns,
            ) = hda_helper.get_query()
        else:
            sql = self.get_query(
                from_=db_table,
                columns=columns,
                aggregates=aggregates,
                periods=timeframe_periods,
                limit=incoming_limit,
                joins=joins,
                join_order=join_order,
                orderby=orderby,
                order=order,
                schema=schema,
                base_table=base_table,
            )

            aggregate_columns = self.get_aliases_from_aggregates(
                aggregates_raw, db_table
            )

        return {
            "db_table": db_table,
            "aggregates": aggregate_columns,
            "column_headers": column_headers,
            "column_names": column_names,
            "sql": sql,
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
        schema=None,
        base_table=None,
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
        q = str(q)

        # Dynamically add at runtime the schema provided by the current connection
        # Check .base.py: MeltanoQuery.add_schema_to_hda_query()
        #   for more details on why we are doing this using replace
        if schema:
            if base_table:
                q = q.replace(f'FROM "{base_table}"', f'FROM "{schema}"."{base_table}"')

            for table in join_order:
                q = q.replace(f'FROM "{table}"', f'FROM "{schema}"."{table}"')
                q = q.replace(f'JOIN "{table}"', f'JOIN "{schema}"."{table}"')

        return f"{q};" if len(q) > 0 else ""
