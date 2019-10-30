import datetime
import logging
import logging.handlers
import os
import atexit
from flask import Flask, request, g
from flask_login import current_user
from flask_cors import CORS
from importlib import reload
from urllib.parse import urlsplit

import meltano
from meltano.core.project import Project
from meltano.core.tracking import GoogleAnalyticsTracker
from meltano.core.plugin.error import PluginMissingError
from meltano.core.plugin.settings_service import (
    PluginSettingsService,
    PluginSettingMissingError,
)
from meltano.core.config_service import ConfigService
from meltano.core.compiler.project_compiler import ProjectCompiler
from meltano.core.tracking import GoogleAnalyticsTracker
from meltano.core.db import project_engine


logger = logging.getLogger(__name__)


def create_app(config={}):
    project = Project.find()

    app = Flask(
        __name__, instance_path=str(project.root), instance_relative_config=True
    )

    app.config.from_object("meltano.api.config")
    app.config.from_pyfile("ui.cfg", silent=True)
    app.config.update(**config)

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
    CORS(app, origins="*")

    # 2) Register the URL Converters
    from .url_converters import PluginRefConverter

    app.url_map.converters["plugin_ref"] = PluginRefConverter

    # 3) Register the controllers
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

        # setup the airflowUrl
        try:
            airflow = ConfigService(project).find_plugin("airflow")
            settings = PluginSettingsService(project)
            airflow_port, _ = settings.get_value(
                db.session, airflow, "webserver.web_server_port"
            )
            g.jsContext["airflowUrl"] = appUrl._replace(
                netloc=f"{appUrl.hostname}:{airflow_port}"
            ).geturl()[:-1]
        except (PluginMissingError, PluginSettingMissingError):
            pass

        # setup the dbtDocsUrl
        g.jsContext["dbtDocsUrl"] = appUrl._replace(path="/-/dbt/").geturl()[:-1]

    @app.after_request
    def after_request(res):
        request_message = f"[{request.url}]"

        if request.method != "OPTIONS":
            request_message += f" as {current_user}"

        logger.info(request_message)

        res.headers["X-Meltano-Version"] = meltano.__version__
        return res

    return app
