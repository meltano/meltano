import json
import os
import sqlalchemy
from os.path import join
from pathlib import Path
from flask import url_for

from meltano.api.models.embed_token import EmbedToken
from meltano.core.db import project_engine
from meltano.core.m5o.m5oc_file import M5ocFile
from meltano.core.m5o.m5o_file_parser import MeltanoAnalysisFileParser
from meltano.core.m5o.m5o_collection_parser import (
    M5oCollectionParser,
    M5oCollectionParserTypes,
)
from meltano.core.project import Project
from meltano.core.schedule_service import ScheduleService
from meltano.core.utils import slugify
from meltano.core.m5o.m5o_collection_parser import (
    M5oCollectionParser,
    M5oCollectionParserTypes,
)
from .sql_helper import SqlHelper


class ReportAlreadyExistsError(Exception):
    """Occurs when a report already exists."""

    def __init__(self, report):
        self.report = report


class ReportsHelper:
    VERSION = "1.0.0"

    def get_embed_snippet(self, session, name):
        try:
            embed_token = session.query(EmbedToken).filter_by(resource_id=name).one()
            is_cached = True
        except sqlalchemy.orm.exc.NoResultFound:
            embed_token = EmbedToken(resource_id=name)
            session.add(embed_token)
            is_cached = False
        finally:
            session.commit()

        embed_url = url_for("root.embed", token=embed_token.token, _external=True)
        return {
            "is_cached": is_cached,
            "url": embed_url,
            "snippet": f"<iframe src={embed_url} />",
        }

    def get_embed(self, session, token):
        return session.query(EmbedToken).filter_by(token=token).one()

    def get_report_by_name(self, name):
        reports = self.get_reports()
        report = next(filter(lambda r: r["name"] == name, reports), None)
        return report

    def get_report_with_query_results(self, name):
        project = Project.find()
        schedule_service = ScheduleService(project)
        sql_helper = SqlHelper()
        report = self.get_report_by_name(name)
        report_with_query_results = self.update_report_with_query_results(
            report, schedule_service, sql_helper
        )

        return report_with_query_results

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

    def update_report_with_query_results(self, report, schedule_service, sql_helper):
        m5oc = sql_helper.get_m5oc_topic(report["namespace"], report["model"])
        design = m5oc.design(report["design"])
        schedule = schedule_service.find_namespace_schedule(
            m5oc.content["plugin_namespace"]
        )

        sql_dict = sql_helper.get_sql(design, report["query_payload"])
        outgoing_sql = sql_dict["sql"]
        aggregates = sql_dict["aggregates"]

        report["query_results"] = sql_helper.get_query_results(
            schedule.loader, outgoing_sql
        )
        report["query_result_aggregates"] = aggregates

        return report
