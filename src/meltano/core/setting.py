import logging
import os

import sqlalchemy.types as types
from sqlalchemy import Column, UniqueConstraint

from .models import SystemModel
from .utils import nest


class Setting(SystemModel):
    __tablename__ = "plugin_settings"

    # represent the mapping to the ENV
    label = Column(types.String)
    description = Column(types.Text)

    # represent a materialized path to support
    # a nested configuration.
    name = Column(types.String, primary_key=True)
    namespace = Column(types.String, primary_key=True, nullable=True)
    value = Column(types.PickleType)
    enabled = Column(types.Boolean, default=False)

    def __repr__(self):
        enabled_marker = "E" if self.enabled else ""
        return f"<({self.namespace}) {self.name}={self.value} {enabled_marker}>"
