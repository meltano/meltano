import subprocess
import requests
import logging
from functools import wraps
from urllib.parse import urlsplit
from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    redirect,
    make_response,
    g,
    current_app,
)
from flask_login import current_user
from flask_security import roles_required, logout_user
from jinja2 import TemplateNotFound

import meltano
from meltano.core.project import Project, ProjectReadonly
from meltano.core.project_settings_service import ProjectSettingsService
from flask_security import roles_required
from meltano.api.api_blueprint import APIBlueprint
from meltano.api.security.auth import passes_authentication_checks, block_if_readonly
from meltano.core.utils import truthy

logger = logging.getLogger(__name__)
root = Blueprint("root", __name__)


def redirect_to_login_if_auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if passes_authentication_checks():
            return f(*args, **kwargs)

        return current_app.login_manager.unauthorized()

    return decorated


@root.route("/-/embed/", defaults={"token": ""})
@root.route("/-/embed/<token>")
def embed(token):
    try:
        return render_template("embed.html", jsContext=g.jsContext)
    except TemplateNotFound:
        return "Please run `make bundle` from src/webapp of the Meltano project."


# this route is a catch-all route to forward
# all oustanding request (not caught by any route)
# to the front-end.
@root.route("/", defaults={"path": ""})
@root.route("/<path:path>")
@redirect_to_login_if_auth_required
def default(path):
    try:
        return render_template("webapp.html", jsContext=g.jsContext)
    except TemplateNotFound:
        return "Please run `make bundle` from src/webapp of the Meltano project."


@root.route("/bootstrap")
@redirect_to_login_if_auth_required
def bootstrap():
    return redirect(current_app.config["MELTANO_UI_URL"])


@root.route("/echo", methods=["POST"])
def echo():
    payload = request.get_json()
    print(payload)
    return jsonify(payload)


api_root = APIBlueprint("api_root", __name__, url_prefix="/api/v1/")


@api_root.route("/version")
def version():
    response_payload = {"version": meltano.__version__}

    if truthy(request.args.get("include_latest")):
        res = requests.get("https://pypi.org/pypi/meltano/json")
        pypi_payload = res.json()
        response_payload["latest_version"] = pypi_payload["info"]["version"]

    return jsonify(response_payload)


@api_root.route("/upgrade", methods=["POST"])
@roles_required("admin")
@block_if_readonly
def upgrade():
    meltano.api.executor.upgrade()
    return "Meltano update in progress.", 201


@api_root.route("/identity")
def identity():
    project = Project.find()
    settings_service = ProjectSettingsService(project)

    if current_user.is_anonymous:
        return jsonify(
            {
                "username": "Anonymous",
                "anonymous": True,
                "can_sign_in": settings_service.get("ui.authentication"),
            }
        )

    return jsonify(
        {"username": current_user.username, "anonymous": False, "can_sign_in": False}
    )


@api_root.route("/health")
def health():
    return jsonify({"healthy": True})
