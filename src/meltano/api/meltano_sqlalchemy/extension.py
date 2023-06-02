"""Implements a flask_sqlalchemy like module."""
from __future__ import annotations

import typing as t


import sqlalchemy as sa
from sqlalchemy import event, orm

from .model import _QueryProperty  # noqa:WPS450
from .model import DefaultMeta
from .model import Model

from .query import Query


class SQLAlchemy:
    """Replaces `flask_sqlalchemy` for Meltano in a minimal manner."""

    def __init__(
        self,
        *,
        metadata: sa.MetaData | None = None,
        query_class: type[Query] = Query,
        model_class: type[Model] | orm.DeclarativeMeta = Model,
    ):
        self.Query = query_class
        self.metadatas: dict[str | None, sa.MetaData] = {}

        if metadata is not None:
            metadata.info["bind_key"] = None
            self.metadatas[None] = metadata
        self.Model = self._make_declarative_base(model_class)

    def _make_metadata(self, bind_key: str | None) -> sa.MetaData:
        """Get or create a :class:`sqlalchemy.schema.MetaData` for the given bind key.

        This method is used for internal setup. Its signature may change at any time.

        Args:
            bind_key: The name of the metadata being created.

        Returns:
            MetaData object.
        """
        if bind_key in self.metadatas:
            return self.metadatas[bind_key]

        if bind_key is not None:
            # Copy the naming convention from the default metadata.
            naming_convention = self._make_metadata(None).naming_convention
        else:
            naming_convention = None

        # Set the bind key in info to be used by session.get_bind.
        metadata = sa.MetaData(
            naming_convention=naming_convention, info={"bind_key": bind_key}
        )
        self.metadatas[bind_key] = metadata
        return metadata

    def _make_declarative_base(
        self, model: type[Model] | orm.DeclarativeMeta
    ) -> type[t.Any]:
        """Create a SQLAlchemy declarative model class.

        The result is available as :attr:`Model`.

        To customize, subclass :class:`.Model` and pass it as ``model_class`` to
        :class:`SQLAlchemy`. To customize at the metaclass level, pass an already
        created declarative model class as ``model_class``.

        This method is used for internal setup. Its signature may change at any time.

        Args:
            model: A model base class, or an already created declarative model class.

        Returns:
            Base object.
        """
        if not isinstance(model, orm.DeclarativeMeta):
            metadata = self._make_metadata(None)
            model = orm.declarative_base(
                metadata=metadata, cls=model, name="Model", metaclass=DefaultMeta
            )

        if None not in self.metadatas:
            # Use the model's metadata as the default metadata.
            model.metadata.info["bind_key"] = None  # type: ignore[union-attr]
            self.metadatas[None] = model.metadata  # type: ignore[union-attr]
        else:
            # Use the passed in default metadata as the model's metadata.
            model.metadata = self.metadatas[None]  # type: ignore[union-attr]

        model.query_class = self.Query
        model.query = _QueryProperty()
        model.__fsa__ = self
        return model

    def __getattr__(self, name: str) -> t.Any:
        if name == "relation":
            return self._relation

        if name == "event":
            return event

        if name.startswith("_"):
            raise AttributeError(name)

        for mod in (sa, orm):
            if hasattr(mod, name):  # noqa:WPS421
                return getattr(mod, name)

        raise AttributeError(name)
