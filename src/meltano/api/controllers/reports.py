from flask import Blueprint, jsonify, request
from .errors import InvalidFileNameError
from .reports_helper import ReportAlreadyExistsError, ReportsHelper

from meltano.api.api_blueprint import APIBlueprint
from meltano.api.security.auth import permit
from meltano.api.security.resource_filter import ResourceFilter, NameFilterMixin, Need
from meltano.api.security.readonly_killswitch import readonly_killswitch

reportsBP = APIBlueprint("reports", __name__)


class ReportFilter(NameFilterMixin, ResourceFilter):
    def __init__(self, *args):
        super().__init__(*args)

        self.needs(self.design_need)

    def design_need(self, permission_type, report):
        if permission_type == "view:reports":
            return Need("view:design", report["design"])


@reportsBP.errorhandler(ReportAlreadyExistsError)
def _handle(ex):
    report_name = ex.report["name"]
    return (
        jsonify(
            {
                "error": True,
                "code": f"A report with the name '{report_name}' already exists. Try renaming the report.",
            }
        ),
        409,
    )


@reportsBP.errorhandler(InvalidFileNameError)
def _handle(ex):
    return (
        jsonify(
            {
                "error": True,
                "code": f"The report name provided is invalid. Try a name without special characters.",
            }
        ),
        400,
    )


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
@readonly_killswitch
def save_report():
    reports_helper = ReportsHelper()
    post_data = request.get_json()
    response_data = reports_helper.save_report(post_data)
    return jsonify(response_data)


@reportsBP.route("/update", methods=["POST"])
@readonly_killswitch
def update_report():
    reports_helper = ReportsHelper()
    post_data = request.get_json()
    response_data = reports_helper.update_report(post_data)
    return jsonify(response_data)
