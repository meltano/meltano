import json
import os

from os.path import join
from pathlib import Path

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


class ReportAlreadyExistsError(Exception):
    """Occurs when a report already exists."""

    def __init__(self, report):
        self.report = report


class ReportsHelper:
    VERSION = "1.0.0"

    def has_reports(self):
        project = Project.find()
        m5oc_file = project.root_dir("model", "reports.m5oc")
        return Path.is_file(m5oc_file)

    def get_report_by_name(self, name):
        reports = self.get_reports()
        report = next(filter(lambda r: r["name"] == name, reports), None)
        return report

    def get_reports(self):
        project = Project.find()
        path = project.root_dir("model")
        reportsParser = M5oCollectionParser(path, M5oCollectionParserTypes.Report)
        return reportsParser.contents()

    def load_report(self, report_name):
        return self.get_report_by_name(report_name)

    def save_report(self, data):
        report_name = data["name"]

        # guard if it already exists
        existing_report = self.get_report_by_name(report_name)
        if existing_report:
            raise ReportAlreadyExistsError(existing_report)

        project = Project.find()
        slug = slugify(report_name)
        file_name = f"{slug}.report.m5o"
        file_path = project.root_dir("model", file_name)
        data = MeltanoAnalysisFileParser.fill_base_m5o_dict(file_path, slug, data)
        data["version"] = ReportsHelper.VERSION
        with open(file_path, "w") as f:
            json.dump(data, f)
        return data

    def update_report(self, data):
        project = Project.find()
        file_name = f"{data['slug']}.report.m5o"
        file_path = project.root_dir("model", file_name)
        with open(file_path, "w") as f:
            json.dump(data, f)
        return data
