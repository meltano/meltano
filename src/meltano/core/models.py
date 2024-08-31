"""Defines SystemModel parent class for other models."""

from __future__ import annotations

import typing as t
from datetime import datetime

from sqlalchemy import MetaData, types
from sqlalchemy.orm import DeclarativeBase

SystemMetadata = MetaData()


class SystemModel(DeclarativeBase):
    """Base class for all database models."""

    metadata = SystemMetadata
    type_annotation_map: t.ClassVar[dict] = {
        str: types.String(),
        bool: types.Boolean(),
        datetime: types.DateTime(),
    }
