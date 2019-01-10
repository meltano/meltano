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
    def dimensions_from_names(dimensions, table):
        return list(filter(lambda x: x["name"] in dimensions, table["dimensions"]))

    # TODO: dedup this non dry situation
    @staticmethod
    def measures_from_names(measures, table):
        return list(filter(lambda x: x["name"] in measures, table["measures"]))

    @staticmethod
    def dimensions(dimensions, table):
        return [AnalysisHelper.field_from_dimension(d, table) for d in dimensions]

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
    def field_from_dimension(d, table):
        sql = d["sql"]
        substitution = Substitution(sql, table, dimension=d)
        return substitution.sql
