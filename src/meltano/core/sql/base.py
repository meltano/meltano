import re

from typing import Dict, List, Tuple
import networkx as nx

from pypika import functions as fn
from pypika import AliasedQuery, Query, Order, Table, Field

from networkx.readwrite import json_graph


class ParseError(Exception):
    pass


class MeltanoBase:
    def __init__(self, definition: Dict = {}):
        self._definition = definition

    def __getattr__(self, attr: str):
        return self._definition.get(attr, None)


class MeltanoDesign(MeltanoBase):
    """
    An internal representation of a design loaded from an m5oc file.

    It provides access to the Tables and Joins defined, together with additional
      metada for the design: {name, label, description, graph}
    """

    def __init__(self, definition: Dict) -> None:
        # Overriding the init method to force a definition for Designs
        super().__init__(definition)

    def tables(self) -> List[MeltanoBase]:
        related_tables = [self._definition.get("related_table", None)]
        related_tables += [
            j["related_table"] for j in self._definition.get("joins", [])
        ]
        return [MeltanoTable(definition, design=self) for definition in related_tables]

    def joins(self) -> List[MeltanoBase]:
        return [
            MeltanoJoin(definition, design=self)
            for definition in self._definition.get("joins", [])
        ]

    def get_table(self, name: str) -> MeltanoBase:
        return next((t for t in self.tables() if t.name == name), None)

    def get_join(self, name: str) -> MeltanoBase:
        return next((t for t in self.joins() if t.name == name), None)


class MeltanoTable(MeltanoBase):
    """
    An internal representation of a Table defined in a design.

    It provides access to the Columns and Aggregates defined, together with additional
      metada for the Table: {name, sql_table_name}
    """

    def __init__(self, definition: Dict = {}, design: MeltanoDesign = None) -> None:
        self.design = design

        # We are going to use class Table in 2 ways:
        # 1. As part of a design, with everything stored in self._definition
        # 2. As a stand alone class with no self._definition where we'll manually
        #     store everything in the following attributes
        self._attributes = {}
        self._columns = []
        self._aggregates = []
        self._timeframes = []

        # Optional Primary Keys stored for tables used in Queries
        # Those are the PK columns of the table that have not been directly
        #  requested in the Query
        self.optional_pkeys = []

        super().__init__(definition)

    def columns(self) -> List[MeltanoBase]:
        return [
            MeltanoColumn(definition=definition, table=self)
            for definition in self._definition.get("columns", [])
        ] + self._columns

    def primary_keys(self) -> List[MeltanoBase]:
        return (
            list(filter(lambda x: x.primary_key, self.columns())) + self.optional_pkeys
        )

    def aggregates(self) -> List[MeltanoBase]:
        return [
            MeltanoAggregate(definition=definition, table=self)
            for definition in self._definition.get("aggregates", [])
        ] + self._aggregates

    def timeframes(self) -> List[MeltanoBase]:
        return [
            MeltanoTimeframe(definition=definition, table=self)
            for definition in self._definition.get("timeframes", [])
        ] + self._timeframes

    def get_column(self, name: str) -> MeltanoBase:
        return next((c for c in self.columns() if c.name == name), None)

    def get_aggregate(self, name: str) -> MeltanoBase:
        return next((a for a in self.aggregates() if a.name == name), None)

    def get_aggregate_by_column_name(self, name: str) -> MeltanoBase:
        return next((a for a in self.aggregates() if a.column_name() == name), None)

    def get_timeframe(self, name: str) -> MeltanoBase:
        return next((t for t in self.timeframes() if t.name == name), None)

    def add_column(self, column) -> None:
        self._columns.append(column)

    def add_aggregate(self, aggregate) -> None:
        self._aggregates.append(aggregate)

    def add_timeframe(self, timeframe) -> None:
        self._timeframes.append(timeframe)

    def __getattr__(self, attr: str):
        try:
            return self._attributes[attr]
        except KeyError:
            return super().__getattr__(attr)

    def __setattr__(self, name, value):
        if name in ["name", "sql_table_name"]:
            self._attributes[name] = value
        else:
            super(MeltanoTable, self).__setattr__(name, value)


class MeltanoColumn(MeltanoBase):
    """
    An internal representation of a Column defined in a Table.

    It provides access to the metada for the Column:
      {label, name, type, primary_key, hidden, sql}
    together with helper functions for getting a qualified name for the Column
     and a proper alias that can be used in queries
    """

    def __init__(self, table: MeltanoTable, definition: Dict = {}) -> None:
        self.table = table

        # Used for manually setting the metadata attributes {label, name, type, primary_key, hidden, sql}
        self._attributes = {}

        super().__init__(definition)

    def alias(self) -> str:
        return f"{self.table.sql_table_name}.{self.column_name()}"

    def column_name(self) -> str:
        if self.sql:
            (table, column) = self.sql.split(".")
        else:
            column = self.name

        return column

    def copy_metadata(self, other_column) -> None:
        self.label = other_column.label
        self.name = other_column.name
        self.type = other_column.type
        self.primary_key = other_column.primary_key
        self.hidden = other_column.hidden
        self.sql = other_column.sql

    def __getattr__(self, attr: str):
        try:
            return self._attributes[attr]
        except KeyError:
            return super().__getattr__(attr)

    def __setattr__(self, name, value):
        if name in ["label", "name", "type", "primary_key", "hidden", "sql"]:
            self._attributes[name] = value
        else:
            super(MeltanoColumn, self).__setattr__(name, value)


class MeltanoAggregate(MeltanoBase):
    """
    An internal representation of an Aggregate defined in a Table.

    It provides access to the metada for the Aggregate:
      {name, type (one of {sum, count, avg}), label, description, sql}
    together with helper functions for getting a qualified name for the Column,
     a proper alias that can be used in queries, the column name used in the aggregate
     and the qualified sql expression to be used in queries.
    """

    def __init__(self, table: MeltanoTable, definition: Dict = {}) -> None:
        self.table = table

        # Used for manually setting the metadata attributes {name, type, label, description, sql}
        self._attributes = {}

        super().__init__(definition)

    def alias(self) -> str:
        return f"{self.table.sql_table_name}.{self.name}"

    def qualified_sql(self, base_table: str = None) -> fn.Coalesce:
        """
        Return the aggregate as a fully qualified SQL clause defined
          as a pypika Aggregate

        The base_table defines whether the Aggregate is evaluated over its
          own table or an intermediary table (e.g. resulting from a with clause)

        If the Aggregate is evaluated over its own table, then things are simple
          as we just want something like: COUNT("region"."id") "region.count"

        But if the attribute has been selected in a previous with clause, then
          its name is its alias as if it was a column (e.g. "region.id")
          and the attribute is selected by the base table, so we want something
          like: COUNT("base_table"."region.id") "region.count"

        On top of that, most of the times we define aggregates as: {{TABLE}}.id
          so we have to first replace {{TABLE}} with its own table name
        """
        if base_table and base_table != self.table.sql_table_name:
            sql = re.sub(
                "\{\{TABLE\}\}",
                self.table.sql_table_name,
                self.sql,
                flags=re.IGNORECASE,
            )
            field = Field(sql, table=Table(base_table))
        else:
            table = Table(self.table.sql_table_name)
            field = Field(self.column_name(), table=table)

        if self.type == "sum":
            return fn.Coalesce(fn.Sum(field), 0, alias=self.alias())
        elif self.type == "count":
            return fn.Coalesce(fn.Count(field), 0, alias=self.alias())
        elif self.type == "avg":
            return fn.Coalesce(fn.Avg(field), 0, alias=self.alias())

    def column_name(self) -> str:
        (table, column) = self.sql.split(".")
        return column

    def column_alias(self) -> str:
        return f"{self.table.sql_table_name}.{self.column_name()}"

    def copy_metadata(self, other_aggregate) -> None:
        self.name = other_aggregate.name
        self.type = other_aggregate.type
        self.label = other_aggregate.label
        self.description = other_aggregate.description
        self.sql = other_aggregate.sql

    def __getattr__(self, attr: str):
        try:
            return self._attributes[attr]
        except KeyError:
            return super().__getattr__(attr)

    def __setattr__(self, name, value):
        if name in ["name", "type", "label", "description", "sql"]:
            self._attributes[name] = value
        else:
            super(MeltanoAggregate, self).__setattr__(name, value)


class MeltanoTimeframe(MeltanoBase):
    """
    An internal representation of a Timeframe defined in a Table.

    It provides access to the metada for the Timeframe:
      {name, type, label, periods:[], description, sql}
    """

    def __init__(self, table: MeltanoTable, definition: Dict = {}) -> None:
        self.table = table
        super().__init__(definition)


class MeltanoJoin(MeltanoBase):
    """
    An internal representation of a Join defined in a Design.

    It provides access to the metada for the Join:
      {name, related_table, label, sql_on, relationship}
    """

    def __init__(self, definition: Dict = {}, design: MeltanoDesign = None) -> None:
        self.design = design
        super().__init__(definition)


class MeltanoQuery(MeltanoBase):
    """
    An internal representation of a Query Definition sent to meltano for evaluation.

    The definition dictionary is parsed and the information is stored in a
    structured way:
     - Tables with only the Columns, Timeframes and Aggregates requested
     - Filters (WIP: access through the filters attribute at the moment)
     - The join order

    It provides also access to additional metada for the query:
      {run (whether to run the query or not), order, limit}
    and support functions for fetching all the columns and aggregates requested,
    the attributes used in the group by, etc
    """

    def __init__(self, definition: Dict, design_helper, schema: str = None) -> None:
        self.design_helper = design_helper

        # The Meltano Design this Query has been built for
        self.design = MeltanoDesign(design_helper.design)

        # The schema used at run time.
        # It is used in order to dynamically lookup the tables at that schema
        #  if it is not None
        self.schema = schema

        # A collection of all tables that arte defined in the Query
        #  with the Columns, Timeframes and Aggregates defined in the Query
        self.tables = []

        # The proper join order that will be used for the query (list of table names)
        self.join_order = []

        self.parse_definition(definition)

        super().__init__(definition)

    def parse_definition(self, definition: Dict) -> None:
        """
        Parse the Query definition and generate the Tables, join_order, etc for
         easy access and lookups.
        """

        # Find the tables defined in the Query and add them as Table Objects
        #  with the proper Columns, Aggregates and Timeframe Objects
        primary_table = {
            "name": definition.get("table", None),
            "columns": definition.get("columns", None),
            "aggregates": definition.get("aggregates", None),
            "timeframes": definition.get("timeframes", None),
        }
        related_tables = [primary_table] + definition.get("joins", [])

        # Keep track of the last table added to the join in order to iterativelly
        #  build the join order from the design.graph
        # Start with the primary_table as it should be always included
        last_table_added = primary_table["name"]

        # get the graph defined in the design: it is used for finding the
        #  shortest path and adding missing tables in case a required table
        #  is missing
        design_graph = json_graph.node_link_graph(self.design.graph)

        for related_table in related_tables:
            # Find the requested table in the Design
            table_def = self.design.get_table(related_table.get("name", None))

            if table_def:
                table = MeltanoTable()
                table.name = table_def.name
                table.sql_table_name = table_def.sql_table_name

                for column in related_table.get("columns", []):
                    column_def = table_def.get_column(column)
                    if column_def:
                        c = MeltanoColumn(table=table)
                        c.copy_metadata(column_def)
                        table.add_column(c)
                    else:
                        raise ParseError(
                            f"Requested column {table.name}.{column} is not defined in the design"
                        )

                for aggregate in related_table.get("aggregates", []):
                    aggregate_def = table_def.get_aggregate(aggregate)
                    if aggregate_def:
                        a = MeltanoAggregate(table=table)
                        a.copy_metadata(aggregate_def)
                        table.add_aggregate(a)
                    else:
                        raise ParseError(
                            f"Requested aggregate {table.name}.{aggregate} is not defined in the design"
                        )

                for timeframe in related_table.get("timeframes", []):
                    timeframe_def = table_def.get_timeframe(timeframe.get("name", None))
                    if timeframe_def:
                        table.add_timeframe(timeframe_def)
                    else:
                        raise ParseError(
                            f"Requested timeframe {table.name}.{timeframe.get('name', None)} is not defined in the design"
                        )

                # Find the primary keys of the Table definition in the Design
                #  that have not been requested in the Query definition
                #  and add them in the Table definition in order to use them
                #  in the SQL generation (we need them in order to select distinct)
                for pk in table_def.primary_keys():
                    if (
                        table.get_column(pk.name) is None
                        and table.get_aggregate_by_column_name(pk.name) is None
                    ):
                        c = MeltanoColumn(table=table)
                        c.copy_metadata(pk)
                        table.optional_pkeys.append(c)

                self.tables.append(table)

                # Add tables that have at least a Column, Aggregate or Timeframe
                #  requested in the Query definition
                if table.name != primary_table["name"] and (
                    table.columns() or table.aggregates() or table.timeframes()
                ):
                    new_joins = self.joins_for_table(
                        design_graph, last_table_added, table.name
                    )
                    new_joins = list(
                        filter(
                            lambda t: t not in [j["table"] for j in self.join_order],
                            new_joins,
                        )
                    )

                    for join in new_joins:
                        join_on = None
                        if join != primary_table["name"]:
                            join_def = self.design.get_join(join)
                            if join_def:
                                join_on = self.design_helper.join_for(
                                    join_def._definition
                                )["on"]
                            else:
                                raise ParseError(
                                    f"Requested join {join} is not defined in the design"
                                )

                        self.join_order.append({"table": join, "on": join_on})

                    last_table_added = table.name
            else:
                raise ParseError(
                    f'Requested table {related_table.get("name", None)} is not defined in the design'
                )

    def joins_for_table(self, design_graph, source_table: str, target_table: str):
        return nx.shortest_path(design_graph, source=source_table, target=target_table)

    def hda_query(self) -> Tuple:
        """
        Build the HDA SQL query for this Query definition.

        For more info on the process followed check the following:
        https://gitlab.com/meltano/meltano/issues/286
        https://gitlab.com/meltano/meltano/issues/344

        Returns a Tuple (sql, column_headers, column_names)
        - sql: A string with the hda_query as a SQL:1999 compatible query
        - (column_names, column_headers): The column names and headers of
           the final result in the same order as the one defined by the HDA query
        """

        # Lists with the column names and headers of the final result when the
        #  HDA query is executed
        column_headers = []
        column_names = []
        aggregate_columns = []

        # Build the base_join table
        base_join_query = Query

        # Start By building the Join
        for join in self.join_order:
            if join["on"] is None:
                db_table = Table(join["table"], alias=join["table"])
                base_join_query = base_join_query.from_(db_table)
            else:
                db_table = Table(join["table"], alias=join["table"])
                base_join_query = base_join_query.join(db_table).on(join["on"])

        # Then Select all the columns that will be required in next steps
        # For each table all base columns, columns that will be used in aggregates,
        #  timeframes and the primary keys in case they are not already included
        select = []
        for table in self.tables:
            if not (table.columns() or table.aggregates() or table.timeframes()):
                # Skip tables that don't have at least a Column, Aggregate or
                #  Timeframe requested in the Query definition
                continue

            pika_table = Table(table.sql_table_name, alias=table.sql_table_name)
            for c in table.columns() + table.optional_pkeys:
                select.append(Field(c.column_name(), table=pika_table, alias=c.alias()))

            # We have to track wich columns have been added to the SELECT clause
            #  for being used in Aggregates as it is valid to have multiple
            #  Aggregates over the same column (e.g. AVG(price), SUM(price))
            # In that case, we don't want to add the column multiple times in the
            #  select clause cause will cause an Error in followup with clauses:
            #  Error: column reference {COLUMN} is ambiguous
            aggregate_columns_selected = set()

            for a in table.aggregates():
                aggregate_columns.append(a.alias())

                if a.column_name() in aggregate_columns_selected:
                    continue

                select.append(
                    Field(a.column_name(), table=pika_table, alias=a.column_alias())
                )
                aggregate_columns_selected.add(a.column_name())

            # Skip timeframes for this iteration
            # for t in table.timeframes():
            #     select.append(AnalysisHelper.periods(t._definition, table.sql_table_name))

        base_join_query = base_join_query.select(*select)

        # Iterativelly build the HDA query by starting with the base_join
        #  and then adding base_XXX and XXX_stats with clauses for each table
        #  involved in this query
        hda_query = Query.with_(base_join_query, "base_join")
        result_query = Query

        # precompute the group_by attributes that will be used in all intermediary
        # base_XXX and XXX_stats with clauses
        group_by_attributes = [c.alias() for t in self.tables for c in t.columns()]
        # Skip timeframes for this iteration
        # + [c.alias for c in table.timeframes()]

        result_query_base_table = None
        for j in self.join_order:
            # Find the table definition in the Query
            table = next((t for t in self.tables if t.name == j["table"]), None)

            # Skip tables that don't have at least a Column, Aggregate or
            #  Timeframe requested in the Query definition
            if not (table.columns() or table.aggregates() or table.timeframes()):
                continue

            # Generate the base_XXX with clause
            base_db_table = f"base_{j['table']}"

            select = list(
                set(
                    group_by_attributes
                    + [c.alias() for c in table.optional_pkeys]
                    + [c.column_alias() for c in table.aggregates()]
                )
            )

            base_query = Query.from_("base_join").select(*select).distinct()
            hda_query = hda_query.with_(base_query, base_db_table)

            # Generate the XXX_stats with clause
            stats_db_table = f"{j['table']}_stats"

            select = group_by_attributes
            select_aggregates = [
                a.qualified_sql(base_db_table) for a in table.aggregates()
            ]

            stats_query = (
                Query.from_(base_db_table)
                .select(*select)
                .select(*select_aggregates)
                .groupby(*group_by_attributes)
            )
            hda_query = hda_query.with_(stats_query, stats_db_table)

            stats_pika_table = Table(stats_db_table, alias=stats_db_table)

            if result_query_base_table:
                if group_by_attributes:
                    result_query = result_query.join(stats_pika_table).on_field(
                        *group_by_attributes
                    )
                else:
                    result_query = result_query.join(stats_pika_table).cross()
            else:
                result_query = result_query.from_(stats_pika_table)

                # Add the group_by attributes once in the result query with base
                #  table the first stats table
                result_group_by_attributes = []
                for a in group_by_attributes:
                    result_group_by_attributes.append(
                        Field(a, table=stats_pika_table, alias=a)
                    )

                result_query = result_query.select(*result_group_by_attributes)

                column_headers.extend(
                    [c.label for t in self.tables for c in t.columns()]
                )
                column_names.extend([c.name for t in self.tables for c in t.columns()])

                result_query_base_table = stats_db_table

            # Add the aggregates specific for this table to the result query
            table_aggregates = []
            for a in table.aggregates():
                table_aggregates.append(
                    Field(a.alias(), table=stats_pika_table, alias=a.alias())
                )

                column_headers.append(a.label)
                column_names.append(a.name)

            result_query = result_query.select(*table_aggregates)

        # Add the result and the Limit, Order By clauses to the final Query
        results_pika_table = Table("result", alias="result")

        hda_query = (
            hda_query.with_(result_query, "result")
            .from_(results_pika_table)
            .select("*")
            .limit(self.limit or 50)
        )

        # Add the Order By clause(s) for the final query
        if self.order:
            orderby = self.order.get("column", None)
            if self.order.get("direction", None) == "desc":
                order = Order.desc
            else:
                order = Order.asc

            try:
                orderby_field = next(
                    Field(t.get_column(orderby).alias(), table=results_pika_table)
                    for t in self.tables
                    if t.get_column(orderby)
                )
            except StopIteration:
                try:
                    orderby_field = next(
                        Field(
                            t.get_aggregate(orderby).alias(), table=results_pika_table
                        )
                        for t in self.tables
                        if t.get_aggregate(orderby)
                    )
                except StopIteration:
                    raise ParseError(
                        f"Requested Order By Attribute {orderby} is not defined in the design"
                    )

            hda_query = hda_query.orderby(orderby_field, order=order)
        else:
            # By default order by all the Group By attributes asc
            order = Order.asc
            orderby_fields = [
                Field(c.alias(), table=results_pika_table)
                for t in self.tables
                for c in t.columns()
            ]
            for field in orderby_fields:
                hda_query = hda_query.orderby(field, order=order)

        final_query = self.add_schema_to_hda_query(str(hda_query))
        return (final_query + ";", column_headers, column_names, aggregate_columns)

    def add_schema_to_hda_query(self, hda_query: str) -> str:
        """
        This is a temporary solution to address an issue in the way pypika
        validates join conditions.

        if you have a schema and an alias, the following SQL is perfectly fine:
            FROM "analytics"."table1" "table1"
            JOIN "analytics"."table2" "table2"
              ON "table1"."id1"="table2"."id2"

        But unfortunately, pypika considers that as not valid:
            pypika.utils.JoinException: Invalid join criterion.
            One field is required from the joined item and another from the
                selected table or an existing join.
            Found ["table1" "table1", "table2" "table2"]

        Until they allow for "join .. on" clauses to be able to use the alias
          of the tables, we have to construct the query without a schema and
          then add the schema by replacing the table name with schema.table
          Pretty ugly but the best we got at the moment.
        """
        if self.schema is None or self.schema == "":
            return hda_query

        schema_query = hda_query
        for join in self.join_order:
            if join["on"] is None:
                schema_query = schema_query.replace(
                    f'FROM "{join["table"]}"', f'FROM "{self.schema}"."{join["table"]}"'
                )
            else:
                schema_query = schema_query.replace(
                    f'JOIN "{join["table"]}"', f'JOIN "{self.schema}"."{join["table"]}"'
                )

        return schema_query
