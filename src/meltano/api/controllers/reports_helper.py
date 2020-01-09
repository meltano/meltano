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

    def get_report_by_name(self, name):
        reports = self.get_reports()
        report = next(filter(lambda r: r["name"] == name, reports), None)
        return report

    def get_reports(self):
        project = Project.find()
        reportsParser = M5oCollectionParser(
            project.analyze_dir("reports"), M5oCollectionParserTypes.Report
        )

        return reportsParser.parse()

    def load_report(self, name):
        return self.get_report_by_name(name)

    def save_report(self, data):
        name = data["name"]

        # guard if it already exists
        existing_report = self.get_report_by_name(name)
        if existing_report:
            raise ReportAlreadyExistsError(existing_report)

        project = Project.find()
        slug = slugify(name)
        file_path = project.analyze_dir("reports", f"{slug}.report.m5o")
        data = MeltanoAnalysisFileParser.fill_base_m5o_dict(file_path, slug, data)
        data["version"] = ReportsHelper.VERSION

        with file_path.open("w") as f:
            json.dump(data, f)

        return data

    def update_report(self, data):
        name = data["name"]
        existing_report = self.get_report_by_name(name)
        slug = existing_report["slug"]
        project = Project.find()
        file_path = project.analyze_dir("reports", f"{slug}.report.m5o")
        with open(file_path, "w") as f:
            json.dump(data, f)

        return data
