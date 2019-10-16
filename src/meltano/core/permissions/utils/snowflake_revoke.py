import logging

from typing import Dict, List, Tuple, Set

from meltano.core.permissions.utils.snowflake_connector import SnowflakeConnector

REVOKE_ROLE_TEMPLATE = "REVOKE ROLE {role_name} FROM {type} {entity_name}"

REVOKE_ALL_PRIVILEGES_ACCOUNTOBJECT_TEMPLATE = (
    "REVOKE {privileges} PRIVILEGES ON {resource_type} {resource_name} FROM ROLE {role}"
)

REVOKE_ALL_PRIVILEGES_OBJECT_TEMPLATE = "REVOKE {privileges} PRIVILEGES ON ALL {resource_type}S IN {parent_resource_type} {parent_resource_name} FROM ROLE {role}"


class SnowflakeRevokesGenerator:
    def __init__(self, grants_to_role: Dict, roles_granted_to_user: Dict) -> None:
        self.grants_to_role = grants_to_role
        self.roles_granted_to_user = roles_granted_to_user

    def generate_revoke_roles(
        self, entity_type: str, entity: str, config: str
    ) -> List[Dict]:
        """
        Generate the REVOKE statements for both roles and users.

        entity_type: "USER" or "ROLE"
        entity: the name of the entity (e.g. "yannis" or "REPORTER")
        config: the subtree for the entity as specified in the spec

        Returns the SQL commands generated as a list
        """
        sql_commands = []

        try:
            for member_role in config["member_of"]:
                granted_role = SnowflakeConnector.snowflaky(member_role).upper()

                sql_commands.append(
                    {
                        "already_granted": False,
                        "sql": REVOKE_ROLE_TEMPLATE.format(
                            role_name=SnowflakeConnector.snowflaky(member_role),
                            type=entity_type,
                            entity_name=SnowflakeConnector.snowflaky(entity),
                        ),
                    }
                )
        except KeyError:
            logging.debug(
                "`member_of` not found for {}, skipping generation of REVOKE ROLE statements.".format(
                    entity
                )
            )

        return sql_commands

    def generate_revoke_privileges_to_role(
        self, role: str, config: str, shared_dbs: Set
    ) -> List[Dict]:
        """
        Generate all the privilege revoking statements for a role.

        Most of the SQL command that will be generated are privileges revoked from
        roles and this function orchestrates the whole process

        role: the name of the role (e.g. "LOADER" or "REPORTER") the privileges
              are REVOKEd from
        config: the subtree for the role as specified in the spec
        shared_dbs: a set of all the shared databases defined in the spec.
                    Used down the road by generate_database_revokes() to also revoke
                    "IMPORTED PRIVILEGES" when access is for a shared DB.

        Returns the SQL commands generated as a list
        """
        sql_commands = []

        try:
            for warehouse in config["warehouses"]:
                new_commands = self.generate_warehouse_revokes(
                    role=role, warehouse=warehouse
                )
                sql_commands.extend(new_commands)
        except KeyError:
            logging.debug(
                "`warehouses` not found for role {}, skipping generation of Warehouse REVOKE statements.".format(
                    role
                )
            )

        try:
            for database in config["privileges"]["databases"]["read"]:
                new_commands = self.generate_database_revokes(
                    role=role, database=database, shared_dbs=shared_dbs
                )
                sql_commands.extend(new_commands)
        except KeyError:
            logging.debug(
                "`privileges.databases.read` not found for role {}, skipping generation of DATABASE read level REVOKE statements.".format(
                    role
                )
            )

        try:
            for database in config["privileges"]["databases"]["write"]:
                new_commands = self.generate_database_revokes(
                    role=role, database=database, shared_dbs=shared_dbs
                )
                sql_commands.extend(new_commands)
        except KeyError:
            logging.debug(
                "`privileges.databases.write` not found for role {}, skipping generation of DATABASE write level REVOKE statements.".format(
                    role
                )
            )

        try:
            for schema in config["privileges"]["schemas"]["read"]:
                database = schema.split(".")[0]
                new_commands = self.generate_database_revokes(
                    role=role, database=database, shared_dbs=shared_dbs
                )
                sql_commands.extend(new_commands)
        except KeyError:
            logging.debug(
                "`privileges.schemas.read` not found for role {}, skipping generation of DATABASE, via schema, read level REVOKE statements.".format(
                    role
                )
            )

        try:
            for schema in config["privileges"]["schemas"]["write"]:
                database = schema.split(".")[0]
                new_commands = self.generate_database_revokes(
                    role=role, database=database, shared_dbs=shared_dbs
                )
                sql_commands.extend(new_commands)
        except KeyError:
            logging.debug(
                "`privileges.schemas.write` not found for role {}, skipping generation of DATABASE, via schema, write level REVOKE statements.".format(
                    role
                )
            )

        try:
            for table in config["privileges"]["tables"]["read"]:
                new_commands = self.generate_table_and_view_revokes(
                    role=role, table=table, shared_dbs=shared_dbs
                )
                sql_commands.extend(new_commands)
        except KeyError:
            logging.debug(
                "`privileges.tables.read` not found for role {}, skipping generation of TABLE read level REVOKE statements.".format(
                    role
                )
            )

        try:
            for table in config["privileges"]["tables"]["write"]:
                new_commands = self.generate_table_and_view_revokes(
                    role=role, table=table, shared_dbs=shared_dbs
                )
                sql_commands.extend(new_commands)
        except KeyError:
            logging.debug(
                "`privileges.tables.write` not found for role {}, skipping generation of TABLE write level REVOKE statements.".format(
                    role
                )
            )

        return sql_commands

    def generate_warehouse_revokes(self, role: str, warehouse: str) -> List[str]:
        """
        Generate the REVOKE statements for Warehouse usage (only one type at the moment).

        role: the name of the role the privileges are REVOKEd to
        warehouse: the name of the warehouse (e.g. "transforming")

        Returns the SQL command generated
        """
        sql_commands = []

        sql_commands.append(
            {
                "already_granted": False,
                "sql": REVOKE_ALL_PRIVILEGES_ACCOUNTOBJECT_TEMPLATE.format(
                    privileges="ALL",
                    resource_type="WAREHOUSE",
                    resource_name=SnowflakeConnector.snowflaky(warehouse),
                    role=SnowflakeConnector.snowflaky(role),
                ),
            }
        )

        return sql_commands

    def generate_database_revokes(
        self, role: str, database: str, shared_dbs: Set
    ) -> List[str]:
        """
        Generate the REVOKE statements for Databases and Schemas.

        role: the name of the role the privileges are REVOKEd from
        database: the name of the database (e.g. "RAW")
        shared_dbs: a set of all the shared databases defined in the spec.

        Returns the SQL commands generated as a list
        """
        sql_commands = []
        already_granted = False

        # If this is a shared database, we have to revoke the "IMPORTED PRIVILEGES"
        #  privilege to the user and skip revoking the specific permissions as
        #  "Revoking individual privileges on imported databases is not allowed."
        if database in shared_dbs:
            sql_commands.append(
                {
                    "already_granted": already_granted,
                    "sql": REVOKE_ALL_PRIVILEGES_ACCOUNTOBJECT_TEMPLATE.format(
                        privileges="ALL IMPORTED",
                        resource_type="DATABASE",
                        resource_name=SnowflakeConnector.snowflaky(database),
                        role=SnowflakeConnector.snowflaky(role),
                    ),
                }
            )

            return sql_commands

        # And then revoke privileges to the database

        sql_commands.append(
            {
                "already_granted": already_granted,
                "sql": REVOKE_ALL_PRIVILEGES_ACCOUNTOBJECT_TEMPLATE.format(
                    privileges="ALL",
                    resource_type="DATABASE",
                    resource_name=SnowflakeConnector.snowflaky(database),
                    role=SnowflakeConnector.snowflaky(role),
                ),
            }
        )

        # Revoke privileges on all schemas in database

        sql_commands.append(
            {
                "already_granted": already_granted,
                "sql": REVOKE_ALL_PRIVILEGES_OBJECT_TEMPLATE.format(
                    privileges="ALL",
                    resource_type="SCHEMA",
                    parent_resource_type="DATABASE",
                    parent_resource_name=SnowflakeConnector.snowflaky(database),
                    role=SnowflakeConnector.snowflaky(role),
                ),
            }
        )
        return sql_commands

    def generate_table_and_view_revokes(
        self, role: str, table: str, shared_dbs: Set
    ) -> List[str]:
        """
        Generate the REVOKE statements for TABLEs and VIEWs.

        role: the name of the role the privileges are REVOKEd from
        table: the name of the TABLE/VIEW (e.g. "RAW.PUBLIC.MY_TABLE")
        shared_dbs: a set of all the shared databases defined in the spec.

        Returns the SQL commands generated
        """
        sql_commands = []

        # Split the table identifier into parts {DB_NAME}.{SCHEMA_NAME}.{TABLE_NAME}
        #  so that we can check and use each one
        name_parts = table.split(".")

        # Do nothing if this is a table inside a shared database:
        #  "Granting individual privileges on imported databases is not allowed."
        if name_parts[0] in shared_dbs:
            return sql_commands

        # Generate the INFORMATION_SCHEMA identifier for that database
        #  in order to be able to filter it out
        info_schema = f"{name_parts[0].upper()}.INFORMATION_SCHEMA"

        schemas = []

        conn = SnowflakeConnector()

        if name_parts[1] == "*":
            # If {DB_NAME}.*.* was provided as the identifier, we have to fetch
            #  each schema in database DB_NAME, so that we can revoke privileges
            #  for all tables in that schema
            # (You can not GRANT to all table with a wild card for the schema name)
            db_schemas = conn.show_schemas(name_parts[0])
            for schema in db_schemas:
                if schema != info_schema:
                    schemas.append(schema)
        elif "*" in name_parts[1]:
            # Similar to above, if {DB_NAME}.partial_*.* was provided,
            #  we need to find each of the schemas that match the pattern.
            conn = SnowflakeConnector()
            db_schemas = conn.show_schemas(name_parts[0])
            for db_schema in db_schemas:
                schema_name = db_schema.split(".", 1)[1].lower()
                if schema_name.startswith(name_parts[1].split("*", 1)[0]):
                    schemas.append(db_schema)
        else:
            schemas = [f"{name_parts[0]}.{name_parts[1]}"]

        for schema in schemas:
            # Revoke on ALL tables
            sql_commands.append(
                {
                    "already_granted": False,
                    "sql": REVOKE_ALL_PRIVILEGES_OBJECT_TEMPLATE.format(
                        privileges="ALL",
                        resource_type="TABLE",
                        parent_resource_type="SCHEMA",
                        parent_resource_name=SnowflakeConnector.snowflaky(schema),
                        role=SnowflakeConnector.snowflaky(role),
                    ),
                }
            )

            # Revoke on ALL views
            sql_commands.append(
                {
                    "already_granted": False,
                    "sql": REVOKE_ALL_PRIVILEGES_OBJECT_TEMPLATE.format(
                        privileges="ALL",
                        resource_type="VIEW",
                        parent_resource_type="SCHEMA",
                        parent_resource_name=SnowflakeConnector.snowflaky(schema),
                        role=SnowflakeConnector.snowflaky(role),
                    ),
                }
            )

        return sql_commands
