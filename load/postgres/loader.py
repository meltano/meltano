from typing import Generator, Dict

from sqlalchemy import create_engine
from pandas import DataFrame
from sqlalchemy.dialects import postgresql


class PostgresLoader:
    def __init__(self, connection_string, table):
        self.engine = create_engine(connection_string)
        self.table = table

    def schema_apply(self):
        if not self.engine.dialect.has_table(self.engine, self.table.name):
            # create table
            self.table.metadata.create_all(self.engine)
        else:
            pass
            print('Schema already exists skipping creation')

    def load(self, entities: Generator[Dict[str, DataFrame], None, None]):
        for entity in entities:
            for schema_name, df in entity.items():
                if not df.empty:
                    # df.to_sql(schema_name, con=self.engine, if_exists='append')
                    dfs_to_load: list = df.to_dict(orient='records')
                    insert_stmt = postgresql.insert(self.table).values(
                        dfs_to_load
                    )
                    insert_stmt = insert_stmt.on_conflict_do_update(
                        index_elements=['id'],
                        set_=insert_stmt.excluded._data  # overwrite the data with the new one
                    )
                    print(f'Loading df: {dfs_to_load}')
                    self.engine.execute(insert_stmt)
                else:
                    print(f'DataFrame {df} is empty -> skipping it')

# import os
# import yaml
# import psycopg2
# import psycopg2.sql
#
# from sqlalchemy import create_engine
# from pandas import DataFrame
# from configparser import ConfigParser
#
# from meltano.schema import Schema, Column, schema_apply
#
# from .utils.db import DB, MeltanoLoader
#
#
# class PostgresLoader(MeltanoLoader):
#     def __init__(self):
#         # Connection settings for the DB used
#         self.db_config = self.get_db_environment()
#
#         # Tables to be extracted
#         # List of {export_schema:, export_table:, export_table_primary_key:,
#         #          export_table_schema: Schema} dictionaries
#         self.tables = []
#
#         connection_string = self.get_connection_string()
#         self.connection = create_engine(connection_string)
#
#     # A MeltanoLoader Class should at least support
#     #  a schema_apply() and a load() method
#     def schema_apply(self, manifest):
#         """
#         Apply the schema for all the tables in self.tables to the EXPORT_DB
#         """
#
#         # Go through the DB manifest, generate the information needed for
#         #  the tables to be extracted and store everything in self.tables
#         self.process_db_manifest(manifest)
#
#         export_db = DB(self.db_config)
#
#         with export_db.open() as db:
#             for table_info in self.tables:
#                 schema_apply(db, table_info['export_table_schema'])
#
#     def load(self, entity_name: str, dataframe: DataFrame):
#         # Fetch the Table Info for the given entity
#         table_info = None
#         for table in self.tables:
#             if table['entity'] == entity_name:
#                 table_info = table
#                 break
#
#         if table_info is None:
#             raise ValueError("entity {} is not defined in the manifest".format(entity_name))
#
#         # Store the data provided in the dataframe in a temporary table
#         # This step is required as UPSERTING is not properly supported in sqlalchemy
#         dataframe.to_sql(
#             schema=table_info['export_schema'],
#             name='temp_{}'.format(table_info['export_table']),
#             con=self.connection,
#             if_exists='replace',
#             index=False
#         )
#
#         # Move the data from the temporary table to the entity table
#         # Use a custom PostgreSQL specific ON CONFLICT clause for making sure
#         # That the data are properly handled.
#
#         # Initialize the export DB connection
#         export_db = DB(self.db_config)
#
#         # generate once the columns used in insert/update clauses
#         target_columns = PostgresLoader.target_columns(table_info['export_table_schema'])
#
#         # Prepare the insert query template to be used
#         upsert_query = 'INSERT INTO {schema}.{table} ({columns}) \
#                         SELECT {columns} FROM {schema}.{tmp_table} \
#                         {upsert}'.format(
#             schema=table_info['export_schema'],
#             table=table_info['export_table'],
#             tmp_table='temp_{}'.format(table_info['export_table']),
#             columns=target_columns,
#             upsert=PostgresLoader.generate_upsert_clause(table_info),
#         )
#
#         with export_db.open() as dw, dw.cursor() as export_cursor:
#             export_cursor.execute(upsert_query)
#             dw.commit()
#
#             # Drop temporary table
#             drop_query = psycopg2.sql.SQL("DROP TABLE {0}.{1}").format(
#                 psycopg2.sql.Identifier(table_info['export_schema']),
#                 psycopg2.sql.Identifier('temp_{}'.format(table_info['export_table'])),
#             )
#             export_cursor.execute(drop_query)
#             dw.commit()
#
#     # Helper functions specific to this Loader
#     def get_db_environment(self):
#         myDir = os.path.dirname(os.path.abspath(__file__))
#         myPath = os.path.join(myDir, 'config', 'db_environment.conf')
#         EnvParser = ConfigParser()
#         EnvParser.read(myPath)
#
#         return {
#             'host': os.path.expandvars(EnvParser.get('POSTGRES', 'host')),
#             'port': os.path.expandvars(EnvParser.get('POSTGRES', 'port')),
#             'user': os.path.expandvars(EnvParser.get('POSTGRES', 'user')),
#             'password': os.path.expandvars(EnvParser.get('POSTGRES', 'pass')),
#             'database': os.path.expandvars(EnvParser.get('POSTGRES', 'database')),
#         }
#
#     def get_connection_string(self):
#         return 'postgresql://{username}:{password}@{host}:{port}/{db_name}'.format(
#             username=self.db_config['user'],
#             password=self.db_config['password'],
#             host=self.db_config['host'],
#             port=self.db_config['port'],
#             db_name=self.db_config['database'],
#         )
#
#     def process_db_manifest(self, db_manifest):
#         """
#         Read the db_manifest for the export source and store all the info for
#          the tables to be extracted in self.tables
#
#         Info stored for each table:
#            {export_schema:, export_table:, export_table_primary_key:,
#             export_table_schema: Schema}
#         """
#         myDir = os.path.dirname(os.path.abspath(__file__))
#         db_manifest = os.path.join(
#             myDir,
#             '../../',
#             '{}'.format(db_manifest),
#         )
#
#         with open(db_manifest, 'r') as f:
#             yaml_str = f.read()
#             raw = yaml.load(yaml_str)
#
#             for table, table_data in raw.items():
#                 table_info = {}
#
#                 table_info['entity'] = table
#                 table_info['export_schema'] = table_data['export_schema']
#                 table_info['export_table'] = table_data['export_table']
#                 table_info['export_table_primary_key'] = table_data['export_table_primary_key'].strip()
#
#                 columns = []
#
#                 for column, data_type in table_data['export_table_schema'].items():
#                     is_mapping_key = column == table_info['export_table_primary_key']
#
#                     column = Column(table_schema=table_data['export_schema'],
#                                     table_name=table_data['export_table'],
#                                     column_name=column,
#                                     data_type=data_type,
#                                     is_nullable=not is_mapping_key,
#                                     is_mapping_key=is_mapping_key)
#                     columns.append(column)
#
#                 table_info['export_table_schema'] = Schema(table_data['export_schema'], columns)
#
#                 self.tables.append(table_info)
#
#     def target_columns(schema):
#         """
#         Helper method that given a target schema generates the attributes as a
#         comma seperated string
#         """
#         return ','.join(map(str, [v.column_name for v in schema.columns.values()]))
#
#     def generate_upsert_clause(table_info):
#         """
#         Generate the ON CONFLICT() DO UPDATE SET clause for a table
#
#         Use the special excluded table alias to skip reiterating the values
#          and allow for mass insert with psycopg2.extras.execute_values()
#         """
#         update_clause = ''
#
#         for column in table_info['export_table_schema'].columns.values():
#             if column.column_name != table_info['export_table_primary_key']:
#                 if update_clause:
#                     update_clause += ', '
#                 update_clause += '{attr} = excluded.{attr}'.format(attr=column.column_name)
#
#         if update_clause:
#             upsert_clause = 'ON CONFLICT ({pkey}) DO UPDATE SET {update_clause}'.format(
#                 pkey=table_info['export_table_primary_key'],
#                 update_clause=update_clause,
#             )
#         else:
#             # Needed for single attribute tables (e.g. schema_migrations)
#             #  and join tables in the future (all attributes are unique)
#             upsert_clause = 'ON CONFLICT ({pkey}) DO NOTHING'.format(
#                 pkey=table_info['export_table_primary_key']
#             )
#
#         return upsert_clause
