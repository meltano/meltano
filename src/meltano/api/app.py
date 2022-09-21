"""Flask app for Meltano UI."""
from __future__ import annotations

import importlib
import logging
from urllib.parse import urlsplit

from flask import Flask, g, jsonify, request  # noqa: WPS347
from flask_cors import CORS
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from meltano import __version__ as meltano_version
from meltano.api import config as api_config
from meltano.api.headers import VERSION_HEADER
from meltano.api.security.auth import HTTP_READONLY_CODE
from meltano.core.db import project_engine
from meltano.core.logging.utils import FORMAT, setup_logging
from meltano.core.project import Project, ProjectReadonly
from meltano.core.project_settings_service import ProjectSettingsService
from meltano.oauth.app import create_app as create_oauth_service

STATUS_SERVER_ERROR = 500

setup_logging()

# the file logger we will set up below is for the `meltano.api` module
logger = logging.getLogger("meltano.api")


def create_app(config: dict = {}) -> Flask:  # noqa: WPS210,WPS213,B006
    """Create flask app for the current project.

    Args:
        config: app configuration

    Returns:
        Flask app
    """
    project = Project.find()
    setup_logging(project)

    settings_service = ProjectSettingsService(project)

    project_engine(project, default=True)

    app = Flask(
        __name__, instance_path=str(project.root), instance_relative_config=True
    )

    # make sure we have the latest environment loaded
    importlib.reload(api_config)

    app.config.from_object("meltano.api.config")
    app.config.from_mapping(**api_config.ProjectSettings(project).as_dict())
    app.config.from_mapping(**config)

    # File logging
    file_handler = logging.handlers.RotatingFileHandler(
        str(project.run_dir("meltano-ui.log")), backupCount=3
    )
    formatter = logging.Formatter(fmt=FORMAT)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 1) Extensions
    from .executor import setup_executor
    from .json import setup_json
    from .mail import mail
    from .models import db
    from .security import setup_security
    from .security.oauth import setup_oauth

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

    from .controllers.orchestrations import orchestrations_bp
    from .controllers.plugins import plugins_bp
    from .controllers.root import api_root, root
    from .controllers.settings import settings_bp

    app.register_blueprint(settings_bp)
    app.register_blueprint(orchestrations_bp)
    app.register_blueprint(plugins_bp)
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

    @app.before_request
    def setup_js_context():
        # setup the appUrl
        g.jsContext = {
            "appUrl": urlsplit(request.host_url).geturl()[:-1],
            "version": meltano_version,
        }

        setting_map = {
            "isSendAnonymousUsageStats": "send_anonymous_usage_stats",
            "projectId": "project_id",
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
        res.headers[VERSION_HEADER] = meltano_version
        return res

    @app.errorhandler(STATUS_SERVER_ERROR)
    def internal_error(exception):
        logger.info(f"Error: {exception}")
        return jsonify({"error": True, "code": str(exception)}), STATUS_SERVER_ERROR

    @app.errorhandler(ProjectReadonly)
    def _handle(ex):
        return (jsonify({"error": True, "code": str(ex)}), HTTP_READONLY_CODE)

    # create the dispatcher to host the `OAuthService`
    app.wsgi_app = DispatcherMiddleware(
        app.wsgi_app, {"/-/oauth": create_oauth_service()}
    )

    return app
