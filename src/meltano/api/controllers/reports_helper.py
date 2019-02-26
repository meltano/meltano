import json
import os

from os.path import join
from pathlib import Path

from meltano.core.m5o.m5o_file_parser import MeltanoAnalysisFileParser
from meltano.core.m5o.m5oc_file import M5ocFile
from meltano.core.m5o.m5o_file_parser import MeltanoAnalysisFileParser
from meltano.core.m5o.m5o_collection_parser import (
    M5oCollectionParser,
    M5oCollectionParserTypes,
)
from meltano.core.project import Project
from meltano.core.utils import slugify
from meltano.core.m5o.m5o_collection_parser import (
    M5oCollectionParser,
    M5oCollectionParserTypes,
)


class ReportsHelper:
    VERSION = "1.0.0"

    def __init__(self):
        pass

    def has_reports(self):
        m5oc_file = Path(Project.meltano_model_path).joinpath("reports.m5oc")
        return Path.is_file(m5oc_file)

    def get_report_m5oc(self):
        m5oc_file = Path(Project.meltano_model_path).joinpath("reports.m5oc")
        return M5ocFile.load(m5oc_file)

    def get_reports(self):
        path = Path(Project.meltano_model_path)
        reportsParser = M5oCollectionParser(path, M5oCollectionParserTypes.Report)
        return reportsParser.contents()

    def load_report(self, report_name):
        reports = self.get_reports()
        target_report = [report for report in reports if report["name"] == report_name]
        return target_report[0]

    def save_report(self, data):
        slug = slugify(data["name"])
        file_name = f"{slug}.report.m5o"
        file_path = Path(Project.meltano_model_path).joinpath(file_name)
        data = MeltanoAnalysisFileParser.fill_base_m5o_dict(file_path, slug, data)
        data["version"] = ReportsHelper.VERSION
        with open(file_path, "w") as f:
            json.dump(data, f)
        return data

    def update_report(self, data):
        file_name = f"{data['slug']}.report.m5o"
        file_path = Path(Project.meltano_model_path).joinpath(file_name)
        with open(file_path, "w") as f:
            json.dump(data, f)
        return data
