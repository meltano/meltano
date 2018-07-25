import json
import sqlalchemy
import psycopg2
import re
from collections import OrderedDict
from decimal import Decimal
from datetime import date, datetime

from pypika import Query, Table, Field

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

def default(obj):
  if isinstance(obj, Decimal):
      return str(obj)
  elif isinstance(obj, (datetime, date)):
    return obj.isoformat()
  raise TypeError("Object of type '%s' is not JSON serialize-able" % type(obj).__name__)

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
  incoming_joins = incoming_json['joins']
  incoming_dimension_groups = incoming_json['dimension_groups']
  incoming_measures = incoming_json['measures']
  incoming_filters = incoming_json['filters']
  # get all timeframes
  timeframes = [t['timeframes'] for t in incoming_dimension_groups]
  # flatten list of timeframes
  timeframes = [y for x in timeframes for y in x]
  group_by = sqlHelper.group_by(incoming_joins, incoming_dimensions, timeframes)
  filter_by = sqlHelper.filter_by(incoming_filters, explore_name)
  to_run = incoming_json['run']
  base_table = view.settings['sql_table_name']
  dimensions = filter(lambda x: x.name in incoming_dimensions, view.dimensions)
  set_dimensions = dimensions
  dimensions = map(lambda x: x.settings['sql'].replace("${TABLE}", explore_name), dimensions)
  dimensions = ',\n\t '.join(map(lambda x: '{}'.format(x), dimensions))
  dimension_groups = sqlHelper.dimension_groups(view.name, explore_name, incoming_dimension_groups)
  
  measures = filter(lambda x: x.name in incoming_measures, view.measures)
  set_measures = list(measures)
  measures = filter(lambda x: x.name in incoming_measures, view.measures)
  measures = ',\n\t '.join([sqlHelper.get_func(x.name, x.settings['type'], explore_name, x.settings['sql']) for x in measures])

  join_dimensions = sqlHelper.join_dimensions(incoming_joins)
  join_measures = sqlHelper.join_measures(incoming_joins)

  if join_dimensions:
    dimensions = join_dimensions
  if join_measures:
    measures = join_measures


  join_sql = sqlHelper.joins_by(incoming_joins, view)

  to_join = []
  
  if dimensions:
    to_join.append(dimensions)
  if dimension_groups:
    to_join.append(dimension_groups)
  if measures:
    to_join.append(measures)

  set_dimensions = ([d.settings for d in set_dimensions])
  set_measures = ([m.settings for m in set_measures])
  measures_as_dict = {}
  for settings in set_measures:
    new_key = re.sub(r'\$\{[A-Za-z]+\}', explore_name, settings['sql']).rstrip()
    measures_as_dict[new_key] = settings

  incoming_order = incoming_json['order']
  incoming_order_desc = incoming_json['desc']
  order_by = 'ORDER BY {}'.format(incoming_order) if incoming_order else ''

  if incoming_order_desc:
    order_by = '{} DESC'.format(order_by)


  base_sql = 'SELECT\n\t{}\nFROM {} AS {} \n{} {} \n{} \n{} \nLIMIT {};'.format(',\n '.join(to_join), base_table, explore_name, filter_by, join_sql, group_by, order_by, limit);
  if to_run:
    db_to_connect = model.settings['connection']
    if not db_to_connect in connections:
      return jsonify({'error': True, 'code': 'Missing connection details to {}. Create a connection to {} in the settings.'.format(db_to_connect, db_to_connect)}), 422
    engine = connections[model.settings['connection']]['engine']

    try:
      results = engine.execute(base_sql)
    except sqlalchemy.exc.DBAPIError as e:
      return jsonify({'error': True, 'code': e.code, 'orig': e.orig.diag.message_primary, 'statement': e.statement}), 422

    results = [OrderedDict(row) for row in results]

    base_dict = {'sql': base_sql, 'results': results, 'error': False}
    if not len(results):
      base_dict['empty'] = True
    else:
      base_dict['empty'] = False
      base_dict['keys'] = list(results[0].keys())
      base_dict['measures'] = measures_as_dict
    return json.dumps(base_dict, default=default)
  else:
    return json.dumps({'sql': base_sql}, default=default)

@bp.route('/distinct/<model_name>/<explore_name>', methods=['POST'])
def get_distinct_field_name(model_name, explore_name):
  update_connections()
  incoming_json = request.get_json()
  field_name = incoming_json['field'].replace('${TABLE}', explore_name)
  model = Model.query.filter(Model.name == model_name).first()
  explore = Explore.query.filter(Explore.name == explore_name).first()
  base_table = explore.view.settings['sql_table_name']
  base_sql = 'SELECT DISTINCT {} FROM {} AS {} ORDER BY {}'.format(field_name, base_table, explore_name, field_name)
  engine = connections[model.settings['connection']]['engine']
  results = engine.execute(base_sql)
  results = [dict(row) for row in results]
  return json.dumps({'sql': base_sql, 'results': results, 'keys': list(results[0].keys())}, default=default)