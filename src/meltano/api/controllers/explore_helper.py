import logging
from enum import Enum
from copy import deepcopy
from typing import Dict

from .analysishelper import AnalysisHelper
from collections import namedtuple


import sqlparse
from functools import singledispatch
from sqlparse.sql import TokenList, Comparison

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
    print(node)


class InvalidIdentifier(Exception):
    pass


Identifier = namedtuple("Identifier", ("schema", "table", "field", "alias"))


class PypikaJoinExecutor:
    def __init__(self, explore, join):
        self.explore = explore
        self.join = join
        self.result = None

    def comparison(self, node, depth):
        view = self.join["related_view"]

        left = self.parse_identifier(node.left)
        right = self.parse_identifier(node.right)

        left_alias = self.join["name"] if left.table == self.join["name"] else None
        right_alias = self.join["name"] if right.table == self.join["name"] else None

        left_field = getattr(
            AnalysisHelper.table(
                view["sql_table_name"] if left_alias else left.table,
                schema=left.schema,
                alias=left_alias or left.alias or left.table,
            ),
            left.field,
        )

        right_field = getattr(
            AnalysisHelper.table(
                view["sql_table_name"] if right_alias else right.table,
                schema=right.schema,
                alias=right_alias or right.alias or right.table,
            ),
            right.field,
        )

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


class ExploreHelper:
    def __init__(self, explore):
        self.explore = explore

    @property
    def name(self):
        return self.explore["name"]

    @property
    def joins(self):
        return deepcopy(self.explore["joins"])

    @property
    def views(self):
        return deepcopy(self.explore["views"])

    def join_for(self, join_selection: Dict):
        join = self.get_join(self, join_selection["name"])
        view = join["related_view"]

        table = AnalysisHelper.table(view["sql_table_name"], alias=join["name"])
        selected = {"dimensions": [], "measures": []}

        try:
            selected["dimensions"] = AnalysisHelper.dimensions_from_names(
                join_selection["dimensions"], view
            )
        except KeyError:
            pass

        try:
            selected["measures"] = AnalysisHelper.measures_from_names(
                join_selection["measures"], view
            )
        except KeyError:
            pass

        join_executor = PypikaJoinExecutor(self, join)
        visit(sqlparse.parse(join["sql_on"])[0], join_executor)

        return {
            "view": view,
            "table": table,
            "on": join_executor.result,
            "join": join,
            **selected,
        }

    @classmethod
    def get_join(cls, explore, name):
        try:
            return next(join for join in explore.joins if join["name"] == name)
        except StopIteration:
            raise JoinNotFound(
                f"No join named '{name}' was found in explore '{explore.name}'."
            )

    def __getitem__(self, idx):
        return self.explore[idx]
