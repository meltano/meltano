import logging

from typing import Dict, List, Tuple, Set

from meltano.core.permissions.utils.error import SpecLoadingError
from meltano.core.permissions.utils.snowflake_connector import SnowflakeConnector


GRANT_ROLE_TEMPLATE = "GRANT ROLE {role_name} TO {type} {entity_name}"

REVOKE_ROLE_TEMPLATE = "REVOKE ROLE {role_name} FROM {type} {entity_name}"

GRANT_PRIVILEGES_TEMPLATE = (
    "GRANT {privileges} ON {resource_type} {resource_name} TO ROLE {role}"
)

REVOKE_PRIVILEGES_TEMPLATE = (
    "REVOKE {privileges} ON {resource_type} {resource_name} FROM ROLE {role}"
)

GRANT_ALL_PRIVILEGES_TEMPLATE = "GRANT {privileges} ON ALL {resource_type}s IN SCHEMA {resource_name} TO ROLE {role}"

GRANT_FUTURE_PRIVILEGES_TEMPLATE = "GRANT {privileges} ON FUTURE {resource_type}s IN SCHEMA {resource_name} TO ROLE {role}"

ALTER_USER_TEMPLATE = "ALTER USER {user_name} SET {privileges}"

GRANT_OWNERSHIP_TEMPLATE = (
    "GRANT OWNERSHIP"
    " ON {resource_type} {resource_name}"
    " TO ROLE {role_name} COPY CURRENT GRANTS"
)


class SnowflakeGrantsGenerator:
    def __init__(self, grants_to_role: Dict, roles_granted_to_user: Dict) -> None:
        self.grants_to_role = grants_to_role
        self.roles_granted_to_user = roles_granted_to_user

    def check_grant_to_role(
        self, role: str, privilege: str, entity_type: str, entity_name: str
    ) -> bool:
        """
        Check if <role> has been granted the privilege <privilege> on entity type
        <entity_type> with name <entity_name>.

        For example:
        check_grant_to_role('reporter', 'usage', 'database', 'analytics') -> True
        means that role reported has been granted the privilege to use the
        Database ANALYTICS on the Snowflake server.
        """
        if SnowflakeConnector.snowflaky(entity_name) in self.grants_to_role.get(
            role, {}
        ).get(privilege, {}).get(entity_type, []):
            return True
        else:
            return False

    def generate_grant_roles(
        self, entity_type: str, entity: str, config: str
    ) -> List[Dict]:
        """
        Generate the GRANT statements for both roles and users.

        entity_type: "users" or "roles"
        entity: the name of the entity (e.g. "yannis" or "reporter")
        config: the subtree for the entity as specified in the spec

        Returns the SQL commands generated as a list
        """
        sql_commands = []

        try:
            for member_role in config["member_of"]:
                granted_role = SnowflakeConnector.snowflaky(member_role)
                already_granted = False
                if (
                    entity_type == "users"
                    and granted_role in self.roles_granted_to_user[entity]
                ) or (
                    entity_type == "roles"
                    and self.check_grant_to_role(entity, "usage", "role", member_role)
                ):
                    already_granted = True

                sql_commands.append(
                    {
                        "already_granted": already_granted,
                        "sql": GRANT_ROLE_TEMPLATE.format(
                            role_name=SnowflakeConnector.snowflaky(member_role),
                            type=entity_type,
                            entity_name=SnowflakeConnector.snowflaky(entity),
                        ),
                    }
                )

            # Iterate through current state
            if entity_type == "users":
                for granted_role in self.roles_granted_to_user[entity]:
                    if granted_role not in config["member_of"]:
                        sql_commands.append(
                            {
                                "already_granted": False,
                                "sql": REVOKE_ROLE_TEMPLATE.format(
                                    role_name=SnowflakeConnector.snowflaky(
                                        granted_role
                                    ),
                                    type=entity_type,
                                    entity_name=SnowflakeConnector.snowflaky(entity),
                                ),
                            }
                        )

            if entity_type == "roles":
                for granted_role in (
                    self.grants_to_role.get(entity, {}).get("usage", {}).get("role", [])
                ):
                    if granted_role not in config["member_of"]:
                        sql_commands.append(
                            {
                                "already_granted": False,
                                "sql": REVOKE_ROLE_TEMPLATE.format(
                                    role_name=SnowflakeConnector.snowflaky(
                                        granted_role
                                    ),
                                    type=entity_type,
                                    entity_name=SnowflakeConnector.snowflaky(entity),
                                ),
                            }
                        )

        except KeyError:
            logging.debug(
                "`member_of` not found for {}, skipping generation of GRANT ROLE statements.".format(
                    entity
                )
            )

        return sql_commands

    def generate_grant_privileges_to_role(
        self, role: str, config: str, shared_dbs: Set
    ) -> List[Dict]:
        """
        Generate all the privilege granting and revocation
        statements for a role so Snowflake matches the spec.

        Most of the SQL command that will be generated are privileges granted to
        roles and this function orchestrates the whole process.

        role: the name of the role (e.g. "loader" or "reporter") the privileges
              are GRANTed to
        config: the subtree for the role as specified in the spec
        shared_dbs: a set of all the shared databases defined in the spec.
                    Used down the road by generate_database_grants() to also grant
                    "imported privileges" when access is granted to a shared DB.

        Returns the SQL commands generated as a list
        """
        sql_commands = []

        # Track all schemas that have been given access to (GRANT usage)
        # the given role. Used in order to recursively grant the required access
        # to schemas implicitly referenced when permissions are GRANTED for a
        # child Schema or Table.
        # Example: A role is given read access to table MY_DB.MY_SCHEMA.MY_TABLE
        # 1. In order to access MY_TABLE, the role has to be able to access MY_DB.MY_SCHEMA
        # 2. The script checks if usage on MY_SCHEMA has been granted to the role and
        #    assigns it to the role if not (and adds the DB to usage_granted["schemas"])
        # 4. Finally the requested permissions are GRANTED to role for MY_TABLE
        usage_granted = {"schemas": set()}

        try:
            warehouses = config["warehouses"]
            new_commands = self.generate_warehouse_grants(
                role=role, warehouses=warehouses
            )
            sql_commands.extend(new_commands)
        except KeyError:
            logging.debug(
                "`warehouses` not found for role {}, skipping generation of Warehouse GRANT statements.".format(
                    role
                )
            )

        databases = {
            "read": config.get("privileges", {}).get("databases", {}).get("read", []),
            "write": config.get("privileges", {}).get("databases", {}).get("write", []),
        }

        if len(databases.get("read")) == 0:
            logging.debug(
                "`privileges.databases.read` not found for role {}, skipping generation of database read level GRANT statements.".format(
                    role
                )
            )

        if len(databases.get("write")) == 0:
            logging.debug(
                "`privileges.databases.write` not found for role {}, skipping generation of database write level GRANT statements.".format(
                    role
                )
            )

        database_commands = self.generate_database_grants(
            role=role, databases=databases, shared_dbs=shared_dbs
        )
        sql_commands.extend(database_commands)

        try:
            for schema in config["privileges"]["schemas"]["read"]:
                new_commands, usage_granted = self.generate_schema_grants(
                    role=role,
                    schema=schema,
                    grant_type="read",
                    usage_granted=usage_granted,
                    shared_dbs=shared_dbs,
                )
                sql_commands.extend(new_commands)
        except KeyError:
            logging.debug(
                "`privileges.schemas.read` not found for role {}, skipping generation of SCHEMA read level GRANT statements.".format(
                    role
                )
            )

        try:
            for schema in config["privileges"]["schemas"]["write"]:
                new_commands, usage_granted = self.generate_schema_grants(
                    role=role,
                    schema=schema,
                    grant_type="write",
                    usage_granted=usage_granted,
                    shared_dbs=shared_dbs,
                )
                sql_commands.extend(new_commands)
        except KeyError:
            logging.debug(
                "`privileges.schemas.write` not found for role {}, skipping generation of SCHEMA write level GRANT statements.".format(
                    role
                )
            )

        try:
            for table in config["privileges"]["tables"]["read"]:
                new_commands, usage_granted = self.generate_table_and_view_grants(
                    role=role,
                    table=table,
                    grant_type="read",
                    usage_granted=usage_granted,
                    shared_dbs=shared_dbs,
                )
                sql_commands.extend(new_commands)
        except KeyError:
            logging.debug(
                "`privileges.tables.read` not found for role {}, skipping generation of TABLE read level GRANT statements.".format(
                    role
                )
            )

        try:
            for table in config["privileges"]["tables"]["write"]:
                new_commands, usage_granted = self.generate_table_and_view_grants(
                    role=role,
                    table=table,
                    grant_type="write",
                    usage_granted=usage_granted,
                    shared_dbs=shared_dbs,
                )
                sql_commands.extend(new_commands)
        except KeyError:
            logging.debug(
                "`privileges.tables.write` not found for role {}, skipping generation of TABLE write level GRANT statements.".format(
                    role
                )
            )

        return sql_commands

    def generate_warehouse_grants(self, role: str, warehouses: list) -> List[str]:
        """
        Generate the GRANT statements for Warehouse usage and operation.

        role: the name of the role the privileges are GRANTed to
        warehouses: list of warehouses for the specified role

        Returns the SQL command generated
        """
        sql_commands = []

        for warehouse in warehouses:
            if self.check_grant_to_role(role, "usage", "warehouse", warehouse):
                already_granted = True
            else:
                already_granted = False

            sql_commands.append(
                {
                    "already_granted": already_granted,
                    "sql": GRANT_PRIVILEGES_TEMPLATE.format(
                        privileges="usage",
                        resource_type="warehouse",
                        resource_name=SnowflakeConnector.snowflaky(warehouse),
                        role=SnowflakeConnector.snowflaky(role),
                    ),
                }
            )

            if self.check_grant_to_role(role, "operate", "warehouse", warehouse):
                already_granted = True
            else:
                already_granted = False

            sql_commands.append(
                {
                    "already_granted": already_granted,
                    "sql": GRANT_PRIVILEGES_TEMPLATE.format(
                        privileges="operate",
                        resource_type="warehouse",
                        resource_name=SnowflakeConnector.snowflaky(warehouse),
                        role=SnowflakeConnector.snowflaky(role),
                    ),
                }
            )

        for granted_warehouse in (
            self.grants_to_role.get(role, {}).get("usage", {}).get("warehouse", [])
        ):
            if granted_warehouse not in warehouses:
                sql_commands.append(
                    {
                        "already_granted": False,
                        "sql": REVOKE_PRIVILEGES_TEMPLATE.format(
                            privileges="usage",
                            resource_type="warehouse",
                            resource_name=SnowflakeConnector.snowflaky(
                                granted_warehouse
                            ),
                            role=SnowflakeConnector.snowflaky(role),
                        ),
                    }
                )

        for granted_warehouse in (
            self.grants_to_role.get(role, {}).get("operate", {}).get("warehouse", [])
        ):
            if granted_warehouse not in warehouses:
                sql_commands.append(
                    {
                        "already_granted": False,
                        "sql": REVOKE_PRIVILEGES_TEMPLATE.format(
                            privileges="operate",
                            resource_type="warehouse",
                            resource_name=SnowflakeConnector.snowflaky(
                                granted_warehouse
                            ),
                            role=SnowflakeConnector.snowflaky(role),
                        ),
                    }
                )

        return sql_commands

    def generate_database_grants(
        self, role: str, databases: Dict, shared_dbs: Set
    ) -> List[str]:
        """
        Generate the GRANT and REVOKE statements for Databases
        to align Snowflake with the spec.

        role: the name of the role the privileges are GRANTed to
        databases: list of databases (e.g. "raw")
        grant_type: What type of privileges are granted? One of {"read", "write", "revoke"}
        usage_granted: Passed by generate_grant_privileges_to_role() to track all
            all the entities a role has been granted access (usage) to.
        shared_dbs: a set of all the shared databases defined in the spec.

        Returns the SQL commands generated as a list
        """
        sql_commands = []

        read_privileges = "usage"
        write_privileges = "usage, monitor, create schema"

        for database in databases.get("read", []):
            already_granted = False
            if self.check_grant_to_role(role, "usage", "database", database):
                already_granted = True

            # If this is a shared database, we have to grant the "imported privileges"
            #  privilege to the user and skip granting the specific permissions as
            #  "Granting individual privileges on imported databases is not allowed."
            if database in shared_dbs:
                sql_commands.append(
                    {
                        "already_granted": already_granted,
                        "sql": GRANT_PRIVILEGES_TEMPLATE.format(
                            privileges="imported privileges",
                            resource_type="database",
                            resource_name=SnowflakeConnector.snowflaky(database),
                            role=SnowflakeConnector.snowflaky(role),
                        ),
                    }
                )
                continue

            sql_commands.append(
                {
                    "already_granted": already_granted,
                    "sql": GRANT_PRIVILEGES_TEMPLATE.format(
                        privileges=read_privileges,
                        resource_type="database",
                        resource_name=SnowflakeConnector.snowflaky(database),
                        role=SnowflakeConnector.snowflaky(role),
                    ),
                }
            )

        for database in databases.get("write", []):
            already_granted = False
            if (
                self.check_grant_to_role(role, "usage", "database", database)
                and self.check_grant_to_role(role, "monitor", "database", database)
                and self.check_grant_to_role(
                    role, "create schema", "database", database
                )
            ):
                already_granted = True

            # If this is a shared database, we have to grant the "imported privileges"
            #  privilege to the user and skip granting the specific permissions as
            #  "Granting individual privileges on imported databases is not allowed."
            if database in shared_dbs:
                sql_commands.append(
                    {
                        "already_granted": already_granted,
                        "sql": GRANT_PRIVILEGES_TEMPLATE.format(
                            privileges="imported privileges",
                            resource_type="database",
                            resource_name=SnowflakeConnector.snowflaky(database),
                            role=SnowflakeConnector.snowflaky(role),
                        ),
                    }
                )
                continue

            sql_commands.append(
                {
                    "already_granted": already_granted,
                    "sql": GRANT_PRIVILEGES_TEMPLATE.format(
                        privileges=write_privileges,
                        resource_type="database",
                        resource_name=SnowflakeConnector.snowflaky(database),
                        role=SnowflakeConnector.snowflaky(role),
                    ),
                }
            )

        for granted_database in (
            self.grants_to_role.get(role, {}).get("usage", {}).get("database", [])
        ):
            # If it's a shared database, only revoke imported
            # We'll only know if it's a shared DB based on the spec
            all_databases = databases.get("read", []) + databases.get("write", [])
            if granted_database not in all_databases and granted_database in shared_dbs:
                sql_commands.append(
                    {
                        "already_granted": False,
                        "sql": REVOKE_PRIVILEGES_TEMPLATE.format(
                            privileges="imported privileges",
                            resource_type="database",
                            resource_name=SnowflakeConnector.snowflaky(
                                granted_database
                            ),
                            role=SnowflakeConnector.snowflaky(role),
                        ),
                    }
                )
            # Can revoke all privileges b/c it will still execute even if it's a no-op
            elif granted_database not in all_databases:
                sql_commands.append(
                    {
                        "already_granted": False,
                        "sql": REVOKE_PRIVILEGES_TEMPLATE.format(
                            privileges=write_privileges,
                            resource_type="database",
                            resource_name=SnowflakeConnector.snowflaky(
                                granted_database
                            ),
                            role=SnowflakeConnector.snowflaky(role),
                        ),
                    }
                )

        return sql_commands

    def generate_schema_grants(
        self,
        role: str,
        schema: str,
        grant_type: str,
        usage_granted: Dict,
        shared_dbs: Set,
    ) -> Tuple[List[str], Dict]:
        """
        Generate the GRANT statements for schemas.

        role: the name of the role the privileges are GRANTed to
        schema: the name of the Schema (e.g. "raw.public")
        grant_type: What type of privileges are granted? One of {"read", "write"}
        usage_granted: Passed by generate_grant_privileges_to_role() to track all
            all the entities a role has been granted access (usage) to.
        shared_dbs: a set of all the shared databases defined in the spec.

        Returns the SQL commands generated and the updated usage_granted as a Tuple
        """
        sql_commands = []

        # Split the schema identifier into parts {DB_NAME}.{SCHEMA_NAME}
        #  so that we can check and use each one
        name_parts = schema.split(".")

        # Do nothing if this is a schema inside a shared database:
        #  "Granting individual privileges on imported databases is not allowed."
        if name_parts[0] in shared_dbs:
            return (sql_commands, usage_granted)

        if grant_type == "read":
            privileges = "usage"
        elif grant_type == "write":
            privileges = (
                "usage, monitor, create table,"
                " create view, create stage, create file format,"
                " create sequence, create function, create pipe"
            )
        else:
            raise SpecLoadingError(
                f"Wrong grant_type {spec_path} provided to generate_schema_grants()"
            )

        # Generate the information_schema identifier for that database
        #  in order to be able to filter it out
        info_schema = f"{name_parts[0]}.information_schema"

        schemas = []

        if name_parts[1] == "*":
            # If {DB_NAME}.* was provided as the schema identifier, we have to fetch
            #  each schema in database DB_NAME, so that we can grant privileges
            #  for each schema seperatelly.
            # We could GRANT {privileges} TO ALL SCHEMAS IN database
            #  but that would not allow us to know if a specific privilege has
            #  been already granted or not
            conn = SnowflakeConnector()
            db_schemas = conn.show_schemas(name_parts[0])
            for db_schema in db_schemas:
                if db_schema != info_schema:
                    schemas.append(db_schema)
        elif "*" in name_parts[1]:
            conn = SnowflakeConnector()
            db_schemas = conn.show_schemas(name_parts[0])
            for db_schema in db_schemas:
                schema_name = db_schema.split(".", 1)[1].lower()
                if schema_name.startswith(name_parts[1].split("*", 1)[0]):
                    schemas.append(db_schema)
        else:
            schemas = [schema]

        for db_schema in schemas:
            already_granted = False

            if (
                grant_type == "read"
                and self.check_grant_to_role(role, "usage", "schema", db_schema)
            ) or (
                grant_type == "write"
                and self.check_grant_to_role(role, "usage", "schema", db_schema)
                and self.check_grant_to_role(role, "monitor", "schema", db_schema)
                and self.check_grant_to_role(role, "create table", "schema", db_schema)
                and self.check_grant_to_role(role, "create view", "schema", db_schema)
                and self.check_grant_to_role(role, "create stage", "schema", db_schema)
                and self.check_grant_to_role(
                    role, "create file format", "schema", db_schema
                )
                and self.check_grant_to_role(
                    role, "create sequence", "schema", db_schema
                )
                and self.check_grant_to_role(
                    role, "create function", "schema", db_schema
                )
                and self.check_grant_to_role(role, "create pipe", "schema", db_schema)
            ):
                already_granted = True

            sql_commands.append(
                {
                    "already_granted": already_granted,
                    "sql": GRANT_PRIVILEGES_TEMPLATE.format(
                        privileges=privileges,
                        resource_type="schema",
                        resource_name=SnowflakeConnector.snowflaky(db_schema),
                        role=SnowflakeConnector.snowflaky(role),
                    ),
                }
            )

        usage_granted["schemas"].add(schema)

        return (sql_commands, usage_granted)

    def generate_table_and_view_grants(
        self,
        role: str,
        table: str,
        grant_type: str,
        usage_granted: Dict,
        shared_dbs: Set,
    ) -> Tuple[List[str], Dict]:
        """
        Generate the GRANT statements for tables and views.

        role: the name of the role the privileges are GRANTed to
        table: the name of the TABLE/VIEW (e.g. "raw.public.my_table")
        grant_type: What type of privileges are granted? One of {"read", "write"}
        usage_granted: Passed by generate_grant_privileges_to_role() to track all
            all the entities a role has been granted access (usage) to.
        shared_dbs: a set of all the shared databases defined in the spec.

        Returns the SQL commands generated and the updated usage_granted as a Tuple
        """
        sql_commands = []

        # Split the table identifier into parts {DB_NAME}.{SCHEMA_NAME}.{TABLE_NAME}
        #  so that we can check and use each one
        name_parts = table.split(".")

        # Do nothing if this is a table inside a shared database:
        #  "Granting individual privileges on imported databases is not allowed."
        if name_parts[0] in shared_dbs:
            return (sql_commands, usage_granted)

        if grant_type == "read":
            privileges = "select"
        elif grant_type == "write":
            privileges = "select, insert, update, delete, truncate, references"
        else:
            raise SpecLoadingError(
                f"Wrong grant_type {spec_path} provided to generate_table_and_view_grants()"
            )

        # Generate the information_schema identifier for that database
        #  in order to be able to filter it out
        info_schema = f"{name_parts[0]}.information_schema"

        # Gather the tables/views that privileges will be granted to
        tables = []
        views = []

        # List of all tables/views in schema
        table_list = []
        view_list = []

        schemas = []

        conn = SnowflakeConnector()

        if name_parts[1] == "*":
            # If {DB_NAME}.*.* was provided as the identifier, we have to fetch
            #  each schema in database DB_NAME, so that we can grant privileges
            #  for all tables in that schema
            # (You can not GRANT to all table with a wild card for the schema name)
            db_schemas = conn.show_schemas(name_parts[0])
            for schema in db_schemas:
                if schema != info_schema:
                    schemas.append(schema)
        elif "*" in name_parts[1]:
            conn = SnowflakeConnector()
            db_schemas = conn.show_schemas(name_parts[0])
            for db_schema in db_schemas:
                schema_name = db_schema.split(".", 1)[1].lower()
                if schema_name.startswith(name_parts[1].split("*", 1)[0]):
                    schemas.append(db_schema)
        else:
            schemas = [f"{name_parts[0]}.{name_parts[1]}"]

        for schema in schemas:
            # first check if the role has been granted usage on the schema
            # either directly or indirectly (by granting to DB.*)
            if (
                schema not in usage_granted["schemas"]
                and f"{name_parts[0]}.*" not in usage_granted["schemas"]
            ):
                new_commands, usage_granted = self.generate_schema_grants(
                    role=role,
                    schema=schema,
                    grant_type="read",
                    usage_granted=usage_granted,
                    shared_dbs=shared_dbs,
                )
                sql_commands.extend(new_commands)

            # And then add the tables for that schema to the tables[] and views[]
            #  that will be granted the permissions
            table_list.extend(conn.show_tables(schema=schema))
            view_list.extend(conn.show_views(schema=schema))

        if name_parts[2] == "*":
            # If *.* then you can grant all, grant future, and exit
            for schema in schemas:
                # Grant on ALL tables
                sql_commands.append(
                    {
                        "already_granted": False,
                        "sql": GRANT_ALL_PRIVILEGES_TEMPLATE.format(
                            privileges=privileges,
                            resource_type="table",
                            resource_name=SnowflakeConnector.snowflaky(schema),
                            role=SnowflakeConnector.snowflaky(role),
                        ),
                    }
                )

                # Grant on ALL views
                sql_commands.append(
                    {
                        "already_granted": False,
                        "sql": GRANT_ALL_PRIVILEGES_TEMPLATE.format(
                            privileges=privileges,
                            resource_type="view",
                            resource_name=SnowflakeConnector.snowflaky(schema),
                            role=SnowflakeConnector.snowflaky(role),
                        ),
                    }
                )

                # Grant future on all tables
                sql_commands.append(
                    {
                        "already_granted": False,
                        "sql": GRANT_FUTURE_PRIVILEGES_TEMPLATE.format(
                            privileges=privileges,
                            resource_type="table",
                            resource_name=SnowflakeConnector.snowflaky(schema),
                            role=SnowflakeConnector.snowflaky(role),
                        ),
                    }
                )
                # Grant future on all views
                sql_commands.append(
                    {
                        "already_granted": False,
                        "sql": GRANT_FUTURE_PRIVILEGES_TEMPLATE.format(
                            privileges=privileges,
                            resource_type="view",
                            resource_name=SnowflakeConnector.snowflaky(schema),
                            role=SnowflakeConnector.snowflaky(role),
                        ),
                    }
                )

            return (sql_commands, usage_granted)

        else:
            # Only one table/view to be granted permissions to
            if table in table_list:
                tables = [table]
            if table in view_list:
                views = [table]

        # And then grant privileges to all tables in that schema
        for db_table in tables:
            already_granted = False
            if (
                grant_type == "read"
                and self.check_grant_to_role(role, "select", "table", db_table)
            ) or (
                grant_type == "write"
                and self.check_grant_to_role(role, "select", "table", db_table)
                and self.check_grant_to_role(role, "insert", "table", db_table)
                and self.check_grant_to_role(role, "update", "table", db_table)
                and self.check_grant_to_role(role, "delete", "table", db_table)
                and self.check_grant_to_role(role, "truncate", "table", db_table)
                and self.check_grant_to_role(role, "references", "table", db_table)
            ):
                already_granted = True

            # And then grant privileges to the db_table
            sql_commands.append(
                {
                    "already_granted": already_granted,
                    "sql": GRANT_PRIVILEGES_TEMPLATE.format(
                        privileges=privileges,
                        resource_type="table",
                        resource_name=SnowflakeConnector.snowflaky(db_table),
                        role=SnowflakeConnector.snowflaky(role),
                    ),
                }
            )

        for db_view in views:
            already_granted = False
            if (
                grant_type == "read"
                and self.check_grant_to_role(role, "select", "view", db_view)
            ) or (
                grant_type == "write"
                and self.check_grant_to_role(role, "select", "view", db_view)
                and self.check_grant_to_role(role, "insert", "view", db_view)
                and self.check_grant_to_role(role, "update", "view", db_view)
                and self.check_grant_to_role(role, "delete", "view", db_view)
                and self.check_grant_to_role(role, "truncate", "view", db_view)
                and self.check_grant_to_role(role, "references", "view", db_view)
            ):
                already_granted = True

            # And then grant privileges to the db_view
            sql_commands.append(
                {
                    "already_granted": already_granted,
                    "sql": GRANT_PRIVILEGES_TEMPLATE.format(
                        privileges=privileges,
                        resource_type="view",
                        resource_name=SnowflakeConnector.snowflaky(db_view),
                        role=SnowflakeConnector.snowflaky(role),
                    ),
                }
            )

        return (sql_commands, usage_granted)

    def generate_alter_user(self, user: str, config: str) -> List[Dict]:
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
                {
                    "already_granted": False,
                    "sql": ALTER_USER_TEMPLATE.format(
                        user_name=SnowflakeConnector.snowflaky(user),
                        privileges=", ".join(alter_privileges),
                    ),
                }
            )

        return sql_commands

    def generate_grant_ownership(self, role: str, config: str) -> List[Dict]:
        """
        Generate the GRANT ownership statements for databases, schemas and tables.

        role: the name of the role (e.g. "loader") ownership will be GRANTed to
        config: the subtree for the role as specified in the spec

        Returns the SQL commands generated as a List
        """
        sql_commands = []

        try:
            for database in config["owns"]["databases"]:
                if self.check_grant_to_role(role, "ownership", "database", database):
                    already_granted = True
                else:
                    already_granted = False

                sql_commands.append(
                    {
                        "already_granted": already_granted,
                        "sql": GRANT_OWNERSHIP_TEMPLATE.format(
                            resource_type="database",
                            resource_name=SnowflakeConnector.snowflaky(database),
                            role_name=SnowflakeConnector.snowflaky(role),
                        ),
                    }
                )
        except KeyError:
            logging.debug(
                "`owns.databases` not found for role {}, skipping generation of database ownership statements.".format(
                    role
                )
            )

        try:
            for schema in config["owns"]["schemas"]:
                name_parts = schema.split(".")
                info_schema = f"{name_parts[0]}.information_schema"

                schemas = []

                if name_parts[1] == "*":
                    conn = SnowflakeConnector()
                    db_schemas = conn.show_schemas(name_parts[0])

                    for db_schema in db_schemas:
                        if db_schema != info_schema:
                            schemas.append(db_schema)
                else:
                    schemas = [schema]

                for db_schema in schemas:
                    if self.check_grant_to_role(role, "ownership", "schema", db_schema):
                        already_granted = True
                    else:
                        already_granted = False

                    sql_commands.append(
                        {
                            "already_granted": already_granted,
                            "sql": GRANT_OWNERSHIP_TEMPLATE.format(
                                resource_type="schema",
                                resource_name=SnowflakeConnector.snowflaky(db_schema),
                                role_name=SnowflakeConnector.snowflaky(role),
                            ),
                        }
                    )
        except KeyError:
            logging.debug(
                "`owns.schemas` not found for role {}, skipping generation of SCHEMA ownership statements.".format(
                    role
                )
            )

        try:
            # Gather the tables that ownership will be granted to
            tables = []

            for table in config["owns"]["tables"]:
                name_parts = table.split(".")
                info_schema = f"{name_parts[0]}.information_schema"

                if name_parts[2] == "*":
                    schemas = []
                    conn = SnowflakeConnector()

                    if name_parts[1] == "*":
                        db_schemas = conn.show_schemas(name_parts[0])

                        for schema in db_schemas:
                            if schema != info_schema:
                                schemas.append(schema)
                    else:
                        schemas = [f"{name_parts[0]}.{name_parts[1]}"]

                    for schema in schemas:
                        tables.extend(conn.show_tables(schema=schema))
                else:
                    tables = [table]

            # And then grant ownership to all tables
            for db_table in tables:
                if self.check_grant_to_role(role, "ownership", "table", db_table):
                    already_granted = True
                else:
                    already_granted = False

                sql_commands.append(
                    {
                        "already_granted": already_granted,
                        "sql": GRANT_OWNERSHIP_TEMPLATE.format(
                            resource_type="table",
                            resource_name=SnowflakeConnector.snowflaky(db_table),
                            role_name=SnowflakeConnector.snowflaky(role),
                        ),
                    }
                )
        except KeyError:
            logging.debug(
                "`owns.tables` not found for role {}, skipping generation of TABLE ownership statements.".format(
                    role
                )
            )

        return sql_commands
