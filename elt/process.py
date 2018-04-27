import psycopg2
import psycopg2.sql
import re
import json


def write_to_db_from_csv(db_conn, csv_file, *,
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

            cursor = db_conn.cursor()

            copy_query = psycopg2.sql.SQL(
                "COPY {0}.{1} ({2}) FROM STDIN WITH DELIMITER AS ',' NULL AS 'null' CSV"
            ).format(
                schema,
                table,
                psycopg2.sql.SQL(', ').join(
                    psycopg2.sql.Identifier(n) for n in header.split(',')
                )
            )
            print(copy_query.as_string(cursor))
            print("Copying file")
            cursor.copy_expert(sql=copy_query, file=file)
            db_conn.commit()
            cursor.close()
        except psycopg2.Error as err:
            print(err)


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
            tmp_table = psycopg2.sql.Identifier(table_name + "_tmp")

            # Create temp table
            create_table = psycopg2.sql.SQL("CREATE TEMP TABLE {0} AS SELECT * FROM {1}.{2} LIMIT 0").format(
                tmp_table,
                schema,
                table,
            )
            cursor.execute(create_table)
            print(create_table.as_string(cursor))
            db_conn.commit()

            # Import into TMP Table
            copy_query = psycopg2.sql.SQL("COPY {0}.{1} ({2}) FROM STDIN WITH DELIMITER AS ',' NULL AS 'null' CSV").format(
                psycopg2.sql.Identifier("pg_temp"),
                tmp_table,
                psycopg2.sql.SQL(', ').join(
                    psycopg2.sql.Identifier(n) for n in header.split(','),
                ),
            )
            print(copy_query.as_string(cursor))
            print("Copying File")
            cursor.copy_expert(sql=copy_query, file=file)
            db_conn.commit()

            # Update primary table
            split_header = [col for col in header.split(
                ',') if col != primary_key]
            set_cols = {col: '.'.join(['excluded', col])
                        for col in split_header}
            rep_colon = re.sub(':', '=', json.dumps(set_cols))
            rep_brace = re.sub('{|}', '', rep_colon)
            set_strings = re.sub('\.', '"."', rep_brace)

            update_query = psycopg2.sql.SQL("INSERT INTO {0}.{1} ({2}) SELECT {2} FROM {3}.{4} ON CONFLICT ({5}) DO UPDATE SET {6}").format(
                schema,
                table,
                psycopg2.sql.SQL(', ').join(
                    psycopg2.sql.Identifier(n) for n in header.split(',')
                ),
                psycopg2.sql.Identifier("pg_temp"),
                tmp_table,
                psycopg2.sql.Identifier(primary_key),
                psycopg2.sql.SQL(set_strings),
            )
            cursor.execute(update_query)
            print(update_query.as_string(cursor))
            db_conn.commit()

            # Drop temporary table
            drop_query = psycopg2.sql.SQL("DROP TABLE {0}.{1}").format(
                psycopg2.sql.Identifier("pg_temp"),
                tmp_table,
            )

            print(drop_query.as_string(cursor))
            cursor.execute(drop_query)
            db_conn.commit()
            cursor.close()

        except psycopg2.Error as err:
            print(err)
