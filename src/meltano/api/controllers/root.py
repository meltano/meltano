from urllib.parse import urlsplit
from flask import Blueprint, render_template, request, jsonify, redirect, g
from flask_security import login_required, roles_required
from jinja2 import TemplateNotFound

from meltano.api.security import api_auth_required


root = Blueprint("root", __name__)


@root.errorhandler(500)
def internal_error(exception):
    logger.info(f"[{request.remote_addr}] request: {now}, error: {exception}")
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


@root.route("/drop")
@roles_required("admin")
@api_auth_required
def drop_it():
    from .sql_helper import SqlHelper

    SqlHelper().reset_db()

    return "Database reset.", 200


@root.route("/echo", methods=["POST"])
def echo():
    payload = request.get_json()
    print(payload)
    return jsonify(payload)
