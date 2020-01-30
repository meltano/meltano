from flask import Flask
import logging
import os


app = Flask(__name__, instance_path=os.getcwd(), instance_relative_config=True)

app.config.from_object("meltano.oauth.config")
app.config.from_pyfile("ui.cfg", silent=True)
# app.config.update(**config)

from .providers import OAuth, facebook

facebook(app)
OAuth.init_app(app)


@app.route("/")
def root():
    return '<a href="/oauth/facebook/login">Facebook</a>'
