from enum import Enum

from pypika import functions as fn

from .substitution import Substitution


class AggregateType(Enum):
    unknown = "UNKNOWN"
    count = "count"
    sum = "sum"
    number = "number"


class Aggregate:
    def __init__(self, measure, table):
        sql = measure.settings["sql"]
        self.substitution = Substitution(sql, table, None, measure.name)
        self.measure = measure
        self.table = table
        self.sql = self.substitution.sql
        self.aggregateType = AggregateType.unknown
        self.getAggregateType()

    def getAggregateType(self):
        type_ = self.measure.settings["type"]
        if type_ == AggregateType.sum.value:
            self.aggregateType = AggregateType.sum
            self.setAggregateSQLSum()
        elif type_ == AggregateType.count.value:
            self.aggregateType = AggregateType.count
            self.setAggregateSQLCount()
        elif type_ == AggregateType.number.value:
            self.aggregateType = AggregateType.number
            self.setAggregateSQLNumber()
        else:
            self.aggregateType = AggregateType.unknown
            raise Exception(f"Aggregate Type {type_} not implemented yet")

    def setAggregateSQLSum(self):
        self.sql = fn.Coalesce(fn.Sum(self.sql), 0, alias=self.substitution.alias)

    def setAggregateSQLCount(self):
        self.sql = fn.Coalesce(fn.Count(self.sql), 0, alias=self.substitution.alias)

    def setAggregateSQLNumber(self):
        self.sql.alias = self.substitution.alias
