import re

from datetime import datetime
from enum import Enum
from typing import Dict, List, Tuple
import networkx as nx
from copy import deepcopy

from pypika import functions as fn
from pypika import AliasedQuery, Query, Order, Table, Field, Criterion, Interval

from networkx.readwrite import json_graph


class ParseError(Exception):
    pass


class EmptyQuery(Exception):
    pass


class MeltanoFilterExpressionType(str, Enum):
    Unknown = "UNKNOWN"
    LessThan = "less_than"
    LessOrEqualThan = "less_or_equal_than"
    EqualTo = "equal_to"
    GreaterOrEqualThan = "greater_or_equal_than"
    GreaterThan = "greater_than"
    Like = "like"
    IsNull = "is_null"
    IsNotNull = "is_not_null"

    def __hash__(self):
        return hash(self.value)

    def __eq__(self, other):
        return self.value.lower() == other.value.lower()

    @classmethod
    def parse(cls, value: str):
        try:
            return next(e for e in cls if e.value.lower() == value)
        except StopIteration:
            return cls.Unknown


class MeltanoBase:
    def __init__(self, definition: Dict = {}):
        self._definition = definition

    def __getattr__(self, attr: str):
        return self._definition.get(attr, None)

    def __repr__(self):
        return f"<{self.__class__.__name__} name={self.name}>"


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
        tables = [
            MeltanoTable(self._definition.get("related_table", None), design=self)
        ]
        for join in self._definition.get("joins", []):
            table = MeltanoTable(join["related_table"], design=self)
            table.source_name = join["name"]
            tables.append(table)

        return tables

    def joins(self) -> List[MeltanoBase]:
        return [
            MeltanoJoin(definition, design=self)
            for definition in self._definition.get("joins", [])
        ]

    def get_table(self, name: str) -> MeltanoBase:
        return next(t for t in self.tables() if t.name == name)

    def get_join(self, name: str) -> MeltanoBase:
        return next(t for t in self.joins() if t.name == name)

    def find_table(self, name: str) -> MeltanoBase:
        try:
            return next(t for t in self.tables() if t.find_source_name() == name)
        except StopIteration:
            raise ParseError(f"Table {name} not found in design {self.name}")

    def find_attribute(self, key: str) -> MeltanoBase:
        try:
            return next(
                qa for t in self.tables() for qa in t.attributes() if qa.alias() == key
            )
        except StopIteration:
            raise ParseError(f"Attribute {key} not found in design {self.name}")

    def find_source_name(self, table_name: str) -> str:
        """
        Given the name of a table, get its source name:
        - If it is the base table for this design then return the name of the design
        - If it is part of a join then return the name of the join
        """
        if self._definition["related_table"]["name"] == table_name:
            return self.name

        try:
            return next(
                j["name"]
                for j in self._definition.get("joins", [])
                if j["related_table"]["name"] == table_name
            )
        except StopIteration:
            raise ParseError(f"Table {table_name} not found in design {self.name}")


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
        self.sql_table_name = definition.get("sql_table_name", None)

        # When a MeltanoTable is used as part of a MeltanoQuery,
        #  we also need to store the column definitions for not selected columns
        #  that have filters, so that we can use them when constructing the query
        self._unselected_columns_with_filters = []

        super().__init__(definition)

    def columns(self) -> List[MeltanoBase]:
        return [
            MeltanoColumn(definition=definition, table=self)
            for definition in self._definition.get("columns", [])
        ] + self._columns

    def unselected_columns_with_filters(self) -> List[MeltanoBase]:
        return self._unselected_columns_with_filters

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

    def timeframe_periods(self) -> List[MeltanoBase]:
        return [tp for timeframe in self.timeframes() for tp in timeframe.periods()]

    def attributes(self) -> List[MeltanoBase]:
        return (
            self.columns()
            + self.aggregates()
            + self.timeframes()
            + self.timeframe_periods()
        )

    def get_column(self, name: str) -> MeltanoBase:
        return next((c for c in self.columns() if c.name == name), None)

    def get_aggregate(self, name: str) -> MeltanoBase:
        return next((a for a in self.aggregates() if a.name == name), None)

    def get_aggregate_by_column_name(self, name: str) -> MeltanoBase:
        return next((a for a in self.aggregates() if a.column_name() == name), None)

    def get_timeframe(self, name: str) -> MeltanoBase:
        return next((t for t in self.timeframes() if t.name == name), None)

    def get_attribute(self, name: str) -> MeltanoBase:
        """
        Given an attribute name, find if there is a column / aggregate / timeframe
         with that name and return it
        """
        if self.get_column(name):
            return self.get_column(name)
        elif self.get_aggregate(name):
            return self.get_aggregate(name)
        elif self.get_timeframe(name):
            return self.get_timeframe(name)
        else:
            raise ParseError(f"Attribute {name} not found in Meltano Table {self.name}")

    def add_column(self, column) -> None:
        self._columns.append(column)

    def add_column_with_filter(self, column) -> None:
        self._unselected_columns_with_filters.append(column)

    def add_aggregate(self, aggregate) -> None:
        self._aggregates.append(aggregate)

    def add_timeframe(self, timeframe) -> None:
        self._timeframes.append(timeframe)

    def find_source_name(self) -> str:
        """
        Get the source name for this table:
        (1) if a source name has been set for this table then return that name
        (2) Otherwise, if it is defined in a design, then get it from the design
        (3) Finally, default to MeltanoTable.name if everything else is missing
        """
        if self.source_name:
            return self.source_name
        elif self.design:
            return self.design.find_source_name(self.name)
        else:
            return self.name

    def copy_metadata(self, other_table) -> None:
        self.name = other_table.name
        self.sql_table_name = other_table.sql_table_name
        self.source_name = other_table.source_name

    def __getattr__(self, attr: str):
        try:
            return self._attributes[attr]
        except KeyError:
            return super().__getattr__(attr)

    def __setattr__(self, name, value):
        if name == "sql_table_name":
            if value is not None:
                try:
                    schema, name = value.split(".")
                    self._attributes["schema"] = schema
                    self._attributes["sql_table_name"] = name
                except ValueError:
                    self._attributes["schema"] = None
                    self._attributes["sql_table_name"] = value
        elif name in ["name", "schema", "source_name"]:
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
        self.attribute_type = "column"

        # Used for manually setting the metadata attributes {label, name, type, primary_key, hidden, sql}
        self._attributes = {}

        super().__init__(definition)

    def alias(self) -> str:
        return f"{self.table.find_source_name()}.{self.column_name()}"

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

    def __repr__(self):
        return f"<{self.__class__.__name__} name={self.name}, alias={self.alias()}>"


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
        self.attribute_type = "aggregate"

        # Used for manually setting the metadata attributes {name, type, label, description, sql}
        self._attributes = {}

        super().__init__(definition)

    def alias(self) -> str:
        return f"{self.table.find_source_name()}.{self.name}"

    def qualified_sql(self, base_table: str = None, pika_table=None) -> fn.Coalesce:
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
        if pika_table:
            field = Field(self.column_name(), table=pika_table)
        elif base_table and base_table != self.table.find_source_name():
            sql = re.sub(
                "\{\{TABLE\}\}",
                self.table.find_source_name(),
                self.sql,
                flags=re.IGNORECASE,
            )
            field = Field(sql, table=Table(base_table))
        else:
            table = Table(self.table.find_source_name())
            field = Field(self.column_name(), table=table)

        if self.type == "sum":
            return fn.Coalesce(fn.Sum(field), 0, alias=self.alias())
        elif self.type == "count":
            return fn.Coalesce(fn.Count(field), 0, alias=self.alias())
        elif self.type == "avg":
            return fn.Coalesce(fn.Avg(field), 0, alias=self.alias())
        elif self.type == "max":
            return fn.Coalesce(fn.Max(field), 0, alias=self.alias())
        elif self.type == "min":
            return fn.Coalesce(fn.Min(field), 0, alias=self.alias())

    def column_name(self) -> str:
        (table, column) = self.sql.split(".")
        return column

    def column_alias(self) -> str:
        return f"{self.table.find_source_name()}.{self.column_name()}"

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
      {name, periods:[], label, description, sql}
    """

    def __init__(self, table: MeltanoTable, definition: Dict = {}) -> None:
        self.table = table
        self.attribute_type = "timeframe"

        # Used for manually setting the metadata attributes
        #  {name, periods:[], label, description, sql}
        self._attributes = {}
        self._periods = definition.get("periods", [])

        super().__init__(definition)

    def periods(self) -> List[MeltanoBase]:
        return [
            MeltanoTimeframePeriod(definition=definition, timeframe=self)
            for definition in self._periods
        ]

    def column_name(self) -> str:
        (table, column) = self.sql.split(".")
        return column

    def alias(self) -> str:
        return f"{self.table.find_source_name()}.{self.column_name()}"

    def copy_metadata(self, other_timeframe, requested_periods=None) -> None:
        """
        Copy the metadata from another timeframe, only keeping the
         periods defined by requested_periods.

        Allows us to copy everything from the Design, by keeping only the
         periods requested in a Query.
        """
        self.name = other_timeframe.name

        # Careful cause requested periods could be []
        if requested_periods is not None:
            self._periods = [
                period
                for request in requested_periods
                for period in other_timeframe._periods
                if (
                    (period["label"] == request["label"])
                    if "label" in request
                    else (period["name"] == request["name"])
                )
            ]
        else:
            self._periods = other_timeframe._periods

        self.label = other_timeframe.label
        self.description = other_timeframe.description
        self.sql = other_timeframe.sql

    def __getattr__(self, attr: str):
        try:
            return self._attributes[attr]
        except KeyError:
            return super().__getattr__(attr)

    def __setattr__(self, name, value):
        if name in ["name", "label", "description", "sql"]:
            self._attributes[name] = value
        else:
            super(MeltanoTimeframe, self).__setattr__(name, value)


class MeltanoTimeframePeriod(MeltanoBase):
    """
    An internal representation of a Timeframe period defined in a Table.

    It provides access to the metada for the Timeframe period:
      {name, label, part}
    """

    def __init__(self, timeframe: MeltanoTimeframe, definition: Dict = {}) -> None:
        self.timeframe = timeframe
        self.table = timeframe.table
        self.attribute_type = "timeframe_period"

        # Used for manually setting the metadata attributes
        #  {name, label, part}
        self._attributes = {}

        super().__init__(definition)

    def column_name(self) -> str:
        return f"{self.timeframe.column_name()}.{self.name}"

    def alias(self) -> str:
        return f"{self.timeframe.alias()}.{self.name}"

    def attribute_label(self) -> str:
        label = self.label or self.name

        if not label:
            raise ParseError(f"Requested period {period} has no name.")

        return f"{self.timeframe.label}: {label}"

    def qualified_sql(self, base_table: str = None, pika_table=None) -> fn.Coalesce:
        """
        Return the period as a fully qualified SQL clause defined as a pypika Extract clause

        The base_table defines whether the Extract is evaluated over its
          own table or an intermediary table (e.g. resulting from a with clause)

        Check MeltanoAggregate.qualified_sql() for more details
        """
        if pika_table:
            field = Field(self.timeframe.column_name(), table=pika_table)
        elif base_table and base_table != self.table.find_source_name():
            sql = re.sub(
                "\{\{TABLE\}\}",
                self.table.find_source_name(),
                self.timeframe.sql,
                flags=re.IGNORECASE,
            )
            field = Field(sql, table=Table(base_table))
        else:
            table = Table(self.table.find_source_name())
            field = Field(self.timeframe.column_name(), table=table)

        return fn.Extract(self.part, field, alias=self.alias())

    def __getattr__(self, attr: str):
        try:
            return self._attributes[attr]
        except KeyError:
            return super().__getattr__(attr)

    def __setattr__(self, name, value):
        if name in ["name", "label", "part"]:
            self._attributes[name] = value
        else:
            super(MeltanoTimeframePeriod, self).__setattr__(name, value)


class MeltanoJoin(MeltanoBase):
    """
    An internal representation of a Join defined in a Design.

    It provides access to the metada for the Join:
      {name, related_table, label, sql_on, relationship}
    """

    def __init__(self, definition: Dict = {}, design: MeltanoDesign = None) -> None:
        self.design = design
        super().__init__(definition)


class MeltanoFilter(MeltanoBase):
    """
    An internal representation of a Filter (WHERE or HAVING clause)
    defined in a MeltanoQuery.

    definition: {key, "expression", "value"}
    legacy definition: {"source_name", "name", "expression", "value"}

    Where:
    + "source name" is the way we call a table in a design:
      - If it is the base table for the design then it is name of the design
      - If it is part of a join then it is the name of the join
      The reason for that is that we can have the same table multiple times in
       a query (e.g. multiple joins or a self join of the base table with its self),
       so we use the source_name in order to know which version of the table we
       refer to.
    + "name" is the name of the attribute accessed (column, aggregate or timeframe)
    + "expression" is one of the supported expressions defined in MeltanoFilterExpressionType
    + "value" is the value we are going to use in the expression (for non unary expressions)

    In the most simple case, the idea is to use MeltanoFilter in order to generate a simple clause:
      table_alias.name {expression} value
    e.g. gitlab_stats_per_user.project_name = 'Meltano'
     or  COALESCE(SUM("gitlab_stats_per_user"."total_issues_authored"),0) > 5

    Because we are using this dynamically over various intermediary tables,
     in reality we use match(...) to find the Filters that match a specific attribute
     and then criterion(...) to generate the proper clause based on a Pypika Field
     (the Pypika Field knows at run time the table, the clause is evaluated against)

    It provides access to the metada for the Filter:
      {key, expression, value}
    """

    def __init__(
        self,
        definition: Dict = {},
        design: MeltanoDesign = None,
        pivot_date: str = None,
    ) -> None:
        definition = deepcopy(definition)

        # The design is used for filters in queries against specific designs
        #  to validate that all the tables and attributes (columns/aggregates)
        #  are properly defined in the design
        self.design = design

        self.expression_type = MeltanoFilterExpressionType.parse(
            definition["expression"]
        )

        self.validate(definition)

        # Some Query definitions may have a pivot_date set in the `today` param
        # We use that pivot_date to define relative date filter
        #  arounf that date and not NOW()
        self.pivot_date = pivot_date

        # Check if there are relative date filter definitions, parse them
        #  and generate the proper SQL clauses
        self.parse_relative_date_filters(definition)

        super().__init__(definition)

    def is_relative_date_expression(self, value: str) -> bool:
        """
        Check if a value is a relative date expression: [+-]N[dmy]
        """
        return value is not None and re.match("^[+-][0-9]+[dmy]$", f"{value}")

    def validate(self, definition: Dict) -> None:
        """
        Validate the Filter definition
        """

        source_name = definition.pop("source_name", None)
        attribute_name = definition.pop("name", None)
        if self.design and source_name is not None and attribute_name is not None:
            table_def = self.design.find_table(source_name)
            query_attribute = table_def.get_attribute(attribute_name)
            definition["key"] = query_attribute.alias()

        key = definition.get("key", None)
        if key is None:
            raise ParseError(
                f"An attribute key was not provided for filter '{definition}'."
            )

        if self.expression_type == MeltanoFilterExpressionType.Unknown:
            raise NotImplementedError(
                f"Unknown filter expression: {definition['expression']}."
            )

        if (
            definition.get("value", None) is None
            and self.expression_type != MeltanoFilterExpressionType.IsNull
            and self.expression_type != MeltanoFilterExpressionType.IsNotNull
        ):
            raise ParseError(
                f"Filter expression: {self.expression_type} needs a non-empty value."
            )

        if (
            self.is_relative_date_expression(definition.get("value", None))
            and not self.design
        ):
            raise ParseError(
                f"[+-]N[dmy] filter expressions require a design to be set for MeltanoFilter"
            )

        if self.design:
            # Will raise ParseError if not found
            attribute_def = self.design.find_attribute(key)

            if self.is_relative_date_expression(definition.get("value", None)):
                if attribute_def.attribute_type == "aggregate":
                    raise ParseError(
                        f"You can't use '[+-]N[dmy]' filter expressions with aggregate attributes"
                    )
                elif attribute_def.type not in ["date", "time"]:
                    raise ParseError(
                        f"[+-]N[dmy] filter expressions require a column atribute of type date or time"
                    )

    def parse_relative_date_filters(self, definition: Dict) -> None:
        """
        Check if there are relative date filter definitions: [+-]N[dmy]

        If so, parse them and generate the proper SQL clauses
        """
        if not self.is_relative_date_expression(definition.get("value", None)):
            # We only care about filter definitions of the type: [+-]N[dmy]
            return

        attribute_def = self.design.find_attribute(definition.get("key", None))

        old_value = definition.get("value", None)

        # Start from the Pivot Date: It can be a preset date or NOW()
        if self.pivot_date:
            pivot_date = fn.Date(self.pivot_date)
        else:
            pivot_date = fn.Date(fn.Now())

        # Then add/substract the Interval period (N) provided in [+-]N[dmy]
        interval_period = int(old_value[1:-1])

        if interval_period == 0:
            # If we have no interval period, we can really simplify the expression
            if attribute_def.type == "date":
                new_value = pivot_date
            elif attribute_def.type == "time":
                if self.expression_type == MeltanoFilterExpressionType.LessOrEqualThan:
                    new_value = (
                        pivot_date
                        + Interval(hours=23)
                        + Interval(minutes=59)
                        + Interval(seconds=59)
                        + Interval(microseconds=999_999)
                    )
                else:
                    new_value = pivot_date
        else:
            # If there is an interval set, use the [dmy] to generate the interval
            if "d" in old_value:
                interval = Interval(days=interval_period)
            elif "m" in old_value:
                interval = Interval(months=interval_period)
            elif "y" in old_value:
                interval = Interval(years=interval_period)

            # End then add or substract accordingly
            if attribute_def.type == "date":
                # Dates are simple as they are always set as they are
                # We just have to convert the timestamp expression to a Date
                if "+" in old_value:
                    new_value = fn.Date(pivot_date + interval)
                else:
                    new_value = fn.Date(pivot_date - interval)
            elif attribute_def.type == "time":
                # Timestamps are a little bit more involved in case of <= expressions
                if "+" in old_value:
                    new_value = pivot_date + interval
                else:
                    new_value = pivot_date - interval

                if self.expression_type == MeltanoFilterExpressionType.LessOrEqualThan:
                    new_value = (
                        new_value
                        + Interval(hours=23)
                        + Interval(minutes=59)
                        + Interval(seconds=59)
                        + Interval(microseconds=999_999)
                    )

        definition["value"] = new_value

    def match(self, attribute: MeltanoBase) -> bool:
        """
        Return True if this filter is defined for the given attribute
        """
        return self.key == attribute.alias()

    def criterion(self, field: Field) -> Criterion:
        """
        Generate the Pypika Criterion for this filter

        field: Pypika Field as we don't know the base table this filter is
                evaluated against (is it the base table or an intermediary table?)

        We have to use the following cases as PyPika does not allow an str
         representation of the clause on its where() and having() functions
        """
        criterion_strategies = {
            MeltanoFilterExpressionType.LessThan: lambda f: f < self.value,
            MeltanoFilterExpressionType.LessOrEqualThan: lambda f: f <= self.value,
            MeltanoFilterExpressionType.EqualTo: lambda f: f == self.value,
            MeltanoFilterExpressionType.GreaterOrEqualThan: lambda f: f >= self.value,
            MeltanoFilterExpressionType.GreaterThan: lambda f: f > self.value,
            MeltanoFilterExpressionType.Like: lambda f: f.like(self.value),
            MeltanoFilterExpressionType.IsNull: lambda f: f.isnull(),
            MeltanoFilterExpressionType.IsNotNull: lambda f: f.notnull(),
        }

        try:
            return criterion_strategies[self.expression_type](field)
        except KeyError:
            raise NotImplementedError(
                f"Unknown filter expression_type: {self.expression_type}."
            )


class MeltanoQuery(MeltanoBase):
    """
    An internal representation of a Query Definition sent to meltano for evaluation.

    The definition dictionary is parsed and the information is stored in a
    structured way:
     - Tables with only the Columns, Timeframes and Aggregates requested
     - Filters
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

        # A collection of all tables that are defined in the Query
        #  with the Columns, Timeframes and Aggregates defined in the Query
        self.tables = []

        # A collection of all the column and aggregate filters in the query
        # column_filters --> WHERE clauses that use columns selected in the query
        # aggregate_filters --> HAVING clauses that use aggregates computed in the query
        self.column_filters = []
        self.aggregate_filters = []

        # The proper join order that will be used for the query (list of table names)
        self.join_order = []

        self.validate_definition(definition)
        self.parse_definition(definition)

        super().__init__(definition)

    def validate_definition(self, definition: Dict) -> None:
        """
        Validate that the definition is properly formatted
        """

        self.validate_table_definition(definition)

        joins = definition.get("joins")
        if joins and not isinstance(joins, list):
            raise ParseError(f"Query definition property `joins` must be a list")

        for join_definition in joins:
            self.validate_table_definition(join_definition)

        order = definition.get("order")
        if order and not isinstance(order, list):
            raise ParseError(f"Query definition property `order` must be a list")

        filters = definition.get("filters", None)
        if filters:
            columns = filters.get("columns")
            if columns and not isinstance(columns, list):
                raise ParseError(
                    f"Query definition property `filters[columns]` must be a list"
                )

            aggregates = filters.get("aggregates")
            if aggregates and not isinstance(aggregates, list):
                raise ParseError(
                    f"Query definition property `filters[aggregates]` must be a list"
                )

    def validate_table_definition(self, definition: Dict) -> None:
        """
        Validate that the query definition for a specific table is properly formatted
        """
        if not isinstance(definition.get("name"), str):
            raise ParseError(f"Query definition property `name` must be a string")

        if not isinstance(definition.get("columns"), list):
            raise ParseError(f"Query definition property `columns` must be a list")

        if not isinstance(definition.get("aggregates"), list):
            raise ParseError(f"Query definition property `aggregates` must be a list")

        timeframes = definition.get("timeframes")
        if timeframes and not isinstance(timeframes, list):
            raise ParseError(f"Query definition property `timeframes` must be a list")

        if definition.get("today", None):
            try:
                datetime.strptime(definition.get("today", None), "%Y-%m-%d")
            except ValueError:
                raise ValueError("Incorrect pivot_date format, should be YYYY-MM-DD")

    def parse_definition(self, definition: Dict) -> None:
        """
        Parse the Query definition and generate the Tables, join_order, etc for
         easy access and lookups.
        """

        # Parse and store the pivot date provided in the Query definition
        pivot_date = definition.get("today", None)

        # Parse and store the provided filters
        filters = definition.get("filters", None)

        if filters:
            for column_filter in filters.get("columns", []):
                # Generate (and automaticaly validate) the filter and then store it
                mf = MeltanoFilter(
                    definition=column_filter, design=self.design, pivot_date=pivot_date
                )
                self.column_filters.append(mf)

            for aggregate_filter in filters.get("aggregates", []):
                # Generate (and automaticaly validate) the filter and then store it
                mf = MeltanoFilter(
                    definition=aggregate_filter,
                    design=self.design,
                    pivot_date=pivot_date,
                )
                self.aggregate_filters.append(mf)

        # Find the tables defined in the Query and add them as Table Objects
        #  with the proper Columns, Aggregates and Timeframe Objects
        primary_definition = {
            "name": definition.get("name", None),
            "columns": definition.get("columns", None),
            "aggregates": definition.get("aggregates", None),
            "timeframes": definition.get("timeframes", None),
        }
        related_definitions = [primary_definition] + definition.get("joins", [])

        # get the graph defined in the design: it is used for finding the
        #  shortest path and adding missing tables in case a required table
        #  is missing
        design_graph = json_graph.node_link_graph(self.design.graph)

        for related_def in related_definitions:
            # Find the requested table in the Design
            table_def = self.design.find_table(related_def["name"])

            if table_def:
                table = MeltanoTable(design=self.design)
                table.copy_metadata(table_def)

                # Add the columns
                for column in related_def.get("columns", []):
                    column_def = table_def.get_column(column)
                    if column_def:
                        c = MeltanoColumn(table=table)
                        c.copy_metadata(column_def)
                        table.add_column(c)
                    else:
                        raise ParseError(
                            f"Requested column {table.name}.{column} is not defined in the design"
                        )

                # Also add all the columns that are referenced in column filters
                #  for this table that are not also selected.
                # This is important in order to:
                # (1) Know that a join is required for a table with no selected columns
                # (2) Make available the missing column_def in get_query()
                for column_filter in self.column_filters:
                    # Will raise ParseError if not found
                    attribute_def = self.design.find_attribute(column_filter.key)
                    if (
                        attribute_def.attribute_type == "column"
                        and attribute_def.table.find_source_name()
                        == table.find_source_name()
                        and attribute_def.column_name()
                        not in related_def.get("columns", [])
                    ):
                        c = MeltanoColumn(table=table)
                        c.copy_metadata(attribute_def)
                        table.add_column_with_filter(c)

                # Add the aggregates
                for aggregate in related_def.get("aggregates", []):
                    aggregate_def = table_def.get_aggregate(aggregate)
                    if aggregate_def:
                        a = MeltanoAggregate(table=table)
                        a.copy_metadata(aggregate_def)
                        table.add_aggregate(a)
                    else:
                        raise ParseError(
                            f"Requested aggregate {table.name}.{aggregate} is not defined in the design"
                        )

                # Add the timeframes
                for timeframe in related_def.get("timeframes", []):
                    requested_periods = timeframe.get("periods", None)

                    timeframe_def = table_def.get_timeframe(timeframe.get("name", None))
                    if timeframe_def:
                        t = MeltanoTimeframe(table=table)
                        t.copy_metadata(timeframe_def, requested_periods)
                        table.add_timeframe(t)
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
                #  or a filter over a non selected column
                #  requested in the Query definition
                if related_def is not primary_definition and (
                    table.columns()
                    or table.aggregates()
                    or table.timeframes()
                    or table.unselected_columns_with_filters()
                ):
                    # Find the related joins needed to gather this data
                    #  Using the design graph, we can find the shortest path to a
                    #  table from the primary table up to any table in the design.
                    #
                    #  base_table → (join tables...) → target_table
                    new_joins = self.joins_for_table(
                        design_graph, primary_definition["name"], related_def["name"]
                    )

                    # filter out already defined joins
                    new_joins = list(
                        filter(
                            lambda t: t not in [j["name"] for j in self.join_order],
                            new_joins,
                        )
                    )

                    for join_name in new_joins:
                        if join_name == primary_definition["name"]:
                            continue

                        try:
                            join = self.design.get_join(join_name)
                            join_on = self.design_helper.join_for(join._definition)[
                                "on"
                            ]

                            self.join_order.append(
                                {
                                    "name": join_name,
                                    "table": join.related_table["name"],
                                    "on": join_on,
                                }
                            )
                        except StopIteration:
                            raise ParseError(
                                f"Requested join {join} is not defined in the design"
                            )

                # Take care care for the single table, no join query case
                if not self.join_order:
                    self.join_order.append(
                        {
                            "name": primary_definition["name"],
                            "table": table.name,
                            "on": None,
                        }
                    )
            else:
                raise ParseError(
                    f"Requested table {related_table.get('name', None)} is not defined in the design"
                )

    def joins_for_table(self, design_graph, source_table: str, target_table: str):
        return nx.shortest_path(design_graph, source=source_table, target=target_table)

    def needs_hda(self) -> bool:
        """
        Check if this MeltanoQuery needs to generate an HDA query or not
        """
        has_join_columns = next(
            filter(lambda x: len(x.get("columns", [])), self._definition["joins"]), None
        )

        has_join_timeframes = next(
            filter(lambda x: len(x.get("timeframes", [])), self._definition["joins"]),
            None,
        )

        has_join_aggregates = next(
            filter(lambda x: len(x.get("aggregates", [])), self._definition["joins"]),
            None,
        )

        has_base_table_aggregate = len(self._definition.get("aggregates", []))

        if not has_join_columns and not has_join_timeframes and not has_join_aggregates:
            # A query that references no columns or aggregates from the joined
            #  tables does not need an HDA
            return False
        else:
            # Even if there are joins needed, switch to an HDA only if aggregates
            #  will be computed.
            return has_base_table_aggregate or has_join_aggregates

    def get_query(self) -> Tuple:
        """
        Return the SQL query for this Query definition.

        Returns a Tuple (sql, query_attributes, aggregate_columns)
        - sql: A string with the SQL:1999 compatible query
        - query_attributes: Array of hashes describing the attributes in the
           final result in the same order as the one defined by the query.
           Keys included in the hash:
           {table_name, source_name, attribute_name, attribute_label, attribute_type}
        - aggregate_columns: Array of hashes describing the aggregate columns.
           Keys included in the hash: {id, label, source}
        """
        if self.needs_hda():
            sql, query_attributes, aggregate_columns = self.hda_query()
        else:
            sql, query_attributes, aggregate_columns = self.single_table_query()

        if sql:
            sql = sql + ";"
        else:
            raise EmptyQuery

        return (sql, query_attributes, aggregate_columns)

    def single_table_query(self) -> Tuple:
        """
        Build a simple, no-join SQL query for this Query definition.

        Returns a Tuple (sql, query_attributes, aggregate_columns)
        - sql: A string with the SQL:1999 compatible query
        - query_attributes: Array of hashes describing the attributes in the
           final result in the same order as the one defined by the query.
           Keys included in the hash:
           {table_name, source_name, attribute_name, attribute_label, attribute_type}
        - aggregate_columns: Array of hashes describing the aggregate columns.
           Keys included in the hash: {id, label, source}
        """

        # Lists with the column names and headers of the final result when the
        #  query is executed
        query_attributes = []
        aggregate_columns = []

        select = []
        select_aggregates = []
        group_by_attributes = []

        where = []
        having = []

        base_query = Query

        # Start By building the Join
        for join in self.join_order:
            table = next(
                iter([t for t in self.tables if t.find_source_name() == join["name"]]),
                None,
            )
            # Create a pypika Table based on the Table's name
            pika_table = Table(table.sql_table_name, alias=table.find_source_name())

            if join["on"] is None:
                base_query = base_query.from_(pika_table)
            else:
                base_query = base_query.join(pika_table).on(join["on"])

            # Add all columns in the SELECT clause and as group_by attributes
            for c in table.columns():
                select.append(Field(c.column_name(), table=pika_table, alias=c.alias()))
                group_by_attributes.append(Field(c.alias()))

                query_attributes.append(
                    {
                        "key": c.alias(),
                        "table_name": table.name,
                        "source_name": table.find_source_name(),
                        "attribute_name": c.name,
                        "attribute_label": c.label,
                        "attribute_type": c.type,
                    }
                )

            # Add the WHERE clauses using the column filters for this table
            for c in table.columns() + table.unselected_columns_with_filters():
                matching_criteria = [
                    f.criterion(Field(c.column_name(), table=pika_table))
                    for f in self.column_filters
                    if f.match(c)
                ]
                where.extend(matching_criteria)

            # Add the timeframe columns in the SELECT clause and as group_by attributes
            for tp in table.timeframe_periods():
                select.append(tp.qualified_sql(pika_table=pika_table))
                group_by_attributes.append(Field(tp.alias()))

                query_attributes.append(
                    {
                        "key": tp.alias(),
                        "table_name": table.name,
                        "source_name": table.find_source_name(),
                        "attribute_name": tp.column_name(),
                        "attribute_label": tp.attribute_label(),
                        "attribute_type": tp.type,
                    }
                )

            # Generate the Aggregate Clauses
            for a in table.aggregates():
                select_aggregates.append(a.qualified_sql(pika_table=pika_table))

                aggregate_columns.append(
                    {"id": a.alias(), "label": a.label, "source": table.name}
                )
                query_attributes.append(
                    {
                        "key": a.alias(),
                        "table_name": table.name,
                        "source_name": table.find_source_name(),
                        "attribute_name": a.name,
                        "attribute_label": a.label,
                        "attribute_type": a.type,
                    }
                )

                # Also check if there is a filter for this aggregate and add it
                #  in the HAVING clase
                for f in self.aggregate_filters:
                    if f.match(a):
                        field = a.qualified_sql(pika_table=pika_table)
                        # remove the alias before adding it to the having clause
                        field.alias = None
                        having.append(f.criterion(field))

        # Generate the query
        no_join_query = base_query.select(*select).select(*select_aggregates)

        if where:
            no_join_query = no_join_query.where(Criterion.all(where))

        no_join_query = no_join_query.groupby(*group_by_attributes)

        if having:
            # The check is necessary as PyPika does not accept in having()
            #  the EmptyCriterion that is generated by an empty array
            no_join_query = no_join_query.having(Criterion.all(having))

        # Add the Order By clause(s) for the final query
        if self.order:
            for order_clause in self.order:
                if order_clause.get("direction", None) == "desc":
                    order = Order.desc
                else:
                    order = Order.asc

                key = order_clause.get("key", None)
                if key is not None:
                    # Will raise ParseError if not found
                    query_attribute = self.design.find_attribute(key)
                else:
                    source_name = order_clause.get("source_name")
                    attribute_name = order_clause.get("attribute_name")

                    # Will raise ParseError if not found
                    table_def = self.design.find_table(source_name)
                    query_attribute = table_def.get_attribute(attribute_name)

                # this only works if the field is present in the Select statement
                orderby_field = Field(query_attribute.alias())

                no_join_query = no_join_query.orderby(orderby_field, order=order)
        else:
            # By default order by all the Group By attributes asc
            order = Order.asc
            for field in group_by_attributes:
                no_join_query = no_join_query.orderby(field, order=order)

        # Add a Limit (by default 50)
        no_join_query = no_join_query.limit(self.limit or 50)

        final_query = self.add_schema_to_query(str(no_join_query))

        return (final_query, query_attributes, aggregate_columns)

    def hda_query(self) -> Tuple:
        """
        Build the HDA SQL query for this Query definition.

        For more info on the process followed check the following:
        https://gitlab.com/meltano/meltano/issues/286
        https://gitlab.com/meltano/meltano/issues/344

        Returns a Tuple (sql, query_attributes, aggregate_columns)
        - sql: A string with the hda_query as a SQL:1999 compatible query
        - query_attributes: Array of hashes describing the attributes in the
           final result in the same order as the one defined by the query.
           Keys included in the hash:
           {table_name, source_name, attribute_name, attribute_label, attribute_type}
        - aggregate_columns: Array of hashes describing the aggregate columns.
           Keys included in the hash: {id, label, source}
        """

        # Lists with the column names and headers of the final result when the
        #  HDA query is executed
        query_attributes = []
        aggregate_columns = []

        where = []

        # Build the base_join table
        base_join_query = Query

        # Start By building the Join
        for join in self.join_order:
            table = next(
                iter([t for t in self.tables if t.find_source_name() == join["name"]]),
                None,
            )

            # Create a pypika Table based on the Table's name
            db_table = Table(table.sql_table_name, alias=table.find_source_name())

            if join["on"] is None:
                base_join_query = base_join_query.from_(db_table)
            else:
                base_join_query = base_join_query.join(db_table).on(join["on"])

        # precompute the group_by attributes that will be used in all intermediary
        # base_XXX and XXX_stats with clauses
        group_by_attributes = [c.alias() for t in self.tables for c in t.columns()]

        # Then Select all the columns that will be required in next steps
        # For each table all base columns, columns that will be used in aggregates,
        #  timeframes and the primary keys in case they are not already included
        select = []
        for table in self.tables:
            pika_table = Table(table.sql_table_name, alias=table.find_source_name())

            # Add the WHERE clauses using the column filters for this table
            for c in table.columns() + table.unselected_columns_with_filters():
                matching_criteria = [
                    f.criterion(Field(c.column_name(), table=pika_table))
                    for f in self.column_filters
                    if f.match(c)
                ]
                where.extend(matching_criteria)

            if not (table.columns() or table.aggregates() or table.timeframes()):
                # Skip tables that don't have at least a Column, Aggregate or
                #  Timeframe requested in the Query definition
                continue

            # We have to track wich columns have been added to the SELECT clause
            #  for being used in Aggregates as it is valid to have multiple
            #  Aggregates over the same column (e.g. AVG(price), SUM(price))
            # In that case, we don't want to add the column multiple times in the
            #  select clause cause will cause an Error in followup with clauses:
            #  Error: column reference {COLUMN} is ambiguous
            # There is also the very rare but syntactically correct case of adding
            #  a column both as a group by column and using an Aggregate.
            groupby_columns_selected = set()
            aggregate_columns_selected = set()

            for c in table.columns() + table.optional_pkeys:
                select.append(Field(c.column_name(), table=pika_table, alias=c.alias()))
                groupby_columns_selected.add(c.column_name())

            for a in table.aggregates():
                if (a.column_name() in groupby_columns_selected) or (
                    a.column_name() in aggregate_columns_selected
                ):
                    continue

                select.append(
                    Field(a.column_name(), table=pika_table, alias=a.column_alias())
                )
                aggregate_columns_selected.add(a.column_name())

            for tp in table.timeframe_periods():
                select.append(tp.qualified_sql(pika_table=pika_table))
                group_by_attributes.append(tp.alias())

                query_attributes.append(
                    {
                        "key": tp.alias(),
                        "table_name": table.name,
                        "source_name": table.find_source_name(),
                        "attribute_name": tp.column_name(),
                        "attribute_label": tp.attribute_label(),
                        "attribute_type": tp.type,
                    }
                )

        base_join_query = base_join_query.select(*select)

        if where:
            base_join_query = base_join_query.where(Criterion.all(where))

        # Iterativelly build the HDA query by starting with the base_join
        #  and then adding base_XXX and XXX_stats with clauses for each table
        #  involved in this query
        hda_query = Query.with_(base_join_query, "base_join")
        result_query = Query

        result_query_base_table = None
        for j in self.join_order:
            # Find the table definition in the Query
            table = next(
                (t for t in self.tables if t.find_source_name() == j["name"]), None
            )

            # Skip tables that don't have at least a Column, Aggregate or
            #  Timeframe requested in the Query definition
            if not (table.columns() or table.aggregates() or table.timeframes()):
                continue

            # Generate the base_XXX with clause
            base_db_table = f"base_{j['name']}"

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
            stats_db_table = f"{j['name']}_stats"

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

            # Add a Having Clause
            having = []

            for a in table.aggregates():
                for f in self.aggregate_filters:
                    if f.match(a):
                        field = a.qualified_sql(base_db_table)
                        # remove the alias before adding it to the having clause
                        field.alias = None
                        having.append(f.criterion(field))

            if having:
                stats_query = stats_query.having(Criterion.all(having))

            # Add the Stats with clause to the hda query
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

                for t in self.tables:
                    for c in t.columns():
                        query_attributes.append(
                            {
                                "key": c.alias(),
                                "table_name": t.name,
                                "source_name": t.find_source_name(),
                                "attribute_name": c.name,
                                "attribute_label": c.label,
                                "attribute_type": c.type,
                            }
                        )

                result_query_base_table = stats_db_table

            # Add the aggregates specific for this table to the result query
            table_aggregates = []
            for a in table.aggregates():
                table_aggregates.append(
                    Field(a.alias(), table=stats_pika_table, alias=a.alias())
                )

                aggregate_columns.append(
                    {"id": a.alias(), "label": a.label, "source": table.name}
                )

                query_attributes.append(
                    {
                        "key": a.alias(),
                        "table_name": table.name,
                        "source_name": table.find_source_name(),
                        "attribute_name": a.name,
                        "attribute_label": a.label,
                        "attribute_type": a.type,
                    }
                )

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
            for order_clause in self.order:
                if order_clause.get("direction", None) == "desc":
                    order = Order.desc
                else:
                    order = Order.asc

                key = order_clause.get("key", None)
                if key is not None:
                    # Will raise ParseError if not found
                    query_attribute = self.design.find_attribute(key)
                else:
                    source_name = order_clause.get("source_name")
                    attribute_name = order_clause.get("attribute_name")

                    # Will raise ParseError if not found
                    table_def = self.design.find_table(source_name)
                    query_attribute = table_def.get_attribute(attribute_name)

                # this only works if the field is present in the Select statement
                orderby_field = Field(query_attribute.alias(), table=results_pika_table)

                hda_query = hda_query.orderby(orderby_field, order=order)
        else:
            # By default order by all the Group By attributes asc
            order = Order.asc
            for attr in group_by_attributes:
                field = Field(attr, table=results_pika_table)
                hda_query = hda_query.orderby(field, order=order)

        final_query = self.add_schema_to_query(str(hda_query))

        return (final_query, query_attributes, aggregate_columns)

    def add_schema_to_query(self, query: str) -> str:
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
            return query

        schema_query = query
        for join in self.join_order:
            table = next(
                (t for t in self.tables if t.find_source_name() == join["name"]), None
            )

            if join["on"] is None:
                schema_query = schema_query.replace(
                    f'FROM "{table.sql_table_name}"',
                    f'FROM "{self.schema}"."{table.sql_table_name}"',
                )
            else:
                schema_query = schema_query.replace(
                    f'JOIN "{table.sql_table_name}"',
                    f'JOIN "{self.schema}"."{table.sql_table_name}"',
                )

        return schema_query
