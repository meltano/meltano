import datetime
import logging
import logging.handlers
import os
import atexit
from flask import Flask, request, g
from flask_login import current_user
from flask_cors import CORS
from urllib.parse import urlsplit

import meltano
from meltano.core.project import Project
from meltano.core.tracking import GoogleAnalyticsTracker
from meltano.core.compiler.project_compiler import ProjectCompiler
from meltano.core.tracking import GoogleAnalyticsTracker
from meltano.core.db import project_engine
from meltano.api.config import VERSION_HEADER


logger = logging.getLogger(__name__)


def create_app(config={}):
    project = Project.find()

    app = Flask(
        __name__, instance_path=str(project.root), instance_relative_config=True
    )

    app.config.from_object("meltano.api.config")
    app.config.from_pyfile("ui.cfg", silent=True)
    app.config.update(**config)

    if app.env == "production":
        from meltano.api.config import ensure_secure_setup

        app.config.from_object("meltano.api.config.Production")
        ensure_secure_setup(app)

    # register
    project_engine(
        project, engine_uri=app.config["SQLALCHEMY_DATABASE_URI"], default=True
    )

    # Initial compilation
    compiler = ProjectCompiler(project)
    try:
        compiler.compile()
    except Exception as e:
        pass

    # Logging
    file_handler = logging.handlers.RotatingFileHandler(
        str(project.run_dir("meltano-ui.log")), backupCount=3
    )
    stdout_handler = logging.StreamHandler()

    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(stdout_handler)

    # 1) Extensions
    security_options = {}

    from .models import db
    from .mail import mail
    from .executor import setup_executor
    from .security import security, users, setup_security
    from .security.oauth import setup_oauth
    from .json import setup_json

    db.init_app(app)
    mail.init_app(app)
    setup_executor(app, project)
    setup_security(app, project)
    setup_oauth(app)
    setup_json(app)

    # we need to setup CORS for development
    if app.env == "development":
        CORS(app, origins="http://localhost:8080", supports_credentials=True)

    # 2) Register the URL Converters
    from .url_converters import PluginRefConverter

    app.url_map.converters["plugin_ref"] = PluginRefConverter

    # 3) Register the controllers

    from .controllers.dashboards import dashboardsBP
    from .controllers.reports import reportsBP
    from .controllers.repos import reposBP
    from .controllers.settings import settingsBP
    from .controllers.sql import sqlBP
    from .controllers.orchestrations import orchestrationsBP
    from .controllers.plugins import pluginsBP
    from .controllers.root import root, api_root

    app.register_blueprint(dashboardsBP)
    app.register_blueprint(reportsBP)
    app.register_blueprint(reposBP)
    app.register_blueprint(settingsBP)
    app.register_blueprint(sqlBP)
    app.register_blueprint(orchestrationsBP)
    app.register_blueprint(pluginsBP)
    app.register_blueprint(root)
    app.register_blueprint(api_root)

    if app.config["PROFILE"]:
        from .profiler import init

        init(app)

    # Google Analytics setup
    tracker = GoogleAnalyticsTracker(project)

    @app.before_request
    def setup_js_context():
        # setup the appUrl
        appUrl = urlsplit(request.host_url)
        g.jsContext = {"appUrl": appUrl.geturl()[:-1]}

        if tracker.send_anonymous_usage_stats:
            g.jsContext["isSendAnonymousUsageStats"] = True
            g.jsContext["projectId"] = tracker.project_id

        g.jsContext["version"] = meltano.__version__

        # setup the dbtDocsUrl
        g.jsContext["dbtDocsUrl"] = appUrl._replace(path="/-/dbt/").geturl()[:-1]

    @app.after_request
    def after_request(res):
        res.headers[VERSION_HEADER] = meltano.__version__
        return res

    return app
