from meltano.core.project import Project
from meltano.core.schedule_service import ScheduleService, ScheduleNotFoundError
from .sql_helper import SqlHelper


class DashboardReportScheduleNotFoundError(Exception):
    """Occurs when dashboard reports cannot be loaded because a schedule could not be found."""

    def __init__(self, namespace):
        self.namespace = namespace


class DashboardsHelper:
    def get_dashboard_reports_with_query_results(self, reports):
        project = Project.find()
        schedule_service = ScheduleService(project)
        sqlHelper = SqlHelper()

        for report in reports:
            m5oc = sqlHelper.get_m5oc_topic(report["namespace"], report["model"])
            design = m5oc.design(report["design"])
            try:
                schedule = schedule_service.find_namespace_schedule(
                    m5oc.content["plugin_namespace"]
                )
            except ScheduleNotFoundError as e:
                raise DashboardReportScheduleNotFoundError(e.namespace)

            sql_dict = sqlHelper.get_sql(design, report["query_payload"])
            outgoing_sql = sql_dict["sql"]
            aggregates = sql_dict["aggregates"]

            report["query_results"] = sqlHelper.get_query_results(
                schedule.loader, outgoing_sql
            )
            report["query_result_aggregates"] = aggregates

        return reports
