import datetime
import logging
import logging.handlers
import os
from flask import Flask, request, render_template, g
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_security import login_required
from flask_login import current_user
from flask_cors import CORS
from jinja2.exceptions import TemplateNotFound
from importlib import reload
from urllib.parse import urlsplit

from meltano.core.project import Project
from meltano.core.plugin.error import PluginMissingError
from meltano.core.plugin.settings_service import (
    PluginSettingsService,
    PluginSettingMissingError,
)
from meltano.core.config_service import ConfigService
from meltano.core.compiler.project_compiler import ProjectCompiler
from .external_connector import ExternalConnector
from .workers import MeltanoBackgroundCompiler, UIAvailableWorker, AirflowWorker
from . import config as default_config


connector = ExternalConnector()
logger = logging.getLogger(__name__)


def create_app(config={}):
    project = Project.find()

    app = Flask(__name__)
    app.config.from_object(reload(default_config))
    app.config.update(**config)

    if not app.config["SQLALCHEMY_DATABASE_URI"]:
        app.config[
            "SQLALCHEMY_DATABASE_URI"
        ] = f"sqlite:///{project.root.joinpath('meltano.db')}"

    # Initial compilation
    compiler = ProjectCompiler(project)
    try:
        compiler.compile()
    except Exception as e:
        pass

    # Logging
    file_handler = logging.handlers.RotatingFileHandler(
        app.config["LOG_PATH"], maxBytes=2000, backupCount=10
    )
    stdout_handler = logging.StreamHandler()

    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(stdout_handler)

    now = str(datetime.datetime.utcnow().strftime("%b %d %Y %I:%M:%S:%f"))
    logger.warning(f"Meltano UI started at: {now}")

    # Extensions
    security_options = {}

    from .models import db
    from .mail import mail
    from .security import security, users, setup_security
    from .security.oauth import setup_oauth

    db.init_app(app)
    mail.init_app(app)
    setup_security(app, project)
    setup_oauth(app)
    CORS(app, origins="*")

    from .controllers.root import root
    from .controllers.dashboards import dashboardsBP
    from .controllers.reports import reportsBP
    from .controllers.repos import reposBP
    from .controllers.settings import settingsBP
    from .controllers.sql import sqlBP
    from .controllers.orchestrations import orchestrationsBP
    from .controllers.plugins import pluginsBP

    app.register_blueprint(root)
    app.register_blueprint(dashboardsBP)
    app.register_blueprint(reportsBP)
    app.register_blueprint(reposBP)
    app.register_blueprint(settingsBP)
    app.register_blueprint(sqlBP)
    app.register_blueprint(orchestrationsBP)
    app.register_blueprint(pluginsBP)

    if app.config["PROFILE"]:
        from .profiler import init

        init(app)

    @app.before_request
    def setup_js_context():
        appUrl = urlsplit(request.host_url)
        g.jsContext = {"appUrl": appUrl.geturl()[:-1]}

        try:
            airflow = ConfigService(project).find_plugin("airflow")
            settings = PluginSettingsService(db.session, project)
            airflow_port, _ = settings.get_value(airflow, "webserver.web_server_port")
            g.jsContext["airflowUrl"] = appUrl._replace(
                netloc=f"{appUrl.hostname}:{airflow_port}"
            ).geturl()[:-1]
        except (PluginMissingError, PluginSettingMissingError):
            pass

    @app.after_request
    def after_request(res):
        request_message = f"[{request.url}]"

        if request.method != "OPTIONS":
            request_message += f" as {current_user}"

        logging.info(request_message)
        return res

    return app


def start(project, **kwargs):
    """Start Meltano UI as a single-threaded web server."""

    cleanup = None
    try:
        app_config = kwargs.pop("app_config", {})
        app = create_app(app_config)
        from .security.identity import create_dev_user

        with app.app_context():
            # TODO: alembic migration
            create_dev_user()

        # ensure we only start the workers on the via the main thread
        # this will make sure we don't start everything twice
        # when code reload is enabled
        if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
            cleanup = start_workers(app, project)

        app.run(**kwargs)
    finally:
        if cleanup:
            cleanup()


def start_workers(app, project):
    workers = []
    try:
        if not app.config["AIRFLOW_DISABLED"]:
            workers.append(AirflowWorker(project))
    except:
        logging.info("Airflow is not installed.")

    workers.append(MeltanoBackgroundCompiler(project))
    workers.append(
        UIAvailableWorker("http://localhost:5000", open_browser=not app.debug)
    )

    def stop_all():
        for worker in workers:
            worker.stop()

    # start all workers
    for worker in workers:
        worker.start()

    return stop_all
