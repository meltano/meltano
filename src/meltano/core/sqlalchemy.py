from __future__ import annotations  # noqa: D100

import datetime
import json
import typing as t
import uuid

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import mapped_column
from sqlalchemy.types import CHAR, INTEGER, VARCHAR, DateTime, TypeDecorator


class JSONEncodedDict(TypeDecorator):
    """Represents an immutable structure as a json-encoded string.

    Usage:
        JSONEncodedDict(VARCHAR_LENGTH)
    """

    impl = VARCHAR
    cache_ok = True

    def process_bind_param(  # noqa: ANN201, D102
        self,
        value,  # noqa: ANN001
        dialect,  # noqa: ANN001, ARG002
    ):
        if value is not None:
            value = json.dumps(value)

        return value

    def process_result_value(  # noqa: ANN201, D102
        self,
        value,  # noqa: ANN001
        dialect,  # noqa: ANN001, ARG002
    ):
        if value is not None:
            value = json.loads(value)
        return value


class IntFlag(TypeDecorator):  # noqa: D101
    impl = INTEGER
    cache_ok = True

    # force the cast to INTEGER
    def process_bind_param(  # noqa: ANN201, D102
        self,
        value,  # noqa: ANN001
        dialect,  # noqa: ANN001, ARG002
    ):
        return int(value)


class GUID(TypeDecorator):
    """Platform-independent GUID type.

    Uses PostgreSQL's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.

    Reference:
    https://docs.sqlalchemy.org/en/13/core/custom_types.html#backend-agnostic-guid-type
    """

    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):  # noqa: ANN001, ANN201, D102
        if dialect.name == "postgresql":
            return dialect.type_descriptor(UUID())
        type_descriptor_length = 32
        return dialect.type_descriptor(CHAR(type_descriptor_length))

    def process_bind_param(self, value, dialect):  # noqa: ANN001, ANN201, D102
        if value is None:
            return value
        if dialect.name == "postgresql":
            return str(value)
        if not isinstance(value, uuid.UUID):
            value = uuid.UUID(value)
        return value.hex

    def process_result_value(  # noqa: ANN201, D102
        self,
        value,  # noqa: ANN001
        dialect,  # noqa: ANN001, ARG002
    ):
        if value is None:
            return value
        if not isinstance(value, uuid.UUID):
            value = uuid.UUID(value)
        return value


class DateTimeUTC(TypeDecorator):
    """Parses datetimes timezone-aware and stores them as UTC."""

    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value: datetime.datetime | None, _dialect: str):  # noqa: ANN201
        """Convert the datetime value to UTC and remove the timezone.

        Args:
            value: The datetime value to convert.

        Returns:
            The converted datetime value.
        """
        if value is None:
            return None

        if value.tzinfo:
            value = value.astimezone(datetime.timezone.utc)
        return value.replace(tzinfo=None)

    def process_result_value(self, value: datetime.datetime | None, _dialect: str):  # noqa: ANN201
        """Convert the naive datetime value to UTC.

        Args:
            value: The datetime value to convert.

        Returns:
            The converted datetime value.
        """
        if value is not None:
            value = value.replace(tzinfo=datetime.timezone.utc)
        return value


GUIDType = t.Annotated[uuid.UUID, mapped_column(GUID, default=uuid.uuid4)]
StateType = t.Annotated[
    dict[str, str],
    mapped_column(MutableDict.as_mutable(JSONEncodedDict)),
]
IntPK = t.Annotated[int, mapped_column(primary_key=True)]
StrPK = t.Annotated[str, mapped_column(primary_key=True)]
