from .substitution import Substitution
from pypika import Table


class AnalysisHelper:
    @staticmethod
    def table(name, alias):
        (schema, name) = name.split(".")
        return Table(name, schema=schema, alias=alias)

    @staticmethod
    def dimensions_from_names(dimensions, view):
        return list(filter(lambda x: x.name in dimensions, view.dimensions))

    # TODO: dedup this non dry situation
    @staticmethod
    def measures_from_names(measures, view):
        return list(filter(lambda x: x.name in measures, view.measures))

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
        sql = d.settings["sql"]
        substitution = Substitution(sql, table, dimension=d)
        return substitution.sql
