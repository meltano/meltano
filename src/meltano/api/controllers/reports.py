from flask import Blueprint, jsonify, request
from .reports_helper import ReportsHelper
from .project_helper import project_api_route, project_from_slug

from meltano.api.security import api_auth_required
from meltano.api.security.auth import permit
from meltano.api.security.resource_filter import ResourceFilter, NameFilterMixin, Need

reportsBP = Blueprint("reports", __name__, url_prefix=project_api_route("reports"))


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
@project_from_slug
def index(project):
    reports_helper = ReportsHelper(project)
    response_data = reports_helper.get_reports()
    return jsonify(response_data)


@reportsBP.route("/load/<report_name>", methods=["GET"])
@project_from_slug
def load_report(report_name, project):
    permit("view:reports", report_name)

    reports_helper = ReportsHelper(project)
    response_data = reports_helper.load_report(report_name)

    permit("view:design", response_data["design"])

    return jsonify(response_data)


@reportsBP.route("/save", methods=["POST"])
@project_from_slug
def save_report(project):
    reports_helper = ReportsHelper(project)
    post_data = request.get_json()
    response_data = reports_helper.save_report(post_data)
    return jsonify(response_data)


@reportsBP.route("/update", methods=["POST"])
@project_from_slug
def update_report(project):
    reports_helper = ReportsHelper(project)
    post_data = request.get_json()
    response_data = reports_helper.update_report(post_data)
    return jsonify(response_data)
