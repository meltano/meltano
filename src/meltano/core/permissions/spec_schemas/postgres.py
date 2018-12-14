PG_SPEC_SCHEMA_YAML = """
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
