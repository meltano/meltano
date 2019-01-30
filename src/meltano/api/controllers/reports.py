from flask import Blueprint, jsonify, request
from .reports_helper import ReportsHelper

reportsBP = Blueprint("reports", __name__, url_prefix="/reports")


@reportsBP.route("/", methods=["GET"])
def index():
    reports_helper = ReportsHelper()
    response_data = reports_helper.get_reports()
    return jsonify(response_data)


@reportsBP.route("/load/<report_name>", methods=["GET"])
def load_report(report_name):
    reports_helper = ReportsHelper()
    response_data = reports_helper.load_report(report_name)
    return jsonify(response_data)


@reportsBP.route("/save", methods=["POST"])
def save_report():
    reports_helper = ReportsHelper()
    post_data = request.get_json()
    response_data = reports_helper.save_report(post_data)
    return jsonify(response_data)


@reportsBP.route("/update", methods=["POST"])
def update_report():
    reports_helper = ReportsHelper()
    post_data = request.get_json()
    response_data = reports_helper.update_report(post_data)
    return jsonify(response_data)
