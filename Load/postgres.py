import os
from typing import Generator, Dict

from sqlalchemy import create_engine
from pandas import DataFrame


class PostgresLoader:
    def __init__(self):
        # we can ask user to enter all this variables in one connection string
        username = os.environ.get("PG_USERNAME")
        password = os.environ.get("PG_PASSWORD")
        host = os.environ.get("PG_ADDRESS")
        port = os.environ.get("PG_PORT")
        db_name = os.environ.get("PG_DATABASE")
        connection_string = f'postgresql://{username}:{password}@{host}:{port}/{db_name}'
        self.connection = create_engine(connection_string)
        self.extracting_entities = ['line_items', 'regions']

    def load(self, entity_data: Generator[Dict[str, DataFrame], None, None]):
        for entity_dict in entity_data:
            for schema_name, dataframe in entity_dict.items():
                if not dataframe.empty:
                    dataframe.to_sql(name=schema_name, con=self.connection, index=False, if_exists='append')
                else:
                    print(f'DataFrame {dataframe} is empty -> skipping it')
