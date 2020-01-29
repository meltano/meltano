import cerberus
import click
import logging
import yaml
import re

from typing import Dict, List, Tuple

from meltano.core.permissions.utils.error import SpecLoadingError
from meltano.core.permissions.utils.snowflake_connector import SnowflakeConnector
from meltano.core.permissions.spec_schemas.snowflake import *
from meltano.core.permissions.utils.snowflake_grants import SnowflakeGrantsGenerator


VALIDATION_ERR_MSG = 'Spec error: {} "{}", field "{}": {}'


class SnowflakeSpecLoader:
    def __init__(self, spec_path: str) -> None:
        # Load the specification file and check for (syntactical) errors
        click.secho("Loading spec file", fg="green")
        self.spec = self.load_spec(spec_path)

        # Generate the entities (e.g databases, schemas, users, etc) referenced
        #  by the spec file and make sure that no syntatical or reference errors
        #  exist (all referenced entities are also defined by the spec)
        click.secho("Checking spec file for errors", fg="green")
        self.entities = self.inspect_spec()

        # Connect to Snowflake to make sure that all entities defined in the
        #  spec file are also defined in Snowflake (no missing databases, etc)
        click.secho(
            "Checking that all entities in the spec file are defined in Snowflake",
            fg="green",
        )
        self.check_entities_on_snowflake_server()

        # Get the privileges granted to users and roles in the Snowflake account
        # Used in order to figure out which permissions in the spec file are
        #  new ones and which already exist (and there is no need to re-grant them)
        click.secho("Fetching granted privileges from Snowflake", fg="green")
        self.grants_to_role = {}
        self.roles_granted_to_user = {}
        self.get_privileges_from_snowflake_server()

    def load_spec(self, spec_path: str) -> Dict:
        """
        Load a permissions specification from a file.

        If the file is not found or at least an error is found during validation,
        raise a SpecLoadingError with the appropriate error messages.

        Otherwise, return the valid specification as a Dictionary to be used
        in other operations.

        Raises a SpecLoadingError with all the errors found in the spec if at
        least one error is found.

        Returns the spec as a dictionary if everything is OK
        """
        try:
            with open(spec_path, "r") as stream:
                spec = yaml.safe_load(stream)
        except FileNotFoundError:
            raise SpecLoadingError(f"Spec File {spec_path} not found")

        error_messages = self.ensure_valid_schema(spec)
        if error_messages:
            raise SpecLoadingError("\n".join(error_messages))

        def lower_values(value):
            if isinstance(value, bool):
                return value
            elif isinstance(value, list):
                return [lower_values(entry) for entry in value]
            elif isinstance(value, str):
                return value.lower()
            elif isinstance(value, dict):
                return {k.lower(): lower_values(v) for k, v in value.items()}

        lower_spec = lower_values(spec)

        return lower_spec

    def ensure_valid_schema(self, spec: Dict) -> List[str]:
        """
        Ensure that the provided spec has no schema errors.

        Returns a list with all the errors found.
        """
        error_messages = []

        validator = cerberus.Validator(yaml.safe_load(SNOWFLAKE_SPEC_SCHEMA))
        validator.validate(spec)
        for entity_type, err_msg in validator.errors.items():
            if isinstance(err_msg[0], str):
                error_messages.append(f"Spec error: {entity_type}: {err_msg[0]}")
                continue

            for error in err_msg[0].values():
                error_messages.append(f"Spec error: {entity_type}: {error[0]}")

        if error_messages:
            return error_messages

        schema = {
            "databases": yaml.safe_load(SNOWFLAKE_SPEC_DATABASE_SCHEMA),
            "roles": yaml.safe_load(SNOWFLAKE_SPEC_ROLE_SCHEMA),
            "users": yaml.safe_load(SNOWFLAKE_SPEC_USER_SCHEMA),
            "warehouses": yaml.safe_load(SNOWFLAKE_SPEC_WAREHOUSE_SCHEMA),
        }

        validators = {
            "databases": cerberus.Validator(schema["databases"]),
            "roles": cerberus.Validator(schema["roles"]),
            "users": cerberus.Validator(schema["users"]),
            "warehouses": cerberus.Validator(schema["warehouses"]),
        }

        entities_by_type = [
            (entity_type, entities)
            for entity_type, entities in spec.items()
            if entities and entity_type != "version"
        ]

        for entity_type, entities in entities_by_type:
            for entity_dict in entities:
                for entity_name, config in entity_dict.items():
                    validators[entity_type].validate(config)
                    for field, err_msg in validators[entity_type].errors.items():
                        error_messages.append(
                            VALIDATION_ERR_MSG.format(
                                entity_type, entity_name, field, err_msg[0]
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

        Raises a SpecLoadingError with all the errors found in the spec if at
        least an error is found.

        Returns a dictionary with all the entities defined in the spec
        """
        entities, error_messages = self.generate_entities()

        error_messages.extend(self.ensure_valid_entity_names(entities))

        error_messages.extend(self.ensure_valid_references(entities))

        if error_messages:
            raise SpecLoadingError("\n".join(error_messages))

        return entities

    def generate_entities(self) -> Tuple[Dict, List[str]]:
        """
        Generate and return a dictionary with all the entities defined or
        referenced in the permissions specification file.

        The xxx_refs entities are referenced by various permissions.
        For example:
        'roles' --> All the roles defined in the spec
        'role_refs' --> All the roles referenced in a member_of permission
        'table_refs' --> All the tables referenced in read/write privileges
                         or in owns entries

        Returns a tuple (entities, error_messages) with all the entities defined
        in the spec and any errors found (e.g. a user not assigned their user role)
        """
        error_messages = []

        entities = {
            "databases": set(),
            "database_refs": set(),
            "shared_databases": set(),
            "schema_refs": set(),
            "table_refs": set(),
            "roles": set(),
            "role_refs": set(),
            "users": set(),
            "warehouses": set(),
            "warehouse_refs": set(),
        }

        entities_by_type = [
            (entity_type, entry)
            for entity_type, entry in self.spec.items()
            if entry and entity_type != "version"
        ]

        for entity_type, entry in entities_by_type:
            for entity_dict in entry:
                for entity_name, config in entity_dict.items():
                    if entity_type == "databases":
                        entities["databases"].add(entity_name)

                        if "shared" in config:
                            if type(config["shared"]) == bool:
                                if config["shared"]:
                                    entities["shared_databases"].add(entity_name)
                            else:
                                logging.debug(
                                    "`shared` for database {} must be boolean, skipping Role Reference generation.".format(
                                        entity_name
                                    )
                                )

                    elif entity_type == "roles":
                        entities["roles"].add(entity_name)

                        try:
                            for member_role in config["member_of"]:
                                entities["role_refs"].add(member_role)
                        except KeyError:
                            logging.debug(
                                "`member_of` not found for role {}, skipping Role Reference generation.".format(
                                    entity_name
                                )
                            )

                        try:
                            for warehouse in config["warehouses"]:
                                entities["warehouse_refs"].add(warehouse)
                        except KeyError:
                            logging.debug(
                                "`warehouses` not found for role {}, skipping Warehouse Reference generation.".format(
                                    entity_name
                                )
                            )

                        try:
                            for schema in config["privileges"]["databases"]["read"]:
                                entities["database_refs"].add(schema)
                        except KeyError:
                            logging.debug(
                                "`privileges.databases.read` not found for role {}, skipping Database Reference generation.".format(
                                    entity_name
                                )
                            )

                        try:
                            for schema in config["privileges"]["databases"]["write"]:
                                entities["database_refs"].add(schema)
                        except KeyError:
                            logging.debug(
                                "`privileges.databases.write` not found for role {}, skipping Database Reference generation.".format(
                                    entity_name
                                )
                            )

                        read_databases = (
                            config.get("privileges", {})
                            .get("databases", {})
                            .get("read", [])
                        )

                        write_databases = (
                            config.get("privileges", {})
                            .get("databases", {})
                            .get("write", [])
                        )

                        try:
                            for schema in config["privileges"]["schemas"]["read"]:
                                entities["schema_refs"].add(schema)
                                schema_db = schema.split(".")[0]
                                if schema_db not in read_databases:
                                    error_messages.append(
                                        f"Privilege Error: Database {schema_db} referenced in "
                                        "schema read privileges but not in database privileges "
                                        f"for role {entity_name}"
                                    )
                        except KeyError:
                            logging.debug(
                                "`privileges.schemas.read` not found for role {}, skipping Schema Reference generation.".format(
                                    entity_name
                                )
                            )

                        try:
                            for schema in config["privileges"]["schemas"]["write"]:
                                entities["schema_refs"].add(schema)
                                schema_db = schema.split(".")[0]
                                if schema_db not in write_databases:
                                    error_messages.append(
                                        f"Privilege Error: Database {schema_db} referenced in "
                                        "schema write privileges but not in database privileges "
                                        f"for role {entity_name}"
                                    )
                        except KeyError:
                            logging.debug(
                                "`privileges.schemas.write` not found for role {}, skipping Schema Reference generation.".format(
                                    entity_name
                                )
                            )

                        try:
                            for table in config["privileges"]["tables"]["read"]:
                                entities["table_refs"].add(table)
                                table_db = schema.split(".")[0]
                                if table_db not in read_databases:
                                    error_messages.append(
                                        f"Privilege Error: Database {table_db} referenced in "
                                        "table read privileges but not in database privileges "
                                        f"for role {entity_name}"
                                    )
                        except KeyError:
                            logging.debug(
                                "`privileges.tables.read` not found for role {}, skipping Table Reference generation.".format(
                                    entity_name
                                )
                            )

                        try:
                            for table in config["privileges"]["tables"]["write"]:
                                entities["table_refs"].add(table)
                                table_db = schema.split(".")[0]
                                if table_db not in write_databases:
                                    error_messages.append(
                                        f"Privilege Error: Database {table_db} referenced in "
                                        "table write privileges but not in database privileges "
                                        f"for role {entity_name}"
                                    )
                        except KeyError:
                            logging.debug(
                                "`privileges.tables.write` not found for role {}, skipping Table Reference generation.".format(
                                    entity_name
                                )
                            )

                        try:
                            for schema in config["owns"]["databases"]:
                                entities["database_refs"].add(schema)
                        except KeyError:
                            logging.debug(
                                "`owns.databases` not found for role {}, skipping Database Reference generation.".format(
                                    entity_name
                                )
                            )

                        try:
                            for schema in config["owns"]["schemas"]:
                                entities["schema_refs"].add(schema)
                        except KeyError:
                            logging.debug(
                                "`owns.schemas` not found for role {}, skipping Schema Reference generation.".format(
                                    entity_name
                                )
                            )

                        try:
                            for table in config["owns"]["tables"]:
                                entities["table_refs"].add(table)
                        except KeyError:
                            logging.debug(
                                "`owns.tables` not found for role {}, skipping Table Reference generation.".format(
                                    entity_name
                                )
                            )

                    elif entity_type == "users":
                        entities["users"].add(entity_name)

                        try:
                            for member_role in config["member_of"]:
                                entities["role_refs"].add(member_role)
                        except KeyError:
                            logging.debug(
                                "`member_of` not found for user {}, skipping Role Reference generation.".format(
                                    entity_name
                                )
                            )

                        try:
                            for schema in config["owns"]["databases"]:
                                entities["database_refs"].add(schema)
                        except KeyError:
                            logging.debug(
                                "`owns.databases` not found for user {}, skipping Database Reference generation.".format(
                                    entity_name
                                )
                            )

                        try:
                            for schema in config["owns"]["schemas"]:
                                entities["schema_refs"].add(schema)
                        except KeyError:
                            logging.debug(
                                "`owns.schemas` not found for user {}, skipping Schema Reference generation.".format(
                                    entity_name
                                )
                            )

                        try:
                            for table in config["owns"]["tables"]:
                                entities["table_refs"].add(table)
                        except KeyError:
                            logging.debug(
                                "`owns.tables` not found for user {}, skipping Table Reference generation.".format(
                                    entity_name
                                )
                            )

                    elif entity_type == "warehouses":
                        entities["warehouses"].add(entity_name)

        # Add implicit references to DBs and Schemas.
        #  e.g. RAW.MYSCHEMA.TABLE references also DB RAW and Schema MYSCHEMA
        for schema in entities["schema_refs"]:
            name_parts = schema.split(".")
            # Add the Database in the database refs
            if name_parts[0] != "*":
                entities["database_refs"].add(name_parts[0])

        for table in entities["table_refs"]:
            name_parts = table.split(".")
            # Add the Database in the database refs
            if name_parts[0] != "*":
                entities["database_refs"].add(name_parts[0])

            # Add the Schema in the schema refs
            if name_parts[1] != "*":
                entities["schema_refs"].add(f"{name_parts[0]}.{name_parts[1]}")

        return (entities, list(set(error_messages)))

    def ensure_valid_entity_names(self, entities: Dict) -> List[str]:
        """
        Check that all entity names are valid.

        Returns a list with all the errors found.
        """
        error_messages = []

        for db in entities["databases"].union(entities["database_refs"]):
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
                    " with *: DB.SCHEMA.[TABLE | *])"
                )

        return error_messages

    def ensure_valid_references(self, entities: Dict) -> List[str]:
        """
        Make sure that all references are well defined.

        Returns a list with all the errors found.
        """
        error_messages = []

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

        return error_messages

    def check_entities_on_snowflake_server(self) -> None:
        """
        Make sure that all [warehouses, dbs, schemas, tables, users, roles]
        referenced in the spec are defined in Snowflake.

        Raises a SpecLoadingError with all the errors found while checking
        Snowflake for missinf entities.
        """
        error_messages = []

        conn = SnowflakeConnector()

        warehouses = conn.show_warehouses()
        for warehouse in self.entities["warehouses"]:
            if warehouse not in warehouses:
                error_messages.append(
                    f"Missing Entity Error: Warehouse {warehouse} was not found on"
                    " Snowflake Server. Please create it before continuing."
                )

        databases = conn.show_databases()
        for db in self.entities["databases"]:
            if db not in databases:
                error_messages.append(
                    f"Missing Entity Error: Database {db} was not found on"
                    " Snowflake Server. Please create it before continuing."
                )

        schemas = conn.show_schemas()
        for schema in self.entities["schema_refs"]:
            if "*" not in schema and schema not in schemas:
                error_messages.append(
                    f"Missing Entity Error: Schema {schema} was not found on"
                    " Snowflake Server. Please create it before continuing."
                )

        tables = conn.show_tables()
        views = conn.show_views()
        for table in self.entities["table_refs"]:
            if "*" not in table and table not in tables and table not in views:
                error_messages.append(
                    f"Missing Entity Error: Table/View {table} was not found on"
                    " Snowflake Server. Please create it before continuing."
                )

        roles = conn.show_roles()
        for role in self.entities["roles"]:
            if role not in roles:
                error_messages.append(
                    f"Missing Entity Error: Role {role} was not found on"
                    " Snowflake Server. Please create it before continuing."
                )

        users = conn.show_users()
        for user in self.entities["users"]:
            if user not in users:
                error_messages.append(
                    f"Missing Entity Error: User {user} was not found on"
                    " Snowflake Server. Please create it before continuing."
                )

        if error_messages:
            raise SpecLoadingError("\n".join(error_messages))

    def get_privileges_from_snowflake_server(self) -> None:
        """
        Get the privileges granted to users and roles in the Snowflake account
        Gets the future privileges granted in all database and schema objects
        Consolidates role and future privileges into a single object for self.grants_to_role
        """
        conn = SnowflakeConnector()

        future_grants = {}
        for database in self.entities["database_refs"]:
            grant_results = conn.show_future_grants(database=database)

            for role in grant_results:
                for privilege in grant_results[role]:
                    for grant_on in grant_results[role][privilege]:
                        (
                            future_grants.setdefault(role, {})
                            .setdefault(privilege, {})
                            .setdefault(grant_on, [])
                            .extend(grant_results[role][privilege][grant_on])
                        )

            # Get all schemas in all ref'd databases. Not all schemas will be
            # ref'd in the spec.
            for schema in conn.show_schemas(database=database):
                grant_results = conn.show_future_grants(schema=schema)

                for role in grant_results:
                    for privilege in grant_results[role]:
                        for grant_on in grant_results[role][privilege]:
                            (
                                future_grants.setdefault(role, {})
                                .setdefault(privilege, {})
                                .setdefault(grant_on, [])
                                .extend(grant_results[role][privilege][grant_on])
                            )

        for role in self.entities["roles"]:
            grant_results = conn.show_grants_to_role(role)
            for privilege in grant_results:
                for grant_on in grant_results[privilege]:
                    (
                        future_grants.setdefault(role, {})
                        .setdefault(privilege, {})
                        .setdefault(grant_on, [])
                        .extend(grant_results[privilege][grant_on])
                    )

        self.grants_to_role = future_grants

        for user in self.entities["users"]:
            self.roles_granted_to_user[user] = conn.show_roles_granted_to_user(user)

    def generate_permission_queries(self) -> List[Dict]:
        """
        Starting point to generate all the permission queries.

        For each entity type (e.g. user or role) that is affected by the spec,
        the proper sql permission queries are generated.

        Returns all the SQL commands as a list.
        """
        sql_commands = []

        generator = SnowflakeGrantsGenerator(
            self.grants_to_role, self.roles_granted_to_user
        )

        click.secho("Generating permission Queries:", fg="green")

        # For each permission in the spec, check if we have to generate an
        #  SQL command granting that permission

        for entity_type, entry in self.spec.items():
            if entity_type in ["databases", "warehouses", "version"]:
                continue

            for entity_dict in entry:
                entity_configs = [
                    (entity_name, config)
                    for entity_name, config in entity_dict.items()
                    if config
                ]

                for entity_name, config in entity_configs:
                    if entity_type == "roles":
                        click.secho(f"     Processing role {entity_name}", fg="green")
                        sql_commands.extend(
                            generator.generate_grant_roles(
                                entity_type, entity_name, config
                            )
                        )

                        sql_commands.extend(
                            generator.generate_grant_ownership(entity_name, config)
                        )

                        sql_commands.extend(
                            generator.generate_grant_privileges_to_role(
                                entity_name,
                                config,
                                self.entities["shared_databases"],
                                self.entities["databases"],
                            )
                        )
                    elif entity_type == "users":
                        click.secho(f"     Processing user {entity_name}", fg="green")
                        sql_commands.extend(
                            generator.generate_alter_user(entity_name, config)
                        )

                        sql_commands.extend(
                            generator.generate_grant_roles(
                                entity_type, entity_name, config
                            )
                        )

        return self.remove_duplicate_queries(sql_commands)

    def remove_duplicate_queries(self, sql_commands: Dict) -> List[Dict]:
        grants = []
        revokes = []

        for i, command in reversed(list(enumerate(sql_commands))):
            # Find all "GRANT OWNERSHIP commands"
            if command["sql"].startswith("GRANT OWNERSHIP ON"):
                grant = command["sql"].split("TO ROLE", 1)[0]

                if grant in grants:
                    # If there is already a GRANT OWNERSHIP for the same
                    #  DB/SCHEMA/TABLE --> remove the one before it
                    #  (only keep the last one)
                    del sql_commands[i]
                else:
                    grants.append(grant)

            if command["sql"].startswith("REVOKE ALL"):
                revoke = command["sql"]
                if revoke in revokes:
                    # If there is already a REVOKE ALL for the same
                    #  DB/SCHEMA/TABLE --> remove the one before it
                    #  (only keep the last one)
                    del sql_commands[i]
                else:
                    revokes.append(revoke)

        return sql_commands
