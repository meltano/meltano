import sqlalchemy
from flask import url_for

from .dashboards_helper import DashboardsHelper
from .reports_helper import ReportsHelper
from meltano.api.models.embed_token import EmbedToken, ResourceType
from meltano.core.m5o.dashboards_service import DashboardsService
from meltano.core.m5o.reports_service import ReportsService
from meltano.core.project import Project


class InvalidEmbedToken(Exception):
    """Occurs when an embed token isn't found."""

    def __init__(self, token):
        self.token = token


class EmbedsHelper:
    def generate_embed_snippet(self, session, resource_id, resource_type, today=None):
        try:
            embed_token = (
                session.query(EmbedToken).filter_by(resource_id=resource_id).one()
            )
            is_new = False
        except sqlalchemy.orm.exc.NoResultFound:
            embed_token = EmbedToken(
                resource_id=resource_id, resource_type=resource_type
            )
            session.add(embed_token)
            is_new = True
        finally:
            session.commit()

        resource_type = ResourceType(embed_token.resource_type)
        if resource_type is ResourceType.REPORT:
            min_width = "500px"
            min_height = "400px"
        elif resource_type is ResourceType.DASHBOARD:
            min_width = "100%"
            min_height = "100vh"
        inline_styles = f"margin: 0; padding: 0; border: 0; font-size: 100%; font: inherit; vertical-align: baseline; min-width: {min_width}; min-height: {min_height};"
        embed_url = url_for(
            "root.embed", token=embed_token.token, today=today, _external=True
        )
        snippet = f'<iframe src="{embed_url}" style="{inline_styles}" />'

        return {
            "is_new": is_new,
            "url": embed_url,
            "resource_type": embed_token.resource_type,
            "snippet": snippet,
        }

    def get_embed_from_token(self, session, token, today=None):
        try:
            embed_token = session.query(EmbedToken).filter_by(token=token).one()
        except sqlalchemy.orm.exc.NoResultFound:
            raise InvalidEmbedToken(token)

        resource_type = ResourceType(embed_token.resource_type)
        resource_id = embed_token.resource_id

        if resource_type is ResourceType.REPORT:
            resource_payload = self.get_report_resource(resource_id, today=today)
        elif resource_type is ResourceType.DASHBOARD:
            resource_payload = self.get_dashboard_resource(resource_id, today=today)

        return {
            "resource": resource_payload,
            "resource_type": embed_token.resource_type,
        }

    def get_dashboard_resource(self, resource_id, today=None):
        project = Project.find()
        reports_service = ReportsService(project)
        dashboards_service = DashboardsService(project)

        dashboard = dashboards_service.get_dashboard(resource_id)
        reports = [
            reports_service.get_report(report_id)
            for report_id in dashboard["report_ids"]
        ]
        dashboards_helper = DashboardsHelper()
        reports_with_query_results = dashboards_helper.get_dashboard_reports_with_query_results(
            reports, today=today
        )
        return {
            "dashboard": dashboard,
            "reports_with_query_results": reports_with_query_results,
        }

    def get_report_resource(self, resource_id, today=None):
        project = Project.find()
        reports_service = ReportsService(project)

        report = reports_service.get_report(resource_id)
        reports_helper = ReportsHelper()
        return reports_helper.get_report_with_query_results(report, today=today)
