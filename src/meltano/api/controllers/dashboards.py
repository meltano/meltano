from flask import Blueprint, jsonify, request
from .dashboards_helper import DashboardsHelper

dashboardsBP = Blueprint("dashboards", __name__, url_prefix="/api/v1/dashboards")


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
def save_dashboard():
    dashboards_helper = DashboardsHelper()
    post_data = request.get_json()
    response_data = dashboards_helper.save_dashboard(post_data)
    return jsonify(response_data)


@dashboardsBP.route("/dashboard/report/add", methods=["POST"])
def add_report_to_dashboard():
    dashboards_helper = DashboardsHelper()
    post_data = request.get_json()
    response_data = dashboards_helper.add_report_to_dashboard(post_data)
    return jsonify(response_data)


@dashboardsBP.route("/dashboard/report/remove", methods=["POST"])
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
