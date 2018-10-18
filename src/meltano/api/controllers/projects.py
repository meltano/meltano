from flask import Blueprint, jsonify, request

projectsBP = Blueprint("projectsBP", __name__, url_prefix="/projects")

from ..app import db
from ..models.projects import Project
from ..models.settings import Settings


@projectsBP.route("/", methods=["GET"])
def index():
    p = Project.query.first()
    return (
        jsonify({"name": p.name, "git_url": p.git_url})
        if p
        else jsonify({"name": "", "git_url": ""})
    )


@projectsBP.route("/new", methods=["POST"])
def add():
    incoming = request.get_json()
    name = incoming.get("name")
    git_url = incoming.get("git_url")
    settings = Settings()
    project = Project(name=name, git_url=git_url)
    project.settings = settings
    db.session.add(settings)
    db.session.add(project)
    db.session.commit()

    return jsonify({"name": name, "git_url": git_url})
