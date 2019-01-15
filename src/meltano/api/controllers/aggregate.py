from enum import Enum

from pypika import functions as fn

from .substitution import Substitution


class AggregateType(Enum):
    unknown = "UNKNOWN"
    count = "count"
    sum = "sum"
    number = "number"


class Aggregate:
    def __init__(self, aggregate, table):
        sql = aggregate["sql"]
        self.substitution = Substitution(sql, table, None, aggregate["name"])
        self.aggregate = aggregate
        self.field = Substitution(
            aggregate["sql"], db_table, None, alias=aggregate["name"]
        )
        self.aggregate_type = AggregateType.parse(aggregate["type"])

    @property
    def alias(self):
        return f"{self.field.table.alias}.{self.aggregate['name']}"

    @property
    def sql(self):
        if self.aggregate_type == AggregateType.Unknown:
            raise NotImplementedError(f"Unknown aggregate type.")

        return getattr(self, self.aggregate_type.value)()

    def sum(self):
        return fn.Coalesce(fn.Sum(self.field.sql), 0, alias=self.alias)

    def count(self):
        return fn.Coalesce(fn.Count(self.field.sql), 0, alias=self.alias)

    def number(self):
        self.field.alias = self.field.alias
        return self.field.sql
