import json
import os
from collections import OrderedDict
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from os.path import join

from flask import Blueprint, jsonify, request
import sqlalchemy

from .sqlhelper import SqlHelper
from .settingshelper import SettingsHelper
from meltano.core.mac_file import MACFile
from meltano.core.project import Project

sqlBP = Blueprint("sql", __name__, url_prefix="/sql")
meltano_model_path = join(os.getcwd(), "model")


class ConnectionNotFound(Exception):
    def __init__(self, connection_name: str):
        self.connection_name = connection_name
        super().__init__("{connection_name} is missing.")


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


@sqlBP.errorhandler(sqlalchemy.exc.DBAPIError)
def _handle(ex):
    return (
        jsonify(
            {"error": True, "code": ex.code, "orig": str(ex), "statement": ex.statement}
        ),
        422,
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
        elif connection["dialect"] == "sqlite":
            db_path = project.root.joinpath(connection["path"])
            connection_url = f"sqlite:///{db_path}"

        return sqlalchemy.create_engine(connection_url)

        raise ConnectionNotFound(connection_name)
    except StopIteration:
        raise ConnectionNotFound(connection_name)


@sqlBP.route("/", methods=["GET"])
def index():
    return jsonify({"result": True})


@sqlBP.route("/get/<model_name>/<explore_name>", methods=["POST"])
def get_sql(model_name, explore_name):
    mac_file = Path(meltano_model_path).joinpath(f"{model_name}.model.mac")
    with mac_file.open() as f:
        mac = MACFile.load(f)

    explore = mac.explore(explore_name)
    incoming_json = request.get_json()

    to_run = incoming_json["run"]
    incoming_order = incoming_json["order"]

    sqlHelper = SqlHelper()
    sql_dict = sqlHelper.get_sql(explore, incoming_json)
    outgoing_sql = sql_dict["sql"]
    measures = sql_dict["measures"]
    dimensions = sql_dict["dimensions"]
    column_headers = sql_dict["column_headers"]
    names = sql_dict["names"]

    if not to_run:
        return json.dumps({"sql": outgoing_sql}, default=default)

    connection_name = mac.connection("connection")
    engine = get_db_engine(connection_name)
    results = engine.execute(outgoing_sql)

    results = [OrderedDict(row) for row in results]
    base_dict = {"sql": outgoing_sql, "results": results, "error": False}
    if not len(results):
        base_dict["empty"] = True
    else:
        base_dict["empty"] = False
        base_dict["column_headers"] = column_headers
        base_dict["names"] = names
        base_dict["keys"] = list(results[0].keys())
        base_dict["measures"] = sqlHelper.get_names(measures)

    return json.dumps(base_dict, default=default)


@sqlBP.route("/distinct/<model_name>/<explore_name>", methods=["POST"])
def get_distinct_field_name(model_name, explore_name):
    # incoming_json = request.get_json()
    # field_name = incoming_json["field"].replace("${TABLE}", explore_name)
    # model = Model.query.filter(Model.name == model_name).first()
    # explore = Explore.query.filter(Explore.name == explore_name).first()

    # base_table = explore.view.settings["sql_table_name"]
    # base_sql = f"SELECT DISTINCT {field_name} FROM {base_table} AS {explore_name} ORDER BY {field_name}"

    # engine = get_db_engine(model.settings["connection"])
    # results = engine.execute(base_sql)
    # results = [dict(row) for row in results]
    # return json.dumps(
    #     {"sql": base_sql, "results": results, "keys": list(results[0].keys())},
    #     default=default,
    # )
    return json.dumps({"tester": "tester"})
