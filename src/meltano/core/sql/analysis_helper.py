from pypika import Table

from .substitution import Substitution
from .aggregate import Aggregate
from .substitution import Substitution
from .timeframe import TimeframePeriod


class AnalysisHelper:
    @staticmethod
    def db_table(name, **kwargs):
        try:
            schema, name = name.split(".")
            options = kwargs
            options["schema"] = schema
            return Table(name, **options)
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
    def timeframe_periods_from_names(cls, timeframe_name, period_names, table):
        timeframe = next(
            timeframe
            for timeframe in table["timeframes"]
            if timeframe["name"] == timeframe_name
        )

        # filter out non-selected periods
        periods = [
            period for period in timeframe["periods"] if period["label"] in period_names
        ]

        return timeframe, periods

    @classmethod
    def columns(cls, columns, db_table):
        return [cls.field_from_column(d, db_table) for d in columns]

    @classmethod
    def aggregates(cls, aggregates, db_table):
        return [
            cls.field_from_aggregate(aggregate, db_table) for aggregate in aggregates
        ]

    @classmethod
    def periods(cls, timeframes, db_table):
        return [
            cls.field_from_timeframe_period(timeframe["timeframe"], period, db_table)
            for timeframe in timeframes
            for period in timeframe["periods"]
        ]

    @classmethod
    def field_from_aggregate(cls, aggregate, db_table):
        return Aggregate(aggregate, db_table).sql

    @classmethod
    def field_from_column(cls, d, db_table):
        return Substitution(d["sql"], db_table, column=d).sql

    @classmethod
    def field_from_timeframe_period(cls, timeframe, period, db_table):
        return TimeframePeriod(timeframe, period, db_table).sql
