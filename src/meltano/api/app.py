import datetime
import logging
import logging.handlers
import os
from flask import Flask, request, render_template
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_security import login_required
from flask_login import current_user
from jinja2.exceptions import TemplateNotFound
from importlib import reload

from .external_connector import ExternalConnector
from .workers import MeltanoBackgroundCompiler
from . import config as default_config

from meltano.core.project import Project
from meltano.core.compiler.project_compiler import ProjectCompiler


connector = ExternalConnector()
logger = logging.getLogger(__name__)


def create_app(config={}):
    app = Flask(__name__)
    app.config.from_object(reload(default_config))
    app.config.update(**config)

    project = Project.find()

    # Initial compilation
    compiler = ProjectCompiler(project)
    compiler.compile()

    # Logging
    file_handler = logging.handlers.RotatingFileHandler(
        app.config["LOG_PATH"], maxBytes=2000, backupCount=10
    )
    stdout_handler = logging.StreamHandler()

    logger.addHandler(file_handler)
    logger.addHandler(stdout_handler)

    now = str(datetime.datetime.utcnow().strftime("%b %d %Y %I:%M:%S:%f"))
    logger.warning(f"Melt started at: {now}")

    # Extensions
    security_options = {}

    from .models import db
    from .mail import mail
    from .security import security, users, init_app as security_init_app
    from .auth import setup_oauth

    db.init_app(app)
    mail.init_app(app)
    security_init_app(app, project)
    setup_oauth(app)

    if app.env != "production":
        from flask_cors import CORS

        CORS(app, origins="http://localhost:8080")

    from .controllers.root import root
    from .controllers.dashboards import dashboardsBP
    from .controllers.reports import reportsBP
    from .controllers.repos import reposBP
    from .controllers.settings import settingsBP
    from .controllers.sql import sqlBP

    app.register_blueprint(root)
    app.register_blueprint(dashboardsBP)
    app.register_blueprint(reportsBP)
    app.register_blueprint(reposBP)
    app.register_blueprint(settingsBP)
    app.register_blueprint(sqlBP)

    @app.before_request
    def before_request():
        request_message = f"[{request.url}]"
        if current_user:
            request_message += f" as {current_user}"

        logger.info(request_message)

    return app


def start(project, **kwargs):
    """Start Meltano UI as a single-threaded web server."""

    worker = MeltanoBackgroundCompiler(project)
    worker.start()

    try:
        app_config = kwargs.pop("app_config", {})
        app = create_app(app_config)
        from .security import create_dev_user

        with app.app_context():
            # TODO: alembic migration
            create_dev_user()

        app.run(**kwargs)
    finally:
        worker.stop()
