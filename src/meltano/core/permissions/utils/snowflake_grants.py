import logging
import re

from typing import Dict, List, Tuple, Set, Any

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

GRANT_FUTURE_SCHEMAS_PRIVILEGES_TEMPLATE = (
    "GRANT {privileges} ON FUTURE SCHEMAS IN DATABASE {resource_name} TO ROLE {role}"
)

GRANT_FUTURE_PRIVILEGES_TEMPLATE = "GRANT {privileges} ON FUTURE {resource_type}s IN SCHEMA {resource_name} TO ROLE {role}"

REVOKE_FUTURE_DB_OBJECT_PRIVILEGES_TEMPLATE = (
    "REVOKE {privileges} ON FUTURE SCHEMAS IN DATABASE {resource_name} FROM ROLE {role}"
)

REVOKE_FUTURE_SCHEMA_OBJECT_PRIVILEGES_TEMPLATE = "REVOKE {privileges} ON FUTURE {resource_type}s IN SCHEMA {resource_name} FROM ROLE {role}"

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
        <entity_type> with name <entity_name>. First checks if it is a future grant
        since snowflaky will format the future grants wrong - i.e. <table> is a part
        of the fully qualified name for a future table grant.

        For example:
        check_grant_to_role('reporter', 'usage', 'database', 'analytics') -> True
        means that role reported has been granted the privilege to use the
        Database ANALYTICS on the Snowflake server.
        """
        future = True if re.search(r"<(table|view|schema)>", entity_name) else False

        grants = (
            self.grants_to_role.get(role, {}).get(privilege, {}).get(entity_type, [])
        )

        if future and entity_name in grants:
            return True
        elif not future and SnowflakeConnector.snowflaky(entity_name) in grants:
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

        if entity_type == "users":
            grant_type = "user"
        if entity_type == "roles":
            grant_type = "role"

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
                            type=grant_type,
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
                                    type=grant_type,
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
                                    type=grant_type,
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
        self, role: str, config: str, shared_dbs: Set, spec_dbs: Set
    ) -> List[Dict]:
        """
        Generate all the privilege granting and revocation
        statements for a role so Snowflake matches the spec.

        Most of the SQL command that will be generated are privileges granted to
        roles and this function orchestrates the whole process.

        role: the name of the role (e.g. "loader" or "reporter") the privileges
              are granted to and revoked from
        config: the subtree for the role as specified in the spec
        shared_dbs: a set of all the shared databases defined in the spec.
                    Used down the road by generate_database_grants() to also grant
                    "imported privileges" when access is granted to a shared DB.
        spec_dbs: a set of all the databases defined in the spec. This is used in revoke
                  commands to validate revocations are only for spec'd databases

        Returns the SQL commands generated as a list
        """
        sql_commands = []

        # TODO Convert to simpler format
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

        # Databases
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
            role=role, databases=databases, shared_dbs=shared_dbs, spec_dbs=spec_dbs
        )
        sql_commands.extend(database_commands)

        # Schemas
        schemas = {
            "read": config.get("privileges", {}).get("schemas", {}).get("read", []),
            "write": config.get("privileges", {}).get("schemas", {}).get("write", []),
        }

        if len(schemas.get("read")) == 0:
            logging.debug(
                "`privileges.schemas.read` not found for role {}, skipping generation of schemas read level GRANT statements.".format(
                    role
                )
            )

        if len(schemas.get("write")) == 0:
            logging.debug(
                "`privileges.schemas.write` not found for role {}, skipping generation of schemas write level GRANT statements.".format(
                    role
                )
            )

        schema_commands = self.generate_schema_grants(
            role=role, schemas=schemas, shared_dbs=shared_dbs, spec_dbs=spec_dbs
        )
        sql_commands.extend(schema_commands)

        # Tables
        tables = {
            "read": config.get("privileges", {}).get("tables", {}).get("read", []),
            "write": config.get("privileges", {}).get("tables", {}).get("write", []),
        }

        if len(tables.get("read")) == 0:
            logging.debug(
                "`privileges.tables.read` not found for role {}, skipping generation of tables read level GRANT statements.".format(
                    role
                )
            )

        if len(tables.get("write")) == 0:
            logging.debug(
                "`privileges.tables.write` not found for role {}, skipping generation of tables write level GRANT statements.".format(
                    role
                )
            )

        table_commands = self.generate_table_and_view_grants(
            role=role, tables=tables, shared_dbs=shared_dbs, spec_dbs=spec_dbs
        )
        sql_commands.extend(table_commands)

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
        self, role: str, databases: Dict[str, List], shared_dbs: Set, spec_dbs: Set
    ) -> List[Dict]:
        """
        Generate the GRANT and REVOKE statements for Databases
        to align Snowflake with the spec.

        role: the name of the role the privileges are GRANTed to
        databases: list of databases (e.g. "raw")
        shared_dbs: a set of all the shared databases defined in the spec.
        spec_dbs: a set of all the databases defined in the spec. This is used in revoke
                  commands to validate revocations are only for spec'd databases

        Returns the SQL commands generated as a list
        """
        sql_commands = []

        read_privileges = "usage"
        partial_write_privileges = "monitor, create schema"
        write_privileges = f"{read_privileges}, {partial_write_privileges}"

        for database in databases.get("read", []):
            already_granted = False
            if self.check_grant_to_role(role, "usage", "database", database):
                already_granted = True

            # If this is a shared database, we have to grant the "imported privileges"
            # privilege to the user and skip granting the specific permissions as
            # "Granting individual privileges on imported databases is not allowed."
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
            # privilege to the user and skip granting the specific permissions as
            # "Granting individual privileges on imported databases is not allowed."
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

        # REVOKES

        # The "Usage" privilege is consistent across read and write.
        # Compare granted usage to full read/write usage set
        # and revoke missing ones
        for granted_database in (
            self.grants_to_role.get(role, {}).get("usage", {}).get("database", [])
        ):
            # If it's a shared database, only revoke imported
            # We'll only know if it's a shared DB based on the spec
            all_databases = databases.get("read", []) + databases.get("write", [])
            if granted_database not in spec_dbs:
                # Skip revocation on database that are not defined in spec
                continue
            elif (
                granted_database not in all_databases and granted_database in shared_dbs
            ):
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

            elif granted_database not in all_databases:
                sql_commands.append(
                    {
                        "already_granted": False,
                        "sql": REVOKE_PRIVILEGES_TEMPLATE.format(
                            privileges=read_privileges,
                            resource_type="database",
                            resource_name=SnowflakeConnector.snowflaky(
                                granted_database
                            ),
                            role=SnowflakeConnector.snowflaky(role),
                        ),
                    }
                )
        # Get all other write privilege dbs in case there are dbs where
        # usage was revoked but other write permissions still exist
        # This also preserves the case where somebody switches write access
        # for read access
        for granted_database in self.grants_to_role.get(role, {}).get(
            "monitor", {}
        ).get("database", []) + self.grants_to_role.get(role, {}).get(
            "create_schema", {}
        ).get(
            "database", []
        ):
            # If it's a shared database, only revoke imported
            # We'll only know if it's a shared DB based on the spec
            if (
                granted_database not in databases.get("write", [])
                and granted_database in shared_dbs
            ):
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
            elif granted_database not in databases.get("write", []):
                sql_commands.append(
                    {
                        "already_granted": False,
                        "sql": REVOKE_PRIVILEGES_TEMPLATE.format(
                            privileges=partial_write_privileges,
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
        self, role: str, schemas: Dict[str, List], shared_dbs: Set, spec_dbs: Set
    ) -> List[Dict]:
        """
        Generate the GRANT and REVOKE statements for schemas
        including future grants.

        role: the name of the role the privileges are GRANTed to
        schemas: the name of the Schema (e.g. "raw.public", "raw.*")
        shared_dbs: a set of all the shared databases defined in the spec.
        spec_dbs: a set of all the databases defined in the spec. This is used in revoke
                  commands to validate revocations are only for spec'd databases

        Returns the SQL commands generated as a List
        """
        sql_commands = []

        # Schema lists to hold read/write grants. This is necessary
        # as the provided schemas are not the full list - we determine
        # the full list via full_schema_list and store in these variables
        read_grant_schemas = []
        write_grant_schemas = []

        read_privileges = "usage"
        partial_write_privileges = (
            "monitor, create table,"
            " create view, create stage, create file format,"
            " create sequence, create function, create pipe"
        )
        write_privileges = f"{read_privileges}, {partial_write_privileges}"
        write_privileges_array = write_privileges.split(", ")

        for schema in schemas.get("read", []):
            # Split the schema identifier into parts {DB_NAME}.{SCHEMA_NAME}
            # so that we can check and use each one
            name_parts = schema.split(".")

            # Do nothing if this is a schema inside a shared database:
            # "Granting individual privileges on imported databases is not allowed."
            database = name_parts[0]
            if database in shared_dbs:
                continue

            conn = SnowflakeConnector()
            fetched_schemas = conn.full_schema_list(schema)
            read_grant_schemas.extend(fetched_schemas)

            if name_parts[1] == "*":
                # If <db_name>.* then you can grant future and add future schema to grant list
                future_schema = f"{database}.<schema>"
                read_grant_schemas.append(future_schema)

                schema_already_granted = False
                if self.check_grant_to_role(
                    role, read_privileges, "schema", future_schema
                ):
                    schema_already_granted = True

                # Grant on FUTURE schemas
                sql_commands.append(
                    {
                        "already_granted": schema_already_granted,
                        "sql": GRANT_FUTURE_SCHEMAS_PRIVILEGES_TEMPLATE.format(
                            privileges=read_privileges,
                            resource_name=SnowflakeConnector.snowflaky(database),
                            role=SnowflakeConnector.snowflaky(role),
                        ),
                    }
                )

            for db_schema in fetched_schemas:
                already_granted = False

                if self.check_grant_to_role(role, read_privileges, "schema", db_schema):
                    already_granted = True

                sql_commands.append(
                    {
                        "already_granted": already_granted,
                        "sql": GRANT_PRIVILEGES_TEMPLATE.format(
                            privileges=read_privileges,
                            resource_type="schema",
                            resource_name=SnowflakeConnector.snowflaky(db_schema),
                            role=SnowflakeConnector.snowflaky(role),
                        ),
                    }
                )

        for schema in schemas.get("write", []):
            # Split the schema identifier into parts {DB_NAME}.{SCHEMA_NAME}
            # so that we can check and use each one
            name_parts = schema.split(".")

            # Do nothing if this is a schema inside a shared database:
            # "Granting individual privileges on imported databases is not allowed."
            database = name_parts[0]
            if database in shared_dbs:
                continue

            conn = SnowflakeConnector()
            fetched_schemas = conn.full_schema_list(schema)
            write_grant_schemas.extend(fetched_schemas)

            if name_parts[1] == "*":
                # If <db_name>.* then you can grant future and add future schema to grant list
                future_schema = f"{database}.<schema>"
                write_grant_schemas.append(future_schema)

                already_granted = True

                for privilege in write_privileges_array:
                    # If any of the privileges are not granted, set already_granted to False
                    if not self.check_grant_to_role(
                        role, privilege, "schema", future_schema
                    ):
                        already_granted = False

                # Grant on FUTURE schemas
                sql_commands.append(
                    {
                        "already_granted": already_granted,
                        "sql": GRANT_FUTURE_SCHEMAS_PRIVILEGES_TEMPLATE.format(
                            privileges=write_privileges,
                            resource_name=SnowflakeConnector.snowflaky(database),
                            role=SnowflakeConnector.snowflaky(role),
                        ),
                    }
                )

            for db_schema in fetched_schemas:
                already_granted = True

                for privilege in write_privileges_array:
                    # If any of the privileges are not granted, set already_granted to False
                    if not self.check_grant_to_role(
                        role, privilege, "schema", db_schema
                    ):
                        already_granted = False

                sql_commands.append(
                    {
                        "already_granted": already_granted,
                        "sql": GRANT_PRIVILEGES_TEMPLATE.format(
                            privileges=write_privileges,
                            resource_type="schema",
                            resource_name=SnowflakeConnector.snowflaky(db_schema),
                            role=SnowflakeConnector.snowflaky(role),
                        ),
                    }
                )

        # REVOKES

        # The "usage" privilege is consistent across read and write.
        # Compare granted usage to full read/write set and revoke missing ones
        for granted_schema in list(
            set(self.grants_to_role.get(role, {}).get("usage", {}).get("schema", []))
        ):
            all_grant_schemas = read_grant_schemas + write_grant_schemas
            database_name = granted_schema.split(".")[0]
            future_schema_name = f"{database_name}.<schema>"
            if granted_schema not in all_grant_schemas and (
                database_name in shared_dbs or database_name not in spec_dbs
            ):
                # No privileges to revoke on imported db. Done at database level
                # Don't revoke on privileges on databases not defined in spec.
                continue
            elif (  # If future privilege is granted on snowflake but not in grant list
                granted_schema == future_schema_name
                and future_schema_name not in all_grant_schemas  #
            ):
                sql_commands.append(
                    {
                        "already_granted": False,
                        "sql": REVOKE_FUTURE_DB_OBJECT_PRIVILEGES_TEMPLATE.format(
                            privileges=read_privileges,
                            resource_name=SnowflakeConnector.snowflaky(database_name),
                            role=SnowflakeConnector.snowflaky(role),
                        ),
                    }
                )
            elif (
                granted_schema not in all_grant_schemas
                and future_schema_name not in all_grant_schemas
            ):
                # Covers case where schema is granted in Snowflake
                # But it's not in the grant list and it's not explicitly granted as a future grant
                sql_commands.append(
                    {
                        "already_granted": False,
                        "sql": REVOKE_PRIVILEGES_TEMPLATE.format(
                            privileges=read_privileges,
                            resource_type="schema",
                            resource_name=SnowflakeConnector.snowflaky(granted_schema),
                            role=SnowflakeConnector.snowflaky(role),
                        ),
                    }
                )

        # Get all other write privilege schemas in case there are schemas where
        # usage was revoked but other write permissions still exist
        # This also preserves the case where somebody switches write access
        # for read access
        for granted_schema in list(
            set(
                self.grants_to_role.get(role, {}).get("monitor", {}).get("schema", [])
                + self.grants_to_role.get(role, {})
                .get("create table", {})
                .get("schema", [])
                + self.grants_to_role.get(role, {})
                .get("create view", {})
                .get("schema", [])
                + self.grants_to_role.get(role, {})
                .get("create stage", {})
                .get("schema", [])
                + self.grants_to_role.get(role, {})
                .get("create file format", {})
                .get("schema", [])
                + self.grants_to_role.get(role, {})
                .get("create sequence", {})
                .get("schema", [])
                + self.grants_to_role.get(role, {})
                .get("create pipe", {})
                .get("schema", [])
            )
        ):
            database_name = granted_schema.split(".")[0]
            future_schema_name = f"{database_name}.<schema>"
            if (
                granted_schema not in write_grant_schemas
                and database_name in shared_dbs
            ):
                # No privileges to revoke on imported db
                continue
            elif (  # If future privilege is granted but not in grant list
                granted_schema == future_schema_name
                and future_schema_name not in write_grant_schemas
            ):
                sql_commands.append(
                    {
                        "already_granted": False,
                        "sql": REVOKE_FUTURE_DB_OBJECT_PRIVILEGES_TEMPLATE.format(
                            privileges=partial_write_privileges,
                            resource_name=SnowflakeConnector.snowflaky(database_name),
                            role=SnowflakeConnector.snowflaky(role),
                        ),
                    }
                )
            elif (
                granted_schema not in write_grant_schemas
                and future_schema_name not in write_grant_schemas
            ):
                # Covers case where schema is granted and it's not explicitly granted as a future grant
                sql_commands.append(
                    {
                        "already_granted": False,
                        "sql": REVOKE_PRIVILEGES_TEMPLATE.format(
                            privileges=partial_write_privileges,
                            resource_type="schema",
                            resource_name=SnowflakeConnector.snowflaky(granted_schema),
                            role=SnowflakeConnector.snowflaky(role),
                        ),
                    }
                )

        return sql_commands

    def generate_table_and_view_grants(
        self, role: str, tables: Dict[str, List], shared_dbs: Set, spec_dbs: Set
    ) -> List[Dict]:
        """
        Generate the GRANT and REVOKE statements for tables and views
        including future grants.

        role: the name of the role the privileges are GRANTed to
        table: the name of the TABLE/VIEW (e.g. "raw.public.my_table")
        shared_dbs: a set of all the shared databases defined in the spec.
        spec_dbs: a set of all the databases defined in the spec. This is used in revoke
                  commands to validate revocations are only for spec'd databases

        Returns the SQL commands generated as a List
        """
        sql_commands = []

        # These are necessary as the provided tables/views are not the full list
        # we determine the full list for granting via full_schema_list()
        # and store in these variables
        read_grant_tables_full = []
        read_grant_views_full = []

        write_grant_tables_full = []
        write_grant_views_full = []

        read_privileges = "select"
        write_partial_privileges = "insert, update, delete, truncate, references"
        write_privileges = f"{read_privileges}, {write_partial_privileges}"
        write_privileges_array = write_privileges.split(", ")

        conn = SnowflakeConnector()

        for table in tables.get("read", []):
            # Split the table identifier into parts {DB_NAME}.{SCHEMA_NAME}.{TABLE_NAME}
            # so that we can check and use each one
            name_parts = table.split(".")

            # Do nothing if this is a table inside a shared database:
            # "Granting individual privileges on imported databases is not allowed."
            if name_parts[0] in shared_dbs:
                continue

            # Gather the tables/views that privileges will be granted to
            # for the given table schema
            read_grant_tables = []
            read_grant_views = []

            # List of all tables/views in schema for validation
            read_table_list = []
            read_view_list = []

            fetched_schemas = conn.full_schema_list(f"{name_parts[0]}.{name_parts[1]}")

            for schema in fetched_schemas:
                # Fetch all tables from Snowflake for each schema and add
                # to the read_tables_list[] and read_views_list[] variables.
                # This is so we can check that a table given in the config
                # Is valid
                read_table_list.extend(conn.show_tables(schema=schema))
                read_view_list.extend(conn.show_views(schema=schema))

            if name_parts[2] == "*":
                # If <schema_name>.* then you add all tables to grant list and then grant future
                # If *.* was provided then we're still ok as the full_schema_list
                # Would fetch all schemas and we'd still iterate through each

                # If == * then append all tables to both
                # the grant list AND the full grant list
                read_grant_tables.extend(read_table_list)
                read_grant_views.extend(read_view_list)
                read_grant_tables_full.extend(read_table_list)
                read_grant_views_full.extend(read_view_list)

                for schema in fetched_schemas:
                    # Adds the future grant table format to the granted lists
                    future_table = f"{schema}.<table>"
                    future_view = f"{schema}.<view>"
                    read_grant_tables_full.append(future_table)
                    read_grant_views_full.append(future_view)

                    table_already_granted = False

                    if self.check_grant_to_role(
                        role, read_privileges, "table", future_table
                    ):
                        table_already_granted = True

                    # Grant future on all tables
                    sql_commands.append(
                        {
                            "already_granted": table_already_granted,
                            "sql": GRANT_FUTURE_PRIVILEGES_TEMPLATE.format(
                                privileges=read_privileges,
                                resource_type="table",
                                resource_name=SnowflakeConnector.snowflaky(schema),
                                role=SnowflakeConnector.snowflaky(role),
                            ),
                        }
                    )

                    view_already_granted = False

                    if self.check_grant_to_role(
                        role, read_privileges, "view", future_view
                    ):
                        view_already_granted = True

                    # Grant future on all views
                    sql_commands.append(
                        {
                            "already_granted": view_already_granted,
                            "sql": GRANT_FUTURE_PRIVILEGES_TEMPLATE.format(
                                privileges=read_privileges,
                                resource_type="view",
                                resource_name=SnowflakeConnector.snowflaky(schema),
                                role=SnowflakeConnector.snowflaky(role),
                            ),
                        }
                    )

            # TODO Future elif to have partial table name

            else:
                # Else the table passed is a single entity
                # Check that it's valid and add to list
                if table in read_table_list:
                    read_grant_tables = [table]
                    read_grant_tables_full.append(table)
                if table in read_view_list:
                    read_grant_views = [table]
                    read_grant_views_full.append(table)

            # Grant privileges to all tables flagged for granting.
            # We have this loop b/c we explicitly grant to each table
            # Instead of doing grant to all tables/views in schema
            for db_table in read_grant_tables:
                already_granted = False
                if self.check_grant_to_role(role, read_privileges, "table", db_table):
                    already_granted = True

                sql_commands.append(
                    {
                        "already_granted": already_granted,
                        "sql": GRANT_PRIVILEGES_TEMPLATE.format(
                            privileges=read_privileges,
                            resource_type="table",
                            resource_name=SnowflakeConnector.snowflaky(db_table),
                            role=SnowflakeConnector.snowflaky(role),
                        ),
                    }
                )

            # Grant privileges to all flagged views
            for db_view in read_grant_views:
                already_granted = False
                if self.check_grant_to_role(role, read_privileges, "view", db_view):
                    already_granted = True

                sql_commands.append(
                    {
                        "already_granted": already_granted,
                        "sql": GRANT_PRIVILEGES_TEMPLATE.format(
                            privileges=read_privileges,
                            resource_type="view",
                            resource_name=SnowflakeConnector.snowflaky(db_view),
                            role=SnowflakeConnector.snowflaky(role),
                        ),
                    }
                )

        for table in tables.get("write", []):
            # Split the table identifier into parts {DB_NAME}.{SCHEMA_NAME}.{TABLE_NAME}
            #  so that we can check and use each one
            name_parts = table.split(".")

            # Do nothing if this is a table inside a shared database:
            #  "Granting individual privileges on imported databases is not allowed."
            if name_parts[0] in shared_dbs:
                continue

            # Gather the tables/views that privileges will be granted to
            write_grant_tables = []
            write_grant_views = []

            # List of all tables/views in schema
            write_table_list = []
            write_view_list = []

            fetched_schemas = conn.full_schema_list(f"{name_parts[0]}.{name_parts[1]}")

            for schema in fetched_schemas:
                # Fetch all tables from Snowflake for each schema and add
                # to the write_tables_list[] and write_views_list[] variables.
                # This is so we can check that a table given in the config
                # Is valid
                write_table_list.extend(conn.show_tables(schema=schema))
                write_view_list.extend(conn.show_views(schema=schema))

            if name_parts[2] == "*":
                # If <schema_name>.* then you add all tables to grant list and then grant future
                # If *.* was provided then we're still ok as the full_schema_list
                # Would fetch all schemas and we'd still iterate through each

                # If == * then append all tables to both
                # the grant list AND the full grant list
                write_grant_tables.extend(write_table_list)
                write_grant_views.extend(write_view_list)
                write_grant_tables_full.extend(write_table_list)
                write_grant_views_full.extend(write_view_list)

                for schema in fetched_schemas:
                    # Adds the future grant table format to the granted lists
                    future_table = f"{schema}.<table>"
                    future_view = f"{schema}.<view>"
                    write_grant_tables_full.append(future_table)
                    write_grant_views_full.append(future_view)

                    table_already_granted = True

                    for privilege in write_privileges_array:
                        # If any of the privileges are not granted, set already_granted to False
                        if not self.check_grant_to_role(
                            role, privilege, "table", future_table
                        ):
                            table_already_granted = False

                    # Grant future on all tables
                    sql_commands.append(
                        {
                            "already_granted": table_already_granted,
                            "sql": GRANT_FUTURE_PRIVILEGES_TEMPLATE.format(
                                privileges=write_privileges,
                                resource_type="table",
                                resource_name=SnowflakeConnector.snowflaky(schema),
                                role=SnowflakeConnector.snowflaky(role),
                            ),
                        }
                    )

                    view_already_granted = True

                    if not self.check_grant_to_role(
                        role, "select", "view", future_view
                    ):
                        view_already_granted = False

                    # Grant future on all views. Select is only privilege
                    sql_commands.append(
                        {
                            "already_granted": view_already_granted,
                            "sql": GRANT_FUTURE_PRIVILEGES_TEMPLATE.format(
                                privileges="select",
                                resource_type="view",
                                resource_name=SnowflakeConnector.snowflaky(schema),
                                role=SnowflakeConnector.snowflaky(role),
                            ),
                        }
                    )

            # TODO Future elif to have partial table name

            else:
                # Only one table/view to be granted permissions to
                if table in write_table_list:
                    write_grant_tables = [table]
                    write_grant_tables_full.append(table)
                if table in write_view_list:
                    write_grant_views = [table]
                    write_grant_views_full.append(table)

            # Grant privileges to all tables flagged for granting.
            # We have this loop b/c we explicitly grant to each table
            # Instead of doing grant to all tables/views in schema
            for db_table in write_grant_tables:

                table_already_granted = True
                for privilege in write_privileges_array:
                    # If any of the privileges are not granted, set already_granted to False
                    if not self.check_grant_to_role(role, privilege, "table", db_table):
                        table_already_granted = False

                sql_commands.append(
                    {
                        "already_granted": table_already_granted,
                        "sql": GRANT_PRIVILEGES_TEMPLATE.format(
                            privileges=write_privileges,
                            resource_type="table",
                            resource_name=SnowflakeConnector.snowflaky(db_table),
                            role=SnowflakeConnector.snowflaky(role),
                        ),
                    }
                )

            # Grant privileges to all views in that schema.
            # Select is the only schemaObjectPrivilege for views
            # https://docs.snowflake.net/manuals/sql-reference/sql/grant-privilege.html
            for db_view in write_grant_views:
                already_granted = False
                if self.check_grant_to_role(role, "select", "view", db_view):
                    already_granted = True

                sql_commands.append(
                    {
                        "already_granted": already_granted,
                        "sql": GRANT_PRIVILEGES_TEMPLATE.format(
                            privileges="select",
                            resource_type="view",
                            resource_name=SnowflakeConnector.snowflaky(db_view),
                            role=SnowflakeConnector.snowflaky(role),
                        ),
                    }
                )

        # REVOKES

        # Read Privileges
        # The "select" privilege is consistent across read and write.
        # Compare granted usage to full read/write set and revoke missing ones
        for granted_table in list(
            set(self.grants_to_role.get(role, {}).get("select", {}).get("table", []))
        ):
            all_grant_tables = read_grant_tables_full + write_grant_tables_full
            table_split = granted_table.split(".")
            database_name = table_split[0]
            schema_name = table_split[1]
            table_name = table_split[2]
            future_table = f"{database_name}.{schema_name}.<table>"
            if granted_table not in all_grant_tables and (
                database_name in shared_dbs or database_name not in spec_dbs
            ):
                # No privileges to revoke on imported db. Done at database level
                # Don't revoke on privileges on databases not defined in spec.
                continue
            elif (  # If future privilege is granted in Snowflake but not in grant list
                granted_table == future_table and future_table not in all_grant_tables
            ):
                sql_commands.append(
                    {
                        "already_granted": False,
                        "sql": REVOKE_FUTURE_SCHEMA_OBJECT_PRIVILEGES_TEMPLATE.format(
                            privileges=read_privileges,
                            resource_type="table",
                            resource_name=SnowflakeConnector.snowflaky(
                                f"{database_name}.{schema_name}"
                            ),
                            role=SnowflakeConnector.snowflaky(role),
                        ),
                    }
                )
            elif (
                granted_table not in all_grant_tables
                and future_table not in all_grant_tables
            ):
                # Covers case where table is granted in Snowflake
                # But it's not in the grant list and it's not explicitly granted as a future grant
                sql_commands.append(
                    {
                        "already_granted": False,
                        "sql": REVOKE_PRIVILEGES_TEMPLATE.format(
                            privileges=read_privileges,
                            resource_type="table",
                            resource_name=SnowflakeConnector.snowflaky(granted_table),
                            role=SnowflakeConnector.snowflaky(role),
                        ),
                    }
                )

        # SELECT is the only privilege for views so this covers both the read
        # and write case since we have "all_grant_views" defined.
        for granted_view in list(
            set(self.grants_to_role.get(role, {}).get("select", {}).get("view", []))
        ):
            all_grant_views = read_grant_views_full + write_grant_views_full
            view_split = granted_view.split(".")
            database_name = view_split[0]
            schema_name = view_split[1]
            view_name = view_split[2]
            future_view = f"{database_name}.{schema_name}.<view>"
            if granted_view not in all_grant_views and (
                database_name in shared_dbs or database_name not in spec_dbs
            ):
                # No privileges to revoke on imported db. Done at database level
                # Don't revoke on privileges on databases not defined in spec.
                continue
            elif granted_view == future_view and future_view not in all_grant_views:
                # If future privilege is granted in Snowflake but not in grant list
                sql_commands.append(
                    {
                        "already_granted": False,
                        "sql": REVOKE_FUTURE_SCHEMA_OBJECT_PRIVILEGES_TEMPLATE.format(
                            privileges=read_privileges,
                            resource_type="view",
                            resource_name=SnowflakeConnector.snowflaky(
                                f"{database_name}.{schema_name}"
                            ),
                            role=SnowflakeConnector.snowflaky(role),
                        ),
                    }
                )
            elif (
                granted_view not in all_grant_views
                and future_view not in all_grant_views
            ):
                # Covers case where view is granted in Snowflake
                # But it's not in the grant list and it's not explicitly granted as a future grant
                sql_commands.append(
                    {
                        "already_granted": False,
                        "sql": REVOKE_PRIVILEGES_TEMPLATE.format(
                            privileges=read_privileges,
                            resource_type="view",
                            resource_name=SnowflakeConnector.snowflaky(granted_view),
                            role=SnowflakeConnector.snowflaky(role),
                        ),
                    }
                )

        # Write Privileges
        # Only need to revoke write privileges for tables since SELECT is the
        # only privilege available for views
        for granted_table in list(
            set(
                self.grants_to_role.get(role, {}).get("insert", {}).get("table", [])
                + self.grants_to_role.get(role, {}).get("update", {}).get("table", [])
                + self.grants_to_role.get(role, {}).get("delete", {}).get("table", [])
                + self.grants_to_role.get(role, {}).get("truncate", {}).get("table", [])
                + self.grants_to_role.get(role, {})
                .get("references", {})
                .get("table", [])
            )
        ):
            table_split = granted_table.split(".")
            database_name = table_split[0]
            schema_name = table_split[1]
            table_name = table_split[2]
            future_table = f"{database_name}.{schema_name}.<table>"
            if granted_table not in write_grant_tables_full and (
                database_name in shared_dbs or database_name not in spec_dbs
            ):
                # No privileges to revoke on imported db. Done at database level
                # Don't revoke on privileges on databases not defined in spec.
                continue
            elif (
                granted_table == future_table
                and future_table not in write_grant_tables_full
            ):
                # If future privilege is granted in Snowflake but not in grant list
                sql_commands.append(
                    {
                        "already_granted": False,
                        "sql": REVOKE_FUTURE_SCHEMA_OBJECT_PRIVILEGES_TEMPLATE.format(
                            privileges=write_partial_privileges,
                            resource_type="table",
                            resource_name=SnowflakeConnector.snowflaky(
                                f"{database_name}.{schema_name}"
                            ),
                            role=SnowflakeConnector.snowflaky(role),
                        ),
                    }
                )
            elif (
                granted_table not in write_grant_tables_full
                and future_table not in write_grant_tables_full
            ):
                # Covers case where table is granted in Snowflake
                # But it's not in the grant list and it's not explicitly granted as a future grant
                sql_commands.append(
                    {
                        "already_granted": False,
                        "sql": REVOKE_PRIVILEGES_TEMPLATE.format(
                            privileges=write_partial_privileges,
                            resource_type="table",
                            resource_name=SnowflakeConnector.snowflaky(granted_table),
                            role=SnowflakeConnector.snowflaky(role),
                        ),
                    }
                )

        return sql_commands

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
