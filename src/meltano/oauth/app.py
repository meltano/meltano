from flask import Flask, url_for, render_template
from werkzeug.contrib.fixers import ProxyFix
import logging
import os


app = Flask(__name__, instance_path=os.getcwd(), instance_relative_config=True)

app.config.from_object("meltano.oauth.config")
app.config.from_pyfile("ui.cfg", silent=True)


@app.route("/")
def root():
    return render_template(
        "home.html",
        providers=(
            {
                "label": "Facebook",
                "url": url_for("OAuth.Facebook.login"),
                "logo": "/static/logos/facebook-logo.png",
            },
        ),
    )


from .providers import OAuth, facebook

facebook(app)
OAuth.init_app(app)

# enable the parsing of X-Forwarded-* headers
app.wsgi_app = ProxyFix(app.wsgi_app)
