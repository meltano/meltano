import os
import copy
import logging
from enum import Enum
from pathlib import Path

from .elt_context import ELTContext
from .plugin_discovery_service import PluginDiscoveryService


class DialectNotSupportedError(Exception):
    pass


class ConnectionService:
    def __init__(self, elt_context: ELTContext):
        self.context = elt_context

    @property
    def dialect(self):
        return self.context.loader.namespace

    def analyze_params(self):
        if self.dialect not in ("postgres", "snowflake"):
            return {}

        if self.context.transformer:
            schema = self.context.transformer.get_config("target_schema")
        else:
            schema = self.context.loader.get_config("schema")

        return {"schema": schema}

    def analyze_uri(self):
        params = self.analyze_params()
        return self.dialect_engine_uri(params)

    def dialect_engine_uri(self, params={}):
        # this part knows probably too much about the setting definition
        # for a plugin, but we have to do this if we want to infer connections
        # from the loader
        db_suffix = lambda s: str(Path(s).with_suffix(".db"))

        dialect_templates = {
            "postgres": lambda params: "postgresql://{user}:{password}@{host}:{port}/{dbname}".format(
                **params
            ),
            "snowflake": lambda params: "snowflake://{username}:{password}@{account}/{database}/{schema}?warehouse={warehouse}&role={role}".format(
                **params
            ),
            "sqlite": lambda params: "sqlite:///{database}".format(
                database=db_suffix(params.pop("database")), **params
            ),
        }

        try:
            url = dialect_templates[self.dialect](
                {**self.context.loader.config_dict(), **params}
            )

            return url
        except KeyError:
            raise DialectNotSupportedError(self.dialect)
