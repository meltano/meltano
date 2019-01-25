import json
import os
from datetime import date, datetime
from decimal import Decimal

from flask import Blueprint, jsonify, request
from flask_security import auth_required
import sqlalchemy

from .sql_helper import ConnectionNotFound
from .sql_helper import SqlHelper
from .settings_helper import SettingsHelper
from meltano.api.security import api_auth_required
from meltano.core.project import Project

sqlBP = Blueprint("sql", __name__, url_prefix="/sql")


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


@sqlBP.before_request
@api_auth_required
def before_request():
    pass


@sqlBP.route("/", methods=["GET"])
def index():
    return jsonify({"result": True})


@sqlBP.route("/get/<model_name>/dialect", methods=["GET"])
def get_dialect(model_name):
    sqlHelper = SqlHelper()
    m5oc = sqlHelper.get_m5oc_model(model_name)
    connection_name = m5oc.connection("connection")
    engine = sqlHelper.get_db_engine(connection_name)
    return jsonify({"connection_dialect": engine.dialect.name})


@sqlBP.route("/get/<model_name>/<design_name>", methods=["POST"])
def get_sql(model_name, design_name):
    sqlHelper = SqlHelper()
    m5oc = sqlHelper.get_m5oc_model(model_name)
    design = m5oc.design(design_name)
    incoming_json = request.get_json()

    sql_dict = sqlHelper.get_sql(design, incoming_json)
    outgoing_sql = sql_dict["sql"]
    aggregates = sql_dict["aggregates"]
    columns = sql_dict["columns"]
    column_headers = sql_dict["column_headers"]
    names = sql_dict["names"]
    db_table = sql_dict["db_table"]

    if not incoming_json["run"]:
        return jsonify({"sql": outgoing_sql})

    connection_name = m5oc.connection("connection")
    results = sqlHelper.get_query_results(connection_name, outgoing_sql)

    base_dict = {"sql": outgoing_sql, "results": results, "error": False}
    if not len(results):
        base_dict["empty"] = True
    else:
        base_dict["empty"] = False
        base_dict["column_headers"] = column_headers
        base_dict["names"] = names
        base_dict["keys"] = list(results[0].keys())
        base_dict["aggregates"] = sqlHelper.get_aliases_from_aggregates(
            aggregates, db_table
        )

    return jsonify(base_dict)


@sqlBP.route("/distinct/<model_name>/<design_name>", methods=["POST"])
def get_distinct_field_name(model_name, design_name):
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
