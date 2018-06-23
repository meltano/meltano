import json

from app import db

from flask import (
  Blueprint, jsonify, request
)

from models.projects import Project
from models.data import (
  Model, Explore, View, Dimension, Measure, Join
)

bp = Blueprint('sql', __name__, url_prefix='/sql')

@bp.route('/', methods=['GET'])
def index():
  return jsonify({'result': True})

@bp.route('/<model_name>/<explore_name>', methods=['POST'])
def model_explore(model_name, explore_name):
  model = Model.query.filter(Model.name == model_name).first()
  explore = Explore.query.filter(Explore.name == explore_name).first()
  incoming_json = request.get_json()
  view_name = incoming_json['view']
  view = View.query.filter(View.name == view_name).first()
  incoming_dimensions = incoming_json['dimensions']
  dimensions = filter(lambda x: x.name in incoming_dimensions, view.dimensions)
  dimensions = map(lambda x: x.settings['sql'], dimensions)
  print(dimensions)
  base_table = view.settings['sql_table_name']
  dimensions = ', '.join(map(lambda x: '{}.{}'.format(explore_name, x), dimensions))
  base_sql = 'SELECT {} FROM {} AS {} LIMIT 3;'.format(dimensions, base_table, explore_name);
  print(base_sql)
  # explore = Explore.query\
  #           .join(Model, Explore.model_id == Model.id)\
  #           .filter(Model.name == model_name)\
  #           .filter(Explore.name == explore_name)\
  #           .first()
  # print(explore.view)
  
  return jsonify({'result': True})
