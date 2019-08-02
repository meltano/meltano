import os
import json
from os.path import join
from pathlib import Path

from meltano.core.m5o.m5o_collection_parser import (
    M5oCollectionParser,
    M5oCollectionParserTypes,
)
from meltano.core.m5o.m5o_file_parser import MeltanoAnalysisFileParser
from meltano.core.project import Project
from meltano.core.utils import slugify
from .sql_helper import SqlHelper


class DashboardsHelper:
    VERSION = "1.0.0"

    def get_dashboards(self):
        project = Project.find()
        path = project.root_dir("model")
        dashboardsParser = M5oCollectionParser(path, M5oCollectionParserTypes.Dashboard)
        return dashboardsParser.contents()

    def get_dashboard_reports_with_query_results(self, reports):
        sqlHelper = SqlHelper()
        for report in reports:
            # TODO: refactor front-end `model` → `topic`
            m5oc = sqlHelper.get_m5oc_topic(report["model"])
            design = m5oc.design(report["design"])
            dialect = report["query_payload"]["dialect"]

            sql_dict = sqlHelper.get_sql(design, report["query_payload"])
            outgoing_sql = sql_dict["sql"]
            aggregates = sql_dict["aggregates"]

            report["query_results"] = sqlHelper.get_query_results(dialect, outgoing_sql)
            report["query_result_aggregates"] = aggregates

        return reports

    def get_dashboard(self, dashboard_id):
        dashboards = self.get_dashboards()
        target_dashboard = [
            dashboard for dashboard in dashboards if dashboard["id"] == dashboard_id
        ]
        return target_dashboard[0]

    def save_dashboard(self, data):
        project = Project.find()
        slug = slugify(data["name"])
        file_name = f"{slug}.dashboard.m5o"
        file_path = project.root_dir("model", file_name)
        data = MeltanoAnalysisFileParser.fill_base_m5o_dict(file_path, slug, data)
        data["version"] = DashboardsHelper.VERSION
        data["description"] = data["description"] or ""
        data["report_ids"] = []
        with open(file_path, "w") as f:
            json.dump(data, f)
        return data

    def add_report_to_dashboard(self, data):
        project = Project.find()
        dashboard = self.get_dashboard(data["dashboard_id"])

        if data["report_id"] not in dashboard["report_ids"]:
            dashboard["report_ids"].append(data["report_id"])
            file_name = f"{dashboard['slug']}.dashboard.m5o"
            file_path = project.root_dir("model", file_name)
            with open(file_path, "w") as f:
                json.dump(dashboard, f)

        return dashboard

    def remove_report_from_dashboard(self, data):
        project = Project.find()
        dashboard = self.get_dashboard(data["dashboard_id"])
        if data["report_id"] in dashboard["report_ids"]:
            dashboard["report_ids"].remove(data["report_id"])
            file_name = f"{dashboard['slug']}.dashboard.m5o"
            file_path = project.root_dir("model", file_name)
            with open(file_path, "w") as f:
                json.dump(dashboard, f)

        return dashboard
