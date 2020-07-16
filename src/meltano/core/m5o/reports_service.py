import os
import json

from meltano.core.utils import slugify

from .m5o_collection_parser import M5oCollectionParser, M5oCollectionParserTypes
from .m5o_file_parser import MeltanoAnalysisFileParser
from .dashboards_service import DashboardsService


class ReportAlreadyExistsError(Exception):
    """Occurs when a report already exists."""

    def __init__(self, report, field):
        self.report = report
        self.field = field

    @property
    def record(self):
        return self.report


class ReportDoesNotExistError(Exception):
    """Occurs when a report does not exist."""

    def __init__(self, report):
        self.report = report


class ReportsService:
    VERSION = "1.0.0"

    def __init__(self, project):
        self.project = project

    def get_reports(self):
        reportsParser = M5oCollectionParser(
            self.project.analyze_dir("reports"), M5oCollectionParserTypes.Report
        )

        return reportsParser.parse()

    def get_report(self, report_id):
        reports = self.get_reports()
        report = next(filter(lambda r: r["id"] == report_id, reports), None)
        return report

    def save_report(self, data):
        if "id" in data:
            existing_report = self.get_report(data["id"])
            if existing_report:
                raise ReportAlreadyExistsError(existing_report, "id")

        name = data["name"]
        slug = slugify(name)
        file_path = self.project.analyze_dir("reports", f"{slug}.report.m5o")

        if os.path.exists(file_path):
            with file_path.open() as f:
                existing_report = json.load(f)
            raise ReportAlreadyExistsError(existing_report, "slug")

        data = MeltanoAnalysisFileParser.fill_base_m5o_dict(
            file_path.relative_to(self.project.root), slug, data
        )
        data["version"] = ReportsService.VERSION

        with self.project.file_update():
            with file_path.open("w") as f:
                json.dump(data, f)

        return data

    def delete_report(self, data):
        report = self.get_report(data["id"])
        slug = report["slug"]
        file_path = self.project.analyze_dir("reports", f"{slug}.report.m5o")
        if not os.path.exists(file_path):
            raise ReportDoesNotExistError(data)

        DashboardsService(self.project).remove_report_from_dashboards(report["id"])

        with self.project.file_update():
            os.remove(file_path)

        return data

    def update_report(self, data):
        id = data["id"]
        existing_report = self.get_report(id)
        slug = existing_report["slug"]

        file_path = self.project.analyze_dir("reports", f"{slug}.report.m5o")

        new_name = data["name"]
        new_slug = slugify(new_name)
        new_file_path = self.project.analyze_dir("reports", f"{new_slug}.report.m5o")
        is_same_file = new_slug == slug
        if not is_same_file and os.path.exists(new_file_path):
            with new_file_path.open() as f:
                existing_report = json.load(f)
            raise ReportAlreadyExistsError(existing_report, "slug")

        with self.project.file_update():
            os.remove(file_path)

        data["slug"] = new_slug
        data["path"] = str(new_file_path.relative_to(self.project.root))

        with self.project.file_update():
            with new_file_path.open("w") as f:
                json.dump(data, f)

        return data
