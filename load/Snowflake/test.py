import os
import pandas as pd

from sqlalchemy import create_engine, inspect, MetaData, Table, Column, String, Integer
from sqlalchemy.schema import CreateSchema

from snowflake.sqlalchemy import URL
from sqlalchemy.sql import select

if __name__ == '__main__':
    engine = create_engine(
        URL(
#                'snowflake://{user}:{password}@{account}/{database}'.format(
            user=os.environ.get('SNOWFLAKE_USERNAME'),
            password=os.environ.get('SNOWFLAKE_PASSWORD'),
            account=os.environ.get('SNOWFLAKE_ACCOUNT_NAME'),
            database = os.environ.get('SNOWFLAKE_DB_NAME'),
            warehouse=os.environ.get('SNOWFLAKE_WAREHOUSE'),
        )
    )

    db_name = os.environ.get('SNOWFLAKE_DB_NAME')

    try:
        print()
        print('Testing that the connection to Snowflake has been properly set up.')

        print()
        print('Connecting to Snowflake')
        connection = engine.connect()

        print()
        print('Executing simple query')
        results = connection.execute('select current_version()').fetchone()
        print(f'Current Snowflake version: {results[0]}')

        demo_metadata = MetaData()
        test_table = Table(
            'test_table',  # Name of the table
            demo_metadata,
            Column('id', Integer, primary_key=True),
            Column('name', String),
            schema='meltano_loader_tests'
        )

        print()
        print('Checking if test schema and test table exist')

        inspector = inspect(engine)

        all_schema_names = inspector.get_schema_names()
        if not (test_table.schema in all_schema_names):
            print(f"Schema {test_table.schema} does not exist -> creating it ")
            engine.execute(CreateSchema(test_table.schema))

            # For testing
            # grant_stmt = f'GRANT USAGE ON SCHEMA {db_name}.{test_table.schema} TO ROLE LOADER;'
            # connection.execute(grant_stmt)
        else:
            print(f"Schema {test_table.schema} found!")

        all_table_names = inspector.get_table_names(test_table.schema)
        if not (test_table.name in all_table_names):
            print(f"Table {test_table.name} does not exist -> creating it ")
            test_table.metadata.create_all(engine)

            # For testing
            # grant_stmt = f'GRANT SELECT ON TABLE {db_name}.{test_table.schema}.{test_table.name} TO ROLE LOADER;'
            # connection.execute(grant_stmt)
        else:
            print(f"Table {test_table.name} found!")

        print()
        print(f'Loading data to table {test_table.name}')

        test_data = [
            {'id': 1, 'name': 'test1'},
            {'id': 2, 'name': 'test2'},
            {'id': 3, 'name': 'test3'},
            {'id': 4, 'name': 'test4'},
            {'id': 5, 'name': 'test5'},
        ]

        df = pd.DataFrame(data=test_data)
        dfs_to_load: list = df.to_dict(orient='records')

        connection.execute(test_table.insert(), dfs_to_load)

        print()
        print(f'Fetching back the data from table {test_table.name}')
        results = connection.execute( select([test_table]) )
        for row in results:
            print(f"{row['id']} - {row['name']}")
        results.close()

        print()
        print('Droping Schema and Table')
        test_table.drop(engine)
        connection.execute(f'DROP SCHEMA {db_name}.{test_table.schema} CASCADE')

        print('Success!')
    finally:
        connection.close()
        engine.dispose()
