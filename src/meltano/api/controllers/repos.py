import json
import os
from os.path import join
from pathlib import Path

import markdown
from flask import jsonify, request
from flask_principal import Need

from .repos_helper import ReposHelper
from meltano.api.api_blueprint import APIBlueprint
from meltano.api.security.resource_filter import ResourceFilter, NameFilterMixin
from meltano.api.security.auth import permit
from meltano.api.json import freeze_keys
from meltano.core.project import Project
from meltano.core.compiler.project_compiler import ProjectCompiler
from meltano.core.m5o.m5o_file_parser import (
    MeltanoAnalysisFileParser,
    MeltanoAnalysisMissingTopicFilesError,
    MeltanoAnalysisFileParserError,
)
from meltano.core.m5o.m5o_collection_parser import (
    M5oCollectionParser,
    M5oCollectionParserTypes,
)


reposBP = APIBlueprint("repos", __name__)


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


@reposBP.route("/", methods=["GET"])
def index():
    project = Project.find()
    onlyfiles = [f for f in project.model_dir().iterdir() if f.is_file()]

    path = project.model_dir()
    dashboardsParser = M5oCollectionParser(path, M5oCollectionParserTypes.Dashboard)
    reportsParser = M5oCollectionParser(path, M5oCollectionParserTypes.Report)

    reportsFiles = reportsParser.parse()
    dashboardFiles = dashboardsParser.parse()

    sortedM5oFiles = {
        "dashboards": {"label": "Dashboards", "items": dashboardFiles},
        "documents": {"label": "Documents", "items": []},
        "topics": {"label": "Topics", "items": []},
        "reports": {"label": "Reports", "items": reportsFiles},
        "tables": {"label": "Tables", "items": []},
    }
    onlydocs = project.model_dir().parent.glob("*.md")

    for d in onlydocs:
        file_dict = MeltanoAnalysisFileParser.fill_base_m5o_dict(
            d.relative_to(project.root), str(d.name)
        )
        sortedM5oFiles["documents"]["items"].append(file_dict)

    for f in onlyfiles:
        filename, ext = os.path.splitext(f)
        if ext != ".m5o":
            continue

        # filename splittext twice occurs due to current *.type.extension convention (two dots)
        filename = filename.lower()
        filename, ext = os.path.splitext(filename)
        file_dict = MeltanoAnalysisFileParser.fill_base_m5o_dict(
            f.relative_to(project.root), filename
        )
        if ext == ".topic":
            sortedM5oFiles["topics"]["items"].append(file_dict)
        if ext == ".table":
            sortedM5oFiles["tables"]["items"].append(file_dict)

    m5o_parser = MeltanoAnalysisFileParser(project)

    for package in m5o_parser.packages():
        package_files = MeltanoAnalysisFileParser.package_files(package)
        sortedM5oFiles["topics"]["items"] += package_files["topics"]["items"]
        sortedM5oFiles["tables"]["items"] += package_files["tables"]["items"]

    if not len(sortedM5oFiles["topics"]["items"]):
        return jsonify(
            {
                "result": False,
                "errors": [{"message": "Missing topic file(s)", "file_name": "*"}],
                "files": [],
            }
        )

    return jsonify(sortedM5oFiles)


def lint_all(compile):
    project = Project.find()
    compiler = ProjectCompiler(project)
    try:
        compiler.parse()
    except MeltanoAnalysisFileParserError as e:
        return jsonify(
            {
                "result": False,
                "errors": [{"message": e.message, "file_name": e.file_name}],
            }
        )
    if compile:
        compiler.compile()
    return jsonify({"result": True})


@reposBP.errorhandler(MeltanoAnalysisFileParserError)
def handle_meltano_analysis_file_parser_error(e):
    return (
        jsonify(
            {
                "result": False,
                "errors": [{"message": e.message, "file_name": e.file_name}],
            }
        ),
        500,
    )


@reposBP.errorhandler(FileNotFoundError)
def handle_file_not_found(e):
    return jsonify({"result": False, "error": str(e)}), 404


@reposBP.route("/lint", methods=["GET"])
def lint():
    return lint_all(False)


@reposBP.route("/sync", methods=["GET"])
def sync():
    return lint_all(True)


@reposBP.route("/designs/<path:namespace>/<topic_name>/<design_name>", methods=["GET"])
def model_design(namespace, topic_name, design_name):
    repos_helper = ReposHelper()
    topic = repos_helper.get_topic(namespace, topic_name)

    designs = topic["designs"]
    design = next(e for e in designs if e["name"] == design_name)

    return jsonify(design)


@reposBP.route("/models", methods=["GET"])
def model_index():
    project = Project.find()
    topicsFile = project.run_dir("models", "topics.index.m5oc")
    path = Path(topicsFile)

    topics = json.load(open(path, "r")) if path.is_file() else {}

    # for now let's freeze the keys, so the we can re-use the
    # key name as the design's name, but this should probably
    # return a list
    topics = freeze_keys(topics)
    return jsonify(topics)


@reposBP.route("/<path:namespace>/<topic_name>", methods=["GET"])
def model_topic(namespace, topic_name):
    repos_helper = ReposHelper()
    topic = repos_helper.get_topic(namespace, topic_name)

    return jsonify(topic)
