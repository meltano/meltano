from flask import Flask
from flask import jsonify

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config.from_object('config')

db = SQLAlchemy(app)

from controllers import projects
app.register_blueprint(projects.bp)

@app.route("/")
def hello():
  return jsonify({"hello": 1})