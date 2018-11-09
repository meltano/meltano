SNOWFLAKE_SPEC_DATABASE_SCHEMA = """
    type:
        type: string
        required: True
    """

SNOWFLAKE_SPEC_ROLE_SCHEMA = """
    type:
        type: string
        required: True
    warehouses:
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
