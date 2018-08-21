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
  to_run = incoming_json['run']
  sql_dict = sqlHelper.get_sql(explore, incoming_json)
  outgoing_sql = sql_dict['sql']
  incoming_order = incoming_json['order']
  incoming_order_desc = incoming_json['desc']
  measures = sql_dict['measures']
  dimensions = sql_dict['dimensions']

  if to_run:
    db_to_connect = model.settings['connection']
    if not db_to_connect in connections:
      return jsonify({'error': True, 'code': 'Missing connection details to {}. Create a connection to {} in the settings.'.format(db_to_connect, db_to_connect)}), 422
    engine = connections[model.settings['connection']]['engine']

    try:
      results = engine.execute(outgoing_sql)
    except sqlalchemy.exc.DBAPIError as e:
      print(e)
      return jsonify({'error': True, 'code': e.code, 'orig': e.orig.diag.message_primary, 'statement': e.statement}), 422

    results = [OrderedDict(row) for row in results]

    base_dict = {'sql': outgoing_sql, 'results': results, 'error': False}
    if not len(results):
      base_dict['empty'] = True
    else:
      base_dict['empty'] = False
      base_dict['keys'] = list(results[0].keys())
      base_dict['measures'] = measures
    return json.dumps(base_dict, default=default)
  else:
    return json.dumps({'sql': outgoing_sql}, default=default)

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