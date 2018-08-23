from sqlalchemy import create_engine, MetaData, inspect
import json


class ExternalConnector:
    def __init__(self):
        self.connections = {}

    def add_connections(self, connections):
        print('adding connections...')
        for connection in connections:
            connection_name = connection['name']
            if connection_name not in connections:
                this_connection = {}
                if connection['dialect'] == 'postgresql':
                    psql_params = ['username', 'password', 'host', 'port', 'database']
                    user, pw, host, port db = [connection[param] for param in psql_params]
                    connection_url = f'postgresql+psycopg2://{user}:{pw}@{host}:{port}/{db}'
                    this_connection['connection_url'] = connection_url
                    this_connection['engine'] = create_engine(this_connection['connection_url'])
                    # inspection = inspect(this_connection['engine'])
                    # schemas = inspection.get_schema_names()
                    # for schema in schemas:
                    #   self.connections[schema] = {}
                    #   tables = inspection.get_table_names(schema)
                    #   for table in tables:
                    #     self.connections[schema][table] = {}
                    #     try:
                    #       columns = inspection.get_columns(table)
                    #       for column in columns:
                    #         self.connections[schema][table][column['name']] = str(column['type'])
                    #     except Exception as e:
                    #       continue
                    # meta = MetaData()
                    # meta.reflect(bind=this_connection['engine'], schema='analytics')
                    # this_connection['meta'] = meta
        return self.connections
