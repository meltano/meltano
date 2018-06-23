from app import db

from flask import (
  Blueprint, jsonify, request, config, current_app
)

from models.projects import Settings

bp = Blueprint('settings', __name__, url_prefix='/settings')

@bp.route('/', methods=['GET'])
def index():
  settings = Settings.query.first()
  return jsonify(settings.serializable())

@bp.route('/new', methods=['POST'])
def new():
  settings = request.get_json()
  current_settings = Settings.query.first()
  current_settings.settings = settings
  db.session.add(current_settings)
  db.session.commit()
  return jsonify(settings)

@bp.route('/connections/<name>/test')
def test(name):
  current_settings = Settings.query.first().settings
  connections = current_settings['connections']
  try:
    found_connection = next(connection for connection in connections if connection['name'] == name)
  except Exception as e:
    found_connection = {} 

  return jsonify(found_connection)