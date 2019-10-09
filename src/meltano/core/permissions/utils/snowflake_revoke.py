import logging

from typing import Dict, List, Tuple, Set

from meltano.core.permissions.utils.snowflake_connector import SnowflakeConnector

REVOKE_ROLE_TEMPLATE = "REVOKE ROLE {role_name} FROM {type} {entity_name}"

REVOKE_ALL_PRIVILEGES_ACCOUNTOBJECT_TEMPLATE = "REVOKE {privileges} PRIVILEGES ON {resource_type} {resource_name} FROM ROLE {role}"

REVOKE_ALL_PRIVILEGES_OBJECT_TEMPLATE = "REVOKE {privileges} PRIVILEGES ON ALL {resource_type}S IN {parent_resource_type} {parent_resource_name} FROM ROLE {role}"

ALTER_USER_TEMPLATE = "ALTER USER {user_name} SET {privileges}"


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
                "`member_of` not found for {}, skipping generation of GRANT ROLE statements.".format(
                    entity
                )
            )

        return sql_commands

    def generate_revoke_privileges_to_role(
        self, role: str, config: str, shared_dbs: Set
    ) -> List[Dict]:
        """
        Generate all the privilege revoking statements for a role.

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

        try:
            for warehouse in config["warehouses"]:
                sql_commands.extend(self.generate_warehouse_revokes(role, warehouse))
        except KeyError:
            logging.debug(
                "`warehouses` not found for role {}, skipping generation of Warehouse REVOKE statements.".format(
                    role
                )
            )
        try:
            for database in config["privileges"]["databases"]["read"]:
                new_commands = self.generate_database_revokes(
                    role=role,
                    database=database,
                    grant_type="read",
                    usage_granted=usage_granted,
                    shared_dbs=shared_dbs,
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
                    role=role,
                    database=database,
                    grant_type="write",
                    usage_granted=usage_granted,
                    shared_dbs=shared_dbs,
                )
                sql_commands.extend(new_commands)
        except KeyError:
            logging.debug(
                "`privileges.databases.write` not found for role {}, skipping generation of DATABASE write level REVOKE statements.".format(
                    role
                )
            )

        # try:
        #     for table in config["privileges"]["tables"]["read"]:
        #         new_commands, usage_granted = self.generate_table_and_view_revokes(
        #             role=role,
        #             table=table,
        #             grant_type="read",
        #             usage_granted=usage_granted,
        #             shared_dbs=shared_dbs,
        #         )
        #         sql_commands.extend(new_commands)
        # except KeyError:
        #     logging.debug(
        #         "`privileges.tables.read` not found for role {}, skipping generation of TABLE read level GRANT statements.".format(
        #             role
        #         )
        #     )

        # try:
        #     for table in config["privileges"]["tables"]["write"]:
        #         new_commands, usage_granted = self.generate_table_and_view_revokes(
        #             role=role,
        #             table=table,
        #             grant_type="write",
        #             usage_granted=usage_granted,
        #             shared_dbs=shared_dbs,
        #         )
        #         sql_commands.extend(new_commands)
        # except KeyError:
        #     logging.debug(
        #         "`privileges.tables.write` not found for role {}, skipping generation of TABLE write level GRANT statements.".format(
        #             role
        #         )
        #     )

        return sql_commands

    def generate_warehouse_revokes(self, role: str, warehouse: str) -> List[str]:
        """
        Generate the REVOKE statements for Warehouse usage (only one type at the moment).

        role: the name of the role the privileges are GRANTed to
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
        self,
        role: str,
        database: str,
        grant_type: str,
        usage_granted: Dict,
        shared_dbs: Set,
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

    def generate_schema_revokes(
            self,
            role: str,
            schema: str,
            grant_type: str,
            usage_granted: Dict,
            shared_dbs: Set,
        ) -> Tuple[List[str], Dict]:
        """
        Generate the REVOKE statements for SCHEMAs.

        role: the name of the role the privileges are GRANTed to
        schema: the name of the Schema (e.g. "RAW.PUBLIC")
        grant_type: What type of privileges are granted? One of {"read", "write"}
        usage_granted: Passed by generate_grant_privileges_to_role() to track all
            all the entities a role has been granted access (USAGE) to.
        shared_dbs: a set of all the shared databases defined in the spec.

        Returns the SQL commands generated and the updated usage_granted as a Tuple
        """
        sql_commands = []

        # Split the schema identifier into parts {DB_NAME}.{SCHEMA_NAME}
        #  so that we can check and use each one
        name_parts = schema.split(".")

        # Do nothing if this is a schema inside a shared database:
        #  "Revoking individual privileges on imported databases is not allowed."
        if name_parts[0] in shared_dbs:
            return (sql_commands, usage_granted)

        sql_commands.append(
            {
                "already_granted": False,
                "sql": REVOKE_ALL_PRIVILEGES_OBJECT_TEMPLATE.format(
                    privileges="ALL",
                    resource_type="SCHEMA",
                    parent_resource_type="DATABASE",
                    parent_resource_name=name_parts[0],
                    role=SnowflakeConnector.snowflaky(role),
                ),
            }
        )

        usage_granted["schemas"].add(schema.upper())

        return (sql_commands, usage_granted)
