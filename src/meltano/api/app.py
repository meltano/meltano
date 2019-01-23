import datetime
import logging
import os
from logging.handlers import RotatingFileHandler
from flask import Flask, request, render_template
from flask import jsonify
from flask_cors import CORS
from jinja2.exceptions import TemplateNotFound

from . import config
from .external_connector import ExternalConnector

app = Flask(__name__)

app.config.from_object(config)

flask_env = os.getenv("FLASK_ENV", "development")

if flask_env == "development":
    CORS(app)

connector = ExternalConnector()

logger = logging.getLogger("melt_logger")
handler = RotatingFileHandler(app.config["LOG_PATH"], maxBytes=2000, backupCount=10)
logger.addHandler(handler)
now = str(datetime.datetime.utcnow().strftime("%b %d %Y %I:%M:%S:%f"))
logger.warning(f"Melt started at: {now}")


@app.before_request
def before_request():
    logger.info(f"[{request.remote_addr}] request: {now}")


@app.errorhandler(500)
def internal_error(exception):
    logger.info(f"[{request.remote_addr}] request: {now}, error: {exception}")
    return jsonify({"error": 1}), 500


@app.route("/model")
@app.route("/")
def analyze():
    try:
        return render_template("analyze.html")
    except TemplateNotFound:
        return "Please run `yarn build` from src/analyze."


@app.route("/drop")
def drop_it():
    from .controllers.sqlhelper import SqlHelper

    SqlHelper().reset_db()
    return jsonify({"dropped_it": "like it's hot"})


from .controllers.reports import reportsBP
from .controllers.repos import reposBP
from .controllers.settings import settingsBP
from .controllers.sql import sqlBP
# from .controllers.orchestrations import orchestrationsBP

app.register_blueprint(reportsBP)
app.register_blueprint(reposBP)
app.register_blueprint(settingsBP)
app.register_blueprint(sqlBP)
# app.register_blueprint(orchestrationsBP)
