from flask import Blueprint, jsonify, request
from .reports_helper import ReportsHelper

from meltano.api.security import api_auth_required
from meltano.api.security.auth import permit
from meltano.api.security.resource_filter import ResourceFilter, NameFilterMixin, Need

reportsBP = Blueprint("reports", __name__, url_prefix="/api/v1/reports")


@reportsBP.before_request
@api_auth_required
def before_request():
    pass


class ReportFilter(NameFilterMixin, ResourceFilter):
    def __init__(self, *args):
        super().__init__(*args)

        self.needs(self.design_need)

    def design_need(self, permission_type, report):
        if permission_type == "view:reports":
            return Need("view:design", report["design"])


@reportsBP.route("/", methods=["GET"])
def index():
    reports_helper = ReportsHelper()
    reports = reports_helper.get_reports()
    reports = ReportFilter().filter_all("view:reports", reports)

    return jsonify(reports)


@reportsBP.route("/load/<report_name>", methods=["GET"])
def load_report(report_name):
    permit("view:reports", report_name)

    reports_helper = ReportsHelper()
    response_data = reports_helper.load_report(report_name)

    permit("view:design", response_data["design"])

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
