from pypika import functions as fn

from .substitution import Substitution


class TimeframePeriod:
    def __init__(self, timeframe, period, table):
        self.timeframe = timeframe
        self.period = period
        self.field = Substitution(
            timeframe["sql"], table, timeframe, alias=timeframe["name"]
        )

    @property
    def alias(self):
        return f"{self.timeframe['name']}.{self.period['label'].lower()}"

    @property
    def sql(self):
        return fn.Extract(self.period["label"], self.field.sql, alias=self.alias)
