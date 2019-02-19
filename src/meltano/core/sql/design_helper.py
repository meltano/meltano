import logging
import sqlparse

import networkx as nx

from copy import deepcopy
from collections import namedtuple
from enum import Enum
from functools import singledispatch
from networkx.readwrite import json_graph
from sqlparse.sql import TokenList, Comparison
from typing import Dict

from .base import MeltanoTable
from .analysis_helper import AnalysisHelper

# Visitor pattern on the SQL AST
@singledispatch
def visit(node, executor, depth=0):
    logging.debug(f"Visiting node {node}")


@visit.register(TokenList)
def _(node: TokenList, executor, depth=0):
    logging.debug(f"Visiting node {node}")
    for t in node.tokens:
        visit(t, executor, depth + 1)


@visit.register(Comparison)
def _(node: Comparison, executor, depth=0):
    logging.debug(f"Visiting node {node}")
    executor.comparison(node, depth)


class InvalidIdentifier(Exception):
    pass


Identifier = namedtuple("Identifier", ("schema", "table", "field", "alias"))

DimensionGroup = namedtuple("DimensionGroup", ("dimensions", "group"))

ComparisonFields = namedtuple("ComparisonFields", ("left", "right"))


class PypikaJoinExecutor:
    def __init__(self, design, join):
        self.design = design
        self.join = join
        self.result = None
        self.comparison_fields = None

    def set_comparison_fields(self, left, right):
        self.comparison_fields = ComparisonFields(left, right)

    def comparison(self, node, depth):
        table = self.join["related_table"]

        left = self.parse_identifier(node.left)
        right = self.parse_identifier(node.right)
        left_alias = self.join["name"] if left.table == self.join["name"] else None
        right_alias = self.join["name"] if right.table == self.join["name"] else None

        left_field = getattr(
            AnalysisHelper.db_table(
                table["sql_table_name"] if left_alias else left.table,
                schema=left.schema,
                alias=left_alias or left.alias or left.table,
            ),
            left.field,
        )

        right_field = getattr(
            AnalysisHelper.db_table(
                table["sql_table_name"] if right_alias else right.table,
                schema=right.schema,
                alias=right_alias or right.alias or right.table,
            ),
            right.field,
        )

        self.set_comparison_fields(left, right)

        # TODO: do a stack based approach to handle complex cases
        self.result = left_field == right_field

    @classmethod
    def parse_identifier(cls, identifier) -> Identifier:
        token_values = map(lambda t: t.value, identifier.tokens)

        # name, field
        if len(identifier.tokens) == 3:
            table, _, field = token_values
            return Identifier(None, table, field, None)

        # schema, name, field
        if len(identifier.tokens) == 5:
            schema, _, table, _, field = token_values
            return Identifier(schema, table, field, None)

        # schema, name, field, alias
        if len(identifier.tokens) == 7:
            schema, _, table, _, field, _, alias = token_values
            return Identifier(schema, table, field, alias)

        raise InvalidIdentifier(str(identifier))


class JoinNotFound(Exception):
    pass


class JoinType(Enum):
    left_join = "left"
    inner_join = "inner"
    full_outer_join = "full_outer"
    cross_join = "cross"


class DesignHelper:
    def __init__(self, design):
        self.design = design

    @property
    def name(self):
        return self.design["name"]

    @property
    def joins(self):
        return deepcopy(self.design["joins"])

    @property
    def tables(self):
        tables = [self.design["related_table"]]
        tables += [j["related_table"] for j in self.design["joins"]]
        return list(map(MeltanoTable, tables))

    @property
    def base_table_name(self):
        return self.design["related_table"]["name"]

    def joins_for_table(self, table_name: str):
        # get the graph for networkx
        G = json_graph.node_link_graph(self.design["graph"])
        return nx.shortest_path(G, source=self.base_table_name, target=table_name)

    def join_for(self, join_selection: Dict):
        join = self.get_join(self, join_selection["name"])
        table = join["related_table"]

        db_table = AnalysisHelper.db_table(table["sql_table_name"], alias=join["name"])
        selected = {"columns": [], "aggregates": [], "timeframes": []}

        try:
            selected["columns"] = AnalysisHelper.columns_from_names(
                join_selection["columns"], table
            )
        except KeyError:
            pass

        try:
            selected["aggregates"] = AnalysisHelper.aggregates_from_names(
                join_selection["aggregates"], table
            )
        except KeyError:
            pass

        try:
            selected["timeframes"] = [
                self.timeframe_periods_for(table, timeframe_selection)
                for timeframe_selection in join_selection["timeframes"]
            ]
        except KeyError:
            pass

        join_executor = PypikaJoinExecutor(self, join)
        visit(sqlparse.parse(join["sql_on"])[0], join_executor)

        return {
            "table": table,
            "db_table": db_table,
            "on": join_executor.result,
            "join": join,
            "name": join_selection["name"],
            **selected,
        }

    def timeframe_periods_for(self, table, timeframe_selection):
        timeframe_name = timeframe_selection["name"]
        period_names = [p["label"] for p in timeframe_selection["periods"]]

        db_table = AnalysisHelper.db_table(
            table["sql_table_name"], alias=timeframe_name
        )
        timeframe, periods = AnalysisHelper.timeframe_periods_from_names(
            timeframe_name, period_names, table
        )

        return {
            "table": table,
            "db_table": db_table,
            "timeframe": timeframe,
            "periods": periods,
            "period_labels": period_names,
        }

    @classmethod
    def get_join(cls, design, name):
        try:
            return next(join for join in design.joins if join["name"] == name)
        except StopIteration:
            raise JoinNotFound(
                f"No join named '{name}' was found in design '{design.name}'."
            )

    def __getitem__(self, idx):
        return self.design[idx]
