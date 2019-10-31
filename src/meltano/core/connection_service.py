import os
import copy
import logging
from enum import Enum
from pathlib import Path

from .elt_context import ELTContext
from .plugin_discovery_service import PluginDiscoveryService


DEFAULT_ANALYZE_SCHEMA = "analytics"
MELTANO_SCHEMA_SUFFIX = os.getenv("MELTANO_SCHEMA_SUFFIX", "")
MELTANO_LOAD_SCHEMA_SUFFIX = os.getenv(
    "MELTANO_LOAD_SCHEMA_SUFFIX", MELTANO_SCHEMA_SUFFIX
)
MELTANO_ANALYZE_SCHEMA_SUFFIX = os.getenv(
    "MELTANO_ANALYZE_SCHEMA_SUFFIX", MELTANO_SCHEMA_SUFFIX
)


class DialectNotSupportedError(Exception):
    pass


class ConnectionService:
    def __init__(self, elt_context: ELTContext):
        self.context = elt_context

    @property
    def dialect(self):
        return self.context.loader.namespace

    def load_params(self):
        schema = (
            os.getenv("MELTANO_LOAD_SCHEMA", self.context.extractor.namespace)
            + MELTANO_LOAD_SCHEMA_SUFFIX
        )

        dialect_params = {
            "postgres": {"schema": schema},
            "snowflake": {"schema": schema.upper()},
        }

        return dialect_params.get(self.dialect, {})

    def analyze_params(self):
        schema = (
            os.getenv("MELTANO_ANALYZE_SCHEMA", DEFAULT_ANALYZE_SCHEMA)
            + MELTANO_ANALYZE_SCHEMA_SUFFIX
        )

        dialect_params = {
            "postgres": {"schema": schema},
            "snowflake": {"schema": schema.upper()},
        }

        return dialect_params.get(self.dialect, {})

    def load_uri(self):
        params = self.load_params()
        return self.dialect_engine_uri(params)

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
                {**self.context.loader.config, **params}
            )

            return url
        except KeyError:
            raise DialectNotSupportedError(self.dialect)
