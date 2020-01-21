import logging

from meltano.core.plugin import PluginInstall, PluginType
from meltano.core.behavior.hookable import hook
from meltano.core.m5o.m5o_collection_parser import (
    M5oCollectionParser,
    M5oCollectionParserTypes,
)
from meltano.core.venv_service import VirtualEnv
from meltano.api.controllers.reports_helper import (
    ReportAlreadyExistsError,
    ReportsHelper,
)
from meltano.api.controllers.dashboards_helper import (
    DashboardAlreadyExistsError,
    DashboardsHelper,
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

        logging.debug(f"Found {len(reports)} reports")

        dashboards_parser = M5oCollectionParser(
            packages_dir.joinpath("dashboards"), M5oCollectionParserTypes.Dashboard
        )
        dashboards = dashboards_parser.parse()

        logging.debug(f"Found {len(dashboards)} dashboards")

        report_id_map = self.add_reports(reports)
        self.add_dashboards(dashboards, report_id_map)

    def add_reports(self, reports):
        report_id_map = {}

        for report in reports:
            original_id = report["id"]

            report = self.add_report(report)

            report_id_map[original_id] = report["id"]
            logging.debug(
                f"Mapped original report ID '{original_id}' to new ID '{report['id']}'"
            )

        return report_id_map

    def add_report(self, report):
        try:
            report = ReportsHelper().save_report(report)

            logging.debug(
                f"Added report with name '{report['name']}', ID '{report['id']}'"
            )
        except ReportAlreadyExistsError as e:
            report = e.report

            logging.debug(
                f"Found existing report with name '{report['name']}', ID '{report['id']}'"
            )

        return report

    def add_dashboards(self, dashboards, report_id_map):
        for dashboard in dashboards:
            original_report_ids = dashboard["report_ids"]

            dashboard = self.add_dashboard(dashboard)

            # Don't add new reports to dashboards that already have some and were presumably imported or created before
            if len(dashboard["report_ids"]) > 0:
                continue

            for original_report_id in original_report_ids:
                try:
                    report_id = report_id_map[original_report_id]
                except KeyError:
                    logging.debug(
                        f"No new report ID found for original ID '{original_report_id}"
                    )
                    continue

                DashboardsHelper().add_report_to_dashboard(
                    {"dashboard_id": dashboard["id"], "report_id": report_id}
                )

                logging.debug(
                    f"Added report with ID '{report_id}' to dashboard with ID '{dashboard['id']}'"
                )

    def add_dashboard(self, dashboard):
        try:
            dashboard = DashboardsHelper().save_dashboard(dashboard)

            logging.debug(
                f"Added dashboard with name '{dashboard['name']}', ID '{dashboard['id']}'"
            )
        except DashboardAlreadyExistsError as e:
            dashboard = e.dashboard

            logging.debug(
                f"Found existing dashboard with name '{dashboard['name']}', ID '{dashboard['id']}'"
            )

        return dashboard
