import os
import logging
import pandas as pd

from sqlalchemy import (
    create_engine,
    inspect,
    MetaData,
    Table,
    Column,
    String,
    Integer,
    Float,
)
from sqlalchemy.schema import CreateSchema

from snowflake.sqlalchemy import URL
from sqlalchemy.sql import select

if __name__ == "__main__":
    # Set proper Logging Level
    Log = logging.getLogger()
    level = logging.getLevelName("INFO")
    Log.setLevel(level)

    # Create engine for Snowflake
    engine = create_engine(
        URL(
            user=os.environ.get("SNOWFLAKE_USERNAME"),
            password=os.environ.get("SNOWFLAKE_PASSWORD"),
            account=os.environ.get("SNOWFLAKE_ACCOUNT_NAME"),
            database=os.environ.get("SNOWFLAKE_DB_NAME"),
            warehouse=os.environ.get("SNOWFLAKE_WAREHOUSE"),
        )
    )

    db_name = os.environ.get("SNOWFLAKE_DB_NAME")

    try:
        logging.info(
            "Testing that the connection to Snowflake has been properly set up."
        )

        logging.info("Connecting to Snowflake")
        connection = engine.connect()

        logging.info("Executing simple query")
        results = connection.execute("select current_version()").fetchone()
        logging.info(f"Current Snowflake version: {results[0]}")

        demo_metadata = MetaData()
        test_table = Table(
            "test_table",
            demo_metadata,
            Column("id", Integer, primary_key=True),
            Column("id2", String, primary_key=True),
            Column("name", String),
            Column("value", Float),
            schema="meltano_loader_tests",
        )

        logging.info("Checking if test schema and test table exist")

        inspector = inspect(engine)

        all_schema_names = inspector.get_schema_names()
        if not (test_table.schema in all_schema_names):
            logging.info(f"Schema {test_table.schema} does not exist -> creating it ")
            engine.execute(CreateSchema(test_table.schema))
        else:
            logging.info(f"Schema {test_table.schema} found!")

        all_table_names = inspector.get_table_names(test_table.schema)
        if not (test_table.name in all_table_names):
            logging.info(f"Table {test_table.name} does not exist -> creating it ")
            test_table.metadata.create_all(engine)
        else:
            logging.info(f"Table {test_table.name} found!")

        logging.info(f"Creating temporary table tmp_{test_table.name}")
        columns = [c.copy() for c in test_table.columns]
        tmp_table = Table(
            f"tmp_{test_table.name}",
            test_table.metadata,
            *columns,
            schema=test_table.schema,
        )

        tmp_table.drop(engine, checkfirst=True)
        tmp_table.create(engine)

        logging.info(f"Loading data to table {tmp_table.name}")

        test_data = [
            {"id": 1, "id2": "a", "name": "test1a", "value": 1.21},
            {"id": 1, "id2": "b", "name": "test1b", "value": 1.26},
            {"id": 2, "id2": "a", "name": "test2a", "value": 2.96},
            {"id": 3, "id2": "a", "name": "test3a", "value": 3.04},
            {"id": 3, "id2": "b", "name": "test3b", "value": 3.09},
            {"id": 4, "id2": "a", "name": "test4a", "value": 4.57},
        ]

        df = pd.DataFrame(data=test_data)
        dfs_to_load: list = df.to_dict(orient="records")

        connection.execute(tmp_table.insert(), dfs_to_load)

        logging.info(f"Merging {tmp_table.name} into {test_table.name}")

        merge_target = f"{test_table.schema}.{test_table.name}"
        merge_source = f"{test_table.schema}.{tmp_table.name}"

        joins = []
        for primary_key in test_table.primary_key:
            pk = primary_key.name
            joins.append(f"{merge_target}.{pk} = {merge_source}.{pk}")
        join_expr = " AND ".join(joins)

        attributes_target = []
        attributes_source = []
        update_sub_clauses = []

        for column in test_table.columns:
            attr = column.name
            attributes_target.append(attr)
            attributes_source.append(f"{merge_source}.{attr}")

            if attr not in test_table.primary_key:
                update_sub_clauses.append(f"{attr} = {merge_source}.{attr}")

        update_clause = ", ".join(update_sub_clauses)
        matched_clause = f"WHEN MATCHED THEN UPDATE SET {update_clause}"

        source_attributes = ", ".join(attributes_target)
        target_attributes = ", ".join(attributes_source)

        insert_clause = f"({source_attributes}) VALUES ({target_attributes})"
        not_matched_clause = f"WHEN NOT MATCHED THEN INSERT {insert_clause}"

        merge_stmt = f"MERGE INTO {merge_target} USING {merge_source} ON {join_expr} {matched_clause} {not_matched_clause}"
        connection.execute(merge_stmt)

        logging.info(f"Fetching back the data from table {tmp_table.name}")
        results = connection.execute(select([tmp_table]).order_by("id", "id2"))
        for row in results:
            logging.info(f"{row['id']} - {row['id2']} - {row['name']} - {row['value']}")
        results.close()

        logging.info(f"Fetching back the data from table {test_table.name}")
        results = connection.execute(select([test_table]).order_by("id", "id2"))
        for row in results:
            logging.info(f"{row['id']} - {row['id2']} - {row['name']} - {row['value']}")
        results.close()

        logging.info("Droping Schema and Tables")
        tmp_table.drop(engine)
        test_table.drop(engine)
        connection.execute(f"DROP SCHEMA {db_name}.{test_table.schema} CASCADE")

        # Facilitate Testing when the tables are not dropped
        # grant_stmt = f'GRANT USAGE ON SCHEMA {db_name}.{test_table.schema} TO ROLE LOADER;'
        # connection.execute(grant_stmt)
        # grant_stmt = f'GRANT SELECT ON ALL TABLES IN SCHEMA {db_name}.{test_table.schema} TO ROLE LOADER;'
        # connection.execute(grant_stmt)

        logging.info("Success!")
    finally:
        connection.close()
        engine.dispose()
