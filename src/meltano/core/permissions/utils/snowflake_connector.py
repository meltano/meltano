import logging
import os
import re

from typing import Dict, List, Any
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
                names.append(result["name"].lower())

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
                    f"{result['database_name'].lower()}.{result['name'].lower()}"
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
                    f"{result['database_name'].lower()}"
                    + f".{result['schema_name'].lower()}"
                    + f".{result['name'].lower()}"
                )

        return names

    def show_views(self, database: str = None, schema: str = None) -> List[str]:
        names = []

        if schema:
            query = f"SHOW TERSE VIEWS IN SCHEMA {schema}"
        elif database:
            query = f"SHOW TERSE VIEWS IN DATABASE {database}"
        else:
            query = f"SHOW TERSE VIEWS IN ACCOUNT"

        with self.engine.connect() as connection:
            results = connection.execute(query).fetchall()

            for result in results:
                names.append(
                    f"{result['database_name'].lower()}"
                    + f".{result['schema_name'].lower()}"
                    + f".{result['name'].lower()}"
                )

        return names

    def show_future_grants(self, database: str = None, schema: str = None) -> List[str]:
        future_grants = {}

        if schema:
            query = f"SHOW FUTURE GRANTS IN SCHEMA {schema}"
        elif database:
            query = f"SHOW FUTURE GRANTS IN DATABASE {database}"
        else:
            pass

        with self.engine.connect() as connection:
            results = connection.execute(query).fetchall()

            for result in results:
                if result["grant_to"] == "ROLE":
                    role = result["grantee_name"].lower()
                    privilege = result["privilege"].lower()
                    granted_on = result["grant_on"].lower()

                    future_grants.setdefault(role, {}).setdefault(
                        privilege, {}
                    ).setdefault(granted_on, []).append(result["name"].lower())

                else:
                    continue

        return future_grants

    def show_grants_to_role(self, role) -> Dict[str, Any]:
        grants = {}

        query = f"SHOW GRANTS TO ROLE {SnowflakeConnector.snowflaky(role)}"
        with self.engine.connect() as connection:
            results = connection.execute(query).fetchall()

            for result in results:
                privilege = result["privilege"].lower()
                granted_on = result["granted_on"].lower()

                grants.setdefault(privilege, {}).setdefault(granted_on, []).append(
                    result["name"].lower()
                )

        return grants

    def show_roles_granted_to_user(self, user) -> List[str]:
        roles = []

        query = f"SHOW GRANTS TO USER {SnowflakeConnector.snowflaky(user)}"
        with self.engine.connect() as connection:
            results = connection.execute(query).fetchall()

            for result in results:
                roles.append(result["role"].lower())

        return roles

    def run_query(self, query: str):

        with self.engine.connect() as connection:
            result = connection.execute(query)

        return result

    def full_schema_list(self, schema: str) -> List[str]:
        """
        For a given schema name, get all schemas it may be referencing.

        For example, if <db>.* is given then all schemas in the database 
        will be returned. If <db>.<schema_partial>_* is given, then all 
        schemas that match the schema partial pattern will be returned. 
        If a full schema name is given, it will return that single schema
        as a list.

        This function can be enhanced in the future to handle more 
        complicated schema names if necessary.

        Returns a list of schema names.
        """
        # Generate the information_schema identifier for that database
        # in order to be able to filter it out
        name_parts = schema.split(".")

        info_schema = f"{name_parts[0]}.information_schema"

        fetched_schemas = []

        # All Schemas
        if name_parts[1] == "*":
            db_schemas = self.show_schemas(name_parts[0])
            for db_schema in db_schemas:
                if db_schema != info_schema:
                    fetched_schemas.append(db_schema)

        # Prefix schema match
        elif "*" in name_parts[1]:
            db_schemas = self.show_schemas(name_parts[0])
            for db_schema in db_schemas:
                schema_name = db_schema.split(".", 1)[1].lower()
                if schema_name.startswith(name_parts[1].split("*", 1)[0]):
                    fetched_schemas.append(db_schema)

        # TODO Handle more complicated matches

        else:
            # If no * in name, then return provided schema name
            fetched_schemas = [schema]

        return fetched_schemas

    def snowflaky(name: str) -> str:
        """
        Convert an entity name to an object identifier that will most probably be
        the proper name for Snowflake.

        e.g. gitlab-ci --> "gitlab-ci"
             527-INVESTIGATE$ISSUES.ANALYTICS.COUNTRY_CODES -->
             --> "527-INVESTIGATE$ISSUES".ANALYTICS.COUNTRY_CODES;

        Pronounced /snəʊfleɪkɪ/ like saying very fast snowflak[e and clarif]y
        Permission granted to use snowflaky as a verb.
        """
        name_parts = name.split(".")
        new_name_parts = []

        for part in name_parts:
            if (
                re.match("^[0-9a-zA-Z_]*$", part) is None  # Proper formatting
                and re.match('^".*"$', part) is None  # Already quoted
            ):
                new_name_parts.append(f'"{part}"')
            else:
                new_name_parts.append(part)

        return ".".join(new_name_parts)
