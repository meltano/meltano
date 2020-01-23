import os
import json

from meltano.core.project import Project
from meltano.core.utils import slugify

from .m5o_collection_parser import M5oCollectionParser, M5oCollectionParserTypes
from .m5o_file_parser import MeltanoAnalysisFileParser


class ReportAlreadyExistsError(Exception):
    """Occurs when a report already exists."""

    def __init__(self, report):
        self.report = report


class ReportsService:
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
        data = MeltanoAnalysisFileParser.fill_base_m5o_dict(
            file_path.relative_to(project.root), slug, data
        )
        data["version"] = ReportsService.VERSION

        with file_path.open("w") as f:
            json.dump(data, f)

        return data

    def update_report(self, data):
        name = data["name"]
        existing_report = self.get_report_by_name(name)
        slug = existing_report["slug"]

        project = Project.find()
        file_path = project.analyze_dir("reports", f"{slug}.report.m5o")

        new_name = data["name"]
        new_slug = slugify(new_name)
        new_file_path = project.analyze_dir("reports", f"{new_slug}.report.m5o")
        is_same_file = new_slug == slug
        if not is_same_file and os.path.exists(new_file_path):
            with new_file_path.open() as f:
                existing_report = json.load(f)
            raise ReportAlreadyExistsError(existing_report)

        os.remove(file_path)

        data["slug"] = new_slug
        data["path"] = str(new_file_path.relative_to(project.root))
        with new_file_path.open("w") as f:
            json.dump(data, f)

        return data
