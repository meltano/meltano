import json
import sqlalchemy
import psycopg2
from decimal import Decimal

from app import db

from flask import (
  Blueprint, jsonify, request
)

from .utils import SqlHelper

from models.projects import Project, Settings
from models.data import (
  Model, Explore, View, Dimension, Measure, Join
)

connections = {}

def update_connections():
  current_connections = Settings.query.first().settings['connections']
  for connection in current_connections:
    connection_name = connection['name']
    if connection_name not in connections:
      this_connection = {}
      if connection['dialect'] == 'postgresql':
        connection_url = 'postgresql+psycopg2://{user}:{pw}@{host}:{port}/{db}'.format(user=connection['username'],pw=connection['password'],host=connection['host'],port=connection['port'], db=connection['database'])
        this_connection['connection_url'] = connection_url
        this_connection['engine'] =  sqlalchemy.create_engine(this_connection['connection_url'])
      connections[connection_name] = this_connection

bp = Blueprint('sql', __name__, url_prefix='/sql')

@bp.route('/', methods=['GET'])
def index():
  return jsonify({'result': True})

@bp.route('/get/<model_name>/<explore_name>', methods=['POST'])
def get_sql(model_name, explore_name):
  update_connections()
  sqlHelper = SqlHelper()
  model = Model.query.filter(Model.name == model_name).first()
  explore = Explore.query.filter(Explore.name == explore_name).first()
  incoming_json = request.get_json()
  view_name = incoming_json['view']
  limit = incoming_json['limit']
  view = View.query.filter(View.name == view_name).first()
  incoming_dimensions = incoming_json['dimensions']
  incoming_measures = incoming_json['measures']
  group_by = sqlHelper.group_by(incoming_dimensions, incoming_measures)
  to_run = incoming_json['run']
  base_table = view.settings['sql_table_name']
  measures = filter(lambda x: x.name in incoming_measures, view.measures)

  dimensions = filter(lambda x: x.name in incoming_dimensions, view.dimensions)
  dimensions = map(lambda x: x.settings['sql'].replace("${TABLE}", explore_name), dimensions)
  dimensions = ', '.join(map(lambda x: '{}'.format(x), dimensions))
  
  measures = filter(lambda x: x.name in incoming_measures, view.measures)
  measures = ', '.join([sqlHelper.get_func(x.settings['type'], explore_name, x.settings['sql']) for x in measures])
  to_join = []
  
  if dimensions:
    to_join.append(dimensions)
  if measures:
    to_join.append(measures)

  order_by = ''

  base_sql = 'SELECT {} FROM {} AS {} {} {} LIMIT {};'.format(', '.join(to_join), base_table, explore_name, group_by, order_by, limit);
  # base_sql = ' '.join(base_sql.split())
  def default(obj):
    if isinstance(obj, Decimal):
        return str(obj)
    raise TypeError("Object of type '%s' is not JSON serializable" % type(obj).__name__)

  if to_run:
    engine = connections[model.settings['connection']]['engine']
    results = engine.execute(base_sql)
    results = [dict(row) for row in results]
    return json.dumps({'sql': base_sql, 'results': results, 'keys': list(results[0].keys())}, default=default)
  else:
    return json.dumps({'sql': base_sql}, default=default)
