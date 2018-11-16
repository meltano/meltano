from typing import Dict, List, Tuple, Set

from meltano.core.permissions.utils.snowflake_connector import SnowflakeConnector


GRANT_ROLE_TEMPLATE = "GRANT ROLE {role_name} TO {type} {entity_name}"

GRANT_PRIVILEGES_TEMPLATE = (
    "GRANT {privileges} ON {resource_type} {resource_name} TO ROLE {role}"
)

ALTER_USER_TEMPLATE = "ALTER USER {user_name} SET {privileges}"

GRANT_OWNERSHIP_TEMPLATE = (
    "GRANT OWNERSHIP"
    " ON {resource_type} {resource_name}"
    " TO ROLE {role_name} COPY CURRENT GRANTS"
)


def generate_grant_roles(entity_type: str, entity: str, config: str) -> List[str]:
    """
    Generate the GRANT statements for both roles and users.

    entity_type: "USER" or "ROLE"
    entity: the name of the entity (e.g. "yannis" or "REPORTER")
    config: the subtree for the entity as specified in the spec

    Returns the SQL commands generated as a list
    """
    sql_commands = []

    if "member_of" in config:
        for member_role in config["member_of"]:
            sql_commands.append(
                GRANT_ROLE_TEMPLATE.format(
                    role_name=member_role, type=entity_type, entity_name=entity
                )
            )

    return sql_commands


def generate_grant_privileges_to_role(
    role: str, config: str, shared_dbs: Set
) -> List[str]:
    """
    Generate all the privilege granting statements for a role.

    Most of the SQL command that will be generated are privileges granted to
    roles and this function orchestrates the whole process

    role: the name of the role (e.g. "LOADER" or "REPORTER") the privileges
          are GRANTed to
    config: the subtree for the role as specified in the spec
    shared_dbs: a set of all the shared databases defined in the spec.
                Used down the road by generate_database_grants() to also grant
                "IMPORTED PRIVILEGES" when access is granted to a shared DB.

    Returns the SQL commands generated as a list
    """
    sql_commands = []

    # Track all the DBs and schemas that have been given access to (GRANT USAGE)
    # the given role. Used in order to recursively grant the required access
    # to DBs or schemas implicetly reference when permissions are GRANTED for a
    # child Schema or Table.
    # Example: A role is given read access to table MY_DB.MY_SCHEMA.MY_TABLE
    # 1. In order to access MY_TABLE, the role has to be able to access MY_DB.MY_SCHEMA
    # 2. The script checks if USAGE on MY_DB has been granted to the role and
    #    assigns it to the role if not (and adds the DB to usage_granted["databases"])
    # 3. The same for the schema MY_SCHEMA
    # 4. Finaly the requested permissions are GRANTED to role for MY_TABLE
    usage_granted = {"databases": set(), "schemas": set()}

    if "warehouses" in config:
        for warehouse in config["warehouses"]:
            sql_commands.append(generate_warehouse_grants(role, warehouse))

    if "privileges" in config:
        if "databases" in config["privileges"]:
            if "read" in config["privileges"]["databases"]:
                for database in config["privileges"]["databases"]["read"]:
                    new_commands, usage_granted = generate_database_grants(
                        role=role,
                        database=database,
                        grant_type="read",
                        usage_granted=usage_granted,
                        shared_dbs=shared_dbs,
                    )
                    sql_commands.extend(new_commands)

            if "write" in config["privileges"]["databases"]:
                for database in config["privileges"]["databases"]["write"]:
                    new_commands, usage_granted = generate_database_grants(
                        role=role,
                        database=database,
                        grant_type="write",
                        usage_granted=usage_granted,
                        shared_dbs=shared_dbs,
                    )
                    sql_commands.extend(new_commands)

        if "schemas" in config["privileges"]:
            if "read" in config["privileges"]["schemas"]:
                for schema in config["privileges"]["schemas"]["read"]:
                    new_commands, usage_granted = generate_schema_grants(
                        role=role,
                        schema=schema,
                        grant_type="read",
                        usage_granted=usage_granted,
                        shared_dbs=shared_dbs,
                    )
                    sql_commands.extend(new_commands)

            if "write" in config["privileges"]["schemas"]:
                for schema in config["privileges"]["schemas"]["write"]:
                    new_commands, usage_granted = generate_schema_grants(
                        role=role,
                        schema=schema,
                        grant_type="write",
                        usage_granted=usage_granted,
                        shared_dbs=shared_dbs,
                    )
                    sql_commands.extend(new_commands)

        if "tables" in config["privileges"]:
            if "read" in config["privileges"]["tables"]:
                for table in config["privileges"]["tables"]["read"]:
                    new_commands, usage_granted = generate_table_grants(
                        role=role,
                        table=table,
                        grant_type="read",
                        usage_granted=usage_granted,
                        shared_dbs=shared_dbs,
                    )
                    sql_commands.extend(new_commands)

            if "write" in config["privileges"]["tables"]:
                for table in config["privileges"]["tables"]["write"]:
                    new_commands, usage_granted = generate_table_grants(
                        role=role,
                        table=table,
                        grant_type="write",
                        usage_granted=usage_granted,
                        shared_dbs=shared_dbs,
                    )
                    sql_commands.extend(new_commands)

    return sql_commands


def generate_warehouse_grants(role: str, warehouse: str) -> str:
    """
    Generate the GRANT statements for Warehouse usage (only one type at the moment).

    role: the name of the role the privileges are GRANTed to
    warehouse: the name of the warehouse (e.g. "transforming")

    Returns the SQL command generated
    """
    sql_grant = GRANT_PRIVILEGES_TEMPLATE.format(
        privileges="USAGE",
        resource_type="WAREHOUSE",
        resource_name=warehouse,
        role=role,
    )

    return sql_grant


def generate_database_grants(
    role: str, database: str, grant_type: str, usage_granted: Dict, shared_dbs: Set
) -> Tuple[List[str], Dict]:
    """
    Generate the GRANT statements for Databases.

    role: the name of the role the privileges are GRANTed to
    database: the name of the database (e.g. "RAW")
    grant_type: What type of privileges are granted? One of {"read", "write"}
    usage_granted: Passed by generate_grant_privileges_to_role() to track all
        all the entities a role has been granted access (USAGE) to.
    shared_dbs: a set of all the shared databases defined in the spec.

    Returns the SQL commands generated and the updated usage_granted as a Tuple
    """
    sql_commands = []

    # If this is a shared database, we have to first grant the
    #  "IMPORTED PRIVILEGES" privilege to the user.
    if database in shared_dbs:
        sql_commands.append(
            GRANT_PRIVILEGES_TEMPLATE.format(
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
        GRANT_PRIVILEGES_TEMPLATE.format(
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
    """
    Generate the GRANT statements for SCHEMAs.

    role: the name of the role the privileges are GRANTed to
    schema: the name of the Schema (e.g. "RAW.PUBLIC")
    grant_type: What type of privileges are granted? One of {"read", "write"}
    usage_granted: Passed by generate_grant_privileges_to_role() to track all
        all the entities a role has been granted access (USAGE) to.
    shared_dbs: a set of all the shared databases defined in the spec.

    Returns the SQL commands generated and the updated usage_granted as a Tuple
    """
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
            GRANT_PRIVILEGES_TEMPLATE.format(
                privileges=privileges,
                resource_type="ALL SCHEMAS IN DATABASE",
                resource_name=name_parts[0],
                role=role,
            )
        )
    else:
        sql_commands.append(
            GRANT_PRIVILEGES_TEMPLATE.format(
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
    """
    Generate the GRANT statements for TABLEs.

    role: the name of the role the privileges are GRANTed to
    table: the name of the TABLE (e.g. "RAW.PUBLIC.MY_TABLE")
    grant_type: What type of privileges are granted? One of {"read", "write"}
    usage_granted: Passed by generate_grant_privileges_to_role() to track all
        all the entities a role has been granted access (USAGE) to.
    shared_dbs: a set of all the shared databases defined in the spec.

    Returns the SQL commands generated and the updated usage_granted as a Tuple
    """
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
                GRANT_PRIVILEGES_TEMPLATE.format(
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
            GRANT_PRIVILEGES_TEMPLATE.format(
                privileges=privileges,
                resource_type="TABLE",
                resource_name=table,
                role=role,
            )
        )

    return (sql_commands, usage_granted)


def generate_alter_user(user: str, config: str) -> List[str]:
    """
    Generate the ALTER statements for USERs.

    user: the name of the USER
    config: the subtree for the user as specified in the spec

    Returns the SQL commands generated as a List
    """
    sql_commands = []

    alter_privileges = []

    if "can_login" in config:
        if config["can_login"]:
            alter_privileges.append("DISABLED = FALSE")
        else:
            alter_privileges.append("DISABLED = TRUE")

    if alter_privileges:
        sql_commands.append(
            ALTER_USER_TEMPLATE.format(
                user_name=user, privileges=", ".join(alter_privileges)
            )
        )

    return sql_commands


def generate_grant_ownership(role: str, config: str) -> List[str]:
    """
    Generate the GRANT OWNERSHIP statements for DATABASEs, SCHEMAs and TABLEs.

    role: the name of the role (e.g. "LOADER") OWNERSHIP will be GRANTed to
    config: the subtree for the role as specified in the spec

    Returns the SQL commands generated as a List
    """
    sql_commands = []

    if "owns" in config:
        if "databases" in config["owns"]:
            for database in config["owns"]["databases"]:
                sql_commands.append(
                    GRANT_OWNERSHIP_TEMPLATE.format(
                        resource_type="DATABASE", resource_name=database, role_name=role
                    )
                )

        if "schemas" in config["owns"]:
            for schema in config["owns"]["schemas"]:
                name_parts = schema.split(".")
                info_schema = f"{name_parts[0].upper()}.INFORMATION_SCHEMA"

                if name_parts[1] == "*":
                    schemas = []
                    conn = SnowflakeConnector()
                    db_schemas = conn.show_schemas(name_parts[0])

                    for db_schema in db_schemas:
                        if db_schema != info_schema:
                            schemas.append(db_schema)

                    for db_schema in schemas:
                        sql_commands.append(
                            GRANT_OWNERSHIP_TEMPLATE.format(
                                resource_type="SCHEMA",
                                resource_name=db_schema,
                                role_name=role,
                            )
                        )
                else:
                    sql_commands.append(
                        GRANT_OWNERSHIP_TEMPLATE.format(
                            resource_type="SCHEMA", resource_name=schema, role_name=role
                        )
                    )

        if "tables" in config["owns"]:
            for table in config["owns"]["tables"]:
                name_parts = table.split(".")
                info_schema = f"{name_parts[0].upper()}.INFORMATION_SCHEMA"

                if name_parts[2] == "*":
                    schemas = []

                    if name_parts[1] == "*":
                        conn = SnowflakeConnector()
                        db_schemas = conn.show_schemas(name_parts[0])

                        for schema in db_schemas:
                            if schema != info_schema:
                                schemas.append(schema)
                    else:
                        schemas = [f"{name_parts[0]}.{name_parts[1]}"]

                    for schema in schemas:
                        sql_commands.append(
                            GRANT_OWNERSHIP_TEMPLATE.format(
                                resource_type="ALL TABLES IN SCHEMA",
                                resource_name=schema,
                                role_name=role,
                            )
                        )
                else:
                    sql_commands.append(
                        GRANT_OWNERSHIP_TEMPLATE.format(
                            resource_type="TABLE", resource_name=table, role_name=role
                        )
                    )

    return sql_commands
