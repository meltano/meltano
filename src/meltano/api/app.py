import datetime
import logging
import logging.handlers
import os
import atexit
import importlib
from flask import Flask, request, g, jsonify
from flask_login import current_user
from flask_cors import CORS
from urllib.parse import urlsplit
from werkzeug.wsgi import DispatcherMiddleware

import meltano.api.config
from meltano.api.headers import *
from meltano.api.security.auth import HTTP_READONLY_CODE
from meltano.core.project import ProjectReadonly
from meltano.core.project_settings_service import ProjectSettingsService
from meltano.core.compiler.project_compiler import ProjectCompiler
from meltano.core.db import project_engine
from meltano.core.logging.utils import setup_logging, FORMAT
from meltano.core.project import Project
from meltano.core.tracking import GoogleAnalyticsTracker
from meltano.oauth.app import create_app as create_oauth_service


setup_logging()

# the file logger we will set up below is for the `meltano.api` module
logger = logging.getLogger("meltano.api")


def create_app(config={}):
    project = Project.find()
    setup_logging(project)

    settings_service = ProjectSettingsService(project)

    project_engine(project, settings_service.get("database_uri"), default=True)

    app = Flask(
        __name__, instance_path=str(project.root), instance_relative_config=True
    )

    # make sure we have the latest environment loaded
    importlib.reload(meltano.api.config)

    app.config.from_object("meltano.api.config")
    app.config.from_mapping(**meltano.api.config.ProjectSettings(project).as_dict())
    app.config.from_mapping(**config)

    if app.env == "production":
        app.config.from_object("meltano.api.config.Production")

    # File logging
    file_handler = logging.handlers.RotatingFileHandler(
        str(project.run_dir("meltano-ui.log")), backupCount=3
    )
    formatter = logging.Formatter(fmt=FORMAT)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

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
    from .controllers.embeds import embedsBP
    from .controllers.reports import reportsBP
    from .controllers.repos import reposBP
    from .controllers.settings import settingsBP
    from .controllers.sql import sqlBP
    from .controllers.orchestrations import orchestrationsBP
    from .controllers.plugins import pluginsBP
    from .controllers.root import root, api_root

    app.register_blueprint(dashboardsBP)
    app.register_blueprint(embedsBP)
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

    # Notifications
    if settings_service.get("ui.notification"):
        from .events import notifications

        notifications.init_app(app)
        logger.debug("Notifications are enabled.")
    else:
        logger.debug("Notifications are disabled.")

    # Google Analytics setup
    tracker = GoogleAnalyticsTracker(project)

    @app.before_request
    def setup_js_context():
        # setup the appUrl
        appUrl = urlsplit(request.host_url)
        g.jsContext = {"appUrl": appUrl.geturl()[:-1], "version": meltano.__version__}

        setting_map = {
            "isSendAnonymousUsageStats": "send_anonymous_usage_stats",
            "projectId": "project_id",
            "trackingID": "tracking_ids.ui",
            "embedTrackingID": "tracking_ids.ui_embed",
            "isProjectReadonlyEnabled": "project_readonly",
            "isReadonlyEnabled": "ui.readonly",
            "isAnonymousReadonlyEnabled": "ui.anonymous_readonly",
            "isNotificationEnabled": "ui.notification",
            "isAnalysisEnabled": "ui.analysis",
            "logoUrl": "ui.logo_url",
            "oauthServiceUrl": "oauth_service.url",
        }

        for context_key, setting_name in setting_map.items():
            g.jsContext[context_key] = settings_service.get(setting_name)

        providers = settings_service.get("oauth_service.providers")
        g.jsContext["oauthServiceProviders"] = [
            provider for provider in providers.split(",") if provider
        ]

    @app.after_request
    def after_request(res):
        res.headers[VERSION_HEADER] = meltano.__version__
        return res

    @app.errorhandler(500)
    def internal_error(exception):
        logger.info(f"Error: {exception}")
        return jsonify({"error": True, "code": str(exception)}), 500

    @app.errorhandler(ProjectReadonly)
    def _handle(ex):
        return (jsonify({"error": True, "code": str(ex)}), HTTP_READONLY_CODE)

    # create the dispatcher to host the `OAuthService`
    app.wsgi_app = DispatcherMiddleware(
        app.wsgi_app, {"/-/oauth": create_oauth_service()}
    )

    return app
