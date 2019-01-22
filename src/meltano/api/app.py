import datetime
import logging
import logging.handlers
import os
from flask import Flask, request, render_template
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_security import login_required
from jinja2.exceptions import TemplateNotFound

from .external_connector import ExternalConnector
from .workers import MeltanoBackgroundCompiler
from . import config

connector = ExternalConnector()
flask_env = os.getenv("FLASK_ENV", "development")
logger = logging.getLogger(__name__)


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

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
    from .models import db

    db.init_app(app)

    from .mail import mail

    mail.init_app(app)

    from .security import security, users

    security.init_app(app, users)

    from .auth import oauth, oauthBP

    oauth.init_app(app)
    app.register_blueprint(oauthBP)

    if flask_env == "development":
        from flask_cors import CORS

        CORS(app)

    @app.before_request
    def before_request():
        logger.info(f"[{request.remote_addr}] request: {now}")

    from .controllers.root import root
    from .controllers.repos import reposBP
    from .controllers.settings import settingsBP
    from .controllers.sql import sqlBP

    app.register_blueprint(root)
    app.register_blueprint(reposBP)
    app.register_blueprint(settingsBP)
    app.register_blueprint(sqlBP)

    return app


def start(project, **kwargs):
    worker = MeltanoBackgroundCompiler(project)
    worker.start()

    app = create_app()
    from .security import create_dev_user

    with app.app_context():
        if flask_env == "development":
            create_dev_user()

    app.run(**kwargs)
    worker.stop()
