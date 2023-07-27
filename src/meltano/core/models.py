"""Defines SystemModel parent class for other models."""

from __future__ import annotations

from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base

SystemMetadata = MetaData()
SystemModel = declarative_base(metadata=SystemMetadata)
