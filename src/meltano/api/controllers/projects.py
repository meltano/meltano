import os
from pathlib import Path
from flask import Blueprint, jsonify, request
from meltano.core.projects import Projects
from meltano.core.project import Project, ProjectNotFound
from meltano.core.project_init_service import (
    ProjectInitService,
    ProjectInitServiceError,
)

projectsBP = Blueprint("projects", __name__, url_prefix="/api/v1/projects")


@projectsBP.route("/", methods=["GET"])
def get_projects():
    projects = Projects(os.getcwd())
    return jsonify(projects.find())


@projectsBP.route("/has_project", methods=["GET"])
def has_project():
    try:
        Project.find()
        project = True
    except ProjectNotFound as e:
        project = False

    return jsonify({"has_project": project})


@projectsBP.route("/cwd", methods=["GET"])
def get_cwd():
    return jsonify({"cwd": os.getcwd()})


@projectsBP.route("/exists/<directory>", methods=["GET"])
def get_dir_exists(directory):
    path = os.path.join(os.getcwd(), directory)
    exists = os.path.exists(path)
    return jsonify({"exists": exists, "path": path})


@projectsBP.route("/create", methods=["POST"])
def post_create_project():
    post_data = request.get_json()
    project_name = post_data.get("project", False)
    init_service = ProjectInitService(project_name)
    try:
        project = init_service.init()
    except Exception as e:
        return jsonify({"result": False, "message": str(e)})
    return jsonify({"result": True, "project": project_name})
