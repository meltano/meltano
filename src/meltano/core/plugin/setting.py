import logging
import sqlalchemy.types as types
import os
from sqlalchemy import Column, UniqueConstraint

from meltano.core.db import SystemModel
from meltano.core.utils import nest
from meltano.core.db import SystemModel


def infer_env(ctx):
    process = lambda s: s.replace(".", "__").upper()

    name = process(ctx.current_parameters.get("name"))
    ns = ctx.current_parameters.get("namespace")

    if ns:
        ns = process(ns)
        return "_".join((ns, name))

    return name


class PluginSetting(SystemModel):
    __tablename__ = "plugin_settings"

    # represent the mapping to the ENV
    label = Column(types.String)
    description = Column(types.Text)

    # represent a materialized path to support
    # a nested configuration.
    name = Column(types.String, primary_key=True)
    namespace = Column(types.String, primary_key=True, nullable=True)
    value = Column(types.PickleType)
    env = Column(types.String, default=infer_env)
    enabled = Column(types.Boolean, default=False)

    def __repr__(self):
        enabled_marker = "E" if self.enabled else ""
        return f"<({self.namespace}) {self.name}={self.value} {enabled_marker}>"
