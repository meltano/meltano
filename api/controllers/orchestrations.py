import os
import json
import tempfile

import yaml
from flask import (
    Blueprint,
    request,
    url_for,
    jsonify,
    make_response,
    Response,
)
import pandas as pd
from sqlalchemy import TIMESTAMP, DATE, DATETIME
from dbt.main import main as dbt_main

from api.config import TEMP_FOLDER, PROJECT_ROOT_DIR
from cli import run_extract, EXTRACTOR_REGISTRY, LOADER_REGISTRY
from models.settings import Settings

bp = Blueprint('orchestrations', __name__, url_prefix='/orchestrations')

DATETIME_TYPES_TO_PARSE = (TIMESTAMP, DATE, DATETIME)
TRANSFORM_DIR = 'transform'


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
def extract(extractor_name: str) -> Response:
    """
    endpoint that performs extraction of the selected datasource to the .csv file(s)
    stored on disk in the /static/tmp/ directory)
    """
    csv_files = run_extract(extractor_name, 'csv')
    csv_files_url = [url_for('static', filename=f'tmp/{file_name}') for file_name in csv_files]
    return jsonify({'extractor_name': extractor_name,
                    'output_file_paths': csv_files_url})


@bp.route('/load/<loader_name>', methods=['POST'])
def load(loader_name: str) -> Response:
    """
    endpoint that performs load of the .csv file(s)(stored on disk in the /static/tmp/ directory)
    of the selected extractor  into the selected loader
    :param loader_name: the name of the loader to use in this request
    """
    incoming = request.get_json()
    try:
        extractor_name = incoming['extractor']
        extractor_class = EXTRACTOR_REGISTRY[extractor_name]
        extractor = extractor_class()
    except KeyError:
        return make_response(
            jsonify(
                {'response': 'extractor not found', 'available extractors': list(EXTRACTOR_REGISTRY.keys())}
            ), 404
        )
    try:
        loader_class = LOADER_REGISTRY.get(loader_name)
    except KeyError:
        return make_response(
            jsonify(
                {'response': 'Loader not found', 'available loaders': list(LOADER_REGISTRY.keys())}
            ), 404
        )
    extractor_temp_files = [filename for filename in os.listdir(TEMP_FOLDER) if filename.startswith(extractor_name)]
    for file_path in extractor_temp_files:
        filename = os.path.splitext(file_path)[0]
        entity_name = filename.split('--')[1]
        loader = loader_class(entity_name=entity_name, extractor=extractor)
        loader.schema_apply()
        datetime_cols = [col.name for col in loader.table.columns if isinstance(col.type, DATETIME_TYPES_TO_PARSE)]
        df = pd.read_csv(os.path.join(TEMP_FOLDER, file_path), parse_dates=datetime_cols)
        df.replace({pd.NaT: None}, inplace=True)
        loader.load(df=df)
    return jsonify({'response': 'done', 'inserted files': extractor_temp_files})


DBT_PROFILE_TEMPLATE = {
    'config': {
        'send_anonymous_usage_stats': False,
        'use_colors': True
    },
    'meltano': {
        'target': 'dev',
        'outputs': {
            'dev': {
                'type': 'postgres',
                'threads': 2,
                'host': '',
                'port': '',
                'user': '',
                'pass': '',
                'dbname': '',
                'schema': '',
            }
        }
    }
}


@bp.route('/transform/<model_name>', methods=['POST'])
def transform(model_name):
    """
    {
        'datastore_name': 'prod_dw',
        ''
    }
    Looks up the credential by the name of the datastore passed to the api

    Generates temp profiles.yml file from the passed credentials,
    then is is passed to the dbt.main function
    :param model_name: nam
    :return:
    """

    incoming = request.get_json()
    datastore_name = incoming.get('datastore_name')
    settings = Settings.query.first()
    available_connections = settings.settings['connections']
    connection = available_connections.get(datastore_name)

    # if not connection:
    #     return jsonify({'response': f'Connection {datastore_name} not found',
    #                     'status': 'error'})
    # DBT_PROFILE_TEMPLATE['meltano']['outputs']['dev'] = {
    #     'type': connection['type'],
    #     'threads': connection['threads'],
    #     'host': connection['host'],
    #     'port': connection['port'],
    #     'user': connection['user'],
    #     'pass': connection['pass'],
    #     'dbname': connection['dbname'],
    #     'schema': connection['schema'],
    # }
    # with tempfile.TemporaryDirectory() as temp_dir:
    #     with open(os.path.join(temp_dir, 'profile.yml'), 'w') as file:
    #         yaml.dump(DBT_PROFILE_TEMPLATE, file, default_flow_style=False)
    #         run_command = ['run', '--profiles-dir', f'{temp_dir}']
    #         if model_name:
    #             run_command.extend(['--models', f'models.{model_name}'])
    #         os.chdir(os.path.join(PROJECT_ROOT_DIR, TRANSFORM_DIR))
    #         dbt_main(run_command)
    return jsonify({
        'response': 'done!',
        'command': str(run_command),
    })
