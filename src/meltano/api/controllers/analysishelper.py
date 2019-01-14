from .substitution import Substitution
from pypika import Table

from .aggregate import Aggregate


class AnalysisHelper:
    @staticmethod
    def table(name, **kwargs):
        try:
            schema, name = name.split(".")
            return Table(name, schema=schema, **kwargs)
        except ValueError:
            return Table(name, **kwargs)

    @staticmethod
    def columns_from_names(columns, table):
        return list(filter(lambda x: x["name"] in columns, table["columns"]))

    # TODO: dedup this non dry situation
    @staticmethod
    def aggregates_from_names(aggregates, table):
        return list(filter(lambda x: x["name"] in aggregates, table["aggregates"]))

    @classmethod
    def columns(cls, columns, db_table):
        return [cls.field_from_column(d, db_table) for d in columns]

    @classmethod
    def timeframe_periods_from_names(cls, timeframe_name, period_names, table):
        timeframe = next(timeframe
                         for timeframe in table["timeframes"]
                         if timeframe["name"] == timeframe_name)

        # filter out non-selected periods
        periods = [period
                   for period in timeframe["periods"]
                   if period["label"] in period_names]

        return timeframe, periods

    @staticmethod
    def aggregates(aggregates, db_table):
        return [
            AnalysisHelper.field_from_aggregate(aggregate, db_table)
            for aggregate in aggregates
        ]

    @staticmethod
    def field_from_aggregate(aggregate, db_table):
        aggregate = Aggregate(aggregate, db_table)
        return aggregate.sql

    @staticmethod
    def field_from_column(d, db_table):
        sql = d["sql"]
        substitution = Substitution(sql, db_table, column=d)
        return substitution.sql
