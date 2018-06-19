import os
from flask import Flask
from flask import jsonify

from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)

app.config.from_object('config')
if os.environ['FLASK_ENV'] == 'development':
  CORS(app)

db = SQLAlchemy(app)

from controllers import projects
from controllers import repos
app.register_blueprint(projects.bp)
app.register_blueprint(repos.bp)

@app.route("/")
def hello():
  return jsonify({"hello": 1})

@app.route("/drop_it_like_its_hot")
def reset_db():
  db.drop_all()
  db.create_all()
  return jsonify({"dropped_it":"like_its_hot"})