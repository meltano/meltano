import subprocess, json

from flask import (
  Blueprint, jsonify, request
)

from app import extract

from app import db

bp = Blueprint('orchestrations', __name__, url_prefix='/orchestrations')

@bp.route('/', methods=['GET'])
def index():
  import os
  import json
  result = {}
  myDir = os.path.dirname(os.path.abspath(__file__))
  extract_dir = os.path.join(myDir, '../../', 'extract/')
  result['extractors'] =  [ name for name in os.listdir(extract_dir) if os.path.isdir(os.path.join(extract_dir, name)) ]
  load_dir = os.path.join(myDir, '../../', 'load/')
  result['loaders'] =  [ name for name in os.listdir(load_dir) if os.path.isdir(os.path.join(load_dir, name)) ]
  return jsonify(result)

@bp.route('/run', methods=['POST'])
def run():
  incoming = request.get_json()
  extractor = incoming['extractor']
  print(extract)
  j = json.loads(p.stdout.decode("utf-8"))
  return jsonify({'append': j})

@bp.route('/extract/<extractor_name>', methods=['POST'])
def extract(extractor_name):
  # do the business
  # save to a file
  # return json

@bp.route('/load/<loader_name>', methods=['POST'])
def extract(extractor_name):
  # do the business
  incoming = request.get_json()
  extract = incoming['extractor']
  # get the file name/extractor name
  # query the setting model to get 
  # load the extracted data to data warehouse
  # return json

@bp.route('/transform/<transform_name>', methods=['POST'])
def extract(transform_name):
  # do the business
  incoming = request.get_json()
  loader = incoming['loader']
  # find the transformer and run with DBT
  # return json