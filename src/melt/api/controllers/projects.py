from flask import (
  Blueprint, jsonify, request
)

from models.projects import Project
from models.projects import Settings
from app import db

bp = Blueprint('projects', __name__, url_prefix='/projects')

@bp.route('/', methods=['GET'])
def index():
  p = Project.query.first()
  return jsonify({'name': p.name, 'git_url': p.git_url}) if p else jsonify({'name': '', 'git_url': ''})

@bp.route('/new', methods=['POST'])
def add():
  incoming = request.get_json()
  name = incoming.get('name')
  git_url = incoming.get('git_url')
  settings = Settings()
  project = Project(name=name, git_url=git_url)
  project.settings = settings
  db.session.add(settings)
  db.session.add(project)
  db.session.commit()

  return jsonify({'name': name, 'git_url': git_url})