import os
from typing import Iterator, Dict
from time import sleep

import pandas as pd
from salesforce_bulk.util import IteratorBytesIO
from salesforce_bulk import SalesforceBulk
from sqlalchemy import MetaData

from extract.utils import tables_from_manifest

client = SalesforceBulk(
    username=os.getenv('SFDC_USERNAME'),
    password=os.getenv('SFDC_PASSWORD'),
    security_token=os.getenv('SFDC_SECURITY_TOKEN'),
)

sfdc_metadata = MetaData()
SFDC_SCHEMA_NAME = 'sfdc'
manifest_file_path = 'extract/sfdc/manifest.yaml'


class SfdcExtractor:
    """
    SaleForce Extractor
    """
    def __init__(self):
        self.name = 'sfdc-extractor'
        self.tables = tables_from_manifest(
            manifest_file_path=manifest_file_path,
            metadata=sfdc_metadata,
            schema_name=SFDC_SCHEMA_NAME,
        )
        self.primary_keys = {
            table_name: [table.primary_key.name]
            for table_name, table in self.tables.items()
        }

    def _extract_entity(self, entity_name) -> IteratorBytesIO:
        job_id = client.create_query_job(entity_name, contentType='JSON', concurrency='Parallel')
        column_names = self.tables[entity_name].columns.keys()
        column_names_string = ','.join(column_names)
        batch_id = client.query(job_id, f"SELECT {column_names_string} FROM {entity_name}")
        client.close_job(job_id)
        while not client.is_batch_done(batch_id):
            sleep(1)
        for result in client.get_all_results_for_query_batch(batch_id):
            return result

    def extract(self) -> Iterator[pd.DataFrame]:
        for entity_name in self.tables:
            result = self._extract_entity(entity_name)
            df = pd.read_json(result, orient='records')
            yield df
