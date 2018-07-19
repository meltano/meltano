import os
import logging
import datetime
from logging.handlers import RotatingFileHandler
from flask import Flask, request
from flask import jsonify

from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from external_connector import ExternalConnector

app = Flask(__name__)

app.config.from_object('config')
if os.environ['FLASK_ENV'] == 'development':
  CORS(app)

db = SQLAlchemy(app)

connector = ExternalConnector()

logger = logging.getLogger('melt_logger')
handler = RotatingFileHandler(app.config['LOG_PATH'], maxBytes=2000, backupCount=10)
logger.addHandler(handler)
now = str(datetime.datetime.utcnow().strftime('%b %d %Y %I:%M:%S:%f'))
logger.warning('Melt started at: {}'.format(now))

@app.before_request
def before_request():
  logger.info('[{}] request: {}'.format(request.remote_addr, now))

from controllers import projects
from controllers import repos
from controllers import settings
from controllers import sql
app.register_blueprint(projects.bp)
app.register_blueprint(repos.bp)
app.register_blueprint(settings.bp)
app.register_blueprint(sql.bp)

@app.route("/")
def hello():
  return jsonify({"hello": 1})

@app.route("/drop_it_like_its_hot")
def reset_db():
  try:
    db.drop_all()
  except sqlalchemy.exc.OperationalError as err:
    logging.error("Failed drop database.")
    
  db.create_all()
  return jsonify({"dropped_it":"like_its_hot"})