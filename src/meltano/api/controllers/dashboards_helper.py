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
from meltano.core.schedule_service import ScheduleService
from meltano.core.utils import slugify, find_named
from .sql_helper import SqlHelper


class DashboardAlreadyExistsError(Exception):
    """Occurs when a dashboard already exists."""

    def __init__(self, dashboard_name):
        self.dashboard_name = dashboard_name


class DashboardDoesNotExistError(Exception):
    """Occurs when a dashboard does not exist."""

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
        project = Project.find()
        schedule_service = ScheduleService(project)
        sqlHelper = SqlHelper()

        for report in reports:
            m5oc = sqlHelper.get_m5oc_topic(report["namespace"], report["model"])
            design = m5oc.design(report["design"])
            schedule = schedule_service.find_namespace_schedule(
                m5oc.content["plugin_namespace"]
            )

            sql_dict = sqlHelper.get_sql(design, report["query_payload"])
            outgoing_sql = sql_dict["sql"]
            aggregates = sql_dict["aggregates"]

            report["query_results"] = sqlHelper.get_query_results(
                schedule.loader, outgoing_sql
            )
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
        name = data["name"]

        # guard if it already exists
        existing_dashboard = self.get_dashboard_by_name(name)
        if existing_dashboard:
            raise DashboardAlreadyExistsError(dashboard_name)

        project = Project.find()
        slug = slugify(name)
        file_path = project.analyze_dir("dashboards", f"{slug}.dashboard.m5o")
        data = MeltanoAnalysisFileParser.fill_base_m5o_dict(file_path, slug, data)
        data["version"] = DashboardsHelper.VERSION
        data["description"] = data["description"] or ""
        data["report_ids"] = []

        with file_path.open("w") as f:
            json.dump(data, f)

        return data

    def delete_dashboard(self, data):
        project = Project.find()
        dashboard = self.get_dashboard(data["id"])
        slug = dashboard["slug"]
        file_path = project.analyze_dir("dashboards", f"{slug}.dashboard.m5o")
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            raise DashboardDoesNotExistError(data)

        return data

    def update_dashboard(self, data):
        project = Project.find()
        dashboard = self.get_dashboard(data["dashboard"]["id"])
        slug = dashboard["slug"]
        file_path = project.analyze_dir("dashboards", f"{slug}.dashboard.m5o")
        if not os.path.exists(file_path):
            raise DashboardDoesNotExistError(data)

        new_settings = data["new_settings"]
        new_name = new_settings["name"]
        new_slug = slugify(new_name)
        new_file_path = project.analyze_dir("dashboards", f"{new_slug}.dashboard.m5o")
        is_same_file = new_slug == slug
        if not is_same_file and os.path.exists(new_file_path):
            raise DashboardAlreadyExistsError(new_name)

        os.remove(file_path)
        dashboard["slug"] = new_slug
        dashboard["name"] = new_name
        dashboard["description"] = new_settings["description"]
        dashboard["path"] = str(new_file_path)
        with new_file_path.open("w") as f:
            json.dump(dashboard, f)

        return dashboard

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
