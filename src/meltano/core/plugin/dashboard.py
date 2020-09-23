import logging

from meltano.core.plugin import ProjectPlugin, PluginType
from meltano.core.plugin_install_service import PluginInstallReason
from meltano.core.behavior.hookable import hook
from meltano.core.m5o.m5o_collection_parser import (
    M5oCollectionParser,
    M5oCollectionParserTypes,
)
from meltano.core.venv_service import VirtualEnv
from meltano.core.m5o.reports_service import ReportAlreadyExistsError, ReportsService
from meltano.core.m5o.dashboards_service import (
    DashboardAlreadyExistsError,
    DashboardsService,
)

logger = logging.getLogger(__name__)


class RecordImporter:
    def __init__(self, packages_dir, project):
        self.packages_dir = packages_dir
        self.project = project

    @property
    def record_type(self):
        return self.__class__.RECORD_TYPE

    def import_records(self):
        print(f"Importing {self.record_type}s...")

        records = self.records_to_import()

        logger.debug(f"Found {len(records)} {self.record_type}s to import")

        for record in records:
            self.import_record(record)

        logger.debug(f"Imported {len(records)} {self.record_type}s")

    def records_to_import(self):
        return self.get_package_records(f"{self.record_type}s")

    def import_record(self, importable_record):
        logger.debug(
            f"Importing {self.record_type} with name '{importable_record['name']}', ID '{importable_record['id']}'"
        )

        existing_record = self._get_record(importable_record["id"])
        if existing_record:
            logger.debug(
                f"Found existing {self.record_type} with ID '{existing_record['id']}'"
            )

            record = existing_record
            record = self.update_record_data(record, importable_record)

            save_func = self._update_record
        else:
            record = importable_record
            save_func = self._save_record

        record = self.save_record(record, save_func)

        print(f"Imported {self.record_type} '{record['name']}'")

    def update_record_data(self, record, importable_record):
        snapshots = self.snapshots_for_record(importable_record["id"])
        if not snapshots:
            logger.debug(
                f"No snapshots found: not overwriting anything with importable values"
            )
            return record

        for attribute in self.__class__.UPDATABLE_ATTRIBUTES:
            existing_value = record.get(attribute, None)
            importable_value = importable_record.get(attribute, None)

            if not importable_value:
                continue

            if importable_value == existing_value:
                logger.debug(
                    f"Existing '{attribute}' value matches importable value: nothing to do"
                )
                continue

            snapshot_values = [s.get(attribute, None) for s in snapshots]

            if existing_value in snapshot_values:
                logger.debug(
                    f"Existing '{attribute}' value matches a snapshot: overwriting with importable value"
                )
                record[attribute] = importable_value
            else:
                logger.debug(
                    f"Existing '{attribute}' value does not match any snapshots: not overwriting with importable value"
                )

        return record

    def snapshots_for_record(self, id):
        return [s for s in self.get_package_records("snapshots", id) if s["id"] == id]

    def save_record(self, record, save_func):
        original_name = record["name"]
        counter = 1

        while True:
            try:
                record = save_func(record)
                break
            except self.__class__.ALREADY_EXISTS_ERROR as e:
                if e.field == "slug":
                    counter += 1
                    record["name"] = f"{original_name} {counter}"

                    # Retry!
                    continue
                else:
                    record = e.record
                    break

        return record

    def get_package_records(self, *args):
        records_parser = M5oCollectionParser(
            self.packages_dir.joinpath(*args), self.record_type
        )
        return records_parser.parse()

    def _get_record(self, id):
        raise NotImplementedError

    def _save_record(self, record):
        raise NotImplementedError

    def _update_record(self, record):
        raise NotImplementedError


class ReportImporter(RecordImporter):
    RECORD_TYPE = M5oCollectionParserTypes.Report
    ALREADY_EXISTS_ERROR = ReportAlreadyExistsError
    UPDATABLE_ATTRIBUTES = [
        "chart_type",
        "design",
        "model",
        "namespace",
        "name",
        "query_payload",
    ]

    def __init__(self, *args):
        super().__init__(*args)

        self.reports_service = ReportsService(self.project)

    def _get_record(self, id):
        return self.reports_service.get_report(id)

    def _save_record(self, report):
        return self.reports_service.save_report(report)

    def _update_record(self, report):
        return self.reports_service.update_report(report)


class DashboardImporter(RecordImporter):
    RECORD_TYPE = M5oCollectionParserTypes.Dashboard
    ALREADY_EXISTS_ERROR = DashboardAlreadyExistsError
    UPDATABLE_ATTRIBUTES = ["name", "description", "report_ids"]

    def __init__(self, *args):
        super().__init__(*args)

        self.dashboards_service = DashboardsService(self.project)

    def import_record(self, dashboard):
        original_report_ids = dashboard["report_ids"]

        super().import_record(dashboard)

        self.add_reports_to_dashboard(dashboard, original_report_ids)

    def add_reports_to_dashboard(self, dashboard, report_ids):
        for report_id in report_ids:
            self.dashboards_service.add_report_to_dashboard(
                {"dashboard_id": dashboard["id"], "report_id": report_id}
            )

            logger.debug(
                f"Added report with ID '{report_id}' to dashboard with ID '{dashboard['id']}'"
            )

    def _get_record(self, id):
        return self.dashboards_service.get_dashboard(id)

    def _save_record(self, dashboard):
        return self.dashboards_service.save_dashboard(dashboard)

    def _update_record(self, dashboard):
        return self.dashboards_service.update_dashboard(
            {"dashboard": {"id": dashboard["id"]}, "new_settings": dashboard}
        )


class DashboardPlugin(ProjectPlugin):
    __plugin_type__ = PluginType.DASHBOARDS

    def __init__(self, *args, **kwargs):
        super().__init__(self.__class__.__plugin_type__, *args, **kwargs)

    @hook("after_install")
    def after_install(self, project, reason):
        if reason in (PluginInstallReason.ADD, PluginInstallReason.UPGRADE):
            venv = VirtualEnv(project.plugin_dir(self, "venv"))
            packages_dir = venv.site_packages_dir

            ReportImporter(packages_dir, project).import_records()
            DashboardImporter(packages_dir, project).import_records()
        else:
            print(
                f"Run `meltano add dashboard {self.name}` to re-add this dashboard to your project."
            )

    def is_invokable(self):
        return False
