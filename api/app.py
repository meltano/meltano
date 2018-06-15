from flask import Flask
from flask import jsonify

from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)

app.config.from_object('config')
if app.config['ENV'] == 'development':
  CORS(app)

db = SQLAlchemy(app)

from controllers import projects
app.register_blueprint(projects.bp)

@app.route("/")
def hello():
  return jsonify({"hello": 1})