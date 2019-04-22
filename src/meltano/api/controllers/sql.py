import json
import os
import sqlalchemy

from datetime import date, datetime
from decimal import Decimal
from flask import Blueprint, jsonify, request
from flask_security import auth_required

from .settings_helper import SettingsHelper
from .sql_helper import SqlHelper, ConnectionNotFound, UnsupportedConnectionDialect
from meltano.api.security import api_auth_required
from meltano.core.project import Project

sqlBP = Blueprint("sql", __name__, url_prefix="/api/v1/sql")


@sqlBP.errorhandler(ConnectionNotFound)
def _handle(ex):
    return (
        jsonify(
            {
                "error": True,
                "code": f"Missing connection details to '{ex.connection_name}'. Create a connection to '{ex.connection_name}' in the settings.",
            }
        ),
        500,
    )


@sqlBP.errorhandler(UnsupportedConnectionDialect)
def _handle(ex):
    return (
        jsonify(
            {
                "error": True,
                "code": f"The dialect ('{ex.connection_dialect}') for the connection provided is not supported.",
            }
        ),
        500,
    )


@sqlBP.errorhandler(sqlalchemy.exc.DBAPIError)
def _handle(ex):
    return (
        jsonify(
            {"error": True, "code": ex.code, "orig": str(ex), "statement": ex.statement}
        ),
        500,
    )


def default(obj):
    if isinstance(obj, Decimal):
        return str(obj)
    elif isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serialize-able")


def get_db_engine(connection_name):
    project = Project.find()
    settings_helper = SettingsHelper()
    connections = settings_helper.get_connections()["settings"]["connections"]

    try:
        connection = next(
            connection
            for connection in connections
            if connection["name"] == connection_name
        )

        if connection["dialect"] == "postgresql":
            psql_params = ["username", "password", "host", "port", "database"]
            user, pw, host, port, db = [connection[param] for param in psql_params]
            connection_url = f"postgresql+psycopg2://{user}:{pw}@{host}:{port}/{db}"
            engine = sqlalchemy.create_engine(connection_url)
            engine.execute(f"SET search_path TO {connection['schema']},public ")
        elif connection["dialect"] == "sqlite":
            db_path = project.root.joinpath(connection["path"])
            connection_url = f"sqlite:///{db_path}"
            engine = sqlalchemy.create_engine(connection_url)

        return engine

        raise ConnectionNotFound(connection_name)
    except StopIteration:
        raise ConnectionNotFound(connection_name)


@sqlBP.before_request
@api_auth_required
def before_request():
    pass


@sqlBP.route("/", methods=["GET"])
def index():
    return jsonify({"result": True})


@sqlBP.route("/get/<topic_name>/dialect", methods=["GET"])
def get_dialect(topic_name):
    sqlHelper = SqlHelper()
    m5oc = sqlHelper.get_m5oc_topic(topic_name)
    connection_name = m5oc.connection("connection")
    engine = sqlHelper.get_db_engine(connection_name)
    return jsonify({"connection_dialect": engine.dialect.name})


@sqlBP.route("/get/<topic_name>/<design_name>", methods=["POST"])
def get_sql(topic_name, design_name):
    sqlHelper = SqlHelper()
    m5oc = sqlHelper.get_m5oc_topic(topic_name)
    design = m5oc.design(design_name)
    incoming_json = request.get_json()

    # Get the connection currently used in Meltano UI
    # It is used in order to dynamically generate the proper SQL queries
    #  using the schema (Postgres) or even the database (Snowflake) at run time
    connection_name = m5oc.connection("connection")
    connection = sqlHelper.get_connection(connection_name)

    sql_dict = sqlHelper.get_sql(design, incoming_json, connection.get("schema", None))
    outgoing_sql = sql_dict["sql"]
    aggregates = sql_dict["aggregates"]
    column_headers = sql_dict["column_headers"]
    column_names = sql_dict["column_names"]
    db_table = sql_dict["db_table"]

    base_dict = {"sql": outgoing_sql, "error": False}
    base_dict["column_headers"] = column_headers
    base_dict["column_names"] = column_names
    base_dict["aggregates"] = aggregates

    if not incoming_json["run"]:
        return jsonify(base_dict)

    results = sqlHelper.get_query_results(connection_name, outgoing_sql)

    base_dict["results"] = results
    if not len(results):
        base_dict["empty"] = True
    else:
        base_dict["empty"] = False
        base_dict["keys"] = list(results[0].keys())

    return jsonify(base_dict)


@sqlBP.route("/distinct/<topic_name>/<design_name>", methods=["POST"])
def get_distinct_field_name(topic_name, design_name):
    # incoming_json = request.get_json()
    # field_name = incoming_json["field"].replace("${TABLE}", design_name)
    # model = Model.query.filter(Model.name == model_name).first()
    # design = Design.query.filter(Design.name == design_name).first()

    # base_table = design.table.settings["sql_table_name"]
    # base_sql = f"SELECT DISTINCT {field_name} FROM {base_table} AS {design_name} ORDER BY {field_name}"

    # engine = get_db_engine(model.settings["connection"])
    # results = engine.execute(base_sql)
    # results = [dict(row) for row in results]
    # return json.dumps(
    #     {"sql": base_sql, "results": results, "keys": list(results[0].keys())},
    #     default=default,
    # )
    return jsonify({"tester": "tester"})
