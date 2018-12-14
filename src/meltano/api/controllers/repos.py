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


@reposBP.route("/lint", methods=["GET"])
def lint():
    p = subprocess.run(parser_command, stdout=subprocess.PIPE)
    j = json.loads(p.stdout.decode("utf-8"))
    print(p.stdout.decode("utf-8"), flush=True)
    if "errors" in j:
        return jsonify({"result": False, "errors": j["errors"]})
    else:
        return jsonify({"result": True})


@reposBP.route("/update", methods=["GET"])
def db_import():
    p = subprocess.run(parser_command, stdout=subprocess.PIPE)
    j = json.loads(p.stdout.decode("utf-8"))

    models = j["models"]
    files = j["files"]
    # process views
    for file in files:
        if file["_file_type"] == "view":
            file_view = file["views"][0]
            new_view_settings = {}
            if "label" in file_view:
                new_view_settings["label"] = file_view["label"].strip()
            if "sql_table_name" in file_view:
                new_view_settings["sql_table_name"] = file_view[
                    "sql_table_name"
                ].strip()
            new_view = View(file_view["_view"], new_view_settings)

            # Add dimensions for view
            if "dimensions" in file_view:
                for dimension in file_view["dimensions"]:
                    new_dimension_settings = {}
                    if "hidden" in dimension:
                        new_dimension_settings["hidden"] = dimension["hidden"]
                    if "primary_key" in dimension:
                        new_dimension_settings["primary_key"] = dimension["primary_key"]
                    if "label" in dimension:
                        new_dimension_settings["label"] = dimension["label"].strip()
                    if "type" in dimension:
                        new_dimension_settings["type"] = dimension["type"].strip()
                    if "sql" in dimension:
                        new_dimension_settings["sql"] = dimension["sql"].strip()
                    new_dimension_settings["_type"] = dimension["_type"]
                    new_dimension_settings["_n"] = dimension["_n"]
                    new_dimension = Dimension(
                        dimension["_dimension"], new_dimension_settings
                    )
                    new_view.dimensions.append(new_dimension)
                    db.session.add(new_dimension)
                    new_view.dimensions.append(new_dimension)

            if "dimension_groups" in file_view:
                for dimension_group in file_view["dimension_groups"]:
                    new_dimension_group_settings = {}
                    if "timeframes" in dimension_group:
                        new_dimension_group_settings["timeframes"] = dimension_group[
                            "timeframes"
                        ]
                    if "sql" in dimension_group:
                        new_dimension_group_settings["sql"] = dimension_group["sql"]
                    if "type" in dimension_group:
                        new_dimension_group_settings["type"] = dimension_group["type"]
                    if "label" in dimension_group:
                        new_dimension_group_settings["label"] = dimension_group["label"]
                    if "convert_tz" in dimension_group:
                        new_dimension_group_settings["convert_tz"] = dimension_group[
                            "convert_tz"
                        ]
                    if "description" in dimension_group:
                        new_dimension_group_settings["description"] = dimension_group[
                            "description"
                        ]

                    new_dimension_group_settings["_n"] = dimension_group["_n"]
                    new_dimension_group_settings["_type"] = dimension_group["_type"]
                    new_dimension_group = DimensionGroup(
                        dimension_group["_dimension_group"],
                        new_dimension_group_settings,
                    )
                    new_view.dimension_groups.append(new_dimension_group)
                    db.session.add(new_dimension_group)

            # Add measures for view
            if "measures" in file_view:
                for measure in file_view["measures"]:
                    new_measure_settings = {}
                    if "hidden" in measure:
                        new_measure_settings["hidden"] = measure["hidden"]
                    if "value_format" in measure:
                        new_measure_settings["value_format"] = measure[
                            "value_format"
                        ].strip()
                    if "label" in measure:
                        new_measure_settings["label"] = measure["label"].strip()
                    if "type" in measure:
                        new_measure_settings["type"] = measure["type"].strip()
                    if "sql" in measure:
                        new_measure_settings["sql"] = measure["sql"].strip()
                    new_measure_settings["_type"] = measure["_type"].strip()
                    new_measure_settings["_n"] = measure["_n"]
                    new_measure = Measure(measure["_measure"], new_measure_settings)
                    new_view.measures.append(new_measure)
                    db.session.add(new_measure)
                    new_view.measures.append(new_measure)
            db.session.add(new_view)
    # process models
    for model in models:
        model_settings = {}
        if "label" in model:
            model_settings["label"] = model["label"]
        model_settings["include"] = model["include"]
        model_settings["connection"] = model["connection"]
        model_settings["_type"] = model["_type"]

        new_model = Model(model["_model"], model_settings)

        # Set the explores for the model
        has_explores = len(model.get("explores") or model.get("explore"))
        explores = model.get("explores", [model.get("explore")])
        if has_explores:
            for explore in explores:
                explore_settings = {}
                if "label" in explore:
                    explore_settings["label"] = explore["label"]
                if "view_label" in explore:
                    explore_settings["view_label"] = explore["view_label"]
                if "description" in explore:
                    explore_settings["description"] = explore["description"]
                if "always_filter" in explore:
                    explore_settings["always_filter"] = explore["always_filter"]
                explore_settings["_type"] = explore["_type"]

                explore_name = explore.get("_explore", explore.get("label"))
                new_explore = Explore(explore_name, explore_settings)

                # Set the view for the explore
                # Name the explore from `from` or from name of explore itself
                view_name = explore.get("from", explore_name)
                connected_view = View.query.filter_by(name=view_name).first()
                new_explore.view = connected_view
                if "joins" in explore:
                    explore_joins = explore["joins"]
                    for join in explore_joins:
                        explore_join_settings = {}
                        if "view_label" in join:
                            explore_join_settings["view_label"] = join["view_label"]
                        if "label" in join:
                            explore_join_settings["label"] = join["label"]
                        if "type" in join:
                            explore_join_settings["type"] = join["type"]
                        if "relationship" in join:
                            explore_join_settings["relationship"] = join["relationship"]
                        if "fields" in join:
                            explore_join_settings["fields"] = join["fields"]
                        if "sql_on" in join:
                            explore_join_settings["sql_on"] = join["sql_on"]
                        if "type" in join:
                            explore_join_settings["type"] = join["type"]

                        new_explore_join = Join(join["_join"], explore_join_settings)
                        new_explore.joins.append(new_explore_join)
                        db.session.add(new_explore_join)

                new_model.explores.append(new_explore)
                db.session.add(new_explore)

        db.session.add(new_model)
    # project = Project(name=name, git_url=git_url)
    db.session.commit()
    return jsonify({"result": True})


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
