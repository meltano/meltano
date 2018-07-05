import os
import logging
import datetime
from logging.handlers import RotatingFileHandler
from flask import Flask, request
from flask import jsonify

from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)

app.config.from_object('config')
if os.environ['FLASK_ENV'] == 'development':
  CORS(app)

db = SQLAlchemy(app)

logger = logging.getLogger('melt_logger')
handler = RotatingFileHandler(app.config['LOG_PATH'], maxBytes=2000, backupCount=10)
logger.addHandler(handler)
now = str(datetime.datetime.utcnow().strftime('%b %d %Y %I:%M:%S:%f'))
logger.warning('Melt started at: {}'.format(now))

@app.before_request
def before_request():
  print('before_request')
  print(request.remote_addr)
  logger.info('[{}] request: {}'.format(request.remote_addr, now))
  print('Logging!')

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
  db.drop_all()
  db.create_all()
  return jsonify({"dropped_it":"like_its_hot"})