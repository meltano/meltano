import os
import json

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
PROFILES_DIR = 'profile'


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
    run_output = ''
    out_nl = '\n'
    incoming = request.get_json()
    extractor_name = incoming['extractor']
    loader_name = incoming['loader']


    run_output += f"Loading and initializing extractor: {extractor_name}"
    extractor_class = EXTRACTOR_REGISTRY.get(extractor_name)
    if not extractor_class:
        run_output += out_nl+f'Extractor {extractor_name} not found please specify one of the: {list(EXTRACTOR_REGISTRY.keys())}'
        return jsonify({'append': run_output})
    extractor = extractor_class()

    run_output += out_nl+f"Loading and initializing loader: {loader_name}"
    loader_class = LOADER_REGISTRY.get(loader_name)
    if not loader_class:
        run_output += out_nl+f'Loader {loader_name} not found please specify one of the following: {list(LOADER_REGISTRY.keys())}'
        return jsonify({'append': run_output})

    run_output += out_nl+"Starting extraction"
    results = set()
    for entity in extractor.entities:
        loader = loader_class(
            extractor=extractor,
            entity_name=entity,
        )
        run_output += out_nl+"Applying the schema"
        loader.schema_apply()

        run_output += out_nl+"Extracting Data"+out_nl
        entity_dfs = extractor.extract(entity)
        for df in entity_dfs:
            run_output += "."
            results.add(loader.load(df=df))
    run_output += out_nl+"Load done!"

    run_output += out_nl+"Starting Transform"
    run_output += out_nl+"Transform Skipped!"

    # print(run_output)
    return jsonify({'append': run_output})


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
    settings = Settings.query.first()
    settings_connections = settings.settings['connections']
    incoming = request.get_json()
    datastore_name = incoming.get('datastore_name')
    connection = settings_connections.get(datastore_name)
    run_command = ['run', '--profiles-dir', f'{PROFILES_DIR}']
    if model_name:
        run_command.extend(['--models', f'models.{model_name}'])
    if not connection:
        return jsonify({'response': f'Connection {datastore_name} not found',
                        'status': 'error'})
    if connection['type'] == 'postgres':
        os.environ['PG_ADDRESS'] = connection['host']
        os.environ['PG_PORT'] = str(connection['port'])
        os.environ['PG_USERNAME'] = connection['user']
        os.environ['PG_PASSWORD'] = str(connection['password'])
        os.environ['PG_DATABASE'] = connection['dbname']
        os.environ['PG_SCHEMA'] = connection['schema']

    os.chdir(os.path.join(PROJECT_ROOT_DIR, TRANSFORM_DIR))
    dbt_main(run_command)
    return jsonify({
        'response': 'done!',
        'command': str(run_command),
    })
