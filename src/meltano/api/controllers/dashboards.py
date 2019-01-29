from flask import Blueprint, jsonify, request
from .dashboards_helper import DashboardsHelper

dashboardsBP = Blueprint("dashboards", __name__, url_prefix="/dashboards")


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


@dashboardsBP.route("/save", methods=["POST"])
def save_dashboard():
    dashboards_helper = DashboardsHelper()
    post_data = request.get_json()
    response_data = dashboards_helper.save_dashboard(post_data)
    return jsonify(response_data)
