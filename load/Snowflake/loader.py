import os
import pandas as pd

from sqlalchemy import create_engine, inspect
from sqlalchemy.schema import CreateSchema

from snowflake.sqlalchemy import URL

class SnowflakeLoader:
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
            self.engine = create_engine(
                URL(
                    user=os.environ.get('SNOWFLAKE_USERNAME'),
                    password=os.environ.get('SNOWFLAKE_PASSWORD'),
                    account=os.environ.get('SNOWFLAKE_ACCOUNT_NAME'),
                    database = os.environ.get('SNOWFLAKE_DB_NAME'),
                    warehouse=os.environ.get('SNOWFLAKE_WAREHOUSE'),
                )
            )

    def schema_apply(self):
        inspector = inspect(self.engine)

        all_schema_names = inspector.get_schema_names()
        if not (self.table.schema in all_schema_names):
            print(f"Schema {self.table.schema} does not exist -> creating it ")
            self.engine.execute(CreateSchema(self.table.schema))

        all_table_names = inspector.get_table_names(self.table.schema)
        if not (self.table.name in all_table_names):
            print(f"Table {self.table.name} does not exist -> creating it ")
            self.table.metadata.create_all(self.engine)

        # GRANT access to the created schema and tables to the LOADER role
        # This is specific to each Snowflake account so it should probably be
        #  handled on the DBT/Transform stage or not at all inside Meltano
        # try:
        #     db_name = os.environ.get('SNOWFLAKE_DB_NAME')
        #     connection = self.engine.connect()
        #     grant_stmt = f'GRANT USAGE ON SCHEMA {db_name}.{self.table.schema} TO ROLE LOADER;'
        #     connection.execute(grant_stmt)
        #     grant_stmt = f'GRANT SELECT ON ALL TABLES IN SCHEMA {db_name}.{self.table.schema} TO ROLE LOADER;'
        #     connection.execute(grant_stmt)
        # finally:
        #     connection.close()


    def load(self, df):
        if not df.empty:
            # Convert tricky NaN and NaT values to None
            #  so that they are properly stored as NULL values
            df2 = df.astype(object).where(pd.notnull(df), None)

            dfs_to_load: list = df2.to_dict(orient='records')

            print(f'Loading data to Snowflake for {self.entity_name}')
            try:
                connection = self.engine.connect()
                connection.execute(self.table.insert(), dfs_to_load)
            finally:
                connection.close()
        else:
            print(f'DataFrame {df} is empty -> skipping it')
