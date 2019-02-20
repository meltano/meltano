import base64
import json
import os
from pathlib import Path
from os.path import join

import markdown
from flask import Blueprint, jsonify, request

from meltano.api.security import api_auth_required
from meltano.core.m5o.m5o_file_parser import (
    MeltanoAnalysisFileParser,
    MeltanoAnalysisFileParserError,
)

reposBP = Blueprint("repos", __name__, url_prefix="/repos")
meltano_model_path = join(os.getcwd(), "model")


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
        for f in os.listdir(meltano_model_path)
        if os.path.isfile(os.path.join(meltano_model_path, f))
    ]
    sortedM5oFiles = {
        "documents": [],
        "tables": [],
        "models": [],
        "dashboards": [],
        "reports": [],
    }
    onlydocs = Path(meltano_model_path).parent.glob("*.md")
    for d in onlydocs:
        file_dict = {"path": str(d), "abs": str(d), "visual": str(d.name)}
        file_dict["unique"] = base64.b32encode(bytes(file_dict["abs"], "utf-8")).decode(
            "utf-8"
        )
        sortedM5oFiles["documents"].append(file_dict)

    for f in onlyfiles:
        filename, ext = os.path.splitext(f)
        if ext != ".m5o":
            continue
        file_dict = {"path": f, "abs": f, "visual": f}
        file_dict["unique"] = base64.b32encode(bytes(file_dict["abs"], "utf-8")).decode(
            "utf-8"
        )
        filename = filename.lower()

        filename, ext = os.path.splitext(filename)
        file_dict["visual"] = filename
        if ext == ".table":
            sortedM5oFiles["tables"].append(file_dict)
        if ext == ".model":
            sortedM5oFiles["models"].append(file_dict)
        if ext == ".dashboard":
            sortedM5oFiles["dashboards"].append(file_dict)
        if ext == ".report":
            sortedM5oFiles["reports"].append(file_dict)

    return jsonify(sortedM5oFiles)


@reposBP.route("/file/<unique>", methods=["GET"])
def file(unique):
    file_path = base64.b32decode(unique).decode("utf-8")
    (filename, ext) = os.path.splitext(file_path)
    is_markdown = False
    path_to_file = os.path.abspath(os.path.join(meltano_model_path, file_path))
    with open(path_to_file, "r") as read_file:
        data = read_file.read()
        if ext == ".md":
            data = markdown.markdown(data)
            is_markdown = True
        return jsonify(
            {
                "file": data,
                "is_markdown": is_markdown,
                "unique": unique,
                "populated": True,
            }
        )


def lint_all(compile):
    m5o_parse = MeltanoAnalysisFileParser(meltano_model_path)
    models = m5o_parse.parse()
    if compile:
        m5o_parse.compile(models)
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


@reposBP.route("/test", methods=["GET"])
def db_test():
    design = Design.query.first()
    return jsonify({"design": {"name": design.name, "settings": design.settings}})


@reposBP.route("/models", methods=["GET"])
def models():
    models = Path(meltano_model_path).joinpath("models.index.m5oc")
    return jsonify(json.loads(open(models, "r").read()))


@reposBP.route("/designs", methods=["GET"])
def designs():
    designs = Design.query.all()
    designs_json = []
    for design in designs:
        designs_json.append(design.serializable())
    return jsonify(designs_json)


@reposBP.route("/tables/<table_name>", methods=["GET"])
def table_read(table_name):
    file_path = Path(meltano_model_path).joinpath(f"{table_name}.table.m5o")
    m5o_parse = MeltanoAnalysisFileParser(meltano_model_path)
    table = m5o_parse.parse_m5o_file(file_path)
    return jsonify(table)


@reposBP.route("/designs/<model_name>/<design_name>", methods=["GET"])
def design_read(model_name, design_name):
    model = Path(meltano_model_path).joinpath(f"{model_name}.model.m5oc")
    with model.open() as f:
        model = json.load(f)
    designs = model["designs"]
    design = next(e for e in designs if e["from"] == design_name)
    return jsonify(design)
