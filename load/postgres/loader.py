from typing import Generator, Dict

from sqlalchemy import create_engine
from pandas import DataFrame
from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateSchema


class PostgresLoader:
    def __init__(self, **kwargs):
        self.engine = create_engine(kwargs['connection_string'])
        self.entity_name = kwargs['entity_name']
        self.extractor = kwargs['extractor']
        self.table = self.extractor.get

    def schema_apply(self):
        if not self.engine.dialect.has_schema(self.engine, self.table.schema):
            print(f"Schema {self.table.schema} does not exist -> creating it ")
            self.engine.execute(CreateSchema(self.table.schema))
        if not self.engine.dialect.has_table(self.engine, self.table.name):
            print(f"Table {self.table.name} does not exist -> creating it ")
            self.table.metadata.create_all(self.engine)

    def load(self, schema_name, df):
        if not df.empty:
            # df.to_sql(schema_name, con=self.engine, if_exists='append')
            dfs_to_load: list = df.to_dict(orient='records')
            insert_stmt = postgresql.insert(self.table).values(dfs_to_load)
            insert_stmt = insert_stmt.on_conflict_do_update(
                index_elements=self.primary_keys,
                set_=insert_stmt.excluded._data,   # overwrite the data with the new one
            )
            print(f'Loading df: {dfs_to_load}')
            self.engine.execute(insert_stmt)
        else:
            print(f'DataFrame {df} is empty -> skipping it')
