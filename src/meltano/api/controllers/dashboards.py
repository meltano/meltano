from flask import jsonify, request
from .dashboards_helper import DashboardsHelper
from meltano.core.project import Project
from meltano.core.m5o.dashboards_service import (
    DashboardAlreadyExistsError,
    DashboardDoesNotExistError,
    DashboardsService,
)
from meltano.core.schedule_service import ScheduleNotFoundError
from .errors import InvalidFileNameError
from meltano.api.api_blueprint import APIBlueprint
from meltano.api.security.auth import block_if_readonly
from flask_security import roles_required


dashboardsBP = APIBlueprint("dashboards", __name__)


def dashboards_service():
    project = Project.find()
    return DashboardsService(project)


@dashboardsBP.errorhandler(DashboardAlreadyExistsError)
def _handle(ex):
    dashboard_name = ex.dashboard["name"]
    return (
        jsonify(
            {
                "error": True,
                "code": f"A dashboard with the name '{dashboard_name}' already exists. Try renaming the dashboard.",
            }
        ),
        409,
    )


@dashboardsBP.errorhandler(DashboardDoesNotExistError)
def _handle(ex):
    dashboard_name = ex.dashboard["name"]
    return (
        jsonify(
            {"error": True, "code": f"The dashboard '{dashboard_name}' does not exist."}
        ),
        404,
    )


@dashboardsBP.errorhandler(InvalidFileNameError)
def _handle(ex):
    return (
        jsonify(
            {
                "error": True,
                "code": f"The dashboard name provided is invalid. Try a name without special characters.",
            }
        ),
        400,
    )


@dashboardsBP.errorhandler(ScheduleNotFoundError)
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


@dashboardsBP.route("/all", methods=["GET"])
def get_dashboards():
    response_data = dashboards_service().get_dashboards()
    return jsonify(response_data)


@dashboardsBP.route("/dashboard/<dashboard_id>", methods=["GET"])
def get_dashboard(dashboard_id):
    response_data = dashboards_service().get_dashboard(dashboard_id)
    return jsonify(response_data)


@dashboardsBP.route("/dashboard/save", methods=["POST"])
@block_if_readonly
def save_dashboard():
    """
    Endpoint for saving a dashboard
    """
    post_data = request.get_json()
    response_data = dashboards_service().save_dashboard(post_data)
    return jsonify(response_data)


@dashboardsBP.route("/dashboard/delete", methods=["DELETE"])
@block_if_readonly
def delete_dashboard():
    """
    Endpoint for deleting a dashboard
    """
    post_data = request.get_json()
    response_data = dashboards_service().delete_dashboard(post_data)
    return jsonify(response_data)


@dashboardsBP.route("/dashboard/update", methods=["POST"])
@block_if_readonly
def update_dashboard():
    """
    Endpoint for updating a dashboard
    """
    post_data = request.get_json()
    response_data = dashboards_service().update_dashboard(post_data)
    return jsonify(response_data)


@dashboardsBP.route("/dashboard/report/add", methods=["POST"])
@block_if_readonly
def add_report_to_dashboard():
    post_data = request.get_json()
    response_data = dashboards_service().add_report_to_dashboard(post_data)
    return jsonify(response_data)


@dashboardsBP.route("/dashboard/report/remove", methods=["POST"])
@block_if_readonly
def remove_report_from_dashboard():
    post_data = request.get_json()
    response_data = dashboards_service().remove_report_from_dashboard(post_data)
    return jsonify(response_data)


@dashboardsBP.route("/dashboard/reports", methods=["POST"])
def get_dashboard_reports_with_query_results():
    dashboards_helper = DashboardsHelper()
    post_data = request.get_json()
    response_data = dashboards_helper.get_dashboard_reports_with_query_results(
        post_data
    )
    return jsonify(response_data)
