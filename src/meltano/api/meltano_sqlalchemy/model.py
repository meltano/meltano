"""Implement placeholder model."""
from __future__ import annotations

import re
import typing as t

import sqlalchemy as sa
import sqlalchemy.orm

from .query import Query

if t.TYPE_CHECKING:
    from .extension import SQLAlchemy


class _QueryProperty:
    """A class property that creates a query object for a model."""

    def __get__(self, obj: Model | None, clss: type[Model]) -> Query:
        return clss.query_class(
            clss, session=clss.__fsa__.session()  # type: ignore[arg-type]
        )


class Model:
    """The base class of the :attr:`.SQLAlchemy.Model` declarative model class."""

    __fsa__: t.ClassVar[SQLAlchemy]  # Internal reference to the extension object
    query_class: t.ClassVar[type[Query]] = Query
    query: t.ClassVar[Query] = _QueryProperty()  # type: ignore[assignment]

    def __repr__(self) -> str:
        state = sa.inspect(self)
        assert state is not None  # noqa:S101

        if state.transient:
            pk = f"(transient {id(self)})"
        elif state.pending:
            pk = f"(pending {id(self)})"
        else:
            pk = ", ".join(map(str, state.identity))

        return f"<{type(self).__name__} {pk}>"


class BindMetaMixin(type):
    """Sets a model's ``metadata`` based on its ``__bind_key__``."""

    __fsa__: SQLAlchemy
    metadata: sa.MetaData

    def __init__(
        cls, name: str, bases: tuple[type, ...], d: dict[str, t.Any], **kwargs: t.Any
    ) -> None:
        if not ("metadata" in cls.__dict__ or "__table__" in cls.__dict__):
            bind_key = getattr(cls, "__bind_key__", None)
            parent_metadata = getattr(cls, "metadata", None)
            metadata = cls.__fsa__._make_metadata(bind_key)  # noqa:WPS437

            if metadata is not parent_metadata:
                cls.metadata = metadata

        super().__init__(name, bases, d, **kwargs)


class NameMetaMixin(type):
    """Sets a model's ``__tablename__``."""

    metadata: sa.MetaData
    __tablename__: str
    __table__: sa.Table

    def __init__(
        cls, name: str, bases: tuple[type, ...], d: dict[str, t.Any], **kwargs: t.Any
    ) -> None:
        if should_set_tablename(cls):
            cls.__tablename__ = camel_to_snake_case(cls.__name__)

        super().__init__(name, bases, d, **kwargs)

        # __table_cls__ has run. If no table was created, use the parent table.
        if (
            "__tablename__" not in cls.__dict__
            and "__table__" in cls.__dict__
            and cls.__dict__["__table__"] is None
        ):
            del cls.__table__

    def __table_cls__(cls, *args: t.Any, **kwargs: t.Any) -> sa.Table | None:
        """Give table class.

        Args:
            args: args
            kwargs: kwargs

        Returns:
            Table object.
        """
        schema = kwargs.get("schema")

        if schema is None:
            key = args[0]
        else:
            key = f"{schema}.{args[0]}"

        # Check if a table with this name already exists. Allows reflected tables to be
        # applied to models by name.
        if key in cls.metadata.tables:
            return sa.Table(*args, **kwargs)

        # If a primary key is found, create a table for joined-table inheritance.
        for arg in args:
            if (isinstance(arg, sa.Column) and arg.primary_key) or isinstance(
                arg, sa.PrimaryKeyConstraint
            ):
                return sa.Table(*args, **kwargs)

        # If no base classes define a table, return one that's missing a primary key
        # so SQLAlchemy shows the correct error.
        for base in cls.__mro__[1:-1]:
            if "__table__" in base.__dict__:
                break
        else:
            return sa.Table(*args, **kwargs)

        # Single-table inheritance, use the parent table name. __init__ will unset
        # __table__ based on this.
        if "__tablename__" in cls.__dict__:
            del cls.__tablename__

        return None


def should_set_tablename(cls: type) -> bool:
    """Determine whether ``__tablename__`` should be generated for a model.

    Args:
        cls: a class

    Returns:
        Boolean.
    """
    if cls.__dict__.get("__abstract__", False) or not any(
        isinstance(b, sa.orm.DeclarativeMeta) for b in cls.__mro__[1:]
    ):
        return False

    for base in cls.__mro__:
        if "__tablename__" not in base.__dict__:
            continue

        if isinstance(base.__dict__["__tablename__"], sa.orm.declared_attr):
            return False

        return not (
            base is cls
            or base.__dict__.get("__abstract__", False)
            or not isinstance(base, sa.orm.DeclarativeMeta)
        )

    return True


def camel_to_snake_case(name: str) -> str:
    """Convert a ``CamelCase`` name to ``snake_case``.

    Args:
        name: the name to change.

    Returns:
        A string.
    """
    name = re.sub(
        r"((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))", r"_\1", name  # noqa:WPS360
    )
    return name.lower().lstrip("_")


class DefaultMeta(BindMetaMixin, NameMetaMixin, sa.orm.DeclarativeMeta):
    """Provides ``__bind_key__`` and ``__tablename__`` support."""
