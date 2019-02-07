import logging
import os
import re

from typing import Dict, List
from sqlalchemy import create_engine
from snowflake.sqlalchemy import URL


# Don't show all the info log messages from Snowflake
for logger_name in ["snowflake.connector", "botocore", "boto3"]:
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.WARNING)


class SnowflakeConnector:
    def __init__(self, config: Dict = None) -> None:
        if not config:
            config = {
                "user": os.getenv("PERMISSION_BOT_USER"),
                "password": os.getenv("PERMISSION_BOT_PASSWORD"),
                "account": os.getenv("PERMISSION_BOT_ACCOUNT"),
                "database": os.getenv("PERMISSION_BOT_DATABASE"),
                "role": os.getenv("PERMISSION_BOT_ROLE"),
                "warehouse": os.getenv("PERMISSION_BOT_WAREHOUSE"),
            }

        self.engine = create_engine(
            URL(
                user=config["user"],
                password=config["password"],
                account=config["account"],
                database=config["database"],
                role=config["role"],
                warehouse=config["warehouse"],
                # Enable the insecure_mode if you get OCSP errors while testing
                # insecure_mode=True,
            )
        )

    def show_query(self, entity) -> List[str]:
        names = []

        query = f"SHOW {entity}"
        with self.engine.connect() as connection:
            results = connection.execute(query).fetchall()

            for result in results:
                names.append(result["name"].upper())

        return names

    def show_databases(self) -> List[str]:
        return self.show_query("DATABASES")

    def show_warehouses(self) -> List[str]:
        return self.show_query("WAREHOUSES")

    def show_roles(self) -> List[str]:
        return self.show_query("ROLES")

    def show_users(self) -> List[str]:
        return self.show_query("USERS")

    def show_schemas(self, database: str = None) -> List[str]:
        names = []

        if database:
            query = f"SHOW TERSE SCHEMAS IN DATABASE {database}"
        else:
            query = f"SHOW TERSE SCHEMAS IN ACCOUNT"

        with self.engine.connect() as connection:
            results = connection.execute(query).fetchall()

            for result in results:
                names.append(
                    f"{result['database_name'].upper()}.{result['name'].upper()}"
                )

        return names

    def show_tables(self, database: str = None, schema: str = None) -> List[str]:
        names = []

        if schema:
            query = f"SHOW TERSE TABLES IN SCHEMA {schema}"
        elif database:
            query = f"SHOW TERSE TABLES IN DATABASE {database}"
        else:
            query = f"SHOW TERSE TABLES IN ACCOUNT"

        with self.engine.connect() as connection:
            results = connection.execute(query).fetchall()

            for result in results:
                names.append(
                    f"{result['database_name'].upper()}"
                    + f".{result['schema_name'].upper()}"
                    + f".{result['name'].upper()}"
                )

        return names

    def show_grants_to_role(self, role) -> List[str]:
        grants = {}

        query = f"SHOW GRANTS TO ROLE {SnowflakeConnector.snowflaky(role)}"
        with self.engine.connect() as connection:
            results = connection.execute(query).fetchall()

            for result in results:
                privilege = result["privilege"].upper()
                granted_on = result["granted_on"].upper()

                grants[privilege] = grants.get(privilege, {})
                grants[privilege][granted_on] = grants[privilege].get(granted_on, [])
                grants[privilege][granted_on].append(result["name"].upper())

        return grants

    def show_roles_granted_to_user(self, user) -> List[str]:
        roles = []

        query = f"SHOW GRANTS TO USER {SnowflakeConnector.snowflaky(user)}"
        with self.engine.connect() as connection:
            results = connection.execute(query).fetchall()

            for result in results:
                roles.append(result["role"].upper())

        return roles

    def snowflaky(name: str) -> str:
        """
        Convert an entity name to an object identifier that will most probably be
        the proper name for Snoflake.

        e.g. gitlab-ci --> "gitlab-ci"
             527-INVESTIGATE$ISSUES.ANALYTICS.COUNTRY_CODES -->
             --> "527-INVESTIGATE$ISSUES".ANALYTICS.COUNTRY_CODES;

        Pronounced /snəʊfleɪkɪ/ like saying very fast snowflak[e and clarif]y
        Permission granted to use snowflaky as a verb.
        """
        name_parts = name.split(".")
        new_name_parts = []

        for part in name_parts:
            if re.match("^[0-9a-zA-Z_]*$", part) is None:
                new_name_parts.append(f'"{part}"')
            else:
                new_name_parts.append(part)

        return ".".join(new_name_parts)
