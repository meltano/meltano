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