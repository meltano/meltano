import re
from collections import namedtuple
from enum import Enum

from pypika import Field, Case


class SubstitutionType(Enum):
    unknown = "UNKNOWN"
    table = "TABLE"
    dimension = "DIMENSION"
    view_dimension = "VIEW_DIMENSION"
    view_sql_table_name = "VIEW_SQL_TABLE_NAME"


class Substitution:
    def __init__(self, _input, table, dimension=None, alias=None):
        self.input = _input
        self.alias = alias
        self.sql = None
        self.table = table

        if not dimension:
            self.type = "string"
        else:
            self.type = dimension.settings["type"]

        self.substitution_type = SubstitutionType.unknown
        self.get_substitution_type()
        self.placeholders = Substitution.placeholder_match(self.input)
        self.set_sql()

    def get_substitution_type(self):
        # trying guess the substitution_type in a cheap way
        if "." in self.input and "${TABLE}" not in self.input:
            if "SQL_TABLE_NAME" in self.input:
                self.substitution_type = SubstitutionType.view_sql_table_name
            else:
                self.substitution_type = SubstitutionType.view_dimension
        elif "${TABLE}" in self.input:
            self.substitution_type = SubstitutionType.table
        elif " " not in self.input:
            self.substitution_type = SubstitutionType.dimension
        else:
            self.substitution_type = SubstitutionType.unknown

    @staticmethod
    def placeholder_match(input_):
        outer_pattern = r"(\$\{[\w\.]*\})"
        inner_pattern = r"\$\{([\w\.]*)\}"
        outer_results = re.findall(outer_pattern, input_)
        inner_results = re.findall(inner_pattern, input_)
        Results = namedtuple("Results", "inner outer")
        return Results(inner=inner_results, outer=outer_results)

    def set_sql(self):
        if self.substitution_type is SubstitutionType.table:
            self.set_sql_table_type()
        else:
            raise Exception(
                f"Substitution Type {self.substitution_type.value} not implemented yet"
            )

    def set_sql_table_type(self):
        self.sql = self.input.replace(
            self.placeholders.outer[0], self.table._table_name
        )
        (table, field) = self.sql.split(".")
        if not self.alias:
            self.alias = self.sql
        if self.type == "yesno":
            field = Field(field, table=self.table)
            self.sql = Case(alias=self.sql).when(field, "yes").else_("no")
        else:
            self.sql = Field(field, table=self.table, alias=self.sql)
