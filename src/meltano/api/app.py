import datetime
import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask, request
from flask import jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from . import config
from .external_connector import ExternalConnector
from meltano.support.db import DB

app = Flask(__name__)

# unused afaik
meltano_model_path = config.meltano_model_path
meltano_transform_path = config.meltano_transform_path

app.config.from_object(config)

if os.environ['FLASK_ENV'] == 'development':
    CORS(app)

# TODO: we need to setup proper dependency injection for
# this kind of hard-coupling. We are building multiple UI on
# the same backend. Almost all component need a ready DB
# connection.
DB.setup(host=app.config['POSTGRES_URL'],
         user=app.config['POSTGRES_USER'],
         password=app.config['POSTGRES_PASSWORD'],
         database=app.config['POSTGRES_DB'])
db = SQLAlchemy(app)

connector = ExternalConnector()

logger = logging.getLogger('melt_logger')
handler = RotatingFileHandler(app.config['LOG_PATH'], maxBytes=2000, backupCount=10)
logger.addHandler(handler)
now = str(datetime.datetime.utcnow().strftime('%b %d %Y %I:%M:%S:%f'))
logger.warning(f'Melt started at: {now}')


@app.before_request
def before_request():
    logger.info(f'[{request.remote_addr}] request: {now}')


@app.errorhandler(500)
def internal_error(exception):
    logger.info(f'[{request.remote_addr}] request: {now}, error: {exception}')
    return jsonify({"error": 1}), 500


@app.route("/")
def hello():
    return jsonify({"hello": 1})


from .controllers.projects import projectsBP
from .controllers.repos import reposBP
from .controllers.settings import settingsBP
from .controllers.sql import sqlBP

from .controllers.orchestrations import orchestrationsBP

app.register_blueprint(projectsBP)
app.register_blueprint(reposBP)
app.register_blueprint(settingsBP)
app.register_blueprint(sqlBP)
app.register_blueprint(orchestrationsBP)
