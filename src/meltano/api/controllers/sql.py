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
from meltano.core.sql.filter import FilterOptions
from meltano.core.sql.base import ParseError, EmptyQuery

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
                "code": f"The dialect '{ex.connection_dialect}' is not yet supported by Meltano Analyze.",
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


@sqlBP.errorhandler(ParseError)
def _handle(ex):
    return (jsonify({"error": True, "code": str(ex)}), 400)


@sqlBP.errorhandler(EmptyQuery)
def _handle(ex):
    return ("", 204)


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


@sqlBP.route("/get/<path:namespace>/<topic_name>/<design_name>", methods=["POST"])
def get_sql(namespace, topic_name, design_name):
    sqlHelper = SqlHelper()
    m5oc = sqlHelper.get_m5oc_topic(namespace, topic_name)
    design = m5oc.design(design_name)
    incoming_json = request.get_json()

    loader = incoming_json["loader"]
    sql_dict = sqlHelper.get_sql(design, incoming_json)

    outgoing_sql = sql_dict["sql"]
    aggregates = sql_dict["aggregates"]
    query_attributes = sql_dict["query_attributes"]

    base_dict = {"sql": outgoing_sql, "error": False}
    base_dict["query_attributes"] = query_attributes
    base_dict["aggregates"] = aggregates

    if not incoming_json["run"]:
        return jsonify(base_dict)

    results = sqlHelper.get_query_results(loader, outgoing_sql)
    base_dict["results"] = results
    base_dict["empty"] = len(results) == 0

    return jsonify(base_dict)


@sqlBP.route("/get/filter-options", methods=["GET"])
def get_filter_options():
    return jsonify(FilterOptions)
