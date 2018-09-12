import os
import pandas as pd

from sqlalchemy import create_engine, inspect, Table
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


    def load(self, df):
        if not df.empty:
            # Convert tricky NaN and NaT values to None
            #  so that they are properly stored as NULL values
            df2 = df.astype(object).where(pd.notnull(df), None)

            dfs_to_load: list = df2.to_dict(orient='records')

            print(f'Loading data to Snowflake for {self.entity_name}')
            try:
                connection = self.engine.connect()

                if len(self.table.primary_key) > 0:
                    # We have to use Snowflake's Merge in order to Upsert

                    # Create Temporary table to load the data to
                    tmp_table = self.create_tmp_table()

                    # Insert data to temporary table
                    connection.execute(tmp_table.insert(), dfs_to_load)

                    # Merge Temporary Table into the Table we want to load data into
                    merge_stmt = self.generate_merge_stmt(tmp_table.name)
                    connection.execute(merge_stmt)

                    # Drop the Temporary Table
                    tmp_table.drop(self.engine)
                else:
                    # Just Insert (append) as no conflicts can arise
                    connection.execute(self.table.insert(), dfs_to_load)
            finally:
                connection.close()
        else:
            print(f'DataFrame {df} is empty -> skipping it')


    def create_tmp_table(self):
        columns = [c.copy() for c in self.table.columns]
        tmp_table = Table(
                        f'tmp_{self.table.name}',
                        self.table.metadata,
                        *columns,
                        schema=self.table.schema,
                        keep_existing=True,
                    )

        tmp_table.drop(self.engine, checkfirst=True)
        tmp_table.create(self.engine)

        return tmp_table


    def generate_merge_stmt(self, tmp_table_name):
        """
        Generate a merge statement for Merging a temporary table into the
          main table.

        The Structure of Merge in Snowflake is as follows:
          MERGE INTO <target_table> USING <source_table>
            ON <join_expression>
          WHEN MATCHED THEN UPDATE SET <update_clause>
          WHEN NOT MATCHED THEN INSERT (source_atts) VALUES {insert_clause}

        In this simple form, it has the same logic as UPSERT in Postgres
            INSERT ... ... ...
            ON CONFLICT ({pkey}) DO UPDATE SET {update_clause}
        """
        target_table = f'{self.table.schema}.{self.table.name}'
        source_table = f'{self.table.schema}.{tmp_table_name}'

        # Join using all primary keys
        joins = []
        for primary_key in self.table.primary_key:
            pk = primary_key.name
            joins.append(f'{target_table}.{pk} = {source_table}.{pk}')
        join_expr = ' AND '.join(joins)

        attributes_target = []
        attributes_source = []
        update_sub_clauses = []

        for column in self.table.columns:
            attr = column.name
            attributes_target.append(attr)
            attributes_source.append(f'{source_table}.{attr}')

            if attr not in self.table.primary_key:
                update_sub_clauses.append(f'{attr} = {source_table}.{attr}')

        update_clause = ', '.join(update_sub_clauses)
        matched_clause = f'WHEN MATCHED THEN UPDATE SET {update_clause}'

        source_attributes = ', '.join(attributes_target)
        target_attributes = ', '.join(attributes_source)

        insert_clause = f"({source_attributes}) VALUES ({target_attributes})"
        not_matched_clause = f'WHEN NOT MATCHED THEN INSERT {insert_clause}'

        merge_stmt = f'MERGE INTO {target_table} USING {source_table} ON {join_expr} {matched_clause} {not_matched_clause}'

        return merge_stmt


    def grant_privileges(self, role):
        # GRANT access to the created schema and tables to the provided role
        try:
            db_name = os.environ.get('SNOWFLAKE_DB_NAME')
            connection = self.engine.connect()
            grant_stmt = f'GRANT USAGE ON SCHEMA {db_name}.{self.table.schema} TO ROLE {role};'
            connection.execute(grant_stmt)
            grant_stmt = f'GRANT SELECT ON ALL TABLES IN SCHEMA {db_name}.{self.table.schema} TO ROLE {role};'
            connection.execute(grant_stmt)
        finally:
            connection.close()
