from flask import Blueprint, render_template, jsonify, redirect
from flask_security import login_required, roles_required
from jinja2 import TemplateNotFound

from meltano.api.security import api_auth_required


root = Blueprint("root", __name__)


@root.errorhandler(500)
def internal_error(exception):
    logger.info(f"[{request.remote_addr}] request: {now}, error: {exception}")
    return jsonify({"error": str(exception)}), 500


@root.route("/model")
@root.route("/")
@login_required
def analyze():
    try:
        return render_template("analyze.html")
    except TemplateNotFound:
        return "Please run `yarn build` from src/analyze."


@root.route("/drop")
@roles_required("admin")
@api_auth_required
def drop_it():
    from .sql_helper import SqlHelper

    SqlHelper().reset_db()

    return "Database reset.", 200
