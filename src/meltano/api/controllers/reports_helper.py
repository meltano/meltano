import os
import json
import time
import uuid
from os.path import join
from pathlib import Path
from meltano.core.utils import slugify

from .m5oc_collection_file import M5ocCollectionFile


class ReportsHelper:
    def __init__(self):
        self.meltano_model_path = join(os.getcwd(), "model")
        self.report_version = "0.1.0"

    def has_reports(self):
        m5oc_file = Path(self.meltano_model_path).joinpath("reports.m5oc")
        return Path.is_file(m5oc_file)

    def get_report_m5oc(self):
        m5oc_file = Path(self.meltano_model_path).joinpath("reports.m5oc")
        with m5oc_file.open() as f:
            m5oc = M5ocCollectionFile.load(f)
        return m5oc

    def get_reports(self):

        # TODO reenable below commented out implementation and remove the other temporary
        # solution when we can leverage Michaël's file watcher implementation as it will
        # allow us to automatically create a reports.m5oc to read/write to more strategically
        # (likely on another thread) vs manually iterating all reports every time get_reports()
        # is called (one m5oc file vs n *.reports.m5o files)
        # reports = self.get_report_m5oc().reports if self.has_reports() else []
        # return reports

        contents = []
        report_files = list(Path(self.meltano_model_path).glob("*.report.m5o"))
        for report in report_files:
            file_name = report.parts[-1]
            m5oc_file = Path(self.meltano_model_path).joinpath(file_name)
            with m5oc_file.open() as f:
                contents.append(json.load(f))
        return contents

    def load_report(self, report_name):

        # TODO reenable below commented out implementation in combination with get_reports() TODO
        # return self.get_report_m5oc().report(report_name)

        reports = self.get_reports()
        target_report = [report for report in reports if report["name"] == report_name]
        return target_report[0]

    def save_report(self, data):
        data["id"] = uuid.uuid4().hex
        data["version"] = self.report_version
        data["createdAt"] = time.time()
        data["slug"] = slugify(data["name"])
        file_name = data["slug"] + ".report.m5o"
        file_path = Path(self.meltano_model_path).joinpath(file_name)
        with open(file_path, "w") as f:
            json.dump(data, f)
        return data

    def update_report(self, data):
        file_name = data["slug"] + ".report.m5o"
        file_path = Path(self.meltano_model_path).joinpath(file_name)
        with open(file_path, "w") as f:
            json.dump(data, f)
        return data
