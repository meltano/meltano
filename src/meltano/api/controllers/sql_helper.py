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
from meltano.api.json import freeze_keys
from meltano.core.project import Project
from meltano.core.config_service import ConfigService
from meltano.core.m5o.m5oc_file import M5ocFile
from meltano.core.sql.analysis_helper import AnalysisHelper
from meltano.core.sql.sql_utils import SqlUtils
from meltano.core.elt_context import ELTContextBuilder
from meltano.core.connection_service import ConnectionService, DialectNotSupportedError
from .settings_helper import SettingsHelper


ENABLED_DIALECTS = ["postgres", "sqlite"]


class ConnectionNotFound(Exception):
    def __init__(self, connection_name: str):
        self.connection_name = connection_name
        super().__init__("{connection_name} is missing.")


class UnsupportedConnectionDialect(Exception):
    def __init__(self, connection_dialect: str):
        self.connection_dialect = connection_dialect
        super().__init__("Dialect {connection_dialect} is not supported.")


class SqlHelper(SqlUtils):
    def parse_sql(self, input):
        placeholders = self.placeholder_match(input)

    def placeholder_match(self, input):
        outer_pattern = r"(\$\{[\w\.]*\})"
        inner_pattern = r"\$\{([\w\.]*)\}"
        outer_results = re.findall(outer_pattern, input)
        inner_results = re.findall(inner_pattern, input)
        return (outer_results, inner_results)

    def get_m5oc_topic(self, namespace, topic_name):
        project = Project.find()
        m5oc_file = project.run_dir("models", namespace, f"{topic_name}.topic.m5oc")
        return M5ocFile.load(m5oc_file)

    def get_db_engine(self, extractor, loader, transform):
        project = Project.find()
        context = (
            ELTContextBuilder(project)
            .with_extractor(extractor)
            .with_loader(loader)
            .with_transform(transform)
            .context(db.session)
        )
        connection_service = ConnectionService(context)

        engine_hooks = []
        dialect = connection_service.dialect
        engine_uri = None
        params = None

        try:
            params = connection_service.analyze_params()
            engine_uri = connection_service.analyze_uri()

            if dialect not in ENABLED_DIALECTS:
                raise UnsupportedConnectionDialect(dialect)
        except DialectNotSupportedError:
            raise UnsupportedConnectionDialect(dialect)

        if dialect == "postgres":

            def set_connection_schema(raw, conn):
                schema = params["schema"]
                with raw.cursor() as cursor:
                    res = cursor.execute(f"SET search_path TO {schema};")
                    logging.debug(f"Connection schema set to {schema}")

            engine_hooks.append(
                lambda engine: listen(engine, "first_connect", set_connection_schema)
            )

        engine = sqlalchemy.create_engine(engine_uri)
        for hook in engine_hooks:
            hook(engine)

        return engine

    # we need to `freeze` each result to make sure
    # the attribute name will be correct for the lookup
    def get_query_results(self, extractor, loader, transform, sql):
        engine = self.get_db_engine(extractor, loader, transform)
        results = engine.execute(sqlalchemy.text(sql))
        results = [freeze_keys(OrderedDict(row)) for row in results]
        return results

    def reset_db(self):
        try:
            db.drop_all()
        except sqlalchemy.exc.OperationalError as err:
            logging.error("Failed drop database.")

        db.create_all()
        create_dev_user()
