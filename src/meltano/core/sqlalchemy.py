from __future__ import annotations

import json
import uuid

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import CHAR, INTEGER, VARCHAR, TypeDecorator


class JSONEncodedDict(TypeDecorator):
    """Represents an immutable structure as a json-encoded string.

    Usage:
        JSONEncodedDict(VARCHAR_LENGTH)
    """

    impl = VARCHAR
    cache_ok = True

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
    cache_ok = True

    # force the cast to INTEGER
    def process_bind_param(self, value, dialect):
        return int(value)


class GUID(TypeDecorator):
    """Platform-independent GUID type.

    Uses PostgreSQL's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.

    Reference: https://docs.sqlalchemy.org/en/13/core/custom_types.html#backend-agnostic-guid-type
    """

    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(UUID())
        type_descriptor_length = 32
        return dialect.type_descriptor(CHAR(type_descriptor_length))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == "postgresql":
            return str(value)
        if not isinstance(value, uuid.UUID):
            value = uuid.UUID(value)
        return value.hex

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if not isinstance(value, uuid.UUID):
            value = uuid.UUID(value)
        return value
