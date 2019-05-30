import logging
import sqlalchemy.types as types
import os
from sqlalchemy import Column, UniqueConstraint

from meltano.core.db import SystemModel
from meltano.core.utils import nest



class PluginSetting(SystemModel):
    __tablename__ = "plugin_settings"

    # represent the mapping to the ENV
    key = Column(types.String, primary_key=True)
    # label = Column(types.String)
    # description = Column(types.String)

    # represent a materialized path to support
    # a nested configuration.
    name = Column(types.String)
    plugin = Column(types.String)
    defined_value = Column(types.PickleType)
    default_value = Column(types.PickleType, nullable=False)
    enabled = Column(types.Boolean, default=False)

    UniqueConstraint('name', 'plugin', name="uix_plugin__name")

    def __repr__(self):
        enabled_marker = "E" if self.enabled else ""
        return f"<({self.plugin}) {self.name}={self.value} {enabled_marker}>"

    def as_dict(self):
        return nest({}, self.name, value=self.value)

    @property
    def value(self):
        if self.key in os.environ:
            logging.debug(f"Found ENV variable {self.key} for {self.plugin}({self.name}).")
            return os.environ[self.key]

        return self.defined_value if self.enabled else self.default_value;

    @value.setter
    def value(self, newval):
        if type(self.default_value) is not type(newval):
            raise ValueError(f"Type mismatch, provided value doesn't match the default value type ({type(self.default_value)}")

        self.defined_value = newval
