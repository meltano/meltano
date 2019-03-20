import os
from pathlib import Path
from flask import Blueprint, jsonify, request
from meltano.core.project import Project, ProjectNotFound
from meltano.core.project_init_service import (
    ProjectInitService,
    ProjectInitServiceError,
)

startBP = Blueprint("start", __name__, url_prefix="/api/v1/start")

@startBP.route("/has_project", methods=["GET"])
def has_project():
    try:
      Project.find()
      project = True
    except ProjectNotFound as e:
      project = False

    return jsonify({ 'has_project': project })

@startBP.route("/cwd", methods=["GET"])
def get_cwd():
    return jsonify({"cwd": os.getcwd()})


@startBP.route("/exists/<directory>", methods=["GET"])
def get_dir_exists(directory):
    path = os.path.join(os.getcwd(), directory)
    exists = os.path.exists(path)
    return jsonify({"exists": exists, "path": path})


@startBP.route("/create", methods=["POST"])
def post_create_project():
    post_data = request.get_json()
    project_name = post_data.get("project", False)
    init_service = ProjectInitService(project_name)
    try:
        project = init_service.init()
    except Exception as e:
        return jsonify({"result": False, "message": e.message})
    os.chdir(project.root_dir())
    return jsonify({"result": True})
