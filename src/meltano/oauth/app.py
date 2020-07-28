import logging
import os
import secrets

from flask import Flask, url_for, render_template
from werkzeug.contrib.fixers import ProxyFix

from meltano.core.project import Project
import meltano.oauth.config


def create_app():
    project = Project.find()

    app = Flask(
        __name__, instance_path=str(project.root), instance_relative_config=True
    )

    app.config.from_object("meltano.oauth.config")
    app.config.from_mapping(**meltano.oauth.config.ProjectSettings(project).as_dict())

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
        return render_template("token.html", token=secrets.token_hex(128))

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
