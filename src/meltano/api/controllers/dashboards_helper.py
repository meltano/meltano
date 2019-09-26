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


class DashboardAlreadyExistsError(Exception):
    """Occurs when a dashboard already exists."""

    def __init__(self, dashboard):
        self.dashboard = dashboard


class DashboardsHelper:
    VERSION = "1.0.0"

    def get_dashboards(self):
        project = Project.find()
        dashboardsParser = M5oCollectionParser(
            project.analyze_dir("dashboards"), M5oCollectionParserTypes.Dashboard
        )

        return dashboardsParser.parse()

    def get_dashboard_reports_with_query_results(self, reports):
        sqlHelper = SqlHelper()

        for report in reports:
            m5oc = sqlHelper.get_m5oc_topic(report["namespace"], report["model"])
            design = m5oc.design(report["design"])
            loader = report["query_payload"]["loader"]

            sql_dict = sqlHelper.get_sql(design, report["query_payload"])
            outgoing_sql = sql_dict["sql"]
            aggregates = sql_dict["aggregates"]

            report["query_results"] = sqlHelper.get_query_results(loader, outgoing_sql)
            report["query_result_aggregates"] = aggregates

        return reports

    def get_dashboard(self, dashboard_id):
        dashboards = self.get_dashboards()
        target_dashboard = [
            dashboard for dashboard in dashboards if dashboard["id"] == dashboard_id
        ]

        return target_dashboard[0]

    def get_dashboard_by_name(self, name):
        dashboards = self.get_dashboards()
        dashboard = next(filter(lambda r: r["name"] == name, dashboards), None)

        return dashboard

    def save_dashboard(self, data):
        dashboard_name = data["name"]

        # guard if it already exists
        existing_dashboard = self.get_dashboard_by_name(dashboard_name)
        if existing_dashboard:
            raise DashboardAlreadyExistsError(existing_dashboard)

        project = Project.find()
        slug = slugify(dashboard_name)
        file_path = project.analyze_dir("dashboards", f"{slug}.dashboard.m5o")
        data = MeltanoAnalysisFileParser.fill_base_m5o_dict(file_path, slug, data)
        data["version"] = DashboardsHelper.VERSION
        data["description"] = data["description"] or ""
        data["report_ids"] = []

        with file_path.open("w") as f:
            json.dump(data, f)

        return data

    def add_report_to_dashboard(self, data):
        project = Project.find()
        dashboard = self.get_dashboard(data["dashboard_id"])

        if data["report_id"] not in dashboard["report_ids"]:
            dashboard["report_ids"].append(data["report_id"])
            file_path = project.analyze_dir(
                "dashboards", f"{dashboard['slug']}.dashboard.m5o"
            )
            with file_path.open("w") as f:
                json.dump(dashboard, f)

        return dashboard

    def remove_report_from_dashboard(self, data):
        project = Project.find()
        dashboard = self.get_dashboard(data["dashboard_id"])

        if data["report_id"] in dashboard["report_ids"]:
            dashboard["report_ids"].remove(data["report_id"])
            file_path = project.analyze_dir(
                "dashboards", f"{dashboard['slug']}.dashboard.m5o"
            )

            with file_path.open("w") as f:
                json.dump(dashboard, f)

        return dashboard
