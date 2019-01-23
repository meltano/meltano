import os
import json
from os.path import join
from pathlib import Path

from .m5oc_file import M5ocFile


class ReportsHelper:
    def __init__(self):
        self.meltano_model_path = join(os.getcwd(), "model")

    def get_report_m5oc(self):
        m5oc_file = Path(self.meltano_model_path).joinpath("reports.m5oc")
        with m5oc_file.open() as f:
            m5oc = M5ocFile.load(f)
        return m5oc

    def get_reports(self):
        return self.get_report_m5oc().reports

    def load_report(self, report_name):
        return self.get_report_m5oc().report(report_name)

    def save_report(self, data):
        name = data["name"]
        file_name = name + ".report.m5o"
        file_path = Path(self.meltano_model_path).joinpath(file_name)
        with open(file_path, "w") as f:
            json.dump(data, f)
        return data
