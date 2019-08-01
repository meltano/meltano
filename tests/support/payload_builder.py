class PayloadBuilder:
    def __init__(self, source_name: str, **kwargs):
        self._name = source_name
        self._columns = set()
        self._aggregates = set()
        self._joins = {}
        self._column_filters = []
        self._aggregate_filters = []
        self._order_by_clauses = []
        self._defaults = kwargs

    def join(self, name: str):
        if name not in self._joins:
            self._joins[name] = PayloadBuilder(name)

        return self._joins[name]

    def columns(self, *columns, join=None):
        if join:
            self.join(join).columns(*columns)
        else:
            self._columns.update(columns)

        return self

    def aggregates(self, *aggregates, join=None):
        if join:
            self.join(join).aggregates(*aggregates)
        else:
            self._aggregates.update(aggregates)

        return self

    def column_filter(self, table_name, name, expression, value):
        filter = {
            "table_name": table_name,
            "name": name,
            "expression": expression,
            "value": value,
        }
        self._column_filters.append(filter)

        return self

    def aggregate_filter(self, table_name, name, expression, value):
        filter = {
            "table_name": table_name,
            "name": name,
            "expression": expression,
            "value": value,
        }
        self._aggregate_filters.append(filter)

        return self

    def order_by(self, source_name, attribute_name, direction):
        order_by_clause = {
            "source_name": source_name,
            "attribute_name": attribute_name,
            "direction": direction,
        }
        self._order_by_clauses.append(order_by_clause)

        return self

    def as_join(self):
        return {
            "name": self._name,
            "columns": list(self._columns),
            "aggregates": list(self._aggregates),
        }

    @property
    def payload(self):
        payload = {
            "run": True,
            "name": self._name,
            "columns": list(self._columns),
            "aggregates": list(self._aggregates),
            "timeframes": [],
            "joins": [join.as_join() for join in self._joins.values()],
            "order": self._order_by_clauses,
            "limit": "50",
            "filters": {
                "columns": self._column_filters,
                "aggregates": self._aggregate_filters,
            },
        }

        payload.update(self._defaults)
        return payload
