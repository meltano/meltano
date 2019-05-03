import logging
import sqlalchemy.types as types
from sqlalchemy import Column


class PluginSetting(SystemModel):
    __tablename__ = "plugin_settings"

    key = Column(types.String, primary_key=True)
    # label = Column(types.String)
    # description = Column(types.String)
    # represent a materialized path to support
    # a nested configuration.
    name = Column(types.String)
    plugin = Column(types.String)
    value = Column(types.PickleType)
