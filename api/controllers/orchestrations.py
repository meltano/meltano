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

from api.config import TEMP_FOLDER
from cli import run_extract, EXTRACTOR_REGISTRY, LOADER_REGISTRY

bp = Blueprint('orchestrations', __name__, url_prefix='/orchestrations')

DATETIME_TYPES_TO_PARSE = (TIMESTAMP, DATE, DATETIME)


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
def extract(extractor_name: str)-> Response:
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
    except TypeError:
        return make_response(
            jsonify({'response': 'extractor not found', 'available extractors': list(EXTRACTOR_REGISTRY.keys())}),
            404
        )
    extractor_class = EXTRACTOR_REGISTRY.get(extractor_name)
    extractor = extractor_class()
    loader_class = LOADER_REGISTRY.get(loader_name)
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


@bp.route('/transform/<transformer_name>', methods=['POST'])
def transform(transformer_name):
    """
    :param transformer_name:
    :return:
    """
    # do the business
    incoming = request.get_json()
    loader = incoming['loader']
    # find the transformer and run with DBT
    # return json
    pass
