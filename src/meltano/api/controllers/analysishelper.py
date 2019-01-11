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
    def measures_from_names(measures, table):
        return list(filter(lambda x: x["name"] in measures, table["measures"]))

    @staticmethod
    def columns(columns, table):
        return [AnalysisHelper.field_from_column(d, table) for d in columns]

    @staticmethod
    def measures(measures, table):
        return [
            AnalysisHelper.field_from_measure(measure, table) for measure in measures
        ]

    @staticmethod
    def field_from_measure(measure, table):
        aggregate = Aggregate(measure, table)
        return aggregate.sql

    @staticmethod
    def field_from_column(d, table):
        sql = d["sql"]
        substitution = Substitution(sql, table, column=d)
        return substitution.sql
