import sqlalchemy
from flask import jsonify, request

from .errors import InvalidFileNameError

from meltano.core.project import Project
from meltano.core.m5o.reports_service import ReportAlreadyExistsError, ReportsService

from meltano.api.api_blueprint import APIBlueprint
from meltano.api.security.resource_filter import ResourceFilter, NameFilterMixin, Need
from meltano.api.security.readonly_killswitch import readonly_killswitch

reportsBP = APIBlueprint("reports", __name__)


def reports_service():
    project = Project.find()
    return ReportsService(project)


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
    reports = reports_service().get_reports()
    reports = ReportFilter().filter_all("view:reports", reports)
    return jsonify(reports)


@reportsBP.route("/save", methods=["POST"])
@readonly_killswitch
def save_report():
    post_data = request.get_json()
    response_data = reports_service().save_report(post_data)
    return jsonify(response_data)


@reportsBP.route("/update", methods=["POST"])
@readonly_killswitch
def update_report():
    post_data = request.get_json()
    response_data = reports_service().update_report(post_data)
    return jsonify(response_data)
