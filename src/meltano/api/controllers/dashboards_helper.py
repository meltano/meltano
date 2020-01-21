from meltano.core.project import Project
from meltano.core.schedule_service import ScheduleService
from meltano.core.utils import slugify, find_named
from .reports_helper import ReportsHelper
from .sql_helper import SqlHelper


class DashboardReportScheduleNotFoundError(Exception):
    """Occurs when dashboard reports cannot be loaded because a schedule could not be found."""

    def __init__(self, namespace):
        self.namespace = namespace


class DashboardsHelper:
    def get_dashboard_reports_with_query_results(self, reports):
        project = Project.find()
        schedule_service = ScheduleService(project)
        sql_helper = SqlHelper()
        reports_helper = ReportsHelper()

        for report in reports:
            reports_helper.update_report_with_query_results(report, schedule_service, sql_helper)

        return reports
