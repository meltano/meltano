import json
import os
from os.path import join
from pathlib import Path

import markdown
from flask import Blueprint, jsonify, request, g

from meltano.core.project import Project
from meltano.core.utils import decode_file_path_from_id
from meltano.api.security import api_auth_required
from meltano.core.m5o.m5o_file_parser import (
    MeltanoAnalysisFileParser,
    MeltanoAnalysisFileParserError,
)
from meltano.core.m5o.m5o_collection_parser import (
    M5oCollectionParser,
    M5oCollectionParserTypes,
)
from flask_principal import Need
from meltano.api.security.resource_filter import ResourceFilter, NameFilterMixin
from meltano.api.security.auth import permit


reposBP = Blueprint("repos", __name__, url_prefix="/api/v1/repos")


class ReportIndexFilter(NameFilterMixin, ResourceFilter):
    def __init__(self, *args):
        super().__init__(*args)

        self.needs(self.design_need)

    def design_need(self, permission_type, report):
        return Need("view:design", report["design"])


class M5ocFilter(ResourceFilter):
    def filter_designs(self, designs):
        return (
            ResourceFilter().needs(self.design_need).filter_all("view:design", designs)
        )

    def design_need(self, permission_type, design_name):
        return Need(permission_type, design_name)

    def scope(self, permission_type, m5oc):
        for topic, topic_def in m5oc.items():
            topic_def["designs"] = self.filter_designs(topic_def["designs"])

        return {
            topic: topic_def
            for topic, topic_def in m5oc.items()
            if topic_def["designs"]
        }


@reposBP.before_request
@api_auth_required
def before_request():
    pass


@reposBP.route("/", methods=["GET"])
def index():
    # For all you know, the first argument to Repo is a path to the repository
    # you want to work with
    onlyfiles = [
        f
        for f in os.listdir(Project.meltano_model_path())
        if os.path.isfile(os.path.join(Project.meltano_model_path(), f))
    ]

    path = Path(Project.meltano_model_path())
    dashboardsParser = M5oCollectionParser(path, M5oCollectionParserTypes.Dashboard)
    reportsParser = M5oCollectionParser(path, M5oCollectionParserTypes.Report)

    items = reportsParser.contents()
    reportsFiles = ReportIndexFilter().filter_all("view:reports", items)

    sortedM5oFiles = {
        "dashboards": {"label": "Dashboards", "items": dashboardsParser.contents()},
        "documents": {"label": "Documents", "items": []},
        "topics": {"label": "Topics", "items": []},
        "reports": {"label": "Reports", "items": reportsFiles},
        "tables": {"label": "Tables", "items": []},
    }

    onlydocs = Path(Project.meltano_model_path()).parent.glob("*.md")
    for d in onlydocs:
        file_dict = MeltanoAnalysisFileParser.fill_base_m5o_dict(d, str(d.name))
        sortedM5oFiles["documents"]["items"].append(file_dict)

    for f in onlyfiles:
        filename, ext = os.path.splitext(f)
        if ext != ".m5o":
            continue

        # filename splittext twice occurs due to current *.type.extension convention (two dots)
        filename = filename.lower()
        filename, ext = os.path.splitext(filename)
        file_dict = MeltanoAnalysisFileParser.fill_base_m5o_dict(f, filename)
        if ext == ".topic":
            sortedM5oFiles["topics"]["items"].append(file_dict)
        if ext == ".table":
            sortedM5oFiles["tables"]["items"].append(file_dict)

    return jsonify(sortedM5oFiles)


@reposBP.route("/file/<unique_id>", methods=["GET"])
def file(unique_id):
    file_path = decode_file_path_from_id(unique_id)
    (filename, ext) = os.path.splitext(file_path)
    is_markdown = False
    path_to_file = os.path.abspath(
        os.path.join(Project.meltano_model_path(), file_path)
    )
    with open(path_to_file, "r") as read_file:
        data = read_file.read()
        if ext == ".md":
            data = markdown.markdown(data)
            is_markdown = True
        return jsonify(
            {
                "file": data,
                "is_markdown": is_markdown,
                "id": unique_id,
                "populated": True,
            }
        )


def lint_all(compile):
    m5o_parse = MeltanoAnalysisFileParser(Project.meltano_model_path())
    topics = m5o_parse.parse()
    if compile:
        m5o_parse.compile(topics)
    return jsonify({"result": True, "hi": "hello"})


@reposBP.errorhandler(MeltanoAnalysisFileParserError)
def handle_meltano_analysis_file_parser_error(e):
    return jsonify(
        {"result": False, "errors": [{"message": e.message, "file_name": e.file_name}]}
    )


@reposBP.errorhandler(FileNotFoundError)
def handle_file_not_found(e):
    return jsonify({"result": False, "error": str(e)})


@reposBP.route("/lint", methods=["GET"])
def lint():
    return lint_all(False)


@reposBP.route("/sync", methods=["GET"])
def sync():
    return lint_all(True)


@reposBP.route("/models", methods=["GET"])
def models():
    topics = Path(Project.meltano_model_path()).joinpath("topic.index.m5oc")
    topics = json.load(open(topics, "r"))
    topics = next(M5ocFilter().filter("view:topic", [topics]))

    return jsonify(topics)


@reposBP.route("/tables/<table_name>", methods=["GET"])
def table_read(table_name):
    file_path = Path(Project.meltano_model_path()).joinpath(f"{table_name}.table.m5o")
    m5o_parse = MeltanoAnalysisFileParser(Project.meltano_model_path())
    table = m5o_parse.parse_m5o_file(file_path)
    return jsonify(table)


@reposBP.route("/designs/<topic_name>/<design_name>", methods=["GET"])
def design_read(topic_name, design_name):
    permit("view:design", design_name)

    topic = Path(Project.meltano_model_path()).joinpath(f"{topic_name}.topic.m5oc")
    with topic.open() as f:
        topic = json.load(f)
    designs = topic["designs"]
    design = next(e for e in designs if e["from"] == design_name)
    return jsonify(design)
