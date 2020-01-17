from flask import jsonify, request
from .dashboards_helper import (
    DashboardAlreadyExistsError,
    DashboardDoesNotExistError,
    DashboardsHelper,
)
from .errors import InvalidFileNameError
from meltano.api.api_blueprint import APIBlueprint
from meltano.api.security.readonly_killswitch import readonly_killswitch


dashboardsBP = APIBlueprint("dashboards", __name__)


@dashboardsBP.errorhandler(DashboardAlreadyExistsError)
def _handle(ex):
    dashboard_name = ex.dashboard_name
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


@dashboardsBP.route("/all", methods=["GET"])
def get_dashboards():
    dashboards_helper = DashboardsHelper()
    response_data = dashboards_helper.get_dashboards()
    return jsonify(response_data)


@dashboardsBP.route("/dashboard/<dashboard_id>", methods=["GET"])
def get_dashboard(dashboard_id):
    dashboards_helper = DashboardsHelper()
    response_data = dashboards_helper.get_dashboard(dashboard_id)
    return jsonify(response_data)


@dashboardsBP.route("/dashboard/save", methods=["POST"])
@readonly_killswitch
def save_dashboard():
    """
    Endpoint for saving a dashboard
    """
    dashboards_helper = DashboardsHelper()
    post_data = request.get_json()
    response_data = dashboards_helper.save_dashboard(post_data)
    return jsonify(response_data)


@dashboardsBP.route("/dashboard/delete", methods=["DELETE"])
@readonly_killswitch
def delete_dashboard():
    """
    Endpoint for deleting a dashboard
    """
    dashboards_helper = DashboardsHelper()
    post_data = request.get_json()
    response_data = dashboards_helper.delete_dashboard(post_data)
    return jsonify(response_data)


@dashboardsBP.route("/dashboard/update", methods=["POST"])
@readonly_killswitch
def update_dashboard():
    """
    Endpoint for updating a dashboard
    """
    dashboards_helper = DashboardsHelper()
    post_data = request.get_json()
    response_data = dashboards_helper.update_dashboard(post_data)
    return jsonify(response_data)


@dashboardsBP.route("/dashboard/report/add", methods=["POST"])
@readonly_killswitch
def add_report_to_dashboard():
    dashboards_helper = DashboardsHelper()
    post_data = request.get_json()
    response_data = dashboards_helper.add_report_to_dashboard(post_data)
    return jsonify(response_data)


@dashboardsBP.route("/dashboard/report/remove", methods=["POST"])
@readonly_killswitch
def remove_report_from_dashboard():
    dashboards_helper = DashboardsHelper()
    post_data = request.get_json()
    response_data = dashboards_helper.remove_report_from_dashboard(post_data)
    return jsonify(response_data)


@dashboardsBP.route("/dashboard/reports", methods=["POST"])
def get_dashboard_reports_with_query_results():
    dashboards_helper = DashboardsHelper()
    post_data = request.get_json()

    response_data = dashboards_helper.get_dashboard_reports_with_query_results(
        post_data
    )
    return jsonify(response_data)
