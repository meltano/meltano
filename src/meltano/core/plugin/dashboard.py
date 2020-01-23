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

        reports_parser = M5oCollectionParser(
            packages_dir.joinpath("reports"), M5oCollectionParserTypes.Report
        )
        reports = reports_parser.parse()

        dashboards_parser = M5oCollectionParser(
            packages_dir.joinpath("dashboards"), M5oCollectionParserTypes.Dashboard
        )
        dashboards = dashboards_parser.parse()

        logging.debug(f"Found {len(reports)} reports to import")
        logging.debug(f"Found {len(dashboards)} dashboards to import")

        report_id_map = self.add_reports(reports)
        self.add_dashboards(dashboards, report_id_map)

    def add_reports(self, reports):
        reports_service = ReportsService()
        local_reports = reports_service.get_reports()

        report_id_map = {}
        for report in reports:
            original_report_id = report["id"]
            report = self.add_report(report, local_reports)

            report_id_map[original_report_id] = report["id"]
            logging.debug(
                f"Mapped original report ID '{original_report_id}' to new ID '{report['id']}'"
            )

        return report_id_map

    def add_report(self, report, local_reports):
        try:
            imported_report = next(
                (
                    lr
                    for lr in local_reports
                    if "imported_from_id" in lr
                    and lr["imported_from_id"] == report["id"]
                ),
                None,
            )
            if imported_report is not None:
                raise ReportAlreadyExistsError(imported_report)

            report["imported_from_id"] = report["id"]
            report = ReportsService().save_report(report)

            logging.debug(
                f"Added report with name '{report['name']}', ID '{report['id']}'"
            )
        except ReportAlreadyExistsError as e:
            # ReportAlreadyExistsError can be raised by the `try` block or `save_report`
            report = e.report

            logging.debug(
                f"Found existing report with name '{report['name']}', ID '{report['id']}'"
            )

        return report

    def add_dashboards(self, dashboards, report_id_map):
        dashboards_service = DashboardsService()
        local_dashboards = dashboards_service.get_dashboards()

        for dashboard in dashboards:
            original_report_ids = dashboard["report_ids"]

            dashboard = self.add_dashboard(dashboard, local_dashboards)

            for original_report_id in original_report_ids:
                try:
                    report_id = report_id_map[original_report_id]
                except KeyError:
                    logging.debug(
                        f"No new report ID found for original ID '{original_report_id}"
                    )
                    continue

                DashboardsService().add_report_to_dashboard(
                    {"dashboard_id": dashboard["id"], "report_id": report_id}
                )

                logging.debug(
                    f"Added report with ID '{report_id}' to dashboard with ID '{dashboard['id']}'"
                )

    def add_dashboard(self, dashboard, local_dashboards):
        try:
            imported_dashboard = next(
                (
                    lr
                    for lr in local_dashboards
                    if "imported_from_id" in lr
                    and lr["imported_from_id"] == dashboard["id"]
                ),
                None,
            )
            if imported_dashboard is not None:
                raise DashboardAlreadyExistsError(imported_dashboard)

            dashboard["imported_from_id"] = dashboard["id"]
            dashboard = DashboardsService().save_dashboard(dashboard)

            logging.debug(
                f"Added dashboard with name '{dashboard['name']}', ID '{dashboard['id']}'"
            )
        except DashboardAlreadyExistsError as e:
            # DashboardAlreadyExistsError can be raised by the `try` block or `save_dashboard`
            dashboard = e.dashboard

            logging.debug(
                f"Found existing dashboard with name '{dashboard['name']}', ID '{dashboard['id']}'"
            )

        return dashboard
