from flask import Blueprint, jsonify, request
from .dashboards_helper import DashboardsHelper
from .project_helper import project_api_route, project_from_slug

dashboardsBP = Blueprint("dashboards", __name__, url_prefix=project_api_route("dashboards"))


@dashboardsBP.route("/all", methods=["GET"])
@project_from_slug
def get_dashboards(project):
    dashboards_helper = DashboardsHelper(project)
    response_data = dashboards_helper.get_dashboards()
    return jsonify(response_data)


@dashboardsBP.route("/dashboard/<dashboard_id>", methods=["GET"])
@project_from_slug
def get_dashboard(dashboard_id, project):
    dashboards_helper = DashboardsHelper(project)
    response_data = dashboards_helper.get_dashboard(dashboard_id)
    return jsonify(response_data)


@dashboardsBP.route("/dashboard/save", methods=["POST"])
@project_from_slug
def save_dashboard(project):
    dashboards_helper = DashboardsHelper(project)
    post_data = request.get_json()
    response_data = dashboards_helper.save_dashboard(post_data)
    return jsonify(response_data)


@dashboardsBP.route("/dashboard/report/add", methods=["POST"])
@project_from_slug
def add_report_to_dashboard(project):
    dashboards_helper = DashboardsHelper(project)
    post_data = request.get_json()
    response_data = dashboards_helper.add_report_to_dashboard(post_data)
    return jsonify(response_data)


@dashboardsBP.route("/dashboard/report/remove", methods=["POST"])
@project_from_slug
def remove_report_from_dashboard(project):
    dashboards_helper = DashboardsHelper(project)
    post_data = request.get_json()
    response_data = dashboards_helper.remove_report_from_dashboard(post_data)
    return jsonify(response_data)


@dashboardsBP.route("/dashboard/reports", methods=["POST"])
@project_from_slug
def get_dashboard_reports_with_query_results(project):
    dashboards_helper = DashboardsHelper(project)
    post_data = request.get_json()
    response_data = dashboards_helper.get_dashboard_reports_with_query_results(
        post_data
    )
    return jsonify(response_data)
