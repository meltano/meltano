import json
import os
import sqlalchemy

from datetime import date, datetime
from decimal import Decimal
from flask import jsonify, request

from .settings_helper import SettingsHelper
from .sql_helper import SqlHelper, ConnectionNotFound, UnsupportedConnectionDialect
from meltano.api.api_blueprint import APIBlueprint
from meltano.core.project import Project
from meltano.core.schedule_service import ScheduleService, ScheduleNotFoundError
from meltano.core.utils import find_named, NotFound
from meltano.core.sql.filter import FilterOptions
from meltano.core.sql.base import ParseError, EmptyQuery


sqlBP = APIBlueprint("sql", __name__)


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


@sqlBP.errorhandler(ScheduleNotFoundError)
def _handle(ex):
    return (
        jsonify(
            {
                "error": True,
                "code": f"A pipeline for data source '{ex.namespace}' has not run yet. Please set up your connection.",
            }
        ),
        404,
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


@sqlBP.route("/", methods=["GET"])
def index():
    return jsonify({"result": True})


@sqlBP.route("/get/<path:namespace>/<topic_name>/<design_name>", methods=["POST"])
def get_sql(namespace, topic_name, design_name):
    sqlHelper = SqlHelper()
    m5oc = sqlHelper.get_m5oc_topic(namespace, topic_name)
    design = m5oc.design(design_name)
    incoming_json = request.get_json()
    sql_dict = sqlHelper.get_sql(design, incoming_json)

    outgoing_sql = sql_dict["sql"]
    aggregates = sql_dict["aggregates"]
    query_attributes = sql_dict["query_attributes"]

    base_dict = {"sql": outgoing_sql, "error": False}
    base_dict["query_attributes"] = query_attributes
    base_dict["aggregates"] = aggregates

    if not incoming_json["run"]:
        return jsonify(base_dict)

    # we need to find the pipeline that loaded the data for this model
    # this is running off the assumption that there is only one pipeline
    # that can load data for a specific model
    project = Project.find()
    schedule_service = ScheduleService(project)
    schedule = schedule_service.find_namespace_schedule(
        m5oc.content["plugin_namespace"]
    )

    results = sqlHelper.get_query_results(
        schedule.extractor, schedule.loader, schedule.transform, outgoing_sql
    )
    base_dict["results"] = results
    base_dict["empty"] = len(results) == 0

    return jsonify(base_dict)


@sqlBP.route("/get/filter-options", methods=["GET"])
def get_filter_options():
    return jsonify(FilterOptions)
