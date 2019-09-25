import subprocess
import requests
import logging
from urllib.parse import urlsplit
from flask import Blueprint, render_template, request, jsonify, redirect, g, current_app
from flask_security import login_required, roles_required
from jinja2 import TemplateNotFound

import meltano
from meltano.api.security import api_auth_required

logger = logging.getLogger(__name__)
root = Blueprint("root", __name__)


@root.errorhandler(500)
def internal_error(exception):
    logger.info(f"[{request.remote_addr}], error: {exception}")
    return jsonify({"error": str(exception)}), 500


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
def upgrade():
    meltano.api.executor.upgrade()
    return "Meltano update in progress.", 201


@root.route("/version")
def version():
    res = requests.get("https://pypi.org/pypi/meltano/json")
    payload = res.json()

    return jsonify(
        {"version": meltano.__version__, "latest_version": payload["info"]["version"]}
    )


@root.route("/echo", methods=["POST"])
def echo():
    payload = request.get_json()
    print(payload)
    return jsonify(payload)
