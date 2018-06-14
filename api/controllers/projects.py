from flask import (
  Blueprint, jsonify
)

from models.projects import Project

bp = Blueprint('projects', __name__, url_prefix='/projects')

@bp.route('/', methods=['GET'])
def index():
  projects = Project.query.all()
  return jsonify([{'name': p.name} for p in projects])