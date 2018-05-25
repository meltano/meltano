import psycopg2
import psycopg2.sql
import re
import json
import logging


def write_to_db_from_csv(db_conn, csv_file, *,
                         primary_key,
                         table_schema,
                         table_name):
    """
    Write to Postgres DB from a CSV

    :param db_conn: psycopg2 database connection
    :param csv_file: name of CSV that you wish to write to table of same name
    :return:
    """
    with open(csv_file, 'r') as file:
        try:
            # Get header row, remove new lines, lowercase
            header = next(file).rstrip().lower()
            schema = psycopg2.sql.Identifier(table_schema)
            table = psycopg2.sql.Identifier(table_name)
            tmp_table = psycopg2.sql.Identifier(table_name + "_tmp")
            cursor = db_conn.cursor()

            # Create temp table
            create_table = psycopg2.sql.SQL("CREATE TEMP TABLE {0} AS SELECT * FROM {1}.{2} LIMIT 0").format(
                tmp_table,
                schema,
                table,
            )
            cursor.execute(create_table)
            logging.debug(create_table.as_string(cursor))
            db_conn.commit()

            # insert into temp table
            copy_query = psycopg2.sql.SQL(
                "COPY {0}.{1} ({2}) FROM STDIN WITH DELIMITER AS ',' NULL AS 'null' CSV"
            ).format(
                psycopg2.sql.Identifier("pg_temp"),
                tmp_table,
                psycopg2.sql.SQL(', ').join(
                    psycopg2.sql.Identifier(n) for n in header.split(',')
                )
            )
            logging.debug(copy_query.as_string(cursor))
            logging.info("Copying file")
            cursor.copy_expert(sql=copy_query, file=file)

            # migrate to real table
            update_query = psycopg2.sql.SQL("INSERT INTO {0}.{1} ({2}) SELECT {2} FROM {3}.{4} ON CONFLICT ({5}) DO NOTHING").format(
                schema,
                table,
                psycopg2.sql.SQL(', ').join(
                    psycopg2.sql.Identifier(n) for n in header.split(',')
                ),
                psycopg2.sql.Identifier("pg_temp"),
                tmp_table,
                psycopg2.sql.Identifier(primary_key),
            )
            cursor.execute(update_query)
            logging.debug(update_query.as_string(cursor))
            db_conn.commit()

            # Drop temporary table
            drop_query = psycopg2.sql.SQL("DROP TABLE {0}.{1}").format(
                psycopg2.sql.Identifier("pg_temp"),
                tmp_table,
            )
            logging.debug(drop_query.as_string(cursor))
            cursor.execute(drop_query)
            db_conn.commit()

            cursor.close()
        except psycopg2.Error as err:
            logging.error(err)


def create_tmp_table(db_conn, table_schema, table_name):
    tmp_table_name = "_".join((table_name, 'tmp'))

    schema = psycopg2.sql.Identifier(table_schema)
    table = psycopg2.sql.Identifier(table_name)
    tmp_table = psycopg2.sql.Identifier(tmp_table_name)

    # Create temp table
    cursor = db_conn.cursor()
    create_table = psycopg2.sql.SQL("CREATE TEMP TABLE {0} AS SELECT * FROM {1}.{2} LIMIT 0").format(
        tmp_table,
        schema,
        table,
        )
    cursor.execute(create_table)
    logging.debug(create_table.as_string(cursor))

    return tmp_table_name


def update_set_stmt(columns):
    """
    [columns] ⇒ "<column>=excluded.<column>,.."
    """
    # Update primary table
    set_cols = {col: '.'.join(['excluded', col]) for col in columns}
    rep_colon = re.sub(':', '=', json.dumps(set_cols))
    rep_brace = re.sub('{|}', '', rep_colon)
    set_cols = re.sub('\.', '"."', rep_brace)
    return set_cols


def upsert_to_db_from_csv(db_conn, csv_file, *,
                          primary_key,
                          table_schema,
                          table_name):
    """
    Upsert to Postgres DB from a CSV

    :param db_conn: psycopg2 database connection
    :param csv_file: name of CSV that you wish to write to table of same name
    :return:
    """
    with open(csv_file, 'r') as file:
        try:
            # Get header row, remove new lines, lowercase
            header = next(file).rstrip().lower()
            cursor = db_conn.cursor()

            schema = psycopg2.sql.Identifier(table_schema)
            table = psycopg2.sql.Identifier(table_name)
            tmp_table = psycopg2.sql.Identifier(create_tmp_table(db_conn,
                                                                  table_schema,
                                                                  table_name))

            # Import into TMP Table
            copy_query = psycopg2.sql.SQL("COPY {0}.{1} ({2}) FROM STDIN WITH DELIMITER AS ',' NULL AS 'null' CSV").format(
                psycopg2.sql.Identifier("pg_temp"),
                tmp_table,
                psycopg2.sql.SQL(', ').join(
                    psycopg2.sql.Identifier(n) for n in header.split(','),
                ),
            )
            logging.debug(copy_query.as_string(cursor))
            logging.info("Copying File")
            cursor.copy_expert(sql=copy_query, file=file)
            db_conn.commit()

            update_columns = [col for col in header.split(',') if col != primary_key]
            update_query = psycopg2.sql.SQL("INSERT INTO {0}.{1} ({2}) SELECT {2} FROM {3}.{4} ON CONFLICT ({5}) DO UPDATE SET {6}").format(
                schema,
                table,
                psycopg2.sql.SQL(', ').join(
                    psycopg2.sql.Identifier(n) for n in header.split(',')
                ),
                psycopg2.sql.Identifier("pg_temp"),
                tmp_table,
                psycopg2.sql.Identifier(primary_key),
                psycopg2.sql.SQL(update_set_stmt(update_columns)),
            )
            cursor.execute(update_query)
            logging.debug(update_query.as_string(cursor))
            db_conn.commit()

            # Drop temporary table
            drop_query = psycopg2.sql.SQL("DROP TABLE {0}.{1}").format(
                psycopg2.sql.Identifier("pg_temp"),
                tmp_table,
            )

            logging.debug(drop_query.as_string(cursor))
            cursor.execute(drop_query)
            db_conn.commit()
            cursor.close()

        except psycopg2.Error as err:
            logging.error(err)
