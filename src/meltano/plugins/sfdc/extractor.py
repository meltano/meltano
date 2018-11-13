from typing import Iterator

import pandas as pd
from meltano.core.extract_utils import tables_from_manifest
from sqlalchemy import MetaData

sfdc_metadata = MetaData()
SFDC_SCHEMA_NAME = "sfdc"
manifest_file_path = "extract/sfdc/manifest.yaml"


class SfdcExtractor:
    """
    SaleForce Extractor
    """

    def __init__(self):
        self.name = "sfdc-extractor"
        self.tables = tables_from_manifest(
            manifest_file_path=manifest_file_path,
            metadata=sfdc_metadata,
            schema_name=SFDC_SCHEMA_NAME,
        )
        self.primary_keys = {
            table_name: [table.primary_key.name]
            for table_name, table in self.tables.items()
        }
        self.entities = [ent for ent in self.tables]

    def extract(self, entity) -> Iterator[pd.DataFrame]:
        pass
