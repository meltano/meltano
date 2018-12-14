import cerberus
import logging
import yaml

from typing import Dict, List
from meltano.core.permissions.utils.error import SpecLoadingError
from meltano.core.permissions.spec_schemas.postgres import *


VALIDATION_ERR_MSG = 'Spec error: Role "{}", field "{}": {}'


class PGSpecLoader:
    def __init__(self, spec_path: str) -> None:
        self.spec = self.load_spec(spec_path)

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

        schema = yaml.load(PG_SPEC_SCHEMA_YAML)
        v = cerberus.Validator(schema)

        role_configs = [(role, config) for role, config in spec.items() if config]

        for role, config in role_configs:
            v.validate(config)
            for field, err_msg in v.errors.items():
                error_messages.append(
                    VALIDATION_ERR_MSG.format(role, field, err_msg[0])
                )

        return error_messages

    def generate_permission_queries(self) -> List[str]:
        sql_commands = []

        role_configs = [(role, config) for role, config in self.spec.items() if config]

        for role, config in role_configs:
            sql_commands.extend(self.generate_alter_role(role, config))
            sql_commands.extend(self.generate_grant_roles_to_role(role, config))
            sql_commands.extend(self.generate_grant_ownership_to_role(role, config))
            sql_commands.extend(self.generate_grant_privileges_to_role(role, config))

        return sql_commands

    def generate_alter_role(self, role: str, config: Dict) -> List[str]:
        ALTER_ROLE_TEMPLATE = "ALTER ROLE {role} {privileges}"
        sql_commands = []
        alter_privileges = []

        try:
            if config["can_login"]:
                alter_privileges.append("LOGIN")
            else:
                alter_privileges.append("NOLOGIN")
        except KeyError:
            logging.debug(
                "`can_login` not found for {}, skipping login rules.".format(role)
            )

        try:
            if config["is_superuser"]:
                alter_privileges.append("SUPERUSER")
            else:
                alter_privileges.append("NOSUPERUSER")
        except KeyError:
            logging.debug(
                "`is_superuser` not found for {}, skipping superuser rules.".format(
                    role
                )
            )

        if alter_privileges:
            sql_commands.append(
                ALTER_ROLE_TEMPLATE.format(
                    role=role, privileges=" ".join(alter_privileges)
                )
            )

        return sql_commands

    def generate_grant_roles_to_role(self, role: str, config: Dict) -> List[str]:
        GRANT_ROLE_TEMPLATE = "GRANT {role_names} TO {role}"
        sql_commands = []

        role_names = config.get("member_of", [])

        if role_names:
            sql_commands.append(
                GRANT_ROLE_TEMPLATE.format(role=role, role_names=", ".join(role_names))
            )

        return sql_commands

    def generate_grant_ownership_to_role(self, role: str, config: Dict) -> List[str]:
        ALTER_SCHEMA_OWNER_TEMPLATE = "ALTER SCHEMA {schema} OWNER TO {role}"
        sql_commands = []

        try:
            for schema in config["owns"]["schemas"]:
                sql_commands.append(
                    ALTER_SCHEMA_OWNER_TEMPLATE.format(role=role, schema=schema)
                )
        except KeyError:
            logging.debug(
                "`owns.schemas` not found for {}, skipping OWNership rules.".format(
                    role
                )
            )

        return sql_commands

    def generate_grant_privileges_to_role(self, role: str, config: Dict) -> List[str]:
        GRANT_READ_ON_SCHEMA_TEMPLATE = "GRANT USAGE ON SCHEMA {schema} TO {role}"
        GRANT_WRITE_ON_SCHEMA_TEMPLATE = "GRANT CREATE ON SCHEMA {schema} TO {role}"
        GRANT_READ_ON_TABLE_TEMPLATE = "GRANT SELECT ON TABLE {table} TO {role}"
        GRANT_WRITE_ON_TABLE_TEMPLATE = (
            "GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE, REFERENCES, TRIGGER "
            "ON TABLE {table} TO {role}"
        )
        GRANT_READ_ON_ALL_TABLES_TEMPLATE = (
            "GRANT SELECT ON ALL TABLES IN SCHEMA {schema} TO {role}"
        )
        GRANT_WRITE_ON_ALL_TABLE_TEMPLATE = (
            "GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE, REFERENCES, TRIGGER "
            "ON ALL TABLES IN SCHEMA {schema} TO {role}"
        )

        sql_commands = []

        try:
            for schema in config["privileges"]["schemas"]["read"]:
                sql_commands.append(
                    GRANT_READ_ON_SCHEMA_TEMPLATE.format(role=role, schema=schema)
                )
        except KeyError:
            logging.debug(
                "`privileges.schemas.read` not found for {}, skipping Schema Read GRANTS.".format(
                    role
                )
            )

        try:
            for schema in config["privileges"]["schemas"]["write"]:
                sql_commands.append(
                    GRANT_WRITE_ON_SCHEMA_TEMPLATE.format(role=role, schema=schema)
                )
        except KeyError:
            logging.debug(
                "`privileges.schemas.write` not found for {}, skipping Schema Write GRANTS.".format(
                    role
                )
            )

        try:
            for table in config["privileges"]["tables"]["read"]:
                if table.endswith(".*"):
                    schema = table[:-2]
                    sql_commands.append(
                        GRANT_READ_ON_ALL_TABLES_TEMPLATE.format(
                            role=role, schema=schema
                        )
                    )
                else:
                    sql_commands.append(
                        GRANT_READ_ON_TABLE_TEMPLATE.format(role=role, table=table)
                    )
        except KeyError:
            logging.debug(
                "`privileges.tables.read` not found for {}, skipping Table Read GRANTS.".format(
                    role
                )
            )

        try:
            for table in config["privileges"]["tables"]["write"]:
                if table.endswith(".*"):
                    schema = table[:-2]
                    sql_commands.append(
                        GRANT_WRITE_ON_ALL_TABLE_TEMPLATE.format(
                            role=role, schema=schema
                        )
                    )
                else:
                    sql_commands.append(
                        GRANT_WRITE_ON_TABLE_TEMPLATE.format(role=role, table=table)
                    )
        except KeyError:
            logging.debug(
                "`privileges.tables.write` not found for {}, skipping Table Write GRANTS.".format(
                    role
                )
            )

        return sql_commands
