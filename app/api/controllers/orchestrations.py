from flask import (
  Blueprint, jsonify, request
)

from app import db

bp = Blueprint('orchestrations', __name__, url_prefix='/orchestrations')

@bp.route('/', methods=['GET'])
def index():
  import os
  import json
  result = {}
  myDir = os.path.dirname(os.path.abspath(__file__))
  extract_dir = os.path.join(myDir, '../../../', 'extract/')
  result['extractors'] =  [ name for name in os.listdir(extract_dir) if os.path.isdir(os.path.join(extract_dir, name)) ]
  load_dir = os.path.join(myDir, '../../../', 'load/')
  result['loaders'] =  [ name for name in os.listdir(load_dir) if os.path.isdir(os.path.join(load_dir, name)) ]
  return jsonify(result)