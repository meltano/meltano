import base64
import json
import os
import subprocess
import sys
from pathlib import Path
from os.path import join
from ..app import db

import markdown
import pkg_resources
from flask import Blueprint, jsonify
from ..models.data import Model, Explore, View, Dimension, DimensionGroup, Measure, Join

reposBP = Blueprint("repos", __name__, url_prefix="/repos")
meltano_model_path = join(os.getcwd(), "model")

path_to_parser = join(
    pkg_resources.resource_filename("meltano.api", "node_modules"),
    "lookml-parser/cli.js",
)
parser_command = [
    path_to_parser,
    "--input={}/*.{{view,model}}.lkml".format(meltano_model_path),
]


@reposBP.route("/", methods=["GET"])
def index():
    # For all you know, the first argument to Repo is a path to the repository
    # you want to work with
    onlyfiles = [
        f
        for f in os.listdir(meltano_model_path)
        if os.path.isfile(os.path.join(meltano_model_path, f))
    ]
    sortedLkml = {"documents": [], "views": [], "models": [], "dashboards": []}
    onlydocs = Path(meltano_model_path).parent.glob("*.md")
    for d in onlydocs:
        file_dict = {"path": str(d), "abs": str(d), "visual": str(d.name)}
        file_dict["unique"] = base64.b32encode(bytes(file_dict["abs"], "utf-8")).decode(
            "utf-8"
        )
        sortedLkml["documents"].append(file_dict)

    for f in onlyfiles:
        filename, ext = os.path.splitext(f)
        if ext != ".lkml":
            continue
        file_dict = {"path": f, "abs": f, "visual": f}
        file_dict["unique"] = base64.b32encode(bytes(file_dict["abs"], "utf-8")).decode(
            "utf-8"
        )
        filename = filename.lower()

        filename, ext = os.path.splitext(filename)
        file_dict["visual"] = filename
        if ext == ".view":
            sortedLkml["views"].append(file_dict)
        if ext == ".model":
            sortedLkml["models"].append(file_dict)
        if ext == ".dashboard":
            sortedLkml["dashboards"].append(file_dict)

    return jsonify(sortedLkml)


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
    from .ma_file_parser import (
        MeltanoAnalysisFileParser,
        MeltanoAnalysisFileParserError,
    )

    ma_parse = MeltanoAnalysisFileParser(meltano_model_path)
    try:
        models = ma_parse.parse()
        if compile:
            ma_parse.compile(models)
        return jsonify({"result": True})
    except MeltanoAnalysisFileParserError as e:
        return jsonify(
            {
                "result": False,
                "errors": [{"message": e.message, "file_name": e.file_name}],
            }
        )


@reposBP.route("/lint", methods=["GET"])
def lint():
    return lint_all(False)


@reposBP.route("/sync", methods=["GET"])
def sync():
    return lint_all(True)


@reposBP.route("/test", methods=["GET"])
def db_test():
    explore = Explore.query.first()
    return jsonify({"explore": {"name": explore.name, "settings": explore.settings}})


@reposBP.route("/models", methods=["GET"])
def models():
    models = Model.query.all()
    models_json = []
    for model in models:
        this_model = {}
        this_model["settings"] = model.settings
        this_model["name"] = model.name
        this_model["explores"] = []
        for explore in model.explores:
            this_explore = {}
            this_explore["settings"] = explore.settings
            this_explore["name"] = explore.name
            this_explore["link"] = f"/explore/{model.name}/{explore.name}"
            this_view = {}
            this_view["name"] = explore.view.name
            this_view["settings"] = explore.view.settings
            this_explore["views"] = this_view
            this_explore["joins"] = []
            for join in explore.joins:
                this_join = {}
                this_join["name"] = join.name
                this_join["settings"] = join.settings
                this_explore["joins"].append(this_join)

            this_model["explores"].append(this_explore)
        models_json.append(this_model)
    return jsonify(models_json)


@reposBP.route("/explores", methods=["GET"])
def explores():
    explores = Explore.query.all()
    explores_json = []
    for explore in explores:
        explores_json.append(explore.serializable())
    return jsonify(explores_json)


@reposBP.route("/views/<view_name>", methods=["GET"])
def view_read(view_name):
    view = View.query.filter(View.name == view_name).first()
    return jsonify(view.serializable(True))


@reposBP.route("/explores/<model_name>/<explore_name>", methods=["GET"])
def explore_read(model_name, explore_name):
    explore = (
        Explore.query.join(Model, Explore.model_id == Model.id)
        .filter(Model.name == model_name)
        .filter(Explore.name == explore_name)
        .first()
    )
    explore_json = explore.serializable(True)
    explore_json["settings"]["has_filters"] = False
    if "always_filter" in explore_json["settings"]:
        explore_json["settings"]["has_filters"] = True
        for a_filter in explore_json["settings"]["always_filter"]["filters"]:
            dimensions = explore_json["view"]["dimensions"]
            for dimension in dimensions:
                if dimension["name"] == a_filter["field"]:
                    a_filter["explore_label"] = a_filter["_explore"].title()
                    a_filter["type"] = dimension["settings"]["type"]
                    if "label" in dimension["settings"]:
                        a_filter["label"] = dimension["settings"]["label"]
                    else:
                        a_filter["label"] = " ".join(
                            dimension["name"].split("_")
                        ).title()
                    a_filter["sql"] = dimension["settings"]["sql"]
                    break
    return jsonify(explore_json)
