import os
import yaml
import logging
import psycopg2
import psycopg2.sql
import time

from configparser import ConfigParser
from datetime import datetime

from elt.schema import Schema, Column, schema_apply
from elt.job import Job, State

from utils.db import DB

class DBExtractor:
    JOB_VERSION = 1
    DATE_MIN = datetime(2013, 1, 1)

    def __init__(self, db_manifest, days_to_run=None, hours_to_run=None):
        # Days/Hours in the past the extractor will fetch
        if days_to_run and int(days_to_run) > 0:
            self.days_to_run = int(days_to_run)
        else:
            self.days_to_run = 10

        if hours_to_run and int(hours_to_run) > 0:
            self.hours_to_run = int(hours_to_run)
        else:
            self.hours_to_run = 8

        # Connection settings for each DB used
        self.db_env_parser = self.get_db_environment()

        # Tables to be extracted
        # List of {import_db:, import_query:, export_db:, export_schema:, export_table:,
        #          export_table_primary_key:, export_table_schema: Schema} dictionaries
        self.tables = []

        # Go through the DB manifest, generate the information needed for
        #  the tables to be extracted and store everything in self.tables
        self.process_db_manifest(db_manifest)


    def get_db_environment(self):
        myDir = os.path.dirname(os.path.abspath(__file__))
        myPath = os.path.join(myDir, 'config', 'db_environment.conf')
        EnvParser = ConfigParser()
        EnvParser.read(myPath)
        return EnvParser


    def get_db_creds(self, db_name):
        return {
            'host': os.path.expandvars(self.db_env_parser.get(db_name, 'host')),
            'port': os.path.expandvars(self.db_env_parser.get(db_name, 'port')),
            'user': os.path.expandvars(self.db_env_parser.get(db_name, 'user')),
            'password': os.path.expandvars(self.db_env_parser.get(db_name, 'pass')),
            'database': os.path.expandvars(self.db_env_parser.get(db_name, 'database')),
        }


    def process_db_manifest(self, db_manifest):
        """
        Read the db_manifest for the export source and store all the info for
         the tables to be extracted in self.tables

        Info stored for each table:
           {import_db:, import_query:, export_db:, export_schema:,
            export_table:, export_table_primary_key:, export_table_schema: Schema}
        """
        myDir = os.path.dirname(os.path.abspath(__file__))
        db_manifest = os.path.join(
                        myDir,
                        'config',
                        '{}_db_manifest.yaml'.format(db_manifest),
                      )

        with open(db_manifest, 'r') as f:
            yaml_str = f.read()
            raw = yaml.load(yaml_str)

            for table, table_data in raw.items():
                table_info = {}

                table_info['import_db'] = table_data['import_db']
                table_info['import_query'] = (table_data['import_query'].format(
                                                    days=self.days_to_run,
                                                    hours=self.hours_to_run,
                                                )
                                             ).strip()
                table_info['export_db'] = table_data['export_db']
                table_info['export_schema'] = table_data['export_schema']
                table_info['export_table'] = table_data['export_table']
                table_info['export_table_primary_key'] = table_data['export_table_primary_key'].strip()

                columns = []

                for column, data_type in table_data['export_table_schema'].items():
                    is_mapping_key = column == table_info['export_table_primary_key']

                    column = Column(table_schema=table_data['export_schema'],
                                    table_name=table_data['export_table'],
                                    column_name=column,
                                    data_type=data_type,
                                    is_nullable=not is_mapping_key,
                                    is_mapping_key=is_mapping_key)
                    columns.append(column)

                table_info['export_table_schema'] = Schema(table_data['export_schema'], columns)

                self.tables.append(table_info)


    def schema_apply(self):
        """
        Apply the schema for all the tables in self.tables to the EXPORT_DB
        """
        db_config = self.get_db_creds('EXPORT_DB')
        export_db = DB(db_config)

        with export_db.open() as db:
            schema_apply(db, Job.describe_schema())

            for table_info in self.tables:
                schema_apply(db, table_info['export_table_schema'])


    def prepare_db_connections(self):
        """
        Create one DB object for each import database we are going to read from
        """
        import_dbs = {}

        for table_info in self.tables:
            if table_info['import_db'] not in import_dbs:
                db_config = self.get_db_creds(table_info['import_db'])
                import_dbs[table_info['import_db']] = DB(db_config)

        return import_dbs


    def export(self):
        """
        Export the data for each table defined in self.tables and import them
        in EXPORT_DB
        """

        # Fetch jason strings as strings in order to easily store them back
        # Otherwise, psycopg2 converts them to python objects and we would have
        #  to run additional check during load and convert them back to strings
        psycopg2.extras.register_default_json(loads=lambda x: x)

        import_dbs = self.prepare_db_connections()

        db_config = self.get_db_creds('EXPORT_DB')
        export_db = DB(db_config)

        for table_info in self.tables:
            logging.info("Exporting data for : {}".format(table_info['export_table']))

            import_db = import_dbs[table_info['import_db']]

            # generate once the columns used for filtering during export and for
            #  inserting data in the DW to make sure that the order is the same
            target_columns = DBExtractor.target_columns(table_info['export_table_schema'])

            # Use a server side cursor as we may have results with millions of records
            # Server side cursors only send what is requested through fetchmany()
            #  and not the whole result at once
            # Choose a unique cursor name with seconds level precision just in
            #  case multiple pipelines run at once
            cursor_unique_name = 'cursor_{}_{}'.format(
                table_info['export_table'],
                int(time.time()),
            )

            with import_db.open() as import_connection:

                # Make the import cursor readonly
                import_connection.set_session(readonly=True)

                with import_connection.cursor(
                    cursor_unique_name,
                    cursor_factory=psycopg2.extras.DictCursor
                ) as import_cursor:

                    # track iterations and total rows exported for logging them
                    iteration_no = 0
                    total_rows_exported = 0

                    # Number of rows to fetch from the backend at each network roundtrip
                    # Increased to 5K from the default 2K in order to balance between
                    #  performance and stable excecution.
                    import_cursor.itersize = 5000

                    # generate the export query with only the target columns
                    #  selected (filter out unwanted or PII)
                    query = DBExtractor.filter_query(
                                table_info['import_query'],
                                target_columns
                            )

                    # Prepare the insert query template to be used in the loop
                    insert_query = DBExtractor.generate_insert_query(table_info, target_columns)

                    insert_template = DBExtractor.generate_template(table_info['export_table_schema'])

                    # Execute the query and start fetching the data in 50K batches
                    import_cursor.execute(query)

                    result = import_cursor.fetchmany(5000)

                    while result:
                        iteration_no += 1
                        total_rows_exported += import_cursor.rowcount
                        logging.info('    iteration #{0:4} | {1:8} total rows'.format(
                                iteration_no,
                                total_rows_exported
                            )
                        )

                        # One connection per iteration in order to commit every 50K
                        #  records fetched and be able to handle imported tables
                        #  with more than a million records in the result
                        with export_db.open() as dw, dw.cursor() as export_cursor:
                            psycopg2.extras.execute_values (
                                export_cursor,
                                insert_query,
                                result,
                                template='({})'.format(insert_template),
                                page_size=5000,
                            )

                        result = import_cursor.fetchmany(5000)


    def target_columns(schema):
        """
        Helper method that given a target schema generates the attributes as a
        comma seperated string
        """
        return ','.join(map(str, [v.column_name for v in schema.columns.values()]))


    def filter_query(query, filtered_columns):
        """
        Helper method that given an SQL query as string and a target schema
        extends the query to select only the attributes from the target schema
        """
        return psycopg2.sql.SQL(
            'SELECT {filtered_columns} FROM ({import_query}) as tmp'.format(
                filtered_columns=filtered_columns,
                import_query=query
            )
        )


    def generate_insert_query(table_info, columns):
        """
        Helper method that given a table_info entry generates the base INSERT SQL
        """
        return 'INSERT INTO {schema}.{table} ({columns}) values %s {upsert}'.format(
                    schema=table_info['export_schema'],
                    table=table_info['export_table'],
                    columns=columns,
                    upsert=DBExtractor.generate_upsert_clause(table_info),
               )

    def generate_upsert_clause(table_info):
        """
        Generate the ON CONFLICT() DO UPDATE SET clause for a table

        Use the special excluded table alias to skip reiterating the values
         and allow for mass insert with psycopg2.extras.execute_values()
        """
        update_clause = ''

        for column in table_info['export_table_schema'].columns.values():
            if column.column_name != table_info['export_table_primary_key']:
                if update_clause:
                    update_clause += ', '
                update_clause += '{attr} = excluded.{attr}'.format(attr=column.column_name)

        if update_clause:
            upsert_clause = 'ON CONFLICT ({pkey}) DO UPDATE SET {update_clause}'.format(
                pkey=table_info['export_table_primary_key'],
                update_clause=update_clause,
            )
        else:
            # Needed for single attribute tables (e.g. schema_migrations)
            #  and join tables in the future (all attributes are unique)
            upsert_clause = 'ON CONFLICT ({pkey}) DO NOTHING'.format(
                pkey=table_info['export_table_primary_key']
            )

        return upsert_clause


    def generate_template(schema):
        """
        Helper method that given a target schema generates the template used by
        execute_values() with the proper order of provided attributes
        """
        return ','.join(map(str, ['%({})s'.format(v.column_name) for v in schema.columns.values()]))
