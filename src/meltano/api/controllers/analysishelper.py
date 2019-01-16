from .substitution import Substitution
from pypika import Table

from .aggregate import Aggregate


class AnalysisHelper:
    @staticmethod
    def table(name, alias):
        try:
            (schema, name) = name.split(".")
            return Table(name, schema=schema, alias=alias)
        except ValueError:
            return Table(name, alias=alias)

    @staticmethod
    def columns_from_names(columns, table):
        return list(filter(lambda x: x["name"] in columns, table["columns"]))

    # TODO: dedup this non dry situation
    @staticmethod
    def aggregates_from_names(aggregates, table):
        return list(filter(lambda x: x["name"] in aggregates, table["aggregates"]))

    @staticmethod
    def columns(columns, table):
        return [AnalysisHelper.field_from_column(d, table) for d in columns]

    @staticmethod
    def aggregates(aggregates, table):
        return [
            AnalysisHelper.field_from_aggregate(aggregate, table)
            for aggregate in aggregates
        ]

    @staticmethod
    def field_from_aggregate(aggregate, table):
        aggregate = Aggregate(aggregate, table)
        return aggregate.sql

    @staticmethod
    def field_from_column(d, table):
        sql = d["sql"]
        substitution = Substitution(sql, table, column=d)
        return substitution.sql
