import copy
from enum import Enum
from pathlib import Path

from .elt_context import ELTContext
from .plugin_discovery_service import PluginDiscoveryService


ANALYZE_SCHEMA = "analytics"


class DialectNotSupportedError(Exception):
    pass


class ConnectionType(str, Enum):
    LOAD = "load"
    ANALYZE = "analyze"


class ConnectionService:
    def __init__(self, elt_context: ELTContext):
        self.context = elt_context

    def connection_params(self, connection_type: ConnectionType) -> dict:
        # TODO: make sure we use the namespace as the dialect for loaders
        dialect = self.context.loader.namespace
        strategies = {
            ConnectionType.LOAD: self.load_dialect_params,
            ConnectionType.ANALYZE: self.analyze_dialect_params,
        }

        return strategies[connection_type](dialect)

    def connection_uri(self, connection_type: ConnectionType) -> str:
        """
        Create the connection uri from an ELTContext for a certain connection type.

        Returns the SQLAlchemy engine URI.
        """
        dialect = self.context.loader.namespace

        strategies = {
            ConnectionType.LOAD: self.load_connection_uri,
            ConnectionType.ANALYZE: self.analyze_connection_uri,
        }

        return strategies[connection_type](dialect)

    def load_dialect_params(self, dialect: str):
        dialect_params = {
            "postgres": lambda: {
                "dialect": dialect,
                "schema": self.context.extractor.namespace,
            },
            "sqlite": lambda: {"dialect": dialect},
        }

        return copy.deepcopy(dialect_params[dialect]())

    def analyze_dialect_params(self, dialect: str):
        dialect_params = {
            "postgres": lambda: {"dialect": dialect, "schema": ANALYZE_SCHEMA},
            "sqlite": lambda: {"dialect": dialect},
        }

        return copy.deepcopy(dialect_params[dialect]())

    def load_connection_uri(self, dialect):
        params = self.load_dialect_params(dialect)
        return self.dialect_engine_uri(dialect, params)

    def analyze_connection_uri(self, dialect):
        params = self.analyze_dialect_params(dialect)
        return self.dialect_engine_uri(dialect, params)

    def dialect_engine_uri(self, dialect: str, params={}):
        # this part knows probably too much about the setting definition
        # for a plugin, but we have to do this if we want to infer connections
        # from the loader
        db_suffix = lambda s: str(Path(s).with_suffix(".db"))

        dialect_templates = {
            "postgres": lambda params: "postgresql://{user}:{password}@{host}:{port}/{dbname}".format(
                **params
            ),
            "sqlite": lambda params: "sqlite:///{database}".format(
                database=db_suffix(params.pop("database")), **params
            ),
        }

        try:
            return dialect_templates[dialect]({**self.context.loader.config, **params})
        except KeyError:
            raise DialectNotSupportedError(dialect)
