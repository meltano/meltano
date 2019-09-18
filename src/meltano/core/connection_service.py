import copy
from enum import Enum
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
        discovery = PluginDiscoveryService(self.context.project)
        loader_def = discovery.find_plugin("loaders", self.context.loader.name)

        dialect = loader_def.namespace # todo: make sure it matches
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
        discovery = PluginDiscoveryService(self.context.project)
        loader_def = discovery.find_plugin("loaders", self.context.loader.name)

        dialect = loader_def.namespace # todo: make sure it matches

        strategies = {
            ConnectionType.LOAD: self.load_connection_uri,
            ConnectionType.ANALYZE: self.analyze_connection_uri,
        }

        return strategies[connection_type](dialect)

    def load_dialect_params(self, dialect: str):
        dialect_params = {
            "postgres": lambda: {
                "dialect": dialect,
                "schema": self.context.namespace,
            },
            "sqlite": lambda: {
                "database": self.context.loader_config["database"],
                # TODO: add that to target-sqlite
                "table_prefix": self.context.namespace,
            },
        }

        return copy.deepcopy(dialect_params[dialect]())


    def analyze_dialect_params(self, dialect: str):
        dialect_params = {
            "postgres": lambda: {
                "dialect": dialect,
                "schema": ANALYZE_SCHEMA,
            },
            "sqlite": lambda: {
                "database": self.context.loader_config["database"],
            }
        }

        return copy.deepcopy(dialect_params[dialect]())

    def load_connection_uri(self, dialect):
        params = self.load_dialect_params(dialect)
        return self.dialect_engine_uri(dialect, params)

    def analyze_connection_uri(self, dialect):
        params = self.analyze_dialect_params(dialect)
        return self.dialect_engine_uri(dialect, params)

    def dialect_engine_uri(self, dialect: str, params = {}):
        # this part knows probably too much about the setting definition
        # for a plugin, but we have to do this if we want to infer connections
        # from the loader
        dialect_templates = {
            "postgres": "postgresql://{user}:{password}@{host}:{port}/{dbname}",
            "sqlite": "sqlite:///{database}",
        }

        try:
            loader_config = self.context.loader_config
            uri = dialect_templates[dialect].format(
                **self.context.loader_config,
                **params
            )
            return uri
        except KeyError:
            raise DialectNotSupportedError(dialect)
