from flask import Flask, url_for, render_template
from werkzeug.contrib.fixers import ProxyFix
import logging
import os


app = Flask(__name__, instance_path=os.getcwd(), instance_relative_config=True)
app.config.from_object("meltano.oauth.config")
app.config.from_pyfile("ui.cfg", silent=True)


@app.route("/")
def root():
    url = url_for("OAuth.Facebook.login")

    return f"<a href='{url}'>Facebook</a>"


from .providers import OAuth, facebook

facebook(app)
OAuth.init_app(app)

# enable the parsing of X-Forwarded-* headers
ProxyFix(app)
