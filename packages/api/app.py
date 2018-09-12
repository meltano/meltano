import datetime
import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask, request, render_template
from flask import jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from api.external_connector import ExternalConnector

app = Flask(__name__)

# unused afaik
meltano_home_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
meltano_model_path = os.path.join(meltano_home_path, 'model')
meltano_load_path = os.path.join(meltano_home_path, 'load')
meltano_transform_path = os.path.join(meltano_home_path, 'transform')

app.config.from_object('api.config')

if os.environ['FLASK_ENV'] == 'development':
    CORS(app)

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
    return render_template('500.html'), 500


from api.controllers.projects import projectsBP
from api.controllers.repos import reposBP
from api.controllers.settings import settingsBP
from api.controllers.sql import sqlBP
from api.controllers.orchestrations import orchestrationsBP

app.register_blueprint(projectsBP)
app.register_blueprint(reposBP)
app.register_blueprint(settingsBP)
app.register_blueprint(sqlBP)
app.register_blueprint(orchestrationsBP)


@app.route("/")
def hello():
    return jsonify({"hello": 1})

if __name__ == '__main__':
    app.run(host='0.0.0.0')
