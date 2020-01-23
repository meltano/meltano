import logging

from meltano.core.plugin import PluginInstall, PluginType
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


class DashboardPlugin(PluginInstall):
    __plugin_type__ = PluginType.DASHBOARDS

    def __init__(self, *args, **kwargs):
        super().__init__(self.__class__.__plugin_type__, *args, **kwargs)

    @hook("after_install")
    def after_install(self, project, args=[]):
        venv = VirtualEnv(project.plugin_dir(self, "venv"))
        packages_dir = venv.site_packages_dir

        logging.debug(f"Importing reports...")

        reports_parser = M5oCollectionParser(
            packages_dir.joinpath("reports"), M5oCollectionParserTypes.Report
        )
        reports = reports_parser.parse()
        logging.debug(f"Found {len(reports)} reports to import")

        reports_service = ReportsService(project)
        self.import_reports(reports, reports_service=reports_service)
        logging.debug(f"Finished importing {len(reports)} reports")

        logging.debug(f"Importing dashboards...")

        dashboards_parser = M5oCollectionParser(
            packages_dir.joinpath("dashboards"), M5oCollectionParserTypes.Dashboard
        )
        dashboards = dashboards_parser.parse()
        logging.debug(f"Found {len(dashboards)} dashboards to import")

        dashboards_service = DashboardsService(project)
        self.import_dashboards(dashboards, dashboards_service=dashboards_service)
        logging.debug(f"Finished importing {len(reports)} reports")

    def import_reports(self, reports, reports_service):
        for report in reports:
            self.import_report(report, reports_service=reports_service)

    def import_dashboards(self, dashboards, dashboards_service):
        for dashboard in dashboards:
            original_report_ids = dashboard["report_ids"]

            dashboard = self.import_dashboard(
                dashboard, dashboards_service=dashboards_service
            )

            self.add_reports_to_dashboard(
                dashboard, original_report_ids, dashboards_service=dashboards_service
            )

    def import_report(self, report, reports_service):
        return self.import_record(
            report,
            "record",
            get_func=reports_service.get_report,
            save_func=reports_service.save_report,
            already_exists_error=ReportAlreadyExistsError,
        )

    def import_dashboard(self, dashboard, dashboards_service):
        return self.import_record(
            dashboard,
            "dashboard",
            get_func=dashboards_service.get_dashboard,
            save_func=dashboards_service.save_dashboard,
            already_exists_error=DashboardAlreadyExistsError,
        )

    def import_record(
        self, record, record_type, get_func, save_func, already_exists_error
    ):
        imported_record = get_func(record["id"])
        if imported_record:
            record = imported_record

            logging.debug(
                f"Found existing {record_type} with name '{record['name']}', ID '{record['id']}'"
            )
        else:
            original_name = record["name"]
            counter = 1
            while True:
                try:
                    record = save_func(record, keep_id=True)
                except already_exists_error:
                    counter += 1
                    record["name"] = f"{original_name} {counter}"
                else:
                    break

            logging.debug(
                f"Added {record_type} with name '{record['name']}', ID '{record['id']}'"
            )

        return record

    def add_reports_to_dashboard(self, dashboard, report_ids, dashboards_service):
        for report_id in report_ids:
            dashboards_service.add_report_to_dashboard(
                {"dashboard_id": dashboard["id"], "report_id": report_id}
            )

            logging.debug(
                f"Added report with ID '{report_id}' to dashboard with ID '{dashboard['id']}'"
            )
