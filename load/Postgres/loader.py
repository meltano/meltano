import os

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateSchema

from extract.utils import DATETIME_COLUMNS


class PostgresLoader:
    def __init__(self, **kwargs):
        """
        :param entity_name: str Name of the entity to load
        :param kwargs:
        """
        self.entity_name = kwargs['entity_name']
        self.extractor = kwargs['extractor']
        self.table = self.extractor.tables.get(self.entity_name)
        self.index_elements = self.extractor.primary_keys.get(self.entity_name)
        if 'connection_string' in kwargs:
            self.engine = create_engine(kwargs['connection_string'])
        else:
            username = os.environ.get('PG_USERNAME')
            password = os.environ.get('PG_PASSWORD')
            host = os.environ.get('PG_ADDRESS')
            port = os.environ.get('PG_PORT')
            database = os.environ.get('PG_DATABASE')
            self.engine = create_engine(f'postgresql://{username}:{password}@{host}:{port}/{database}')

    def schema_apply(self):
        # TODO: add loaded_at(timestamp) col to the schema
        if not self.engine.dialect.has_schema(self.engine, self.table.schema):
            print(f"Schema {self.table.schema} does not exist -> creating it ")
            self.engine.execute(CreateSchema(self.table.schema))
        # TODO: update table
        if not self.engine.dialect.has_table(self.engine, self.table.name, self.table.schema):
            print(f"Table {self.table.name} does not exist -> creating it ")
            self.table.metadata.create_all(self.engine)

    def load(self, df):
        if not df.empty:
            entity_columns = self.table.columns
            datetime_col_names = [
                col.name
                for col in entity_columns
                if isinstance(col.type, DATETIME_COLUMNS)
            ]
            # TODO: potentially discover datetime rows from the dataframe itself
            # datetime_col_names = [col for col in df.columns if df[col].dtype == np.dtype('datetime64[ns]')]

            # Converting datetimes to strings, then replace the pandas NaT values to python None
            # which is what postgresql.insert() expects (it does not handle NaT by itself)
            df[datetime_col_names] = df[datetime_col_names].astype(object).where(pd.notnull(df), None)
            dict_to_load: list = df.to_dict(orient='records')
            dict_to_load = dict_to_load[0:50]
            insert_stmt = postgresql.insert(self.table).values(dict_to_load)
            insert_stmt = insert_stmt.on_conflict_do_update(
                index_elements=self.index_elements,
                # only compatible with Postgres >= 9.5
                set_=insert_stmt.excluded._data,  # link to the conflicting data
            )
            print(f'Loading data to Postgres for {self.entity_name}')
            self.engine.execute(insert_stmt)
            print(f'Loading Done ')
        else:
            print(f'DataFrame {df} is empty -> skipping it')
