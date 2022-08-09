from __future__ import annotations

import logging
import secrets

from flask import Flask, render_template, url_for
from werkzeug.middleware.proxy_fix import ProxyFix

from meltano.core.project import Project
from meltano.oauth import config as oauth_config


def create_app():
    project = Project.find()

    app = Flask(
        __name__, instance_path=str(project.root), instance_relative_config=True
    )

    app.config.from_object("meltano.oauth.config")
    app.config.from_mapping(**oauth_config.ProjectSettings(project).as_dict())

    @app.errorhandler(Exception)
    def _handle(e):
        logging.exception("An error occurred")
        return error()

    @app.route("/")
    def root():
        return render_template(
            "home.html",
            providers=(
                {
                    "label": "Facebook",
                    "url": url_for("OAuth.Facebook.login"),
                    "logo": url_for("static", filename="logos/facebook-logo.png"),
                },
                {
                    "label": "Google Ads",
                    "url": url_for("OAuth.GoogleAdwords.login"),
                    "logo": url_for("static", filename="logos/adwords-logo.png"),
                },
            ),
        )

    @app.route("/sample")
    def sample():
        secret_token_size = 128
        return render_template("token.html", token=secrets.token_hex(secret_token_size))

    @app.route("/error")
    def error():
        return render_template("error.html")

    from .providers import OAuth, facebook, google_adwords

    facebook(app)
    google_adwords(app)
    OAuth.init_app(app)

    # enable the parsing of X-Forwarded-* headers
    app.wsgi_app = ProxyFix(app.wsgi_app)

    return app
