import os
import json
import time
import uuid
from os.path import join
from pathlib import Path
from meltano.core.utils import slugify

from .sql_helper import SqlHelper


class DashboardsHelper:
    def __init__(self):
        self.meltano_model_path = join(os.getcwd(), "model")
        self.dashboard_version = "0.1.0"

    def get_dashboards(self):
        contents = []
        dashboard_files = list(Path(self.meltano_model_path).glob("*.dashboard.m5o"))
        for dashboard in dashboard_files:
            file_name = dashboard.parts[-1]
            file = Path(self.meltano_model_path).joinpath(file_name)
            with file.open() as f:
                contents.append(json.load(f))
        return contents

    def get_dashboard_reports_with_query_results(self, reports):
        sqlHelper = SqlHelper()
        for report in reports:
            m5oc = sqlHelper.get_m5oc_model(report["model"])
            design = m5oc.design(report["design"])
            connection_name = m5oc.connection("connection")

            sql_dict = sqlHelper.get_sql(design, report["queryPayload"])
            outgoing_sql = sql_dict["sql"]
            report["queryResults"] = sqlHelper.get_query_results(connection_name, outgoing_sql)
        return reports

    def get_dashboard(self, dashboard_id):
        dashboards = self.get_dashboards()
        target_dashboard = [
            dashboard for dashboard in dashboards if dashboard["id"] == dashboard_id
        ]
        return target_dashboard[0]

    def save_dashboard(self, data):
        data["id"] = uuid.uuid4().hex
        data["version"] = self.dashboard_version
        data["createdAt"] = time.time()
        data["slug"] = slugify(data["name"])
        data["reportIds"] = []
        file_name = data["slug"] + ".dashboard.m5o"
        file_path = Path(self.meltano_model_path).joinpath(file_name)
        with open(file_path, "w") as f:
            json.dump(data, f)
        return data

    def add_report_to_dashboard(self, data):
        dashboard = self.get_dashboard(data["dashboardId"])
        dashboard["reportIds"].append(data["reportId"])
        file_name = dashboard["slug"] + ".dashboard.m5o"
        file_path = Path(self.meltano_model_path).joinpath(file_name)
        with open(file_path, "w") as f:
            json.dump(dashboard, f)
        return dashboard

    def remove_report_from_dashboard(self, data):
        dashboard = self.get_dashboard(data["dashboardId"])
        dashboard["reportIds"].remove(data["reportId"])
        file_name = dashboard["slug"] + ".dashboard.m5o"
        file_path = Path(self.meltano_model_path).joinpath(file_name)
        with open(file_path, "w") as f:
            json.dump(dashboard, f)
        return dashboard
