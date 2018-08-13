import os
import json

from flask import (
    Blueprint, jsonify, request
)
from cli import run_extract
bp = Blueprint('orchestrations', __name__, url_prefix='/orchestrations')


@bp.route('/', methods=['GET'])
def index():
    result = {}
    myDir = os.path.dirname(os.path.abspath(__file__))
    extract_dir = os.path.join(myDir, '../../', 'extract/')
    result['extractors'] = [name for name in os.listdir(extract_dir) if os.path.isdir(os.path.join(extract_dir, name))]
    load_dir = os.path.join(myDir, '../../', 'load/')
    result['loaders'] = [name for name in os.listdir(load_dir) if os.path.isdir(os.path.join(load_dir, name))]
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
    run_extract(extractor_name, 'csv')
    return jsonify({'extractor_name': extractor_name,
                    'output_file_path': f'{extractor_name}.csv'})


@bp.route('/load/<loader_name>', methods=['POST'])
def load(extractor_name):
    # do the business
    incoming = request.get_json()
    extract = incoming['extractor']
    # get the file name/extractor name
    # query the setting model to get
    # load the extracted data to data warehouse
    # return json
    pass


@bp.route('/transform/<transform_name>', methods=['POST'])
def transform(transform_name):
    # do the business
    incoming = request.get_json()
    loader = incoming['loader']
    # find the transformer and run with DBT
    # return json
    pass
