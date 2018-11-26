import json
from collections import OrderedDict
from datetime import date, datetime
from decimal import Decimal

from flask import Blueprint, jsonify, request

sqlBP = Blueprint("sql", __name__, url_prefix="/sql")

import sqlalchemy

from .utils import SqlHelper
from ..models.data import Model, Explore
from ..models.settings import Settings

connections = {}


def default(obj):
    if isinstance(obj, Decimal):
        return str(obj)
    elif isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serialize-able")


def update_connections():
    current_connections = Settings.query.first().settings["connections"]
    for connection in current_connections:
        connection_name = connection["name"]
        if connection_name not in connections:
            this_connection = {}
            if connection["dialect"] == "postgresql":
                psql_params = ["username", "password", "host", "port", "database"]
                user, pw, host, port, db = [connection[param] for param in psql_params]
                connection_url = f"postgresql+psycopg2://{user}:{pw}@{host}:{port}/{db}"
                this_connection["connection_url"] = connection_url
                this_connection["engine"] = sqlalchemy.create_engine(
                    this_connection["connection_url"]
                )
            connections[connection_name] = this_connection


@sqlBP.route("/", methods=["GET"])
def index():
    return jsonify({"result": True})


@sqlBP.route("/get/<model_name>/<explore_name>", methods=["POST"])
def get_sql(model_name, explore_name):
    update_connections()
    sqlHelper = SqlHelper()
    model = Model.query.filter(Model.name == model_name).first()
    explore = Explore.query.filter(Explore.name == explore_name).first()
    incoming_json = request.get_json()
    to_run = incoming_json["run"]
    incoming_order = incoming_json["order"]
    sql_dict = sqlHelper.get_sql(explore, incoming_json)
    outgoing_sql = sql_dict["sql"]
    measures = sql_dict["measures"]
    dimensions = sql_dict["dimensions"]
    column_headers = sql_dict["column_headers"]
    names = sql_dict["names"]

    if to_run:
        db_to_connect = model.settings["connection"]
        if not db_to_connect in connections:
            return (
                jsonify(
                    {
                        "error": True,
                        "code": f"Missing connection details to {db_to_connect}. Create a connection to {db_to_connect} in the settings.",
                    }
                ),
                422,
            )
        engine = connections[model.settings["connection"]]["engine"]

        try:
            results = engine.execute(outgoing_sql)
        except sqlalchemy.exc.DBAPIError as e:
            return (
                jsonify(
                    {
                        "error": True,
                        "code": e.code,
                        "orig": str(e),
                        "statement": e.statement,
                    }
                ),
                422,
            )

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
    else:
        return json.dumps({"sql": outgoing_sql}, default=default)


@sqlBP.route("/distinct/<model_name>/<explore_name>", methods=["POST"])
def get_distinct_field_name(model_name, explore_name):
    update_connections()
    incoming_json = request.get_json()
    field_name = incoming_json["field"].replace("${TABLE}", explore_name)
    model = Model.query.filter(Model.name == model_name).first()
    explore = Explore.query.filter(Explore.name == explore_name).first()
    base_table = explore.view.settings["sql_table_name"]
    base_sql = f"SELECT DISTINCT {field_name} FROM {base_table} AS {explore_name} ORDER BY {field_name}"
    engine = connections[model.settings["connection"]]["engine"]
    results = engine.execute(base_sql)
    results = [dict(row) for row in results]
    return json.dumps(
        {"sql": base_sql, "results": results, "keys": list(results[0].keys())},
        default=default,
    )
