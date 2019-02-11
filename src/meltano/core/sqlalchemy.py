from sqlalchemy.types import TypeDecorator, VARCHAR, INTEGER
import json


class JSONEncodedDict(TypeDecorator):
    """Represents an immutable structure as a json-encoded string.

    Usage::
        JSONEncodedDict(255)
    """

    impl = VARCHAR

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)

        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


class IntFlag(TypeDecorator):
    impl = INTEGER

    # force the cast to INTEGER
    def process_bind_param(self, value, dialect):
        return int(value)
