import json
import os
from os.path import join
from pathlib import Path

import markdown
from flask import Blueprint, jsonify, request

from meltano.core.project import Project
from meltano.core.utils import decode_file_path_from_id
from meltano.core.compiler.project_compiler import ProjectCompiler
from meltano.api.security import api_auth_required
from meltano.core.m5o.m5o_file_parser import (
    MeltanoAnalysisFileParser,
    MeltanoAnalysisMissingTopicFilesError,
    MeltanoAnalysisFileParserError,
)
from meltano.core.m5o.m5o_collection_parser import (
    M5oCollectionParser,
    M5oCollectionParserTypes,
)

reposBP = Blueprint("repos", __name__, url_prefix="/api/v1/repos")


@reposBP.before_request
@api_auth_required
def before_request():
    pass


@reposBP.route("/", methods=["GET"])
def index():
    project = Project.find()
    onlyfiles = [f for f in project.model_dir().iterdir() if f.is_file()]

    path = project.model_dir()
    dashboardsParser = M5oCollectionParser(path, M5oCollectionParserTypes.Dashboard)
    reportsParser = M5oCollectionParser(path, M5oCollectionParserTypes.Report)
    sortedM5oFiles = {
        "dashboards": {"label": "Dashboards", "items": dashboardsParser.contents()},
        "documents": {"label": "Documents", "items": []},
        "topics": {"label": "Topics", "items": []},
        "reports": {"label": "Reports", "items": reportsParser.contents()},
        "tables": {"label": "Tables", "items": []},
    }
    onlydocs = project.model_dir().parent.glob("*.md")
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


@reposBP.route("/file/<unique_id>", methods=["GET"])
def file(unique_id):
    file_path = decode_file_path_from_id(unique_id)
    (filename, ext) = os.path.splitext(file_path)
    is_markdown = False
    project = Project.find()
    path_to_file = project.model_dir(file_path).resolve()
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


@reposBP.route("/test", methods=["GET"])
def db_test():
    design = Design.query.first()
    return jsonify({"design": {"name": design.name, "settings": design.settings}})


@reposBP.route("/models", methods=["GET"])
def models():
    project = Project.find()
    topics = project.root_dir("model", "topics.index.m5oc")
    return jsonify(json.loads(open(topics, "r").read()))


@reposBP.route("/designs", methods=["GET"])
def designs():
    designs = Design.query.all()
    designs_json = []
    for design in designs:
        designs_json.append(design.serializable())
    return jsonify(designs_json)


@reposBP.route("/tables/<table_name>", methods=["GET"])
def table_read(table_name):
    project = Project.find()
    file_path = project.model_dir(f"{table_name}.table.m5o")
    m5o_parse = MeltanoAnalysisFileParser(project)
    table = m5o_parse.parse_m5o_file(file_path)
    return jsonify(table)


@reposBP.route("/designs/<topic_name>/<design_name>", methods=["GET"])
def design_read(topic_name, design_name):
    project = Project.find()
    topic = project.root_dir("model", f"{topic_name}.topic.m5oc")
    with topic.open() as f:
        topic = json.load(f)
    designs = topic["designs"]
    design = next(e for e in designs if e["from"] == design_name)
    return jsonify(design)
