import cerberus
import yaml
import re

from typing import Dict, List

from meltano.core.permissions.utils.error import SpecLoadingError
from meltano.core.permissions.utils.snowflake_connector import SnowflakeConnector
from meltano.core.permissions.spec_schemas.snowflake import *


VALIDATION_ERR_MSG = 'Spec error: {} "{}", field "{}": {}'


class SnowflakeSpecLoader:
    def __init__(self, spec_path: str) -> None:
        # Load the specification file and check for (syntactical) errors
        self.spec = self.load_spec(spec_path)

        # Generate the entities (e.g databases, schemas, users, etc) referenced
        #  by the spec file and make sure that no syntatical or refernce errors
        #  exist (all referenced entities are also defined by the spec)
        self.entities = self.inspect_spec()

        # Connect to Snowflake to make sure that all entities defined in the
        #  spec file are also defined in Snowflake (no missing databases, etc)
        self.check_entities_on_snowflake_server()

    def load_spec(self, spec_path: str) -> Dict:
        """
        Load a permissions specification from a file.

        If the file is not found or at least an error is found during validation,
        raise a SpecLoadingError with the appropriate error messages.

        Otherwise, return the valid specification as a Dictionary to be used
        in other operations.
        """
        try:
            with open(spec_path, "r") as stream:
                spec = yaml.load(stream)
        except FileNotFoundError:
            raise SpecLoadingError(f"Spec File {spec_path} not found")

        error_messages = self.ensure_valid_schema(spec)
        if error_messages:
            raise SpecLoadingError("\n".join(error_messages))

        return spec

    def ensure_valid_schema(self, spec: Dict) -> List[str]:
        """
        Ensure that the provided spec has no schema errors.

        Return a list with all the errors found.
        """
        error_messages = []

        schema = {
            "database": yaml.load(SNOWFLAKE_SPEC_DATABASE_SCHEMA),
            "role": yaml.load(SNOWFLAKE_SPEC_ROLE_SCHEMA),
            "user": yaml.load(SNOWFLAKE_SPEC_USER_SCHEMA),
            "warehouse": yaml.load(SNOWFLAKE_SPEC_WAREHOUSE_SCHEMA),
        }

        validators = {
            "database": cerberus.Validator(schema["database"]),
            "role": cerberus.Validator(schema["role"]),
            "user": cerberus.Validator(schema["user"]),
            "warehouse": cerberus.Validator(schema["warehouse"]),
        }

        for entity_name, config in spec.items():
            if not config:
                continue

            if "type" not in config:
                error_messages.append(f"Spec error: {entity_name} has no type field")
                continue

            validators[config["type"]].validate(config)
            for field, err_msg in validators[config["type"]].errors.items():
                error_messages.append(
                    VALIDATION_ERR_MSG.format(
                        config["type"], entity_name, field, err_msg[0]
                    )
                )

        return error_messages

    def inspect_spec(self) -> Dict:
        """
        Inspect a valid spec and make sure that no logic errors exist.

        e.g. a role granted to a user not defined in roles
             or a user given acces to a database not defined in databases

        If at least an error is found during inspection, raise a
        SpecLoadingError with the appropriate error messages.

        Otherwise, return the entities found as a Dictionary to be used
        in other operations.
        """
        error_messages = []

        entities = self.generate_entities()

        # Check that all the referenced entities are also defined
        for database in entities["database_refs"]:
            if database not in entities["databases"]:
                error_messages.append(
                    f"Reference error: Database {database} is referenced "
                    "in the spec but not defined"
                )

        for role in entities["role_refs"]:
            if role not in entities["roles"]:
                error_messages.append(
                    f"Reference error: Role {role} is referenced in the "
                    "spec but not defined"
                )

        for warehouse in entities["warehouse_refs"]:
            if warehouse not in entities["warehouses"]:
                error_messages.append(
                    f"Reference error: Warehouse {warehouse} is referenced "
                    "in the spec but not defined"
                )

        # Check that all users have a same name role defined
        for user in entities["users"]:
            if f"{user}_role" not in entities["roles"]:
                error_messages.append(
                    f"Missing role {user}_role for user {user}. All users must "
                    "have a role defined in order to assign user specific "
                    "permissions. The name of the role for a user XXX should "
                    "be XXX_role."
                )

        if error_messages:
            raise SpecLoadingError("\n".join(error_messages))

        return entities

    def generate_entities(self) -> Dict:
        """
        Generate and return a dictionary with all the entities defined or
        referenced in the permissions specification file.

        The xxx_refs entities are referenced by various permissions.
        For example:
        'roles' --> All the roles defined in the spec
        'role_refs' --> All the roles referenced in a member_of permission
        'table_refs' --> All the tables referenced in read/write privileges
                         or in owns entries
        """
        error_messages = []

        entities = {
            "databases": set(),
            "database_refs": set(),
            "schema_refs": set(),
            "table_refs": set(),
            "roles": set(),
            "role_refs": set(),
            "users": set(),
            "warehouses": set(),
            "warehouse_refs": set(),
        }

        for entity_name, config in self.spec.items():
            permission_type = config["type"]

            if permission_type == "database":
                entities["databases"].add(entity_name)
            elif permission_type == "role":
                entities["roles"].add(entity_name)

                if "member_of" in config:
                    for member_role in config["member_of"]:
                        entities["role_refs"].add(member_role)

                if "warehouses" in config:
                    for warehouse in config["warehouses"]:
                        entities["warehouse_refs"].add(warehouse)

                if "privileges" in config:
                    if "databases" in config["privileges"]:
                        if "read" in config["privileges"]["databases"]:
                            for schema in config["privileges"]["databases"]["read"]:
                                entities["database_refs"].add(schema)

                        if "write" in config["privileges"]["databases"]:
                            for schema in config["privileges"]["databases"]["write"]:
                                entities["database_refs"].add(schema)

                    if "schemas" in config["privileges"]:
                        if "read" in config["privileges"]["schemas"]:
                            for schema in config["privileges"]["schemas"]["read"]:
                                entities["schema_refs"].add(schema)

                        if "write" in config["privileges"]["schemas"]:
                            for schema in config["privileges"]["schemas"]["write"]:
                                entities["schema_refs"].add(schema)

                    if "tables" in config["privileges"]:
                        if "read" in config["privileges"]["tables"]:
                            for table in config["privileges"]["tables"]["read"]:
                                entities["table_refs"].add(table)

                        if "write" in config["privileges"]["tables"]:
                            for table in config["privileges"]["tables"]["write"]:
                                entities["table_refs"].add(table)

                if "owns" in config:
                    if "databases" in config["owns"]:
                        for schema in config["owns"]["databases"]:
                            entities["database_refs"].add(schema)

                    if "schemas" in config["owns"]:
                        for schema in config["owns"]["schemas"]:
                            entities["schema_refs"].add(schema)

                    if "tables" in config["owns"]:
                        for table in config["owns"]["tables"]:
                            entities["table_refs"].add(table)

            elif permission_type == "user":
                # Check if this user is member of the user role ($USER_role)
                is_member_of_user_role = False

                entities["users"].add(entity_name)

                if "member_of" in config:
                    for member_role in config["member_of"]:
                        entities["role_refs"].add(member_role)

                        if member_role == f"{entity_name}_role":
                            is_member_of_user_role = True

                if is_member_of_user_role == False:
                    error_messages.append(
                        f"Role error: User {entity_name} in not a member of her "
                        f"user role ({entity_name}_role)"
                    )

                if "owns" in config:
                    if "databases" in config["owns"]:
                        for schema in config["owns"]["databases"]:
                            entities["database_refs"].add(schema)

                    if "schemas" in config["owns"]:
                        for schema in config["owns"]["schemas"]:
                            entities["schema_refs"].add(schema)

                    if "tables" in config["owns"]:
                        for table in config["owns"]["tables"]:
                            entities["table_refs"].add(table)

            elif permission_type == "warehouse":
                entities["warehouses"].add(entity_name)

        # Check that all names are valid and also add implicit references to
        #  DBs and Schemas. e.g. RAW.TEST_SCHEMA.TABLE references also
        #  DB RAW and Schema TEST_SCHEMA
        for db in entities["databases"] | entities["database_refs"]:
            name_parts = db.split(".")
            if not len(name_parts) == 1:
                error_messages.append(
                    f"Name error: Not a valid database name: {db}"
                    " (Proper definition: DB)"
                )

        for schema in entities["schema_refs"]:
            name_parts = schema.split(".")
            if (not len(name_parts) == 2) or (name_parts[0] == "*"):
                error_messages.append(
                    f"Name error: Not a valid schema name: {schema}"
                    " (Proper definition: DB.[SCHEMA | *])"
                )

            # Add the Database in the database refs
            if name_parts[0] != "*":
                entities["database_refs"].add(name_parts[0])

        for table in entities["table_refs"]:
            name_parts = table.split(".")
            if (not len(name_parts) == 3) or (name_parts[0] == "*"):
                error_messages.append(
                    f"Name error: Not a valid table name: {table}"
                    " (Proper definition: DB.[SCHEMA | *].[TABLE | *])"
                )
            elif name_parts[1] == "*" and name_parts[2] != "*":
                error_messages.append(
                    f"Name error: Not a valid table name: {table}"
                    " (Can't have a Table name after selecting all schemas"
                    " with *: DB.[SCHEMA | *].[TABLE | *])"
                )

            # Add the Database in the database refs
            if name_parts[0] != "*":
                entities["database_refs"].add(name_parts[0])

            # Add the Schema in the schema refs
            if name_parts[1] != "*":
                entities["schema_refs"].add(f"{name_parts[0]}.{name_parts[1]}")

        if error_messages:
            raise SpecLoadingError("\n".join(error_messages))

        return entities

    def check_entities_on_snowflake_server(self) -> None:
        error_messages = []

        conn = SnowflakeConnector()

        warehouses = conn.show_warehouses()
        for warehouse in self.entities["warehouses"]:
            if warehouse.upper() not in warehouses:
                error_messages.append(
                    f"Missing Entity Error: Warehouse {warehouse} was not found on"
                    " Snowflake Server. Please create it before continuing."
                )

        databases = conn.show_databases()
        for db in self.entities["databases"]:
            if db.upper() not in databases:
                error_messages.append(
                    f"Missing Entity Error: Database {db} was not found on"
                    " Snowflake Server. Please create it before continuing."
                )

        schemas = conn.show_schemas()
        for schema in self.entities["schema_refs"]:
            if "*" not in schema and schema.upper() not in schemas:
                error_messages.append(
                    f"Missing Entity Error: Schema {schema} was not found on"
                    " Snowflake Server. Please create it before continuing."
                )

        tables = conn.show_tables()
        for table in self.entities["table_refs"]:
            if "*" not in table and table.upper() not in tables:
                error_messages.append(
                    f"Missing Entity Error: Table {table} was not found on"
                    " Snowflake Server. Please create it before continuing."
                )

        roles = conn.show_roles()
        for role in self.entities["roles"]:
            if role.upper() not in roles:
                error_messages.append(
                    f"Missing Entity Error: Role {role} was not found on"
                    " Snowflake Server. Please create it before continuing."
                )

        users = conn.show_users()
        for user in self.entities["users"]:
            if user.upper() not in users:
                error_messages.append(
                    f"Missing Entity Error: User {user} was not found on"
                    " Snowflake Server. Please create it before continuing."
                )

        if error_messages:
            raise SpecLoadingError("\n".join(error_messages))

    def generate_permission_queries(self) -> List[str]:
        sql_commands = []

        # For each permission in the spec, check if we have to generate an
        #  SQL command granting that permission
        for entity_name, config in self.spec.items():
            alter_privileges = []

            if not config:
                continue

            permission_type = config["type"]

            if permission_type == "database":
                continue
            elif permission_type == "role":
                sql_commands.extend(
                    self.generate_grant_roles("ROLE", entity_name, config)
                )

                sql_commands.extend(self.generate_grant_ownership(entity_name, config))

                sql_commands.extend(
                    self.generate_grant_privileges_to_role(entity_name, config)
                )
            elif permission_type == "user":
                sql_commands.extend(self.generate_alter_user(entity_name, config))

                sql_commands.extend(
                    self.generate_grant_roles("USER", entity_name, config)
                )
            elif permission_type == "warehouse":
                continue

        return sql_commands

    def generate_alter_user(self, user: str, config: str) -> List[str]:
        ALTER_USER_TEMPLATE = "ALTER USER {user_name} SET {privileges}"

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

    def generate_grant_roles(
        self, entity_type: str, entity: str, config: str
    ) -> List[str]:
        GRANT_ROLE_TEMPLATE = "GRANT {role_name} TO {type} {entity_name}"
        sql_commands = []

        if "member_of" in config:
            for member_role in config["member_of"]:
                sql_commands.append(
                    GRANT_ROLE_TEMPLATE.format(
                        role_name=member_role, type=entity_type, entity_name=entity
                    )
                )

        return sql_commands

    def generate_grant_ownership(self, role: str, config: str) -> List[str]:
        Grant_Ownership_TEMPLATE = (
            "GRANT OWNERSHIP"
            " ON {resource_type} {resource_name}"
            " TO ROLE {role_name} COPY CURRENT GRANTS"
        )

        sql_commands = []

        if "owns" in config:
            if "databases" in config["owns"]:
                for database in config["owns"]["databases"]:
                    sql_commands.append(
                        Grant_Ownership_TEMPLATE.format(
                            resource_type="DATABASE",
                            resource_name=database,
                            role_name=role,
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
                                Grant_Ownership_TEMPLATE.format(
                                    resource_type="SCHEMA",
                                    resource_name=db_schema,
                                    role_name=role,
                                )
                            )
                    else:
                        sql_commands.append(
                            Grant_Ownership_TEMPLATE.format(
                                resource_type="SCHEMA",
                                resource_name=name_parts[1],
                                role_name=role,
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
                            schemas = [name_parts[1]]

                        for schema in schemas:
                            sql_commands.append(
                                Grant_Ownership_TEMPLATE.format(
                                    resource_type="ALL TABLES IN SCHEMA",
                                    resource_name=schema,
                                    role_name=role,
                                )
                            )
                    else:
                        sql_commands.append(
                            Grant_Ownership_TEMPLATE.format(
                                resource_type="TABLE",
                                resource_name=name_parts[2],
                                role_name=role,
                            )
                        )

        return sql_commands

    def generate_grant_privileges_to_role(self, role: str, config: str) -> List[str]:
        sql_commands = []

        Privileges_TEMPLATE = (
            "GRANT {privileges} ON {resource_type} {resource_name} TO ROLE {role}"
        )

        if "warehouses" in config:
            for warehouse in config["warehouses"]:
                sql_commands.append(
                    Privileges_TEMPLATE.format(
                        privileges="USAGE",
                        resource_type="WAREHOUSE",
                        resource_name=warehouse,
                        role=role,
                    )
                )

        if "privileges" in config:

            if "databases" in config["privileges"]:
                if "read" in config["privileges"]["databases"]:
                    for database in config["privileges"]["databases"]["read"]:
                        sql_commands.append(
                            Privileges_TEMPLATE.format(
                                privileges="USAGE",
                                resource_type="DATABASE",
                                resource_name=database,
                                role=role,
                            )
                        )

                if "write" in config["privileges"]["databases"]:
                    for database in config["privileges"]["databases"]["write"]:
                        sql_commands.append(
                            Privileges_TEMPLATE.format(
                                privileges="USAGE, MONITOR, CREATE SCHEMA",
                                resource_type="DATABASE",
                                resource_name=database,
                                role=role,
                            )
                        )

            if "schemas" in config["privileges"]:
                if "read" in config["privileges"]["schemas"]:
                    Schema_Read_Privileges = "USAGE, MONITOR"

                    for schema in config["privileges"]["schemas"]["read"]:
                        name_parts = schema.split(".")
                        if name_parts[1] == "*":
                            sql_commands.append(
                                Privileges_TEMPLATE.format(
                                    privileges=Schema_Read_Privileges,
                                    resource_type="ALL SCHEMAS IN DATABASE",
                                    resource_name=name_parts[0],
                                    role=role,
                                )
                            )
                        else:
                            sql_commands.append(
                                Privileges_TEMPLATE.format(
                                    privileges=Schema_Read_Privileges,
                                    resource_type="SCHEMA",
                                    resource_name=name_parts[1],
                                    role=role,
                                )
                            )

                if "write" in config["privileges"]["schemas"]:
                    Schema_Write_Privileges = (
                        "USAGE, MONITOR, CREATE TABLE,"
                        " CREATE VIEW, CREATE STAGE, CREATE FILE FORMAT,"
                        " CREATE SEQUENCE, CREATE FUNCTION, CREATE PIPE"
                    )

                    for schema in config["privileges"]["schemas"]["write"]:
                        name_parts = schema.split(".")
                        if name_parts[1] == "*":
                            sql_commands.append(
                                Privileges_TEMPLATE.format(
                                    privileges=Schema_Write_Privileges,
                                    resource_type="ALL SCHEMAS IN DATABASE",
                                    resource_name=name_parts[0],
                                    role=role,
                                )
                            )
                        else:
                            sql_commands.append(
                                Privileges_TEMPLATE.format(
                                    privileges=Schema_Write_Privileges,
                                    resource_type="SCHEMA",
                                    resource_name=name_parts[1],
                                    role=role,
                                )
                            )

            if "tables" in config["privileges"]:
                if "read" in config["privileges"]["tables"]:
                    for table in config["privileges"]["tables"]["read"]:
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
                                schemas = [name_parts[1]]

                            for schema in schemas:
                                sql_commands.append(
                                    Privileges_TEMPLATE.format(
                                        privileges="SELECT",
                                        resource_type="ALL TABLES IN SCHEMA",
                                        resource_name=schema,
                                        role=role,
                                    )
                                )
                        else:
                            sql_commands.append(
                                Privileges_TEMPLATE.format(
                                    privileges="SELECT",
                                    resource_type="TABLE",
                                    resource_name=name_parts[2],
                                    role=role,
                                )
                            )

                if "write" in config["privileges"]["tables"]:
                    Table_Write_Privileges = (
                        "SELECT, INSERT, UPDATE, DELETE, TRUNCATE, REFERENCES"
                    )

                    for table in config["privileges"]["tables"]["write"]:
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
                                schemas = [name_parts[1]]

                            for schema in schemas:
                                sql_commands.append(
                                    Privileges_TEMPLATE.format(
                                        privileges=Table_Write_Privileges,
                                        resource_type="ALL TABLES IN SCHEMA",
                                        resource_name=schema,
                                        role=role,
                                    )
                                )
                        else:
                            sql_commands.append(
                                Privileges_TEMPLATE.format(
                                    privileges=Table_Write_Privileges,
                                    resource_type="TABLE",
                                    resource_name=name_parts[2],
                                    role=role,
                                )
                            )

        return sql_commands
