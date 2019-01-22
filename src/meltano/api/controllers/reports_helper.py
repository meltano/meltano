import os
import json
from os.path import join
from pathlib import Path


class ReportsHelper:
    def __init__(self):
        self.meltano_model_path = join(os.getcwd(), "model")

        self.reports_directory_path = Path(self.meltano_model_path).joinpath("reports")
        if not Path.is_dir(self.reports_directory_path):
            Path.mkdir(self.reports_directory_path)

    def save_report(self, data):
        name = data["name"]
        file_name = name + ".report.m5o"
        file_path = Path(self.reports_directory_path).joinpath(file_name)
        with open(file_path, "w") as f:
            json.dump(data, f)
        return data
