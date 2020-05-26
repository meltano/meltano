from meltano.core.project import Project
from meltano.core.schedule_service import ScheduleService

from .sql_helper import SqlHelper


class ReportsHelper:
    VERSION = "1.0.0"

    def get_report_with_query_results(self, report, today=None):
        project = Project.find()
        schedule_service = ScheduleService(project)
        sql_helper = SqlHelper()
        report_with_query_results = self.update_report_with_query_results(
            report, schedule_service, sql_helper, today=today
        )

        return report_with_query_results

    def update_report_with_query_results(
        self, report, schedule_service, sql_helper, today=None
    ):
        m5oc = sql_helper.get_m5oc_topic(report["namespace"], report["model"])
        design_helper = m5oc.design(report["design"])
        schedule = schedule_service.find_namespace_schedule(
            m5oc.content["plugin_namespace"]
        )

        report["full_design"] = design_helper.design

        query_payload = report["query_payload"]
        if today:
            query_payload["today"] = today

        sql_dict = sql_helper.get_sql(design_helper, query_payload)
        outgoing_sql = sql_dict["sql"]
        aggregates = sql_dict["aggregates"]

        report["query_results"] = sql_helper.get_query_results(
            schedule.extractor, schedule.loader, schedule.transform, outgoing_sql
        )
        report["query_result_aggregates"] = aggregates

        return report
