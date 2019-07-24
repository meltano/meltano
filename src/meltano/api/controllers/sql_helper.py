import logging
import os
import sqlalchemy
from pathlib import Path
from collections import OrderedDict
from flask import jsonify, redirect, url_for
from pypika import Query, Order
from sqlalchemy.event import listen

from meltano.api.models import db
from meltano.api.security import create_dev_user
from meltano.core.project import Project
from meltano.core.config_service import ConfigService
from meltano.core.plugin.settings_service import PluginSettingsService
from meltano.core.m5o.m5oc_file import M5ocFile
from meltano.core.sql.analysis_helper import AnalysisHelper
from meltano.core.sql.sql_utils import SqlUtils
from .settings_helper import SettingsHelper


class ConnectionNotFound(Exception):
    def __init__(self, connection_name: str):
        self.connection_name = connection_name
        super().__init__("{connection_name} is missing.")


class UnsupportedConnectionDialect(Exception):
    def __init__(self, connection_dialect: str):
        self.connection_dialect = connection_dialect
        super().__init__("Dialect {connection_dialect} is not supprted.")


class SqlHelper(SqlUtils):
    def parse_sql(self, input):
        placeholders = self.placeholder_match(input)

    def placeholder_match(self, input):
        outer_pattern = r"(\$\{[\w\.]*\})"
        inner_pattern = r"\$\{([\w\.]*)\}"
        outer_results = re.findall(outer_pattern, input)
        inner_results = re.findall(inner_pattern, input)
        return (outer_results, inner_results)

    def get_m5oc_topic(self, topic_name):
        project = Project.find()
        m5oc_file = project.root_dir("model", f"{topic_name}.topic.m5oc")
        return M5ocFile.load(m5oc_file)

    def get_connection(self, dialect):
        project = Project.find()
        config = ConfigService(project)
        connections = list(config.get_connections())

        # for now let's just find the first connection that
        # match dialect-wise
        try:
            return next(
                connection for connection in connections if connection.name == dialect
            )
        except StopIteration:
            raise ConnectionNotFound(dialect)

    def get_db_engine(self, dialect):
        project = Project.find()
        connection = self.get_connection(dialect)
        config = PluginSettingsService(db.session, project).as_config(connection)
        engine_hooks = []

        if dialect == "postgresql":
            psql_params = ["user", "password", "host", "dbname"]
            user, pw, host, dbname = [config[param] for param in psql_params]
            connection_url = f"postgresql+psycopg2://{user}:{pw}@{host}/{dbname}"

            def set_connection_schema(raw, conn):
                schema = config["schema"]
                with raw.cursor() as cursor:
                    res = cursor.execute(f"SET search_path TO {schema};")
                    logging.debug(f"Connection schema set to {schema}")

            engine_hooks.append(
                lambda engine: listen(engine, "first_connect", set_connection_schema)
            )
        elif dialect == "sqlite":
            db_path = project.root.joinpath(config["dbname"])
            connection_url = f"sqlite:///{db_path}"
        else:
            raise UnsupportedConnectionDialect(dialect)

        engine = sqlalchemy.create_engine(connection_url)

        for hook in engine_hooks:
            hook(engine)

        return engine

    def get_query_results(self, connection_name, sql):
        engine = self.get_db_engine(connection_name)
        results = engine.execute(sqlalchemy.text(sql))
        results = [OrderedDict(row) for row in results]
        return results

    def reset_db(self):
        try:
            db.drop_all()
        except sqlalchemy.exc.OperationalError as err:
            logging.error("Failed drop database.")

        db.create_all()
        create_dev_user()
