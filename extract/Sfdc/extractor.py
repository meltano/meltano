import os
from typing import Iterator, Dict
from time import sleep

import pandas as pd
from salesforce_bulk.util import IteratorBytesIO
from salesforce_bulk import SalesforceBulk
from sqlalchemy import MetaData

from extract.utils import tables_from_manifest, DATETIME_COLUMNS

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

    @staticmethod
    def _extract_entity(entity_name, column_names) -> IteratorBytesIO:
        job_id = client.create_query_job(entity_name, contentType='JSON', concurrency='Parallel')
        column_names_string = ','.join(column_names)
        batch_id = client.query(job_id, f"SELECT {column_names_string} FROM {entity_name}")
        client.close_job(job_id)
        while not client.is_batch_done(batch_id):
            sleep(1)
        for result in client.get_all_results_for_query_batch(batch_id):
            # Since we are adding only one client.query request there will be only one result in the generator
            return result

    @staticmethod
    def _cleanup_df(df, entity_columns, entity_column_names):
        # Lowercase names of the columns to match the format in the manifest file
        df.rename(columns=lambda x: x.lower(), inplace=True)
        # Include only the columns specified in the the manifest file
        df = df[entity_column_names]
        # Convert the datetime columns to pandas datatime
        datetime_col_names = [
            col.name
            for col in entity_columns
            if isinstance(col.type, DATETIME_COLUMNS)
        ]
        df[datetime_col_names] = df[datetime_col_names].apply(pd.to_datetime)
        return df

    def extract(self, entity_name) -> Iterator[pd.DataFrame]:
        entity_columns = self.tables[entity_name].columns
        entity_column_names = entity_columns.keys()
        result = self._extract_entity(entity_name, entity_column_names)
        df = pd.read_json(result)
        df = self._cleanup_df(df, entity_columns, entity_column_names)
        yield df
