from typing import Generator, Dict

from sqlalchemy import create_engine
from pandas import DataFrame
from sqlalchemy.dialects import postgresql


class CsvLoader:
    def __init__(self, extractor):
        self.extractor = extractor

    def load(self, schema_name, df):
        if not df.empty:
            df.to_csv(schema_name)

        else:
            print(f'DataFrame {df} is empty -> skipping it')
