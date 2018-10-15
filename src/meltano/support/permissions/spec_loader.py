import argparse
import cerberus
import sys
import yaml

from typing import Dict, List

SPEC_SCHEMA_YAML = """
    can_login:
        type: boolean
    is_superuser:
        type: boolean
    member_of:
        type: list
        schema:
            type: string
    owns:
        type: dict
        allowed:
            - schemas
        valueschema:
            type: list
            schema:
                type: string
    privileges:
        type: dict
        allowed:
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
    """


VALIDATION_ERR_MSG = 'Spec error: Role "{}", field "{}": {}'


def fail(msg: str):
    # click.secho(msg, fg='red')
    print(f'{msg}')
    sys.exit(1)

def load_spec(spec_path: str) -> Dict:

    with open(spec_path, 'r') as stream:
        spec = yaml.load(stream)

    error_messages = ensure_valid_schema(spec)
    if error_messages:
        fail('\n'.join(error_messages))

    return spec

def ensure_valid_schema(spec: Dict) -> List[str]:
    """ Ensure spec has no schema errors """
    error_messages = []

    schema = yaml.load(SPEC_SCHEMA_YAML)
    v = cerberus.Validator(schema)
    for rolename, config in spec.items():
        if not config:
            continue
        v.validate(config)
        for field, err_msg in v.errors.items():
            error_messages.append(VALIDATION_ERR_MSG.format(rolename, field, err_msg[0]))

    return error_messages


def generate_sql_commands(spec: Dict) -> List[str]:
    sql_commands = []

    for role, config in spec.items():
        alter_privileges = []

        if not config:
            continue

        sql_commands.extend(generate_alter_role(role, config))

        sql_commands.extend(generate_grant_roles_to_role(role, config))

        sql_commands.extend(generate_grant_ownership_to_role(role, config))

        sql_commands.extend(generate_grant_privileges_to_role(role, config))

    return sql_commands


def generate_alter_role(role: str, config: str) -> List[str]:
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


def generate_grant_roles_to_role(role: str, config: str) -> List[str]:
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


def generate_grant_ownership_to_role(role: str, config: str) -> List[str]:
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


def generate_grant_privileges_to_role(role: str, config: str) -> List[str]:
    GRANT_READ_ON_SCHEMA_TEMPLATE = 'GRANT USAGE ON SCHEMA {schema} TO {role}'
    GRANT_WRITE_ON_SCHEMA_TEMPLATE = 'GRANT CREATE ON SCHEMA {schema} TO {role}'
    GRANT_READ_ON_TABLE_TEMPLATE = 'GRANT SELECT ON TABLE {table} TO {role}'
    GRANT_WRITE_ON_TABLE_TEMPLATE = '''
        GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE, REFERENCES, TRIGGER
        ON TABLE {table} TO {role}
    '''
    GRANT_READ_ON_ALL_TABLES_TEMPLATE = 'GRANT SELECT ON ALL TABLES IN SCHEMA {schema} TO {role}'
    GRANT_WRITE_ON_ALL_TABLE_TEMPLATE = '''
        GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE, REFERENCES, TRIGGER
        ON ALL TABLES IN SCHEMA {schema} TO {role}
    '''

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


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('spec', help='The spec file path')
    args = parser.parse_args()

    if args.spec:
        spec = load_spec(args.spec)

        sql_commands = generate_sql_commands(spec)

        for command in sql_commands:
            print(command)
    else:
        raise Exception("No spec file provided")
