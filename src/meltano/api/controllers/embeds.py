import sqlalchemy
from flask import jsonify, request, url_for

from .dashboards_helper import DashboardsHelper
from .reports_helper import ReportsHelper
from meltano.api.api_blueprint import APIBlueprint
from meltano.api.models.embed_token import EmbedToken, ResourceType
from meltano.api.models import db
from meltano.core.m5o.dashboards_service import DashboardsService
from meltano.core.m5o.reports_service import ReportsService
from meltano.core.project import Project


embedsBP = APIBlueprint("embeds", __name__)


class InvalidEmbedToken(Exception):
    """Occurs when an embed token isn't found."""

    def __init__(self, token):
        self.token = token


@embedsBP.errorhandler(InvalidEmbedToken)
def _handle(ex):
    return (
        jsonify(
            {
                "error": True,
                "code": f"No matching resource found or this resource is no longer public.",
            }
        ),
        400,
    )


@embedsBP.route("/embed/<token>", methods=["GET"])
def get_embed(token):
    embed_token = get_embed_from_token(db.session, token)
    resource_type = embed_token.resource_type
    resource_id = embed_token.resource_id

    if resource_type == ResourceType.REPORT.value:
        resource_payload = get_report_resource(resource_id)
    elif resource_type == ResourceType.DASHBOARD.value:
        resource_payload = get_dashboard_resource(resource_id)

    return jsonify({"resource": resource_payload, "type": embed_token.resource_type})


@embedsBP.route("/embed", methods=["POST"])
def embed():
    post_data = request.get_json()
    response_data = generate_embed_snippet(
        db.session, post_data["id"], post_data["type"]
    )

    return jsonify(response_data)


def generate_embed_snippet(session, resource_id, resource_type):
    try:
        embed_token = session.query(EmbedToken).filter_by(resource_id=resource_id).one()
        is_new = False
    except sqlalchemy.orm.exc.NoResultFound:
        embed_token = EmbedToken(resource_id=resource_id, resource_type=resource_type)
        session.add(embed_token)
        is_new = True
    finally:
        session.commit()

    embed_url = url_for("root.embed", token=embed_token.token, _external=True)
    inline_styles = "margin: 0; padding: 0; border: 0; font-size: 100%; font: inherit; vertical-align: baseline; min-width: 500px; min-height: 400px;"
    return {
        "is_new": is_new,
        "url": embed_url,
        "resource_type": embed_token.resource_type,
        "snippet": f"<iframe src='{embed_url}' style='{inline_styles}' />",
    }


def get_embed_from_token(session, token):
    try:
        return session.query(EmbedToken).filter_by(token=token).one()
    except sqlalchemy.orm.exc.NoResultFound:
        raise InvalidEmbedToken(token)


def get_dashboard_resource(resource_id):
    project = Project.find()
    reports_service = ReportsService(project)
    dashboards_service = DashboardsService(project)

    dashboard = dashboards_service.get_dashboard(resource_id)
    reports = [
        reports_service.get_report(report_id) for report_id in dashboard["report_ids"]
    ]
    dashboards_helper = DashboardsHelper()
    reports_with_query_results = dashboards_helper.get_dashboard_reports_with_query_results(
        reports
    )
    return {
        "dashboard": dashboard,
        "reports_with_query_results": reports_with_query_results,
    }


def get_report_resource(resource_id):
    project = Project.find()
    reports_service = ReportsService(project)

    report = reports_service.get_report(resource_id)
    reports_helper = ReportsHelper()
    return reports_helper.get_report_with_query_results(report)
