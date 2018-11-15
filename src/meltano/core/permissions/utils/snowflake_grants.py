from typing import Dict, List, Tuple, Set

from meltano.core.permissions.utils.snowflake_connector import SnowflakeConnector


Privileges_TEMPLATE = (
    "GRANT {privileges} ON {resource_type} {resource_name} TO ROLE {role}"
)


def generate_warehouse_grants(role: str, warehouse: str) -> str:
    sql_grant = Privileges_TEMPLATE.format(
        privileges="USAGE",
        resource_type="WAREHOUSE",
        resource_name=warehouse,
        role=role,
    )

    return sql_grant


def generate_database_grants(
    role: str, database: str, grant_type: str, usage_granted: Dict, shared_dbs: Set
) -> Tuple[List[str], Dict]:
    sql_commands = []

    # If this is a shared database, we have to first
    if database in shared_dbs:
        sql_commands.append(
            Privileges_TEMPLATE.format(
                privileges="IMPORTED PRIVILEGES",
                resource_type="DATABASE",
                resource_name=database,
                role=role,
            )
        )

    # And then grant privileges to the database
    if grant_type == "read":
        privileges = "USAGE"
    elif grant_type == "write":
        privileges = "USAGE, MONITOR, CREATE SCHEMA"
    else:
        raise SpecLoadingError(
            f"Wrong grant_type {spec_path} provided to generate_database_grants()"
        )

    sql_commands.append(
        Privileges_TEMPLATE.format(
            privileges=privileges,
            resource_type="DATABASE",
            resource_name=database,
            role=role,
        )
    )

    usage_granted["databases"].add(database.upper())

    return (sql_commands, usage_granted)


def generate_schema_grants(
    role: str, schema: str, grant_type: str, usage_granted: Dict, shared_dbs: Set
) -> Tuple[List[str], Dict]:
    sql_commands = []

    if grant_type == "read":
        privileges = "USAGE"
    elif grant_type == "write":
        privileges = (
            "USAGE, MONITOR, CREATE TABLE,"
            " CREATE VIEW, CREATE STAGE, CREATE FILE FORMAT,"
            " CREATE SEQUENCE, CREATE FUNCTION, CREATE PIPE"
        )
    else:
        raise SpecLoadingError(
            f"Wrong grant_type {spec_path} provided to generate_schema_grants()"
        )

    # Split the schema identifier into parts {DB_NAME}.{SCHEMA_NAME}
    #  so that we can check and use each one
    name_parts = schema.split(".")

    # Before assigning privileges to a schema, check if
    #  usage to the database has been granted and
    # if not grant usage first to the database
    if name_parts[0].upper() not in usage_granted["databases"]:
        new_commands, usage_granted = generate_database_grants(
            role=role,
            database=name_parts[0],
            grant_type="read",
            usage_granted=usage_granted,
            shared_dbs=shared_dbs,
        )
        sql_commands.extend(new_commands)

    if name_parts[1] == "*":
        sql_commands.append(
            Privileges_TEMPLATE.format(
                privileges=privileges,
                resource_type="ALL SCHEMAS IN DATABASE",
                resource_name=name_parts[0],
                role=role,
            )
        )
    else:
        sql_commands.append(
            Privileges_TEMPLATE.format(
                privileges=privileges,
                resource_type="SCHEMA",
                resource_name=schema,
                role=role,
            )
        )

    usage_granted["schemas"].add(schema.upper())

    return (sql_commands, usage_granted)


def generate_table_grants(
    role: str, table: str, grant_type: str, usage_granted: Dict, shared_dbs: Set
) -> Tuple[List[str], Dict]:
    sql_commands = []

    if grant_type == "read":
        privileges = "SELECT"
    elif grant_type == "write":
        privileges = "SELECT, INSERT, UPDATE, DELETE, TRUNCATE, REFERENCES"
    else:
        raise SpecLoadingError(
            f"Wrong grant_type {spec_path} provided to generate_table_grants()"
        )

    # Split the table identifier into parts {DB_NAME}.{SCHEMA_NAME}.{TABLE_NAME}
    #  so that we can check and use each one
    name_parts = table.split(".")

    # Generate the INFORMATION_SCHEMA identifier for that database
    #  in order to be able to filter it out
    info_schema = f"{name_parts[0].upper()}.INFORMATION_SCHEMA"

    # Before assigning privileges to a Table, check if
    #  usage to the database has been granted and
    # if not grant usage first to the database
    # Schemas will be checked as we generate them
    if name_parts[0].upper() not in usage_granted["databases"]:
        new_commands, usage_granted = generate_database_grants(
            role=role,
            database=name_parts[0],
            grant_type="read",
            usage_granted=usage_granted,
            shared_dbs=shared_dbs,
        )
        sql_commands.extend(new_commands)

    if name_parts[2] == "*":
        schemas = []

        if name_parts[1] == "*":
            # If {DB_NAME}.*.* was provided as the identifier, we have to fetch
            #  each schema in database DB_NAME, so that we can grant privileges
            #  for all tables in that schema
            # (You can not GRANT to all table with a wild card for the schema name)
            conn = SnowflakeConnector()
            db_schemas = conn.show_schemas(name_parts[0])
            for schema in db_schemas:
                if schema != info_schema:
                    schemas.append(schema)
        else:
            schemas = [f"{name_parts[0]}.{name_parts[1]}"]

        for schema in schemas:
            # first check if the role has been granted usage on the schema
            # either directly or indirectly (by granting to DB.*)
            if (
                schema.upper() not in usage_granted["schemas"]
                and f"{name_parts[0].upper()}.*" not in usage_granted["schemas"]
            ):
                new_commands, usage_granted = generate_schema_grants(
                    role=role,
                    schema=schema,
                    grant_type="read",
                    usage_granted=usage_granted,
                    shared_dbs=shared_dbs,
                )
                sql_commands.extend(new_commands)

            # And then grant privileges to all tables in that schema
            sql_commands.append(
                Privileges_TEMPLATE.format(
                    privileges=privileges,
                    resource_type="ALL TABLES IN SCHEMA",
                    resource_name=schema,
                    role=role,
                )
            )
    else:
        # Check if the role has been granted usage on the schema
        schema = f"{name_parts[0]}.{name_parts[1]}"
        if (
            schema.upper() not in usage_granted["schemas"]
            and f"{name_parts[0].upper()}.*" not in usage_granted["schemas"]
        ):
            new_commands, usage_granted = generate_schema_grants(
                role=role,
                schema=schema,
                grant_type="read",
                usage_granted=usage_granted,
                shared_dbs=shared_dbs,
            )
            sql_commands.extend(new_commands)

        # And then grant privileges to the table
        sql_commands.append(
            Privileges_TEMPLATE.format(
                privileges=privileges,
                resource_type="TABLE",
                resource_name=table,
                role=role,
            )
        )

    return (sql_commands, usage_granted)
