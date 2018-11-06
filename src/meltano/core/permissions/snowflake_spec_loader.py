import cerberus
import yaml

from typing import Dict, List
from .error import SpecLoadingError


SNOWFLAKE_SPEC_DATABASE_SCHEMA = """
    type:
        type: string
        required: True
    """

SNOWFLAKE_SPEC_ROLE_SCHEMA = """
    type:
        type: string
        required: True
    warehouse:
        type: list
        schema:
            type: string
    member_of:
        type: list
        schema:
            type: string
    privileges:
        type: dict
        allowed:
            - databases
            - schemas
            - tables
        valueschema:
            type: dict
            allowed:
                - read
                - write
            valueschema:
                type: list
                schema:
                    type: string
    owns:
        type: dict
        allowed:
            - databases
            - schemas
            - tables
        valueschema:
            type: list
            schema:
                type: string
    """

SNOWFLAKE_SPEC_USER_SCHEMA = """
    type:
        type: string
        required: True
    can_login:
        type: boolean
        required: True
    warehouse:
        type: list
        schema:
            type: string
    member_of:
        type: list
        schema:
            type: string
    owns:
        type: dict
        allowed:
            - databases
            - schemas
            - tables
        valueschema:
            type: list
            schema:
                type: string
    """

SNOWFLAKE_SPEC_WAREHOUSE_SCHEMA = """
    type:
        type: string
        required: True
    size:
        type: string
        required: True
    """


VALIDATION_ERR_MSG = 'Spec error: {} "{}", field "{}": {}'


class SnowflakeSpecLoader:
    def __init__(self, spec_path: str) -> None:
        self.spec = self.load_spec(spec_path)

        self.entities = self.inspect_spec()


    def load_spec(self, spec_path: str) -> Dict:
        """
        Load a permissions specification from a file.

        If the file is not found or at least an error is found during validation,
        raise a SpecLoadingError with the appropriate error messages.

        Otherwise, return the valid specification as a Dictionary to be used
        in other operations.
        """
        try:
            with open(spec_path, 'r') as stream:
                spec = yaml.load(stream)
        except FileNotFoundError:
            raise SpecLoadingError(f"Spec File {spec_path} not found")

        error_messages = self.ensure_valid_schema(spec)
        if error_messages:
            raise SpecLoadingError('\n'.join(error_messages))

        return spec


    def ensure_valid_schema(self, spec: Dict) -> List[str]:
        """
        Ensure that the provided spec has no schema errors.

        Return a list with all the errors found.
        """
        error_messages = []

        schema = {
            'database': yaml.load(SNOWFLAKE_SPEC_DATABASE_SCHEMA),
            'role': yaml.load(SNOWFLAKE_SPEC_ROLE_SCHEMA),
            'user': yaml.load(SNOWFLAKE_SPEC_USER_SCHEMA),
            'warehouse': yaml.load(SNOWFLAKE_SPEC_WAREHOUSE_SCHEMA),
        }

        validators = {
            'database': cerberus.Validator(schema['database']),
            'role': cerberus.Validator(schema['role']),
            'user': cerberus.Validator(schema['user']),
            'warehouse': cerberus.Validator(schema['warehouse']),
        }

        for entity_name, config in spec.items():
            if not config:
                continue

            if 'type' not in config:
                error_messages.append(f'{entity_name} : has no type field')
                continue

            validators[config['type']].validate(config)
            for field, err_msg in validators[config['type']].errors.items():
                error_messages.append(VALIDATION_ERR_MSG.format(
                        config['type'],
                        entity_name,
                        field,
                        err_msg[0]
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

        if error_messages:
            raise SpecLoadingError('\n'.join(error_messages))

        return entities


    def generate_entities(self) -> Dict:
        entities = {
            'databases': set(),
            'database_refs': set(),
            'schema_refs': set(),
            'table_refs': set(),
            'roles': set(),
            'role_refs': set(),
            'users': set(),
            'warehouses': set(),
            'warehouse_refs': set(),
        }

        for entity_name, config in self.spec.items():
            permission_type = config['type']

            if permission_type == 'database':
                entities['databases'].add(entity_name)
            elif permission_type == 'role':
                entities['roles'].add(entity_name)

                if 'member_of' in config:
                    for member_role in config['member_of']:
                        entities['role_refs'].add(member_role)

                if 'warehouse' in config:
                    for warehouse in config['warehouse']:
                        entities['warehouse_refs'].add(warehouse)

                if 'privileges' in config:
                    if 'databases' in config['privileges']:
                        if 'read' in config['privileges']['databases']:
                            for schema in config['privileges']['databases']['read']:
                                entities['database_refs'].add(schema)

                        if 'write' in config['privileges']['databases']:
                            for schema in config['privileges']['databases']['write']:
                                entities['database_refs'].add(schema)

                    if 'schemas' in config['privileges']:
                        if 'read' in config['privileges']['schemas']:
                            for schema in config['privileges']['schemas']['read']:
                                entities['schema_refs'].add(schema)

                        if 'write' in config['privileges']['schemas']:
                            for schema in config['privileges']['schemas']['write']:
                                entities['schema_refs'].add(schema)

                    if 'tables' in config['privileges']:
                        if 'read' in config['privileges']['tables']:
                            for table in config['privileges']['tables']['read']:
                                entities['table_refs'].add(table)

                        if 'write' in config['privileges']['tables']:
                            for table in config['privileges']['tables']['write']:
                                entities['table_refs'].add(table)

                if 'owns' in config:
                    if 'databases' in config['owns']:
                        for schema in config['owns']['databases']:
                            entities['database_refs'].add(schema)

                    if 'schemas' in config['owns']:
                        for schema in config['owns']['schemas']:
                            entities['schema_refs'].add(schema)

                    if 'tables' in config['owns']:
                        for table in config['owns']['tables']:
                            entities['table_refs'].add(table)

            elif permission_type == 'user':
                entities['users'].add(entity_name)

                if 'member_of' in config:
                    for member_role in config['member_of']:
                        entities['role_refs'].add(member_role)

                if 'warehouse' in config:
                    for warehouse in config['warehouse']:
                        entities['warehouse_refs'].add(warehouse)

                if 'owns' in config:
                    if 'databases' in config['owns']:
                        for schema in config['owns']['databases']:
                            entities['database_refs'].add(schema)

                    if 'schemas' in config['owns']:
                        for schema in config['owns']['schemas']:
                            entities['schema_refs'].add(schema)

                    if 'tables' in config['owns']:
                        for table in config['owns']['tables']:
                            entities['table_refs'].add(table)

            elif permission_type == 'warehouse':
                entities['warehouses'].add(entity_name)

        return entities


    def generate_sql_commands(self) -> List[str]:
        sql_commands = []

        for entity_name, config in self.spec.items():
            alter_privileges = []

            if not config:
                continue

            permission_type = config['type']

            if permission_type == 'database':
                continue
            elif permission_type == 'role':
                sql_commands.extend(self.generate_grant_roles_to_role(entity_name, config))

                sql_commands.extend(self.generate_grant_ownership_to_role(entity_name, config))

                sql_commands.extend(self.generate_grant_privileges_to_role(entity_name, config))
            elif permission_type == 'user':
                sql_commands.extend(self.generate_alter_role(entity_name, config))

                sql_commands.extend(self.generate_grant_roles_to_role(entity_name, config))

                sql_commands.extend(self.generate_grant_ownership_to_role(entity_name, config))
            elif permission_type == 'warehouse':
                continue

        return sql_commands


    def generate_alter_role(self, role: str, config: str) -> List[str]:
        ALTER_ROLE_TEMPLATE = 'ALTER ROLE {role} {privileges}'

        sql_commands = []

        alter_privileges = []

        if 'can_login' in config:
            if config['can_login']:
                alter_privileges.append('LOGIN')
            else:
                alter_privileges.append('NOLOGIN')

        if 'is_superuser' in config:
            if config['is_superuser']:
                alter_privileges.append('SUPERUSER')
            else:
                alter_privileges.append('NOSUPERUSER')

        if alter_privileges:
            sql_commands.append(ALTER_ROLE_TEMPLATE.format(
                    role=role,
                    privileges=' '.join(alter_privileges)
                )
            )

        return sql_commands


    def generate_grant_roles_to_role(self, role: str, config: str) -> List[str]:
        GRANT_ROLE_TEMPLATE = 'GRANT {role_names} TO {role}'

        sql_commands = []

        role_names = []

        if 'member_of' in config:
            for member_role in config['member_of']:
                role_names.append(member_role)

        if role_names:
            sql_commands.append(GRANT_ROLE_TEMPLATE.format(
                    role=role,
                    role_names=', '.join(role_names)
                )
            )

        return sql_commands


    def generate_grant_ownership_to_role(self, role: str, config: str) -> List[str]:
        ALTER_SCHEMA_OWNER_TEMPLATE = 'ALTER SCHEMA {schema} OWNER TO {role}'

        sql_commands = []

        if 'owns' in config:

            if 'schemas' in config['owns']:
                for schema in config['owns']['schemas']:
                    sql_commands.append(ALTER_SCHEMA_OWNER_TEMPLATE.format(
                            role=role,
                            schema=schema
                        )
                    )

        return sql_commands


    def generate_grant_privileges_to_role(self, role: str, config: str) -> List[str]:
        GRANT_READ_ON_SCHEMA_TEMPLATE = 'GRANT USAGE ON SCHEMA {schema} TO {role}'
        GRANT_WRITE_ON_SCHEMA_TEMPLATE = 'GRANT CREATE ON SCHEMA {schema} TO {role}'
        GRANT_READ_ON_TABLE_TEMPLATE = 'GRANT SELECT ON TABLE {table} TO {role}'
        GRANT_WRITE_ON_TABLE_TEMPLATE = (
            "GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE, REFERENCES, TRIGGER "
            "ON TABLE {table} TO {role}"
        )
        GRANT_READ_ON_ALL_TABLES_TEMPLATE = 'GRANT SELECT ON ALL TABLES IN SCHEMA {schema} TO {role}'
        GRANT_WRITE_ON_ALL_TABLE_TEMPLATE = (
            "GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE, REFERENCES, TRIGGER "
            "ON ALL TABLES IN SCHEMA {schema} TO {role}"
        )

        sql_commands = []

        if 'privileges' in config:

            if 'schemas' in config['privileges']:
                if 'read' in config['privileges']['schemas']:
                    for schema in config['privileges']['schemas']['read']:
                        sql_commands.append(GRANT_READ_ON_SCHEMA_TEMPLATE.format(
                                role=role,
                                schema=schema
                            )
                        )

                if 'write' in config['privileges']['schemas']:
                    for schema in config['privileges']['schemas']['write']:
                        sql_commands.append(GRANT_WRITE_ON_SCHEMA_TEMPLATE.format(
                                role=role,
                                schema=schema
                            )
                        )

            if 'tables' in config['privileges']:
                if 'read' in config['privileges']['tables']:
                    for table in config['privileges']['tables']['read']:
                        if table.endswith('.*'):
                            schema = table[:-2]
                            sql_commands.append(GRANT_READ_ON_ALL_TABLES_TEMPLATE.format(
                                    role=role,
                                    schema=schema
                                )
                            )
                        else:
                            sql_commands.append(GRANT_READ_ON_TABLE_TEMPLATE.format(
                                    role=role,
                                    table=table
                                )
                            )

                if 'write' in config['privileges']['tables']:
                    for table in config['privileges']['tables']['write']:
                        if table.endswith('.*'):
                            schema = table[:-2]
                            sql_commands.append(GRANT_WRITE_ON_ALL_TABLE_TEMPLATE.format(
                                    role=role,
                                    schema=schema
                                )
                            )
                        else:
                            sql_commands.append(GRANT_WRITE_ON_TABLE_TEMPLATE.format(
                                    role=role,
                                    table=table
                                )
                            )

        return sql_commands
