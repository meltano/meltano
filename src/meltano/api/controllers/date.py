from pypika import Field, functions as fn
from pypika.terms import Function


class DateTrunc(Function):
    def __init__(self, part, term, alias=None):
        super(DateTrunc, self).__init__("DATE_TRUNC", part, term, alias=alias)


class Date:
    def __init__(self, timeframe, table, name):
        self.sql = None
        field = Field(name, table=table)
        if timeframe == "date*":
            alias = "{}_date".format((field.get_sql().replace("_", "")))
            self.sql = fn.Date(field, alias=alias)
        elif timeframe == "month*":
            alias = "{}_month".format((field.get_sql().replace("_", "")))
            self.sql = fn.ToChar(DateTrunc("month", field), "YYYY-MM", alias=alias)
        elif timeframe == "week*":
            alias = "{}_week".format((field.get_sql().replace("_", "")))
            self.sql = fn.ToChar(DateTrunc("week", field), "YYYY-MM-DD", alias=alias)
        elif timeframe == "year*":
            alias = "{}_year".format((field.get_sql().replace("_", "")))
            self.sql = fn.Extract("YEAR", field, alias=alias)
