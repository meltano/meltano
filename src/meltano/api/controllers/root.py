import subprocess
import requests
import logging
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
from flask_security import login_required, roles_required, logout_user
from jinja2 import TemplateNotFound

import meltano
from meltano.api.security import api_auth_required
from meltano.api.security.readonly_killswitch import readonly_killswitch
from meltano.api.api_blueprint import APIBlueprint
from meltano.core.utils import truthy

logger = logging.getLogger(__name__)
root = Blueprint("root", __name__)


@root.errorhandler(500)
def internal_error(exception):
    logger.info(f"[{request.remote_addr}], error: {exception}")
    return jsonify({"error": str(exception)}), 500


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
@login_required
def default(path):
    try:
        return render_template("webapp.html", jsContext=g.jsContext)
    except TemplateNotFound:
        return "Please run `make bundle` from src/webapp of the Meltano project."


@root.route("/upgrade", methods=["POST"])
@roles_required("admin")
@readonly_killswitch
def upgrade():
    meltano.api.executor.upgrade()
    return "Meltano update in progress.", 201


@root.route("/version")
def version():
    response_payload = {"version": meltano.__version__}

    if truthy(request.args.get("include_latest")):
        res = requests.get("https://pypi.org/pypi/meltano/json")
        pypi_payload = res.json()
        response_payload["latest_version"] = pypi_payload["info"]["version"]

    return jsonify(response_payload)


@root.route("/bootstrap")
@login_required
def bootstrap():
    return redirect(current_app.config["MELTANO_UI_URL"])


@root.route("/echo", methods=["POST"])
def echo():
    payload = request.get_json()
    print(payload)
    return jsonify(payload)


api_root = APIBlueprint("api_root", __name__, url_prefix="/api/v1/")


@api_root.route("/identity")
def identity():
    if current_user.is_anonymous:
        return "", 204

    return jsonify({"username": current_user.username})
