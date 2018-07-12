import psycopg2
import psycopg2.sql
import re
import json
import logging


def read_header(file):
    file.seek(0)
    return next(file).rstrip().lower().replace('"', '')


def identifiers(*exprs):
    """
    expr => psycopg2.sql.Identifier(expr)
    [exprs] => [psycopg2.sql.Identifier(expr, ...)]
    """
    if len(exprs) == 1:
        return psycopg2.sql.Identifier(exprs[0])

    return [psycopg2.sql.Identifier(expr) for expr in exprs]


def create_tmp_table(db_conn, table_schema, table_name):
    tmp_table_name = "_".join((table_name, 'tmp'))

    schema, table, tmp_table = identifiers(table_schema,
                                           table_name,
                                           tmp_table_name)

    # Create temp table
    cursor = db_conn.cursor()
    create_table = psycopg2.sql.SQL(
        "CREATE TEMP TABLE {0} AS SELECT * FROM {1}.{2} LIMIT 0"
    ).format(
        tmp_table,
        schema,
        table,
    )
    cursor.execute(create_table)
    logging.debug(create_table.as_string(cursor))

    return tmp_table_name


def update_stmt(action, columns):
    """
    Return the INSERT INTO ... ON CONFLICT ... DO <update_stmt>

    action -> NOTHING|UPDATE
    [columns] ⇒ "<column>=excluded.<column>,.."
    """
    action = action.upper()
    if action not in {"NOTHING", "UPDATE"}:
        raise ValueError("action must either be `NOTHING` or `UPDATE`: received {}".format(action))

    if action == "NOTHING":
        return action

    # Update primary table
    set_cols = {col: '.'.join(['excluded', col]) for col in columns}
    rep_colon = re.sub(':', '=', json.dumps(set_cols))
    rep_brace = re.sub('{|}', '', rep_colon)
    set_cols = re.sub('\.', '"."', rep_brace)

    return "UPDATE SET {}".format(set_cols)


def csv_options_stmt(**options):
    """
    Return the statement to be included in the COPY ... WITH (<csv_options_stmt>)

    The following interpolation are available:
      - schema
      - table
      - columns
    """
    defaults = {
        'format': "csv",
    }

    components = [
        " ".join((option.upper(), str(value))) \
        for option, value in {**defaults, **options}.items()
    ]

    return ", ".join(components)


def csv_to_temp_table(db_conn, csv_path, *,
                      table_schema,
                      table_name,
                      csv_options={}):
    with open(csv_path, 'r') as csv_file:
        csv_file_to_temp_table(db_conn, csv_file,
                               table_schema=table_schema,
                               table_name=table_name,
                               csv_options=csv_options)


def csv_file_to_temp_table(db_conn, csv_file, *,
                           table_schema,
                           table_name,
                           csv_options={}):
    with db_conn.cursor() as cursor:
        header = read_header(csv_file)
        tmp_table_name = create_tmp_table(db_conn,
                                          table_schema,
                                          table_name)

        schema, tmp_schema, table, tmp_table = identifiers(table_schema,
                                                           "pg_temp",
                                                           table_name,
                                                           tmp_table_name)

        copy_stmt = """
                    COPY {schema}.{table} ({columns}) FROM STDIN WITH (%s)
                    """ % csv_options_stmt(**csv_options)
        copy_query = psycopg2.sql.SQL(
            copy_stmt
        ).format(
            schema=tmp_schema,
            table=tmp_table,
            columns=psycopg2.sql.SQL(', ').join(identifiers(*header.split(','))),
        )
        logging.debug(copy_query.as_string(cursor))
        cursor.copy_expert(sql=copy_query, file=csv_file)
        db_conn.commit()

        return tmp_table_name


def upsert_to_db_from_csv(db_conn, csv_path, *,
                         primary_key,
                         table_schema,
                         table_name,
                         csv_options={}):
    """
    Write to Postgres DB from a CSV

    :param db_conn: psycopg2 database connection
    :param csv_path: path of CSV that you wish to write to table of same name
    :return:
    """
    return integrate_csv(db_conn, csv_path,
                         table_schema=table_schema,
                         table_name=table_name,
                         primary_key=primary_key,
                         csv_options=csv_options,
                         update_action="UPDATE")


def write_to_db_from_csv(db_conn, csv_path, *,
                         primary_key,
                         table_schema,
                         table_name,
                         csv_options={}):
    """
    Append to Postgres DB from a CSV

    :param db_conn: psycopg2 database connection
    :param csv_path: path of CSV that you wish to write to table of same name
    :return:
    """
    return integrate_csv(db_conn, csv_path,
                         table_schema=table_schema,
                         table_name=table_name,
                         primary_key=primary_key,
                         csv_options=csv_options,
                         update_action="NOTHING")


def integrate_csv(db_conn, csv_path, *,
                  primary_key,
                  table_schema,
                  table_name,
                  csv_options={},
                  update_action="NOTHING"):
    """
    Upsert to Postgres DB from a CSV

    :param db_conn: psycopg2 database connection
    :param csv_path: name of CSV that you wish to write to table of same name
    :return:
    """
    logging.info("Importing {} as {}...".format(csv_path, table_name))
    with open(csv_path, 'r') as csv_file:
        return integrate_csv_file(db_conn, csv_file,
                                  table_schema=table_schema,
                                  table_name=table_name,
                                  primary_key=primary_key,
                                  csv_options=csv_options,
                                  update_action="NOTHING")


def integrate_csv_file(db_conn, csv_file, *,
                       primary_key,
                       table_schema,
                       table_name,
                       csv_options={},
                       update_action="NOTHING"):
    try:
        tmp_table_name = csv_file_to_temp_table(db_conn, csv_file,
                                                table_schema=table_schema,
                                                table_name=table_name,
                                                csv_options=csv_options)

        header = read_header(csv_file)
        schema, tmp_schema, table, tmp_table = identifiers(table_schema,
                                                           "pg_temp",
                                                           table_name,
                                                           tmp_table_name)

        update_columns = [col for col in header.split(',') if col != primary_key]
        query_stmt = """
                     INSERT INTO {schema}.{table} ({columns})
                     SELECT {columns} FROM {tmp_schema}.{tmp_table}
                     ON CONFLICT ({primary_key}) DO %s
                     """ % update_stmt(update_action, update_columns)

        update_query = psycopg2.sql.SQL(
            query_stmt
        ).format(
            schema=schema,
            table=table,
            columns=psycopg2.sql.SQL(', ').join(identifiers(*header.split(','))),
            tmp_schema=tmp_schema,
            tmp_table=tmp_table,
            primary_key=identifiers(primary_key),
        )

        with db_conn.cursor() as cursor:
            cursor.execute(update_query)
            logging.debug(update_query.as_string(cursor))
            db_conn.commit()

            # Drop temporary table
            drop_query = psycopg2.sql.SQL("DROP TABLE {0}.{1}").format(
                tmp_schema,
                tmp_table,
            )

            logging.debug(drop_query.as_string(cursor))
            cursor.execute(drop_query)
            db_conn.commit()

    except psycopg2.Error as err:
        logging.error(err)
