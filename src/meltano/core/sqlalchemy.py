from __future__ import annotations  # noqa: D100

import datetime
import json
import typing as t
import uuid

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import mapped_column
from sqlalchemy.types import CHAR, INTEGER, VARCHAR, DateTime, TypeDecorator

from meltano.core.utils import uuid7

if t.TYPE_CHECKING:
    from sqlalchemy.engine.interfaces import Dialect
    from sqlalchemy.types import TypeEngine


class JSONEncodedDict(TypeDecorator[dict]):
    """Represents an immutable structure as a json-encoded string.

    Usage:
        JSONEncodedDict(VARCHAR_LENGTH)
    """

    impl = VARCHAR
    cache_ok = True

    def process_bind_param(
        self,
        value: dict | None,
        _dialect: Dialect,
    ) -> str | None:
        """Process the bind parameter.

        Args:
            value: The value to process.
            dialect: The dialect to use.
        """
        return json.dumps(value) if value is not None else value

    def process_result_value(
        self,
        value: str | None,
        _dialect: Dialect,
    ) -> dict | None:
        """Process the result value.

        Args:
            value: The value to process.
            dialect: The dialect to use.
        """
        return json.loads(value) if value is not None else value


class IntFlag(TypeDecorator):  # noqa: D101
    impl = INTEGER
    cache_ok = True

    # force the cast to INTEGER
    def process_bind_param(
        self,
        value: int | str | None,
        _dialect: Dialect,
    ) -> int | None:
        """Process the bind parameter.

        Args:
            value: The value to process.
            dialect: The dialect to use.
        """
        return int(value) if value is not None else value


class GUID(TypeDecorator[uuid.UUID | str]):
    """Platform-independent GUID type.

    Uses PostgreSQL's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.

    Reference:
    https://docs.sqlalchemy.org/en/13/core/custom_types.html#backend-agnostic-guid-type
    """

    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect: Dialect) -> TypeEngine:  # noqa: D102
        if dialect.name == "postgresql":
            return dialect.type_descriptor(UUID())
        type_descriptor_length = 32
        return dialect.type_descriptor(CHAR(type_descriptor_length))

    def process_bind_param(
        self,
        value: uuid.UUID | str | None,
        dialect: Dialect,
    ) -> uuid.UUID | str | None:
        """Process the bind parameter.

        Args:
            value: The value to process.
            dialect: The dialect to use.
        """
        if value is None:
            return value
        if dialect.name == "postgresql":
            return str(value)
        if not isinstance(value, uuid.UUID):
            value = uuid.UUID(value)
        return value.hex

    def process_result_value(
        self,
        value: uuid.UUID | str | None,
        _dialect: Dialect,
    ) -> uuid.UUID | str | None:
        """Process the result value.

        Args:
            value: The value to process.
            dialect: The dialect to use.
        """
        if value is None:
            return value
        if not isinstance(value, uuid.UUID):
            value = uuid.UUID(value)
        return value


class DateTimeUTC(TypeDecorator[datetime.datetime]):
    """Parses datetimes timezone-aware and stores them as UTC."""

    impl = DateTime
    cache_ok = True

    def process_bind_param(
        self,
        value: datetime.datetime | None,
        _dialect: Dialect,
    ) -> datetime.datetime | None:
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

    def process_result_value(
        self,
        value: datetime.datetime | None,
        _dialect: Dialect,
    ) -> datetime.datetime | None:
        """Convert the naive datetime value to UTC.

        Args:
            value: The datetime value to convert.

        Returns:
            The converted datetime value.
        """
        if value is not None:
            value = value.replace(tzinfo=datetime.timezone.utc)
        return value


GUIDType = t.Annotated[uuid.UUID, mapped_column(GUID, default=uuid7)]
StateType = t.Annotated[
    dict[str, str],
    mapped_column(MutableDict.as_mutable(JSONEncodedDict)),
]
IntPK = t.Annotated[int, mapped_column(primary_key=True)]
StrPK = t.Annotated[str, mapped_column(primary_key=True)]
