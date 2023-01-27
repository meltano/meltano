"""Dialect-specific SQLAlchemy types."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.mssql import DATETIME2
from sqlalchemy.engine import Connection


def get_dialect_name() -> str:
    """Get the dialect name from the Alembic op.

    Returns:
        The dialect name.
    """
    database_connection: Connection = op.get_bind()
    return database_connection.dialect.name


def datetime_for_dialect(dialect_name: str) -> DATETIME2 | sa.DateTime:
    """Get the datetime type for the given dialect.

    Args:
        dialect_name: The SQL dialect name.

    Returns:
        The datetime type.
    """
    # We need to use the DATETIME2 type for MSSQL, because the
    # default DATETIME type does not go back to the year 1.
    if dialect_name == "mssql":
        return DATETIME2

    return sa.DateTime


def max_string_length_for_dialect(dialect_name: str) -> int | None:
    """Get the maximum string length for the given dialect.

    We need to limit the size of the string to avoid MySQL throwing an error.

    Args:
        dialect_name: The SQL dialect name.

    Returns:
        The maximum string length or None if there is no limit.
    """
    if dialect_name == "mysql":
        return 1024

    return None
