"""StateStoreManager for Snowflake state backend."""

from __future__ import annotations

import json
import typing as t
from contextlib import contextmanager
from functools import cached_property
from time import sleep
from urllib.parse import urlparse

from meltano.core.error import MeltanoError
from meltano.core.setting_definition import SettingDefinition, SettingKind
from meltano.core.state_store.base import (
    MeltanoState,
    MissingStateBackendSettingsError,
    StateIDLockedError,
    StateStoreManager,
)

if t.TYPE_CHECKING:
    from collections.abc import Generator, Iterable

    from snowflake.connector import SnowflakeConnection

SNOWFLAKE_INSTALLED = True

try:
    import snowflake.connector
    from snowflake.connector.errors import ProgrammingError
except ImportError:
    SNOWFLAKE_INSTALLED = False


class MissingSnowflakeConnectorError(MeltanoError):
    """Raised when snowflake-connector-python is required but not installed."""

    def __init__(self) -> None:
        """Initialize a MissingSnowflakeConnectorError."""
        super().__init__(
            "snowflake-connector-python required but not installed. "
            "Install meltano[snowflake] to use Snowflake as a state backend.",
        )


@contextmanager
def requires_snowflake_connector() -> Generator[None, None, None]:
    """Raise MissingSnowflakeConnectorError if snowflake-connector-python is missing.

    Raises:
        MissingSnowflakeConnectorError: if snowflake-connector-python is not installed.

    Yields:
        None
    """
    if not SNOWFLAKE_INSTALLED:
        raise MissingSnowflakeConnectorError
    yield


class SnowflakeStateBackendError(MeltanoError):
    """Base error for Snowflake state backend."""


SNOWFLAKE_ACCOUNT = SettingDefinition(
    name="state_backend.snowflake.account",
    label="Snowflake Account",
    description="Snowflake account identifier",
    kind=SettingKind.STRING,
    env_specific=True,
)

SNOWFLAKE_USER = SettingDefinition(
    name="state_backend.snowflake.user",
    label="Snowflake User",
    description="Snowflake username",
    kind=SettingKind.STRING,
    env_specific=True,
)

SNOWFLAKE_PASSWORD = SettingDefinition(
    name="state_backend.snowflake.password",
    label="Snowflake Password",
    description="Snowflake password",
    kind=SettingKind.STRING,
    sensitive=True,
    env_specific=True,
)

SNOWFLAKE_WAREHOUSE = SettingDefinition(
    name="state_backend.snowflake.warehouse",
    label="Snowflake Warehouse",
    description="Snowflake compute warehouse",
    kind=SettingKind.STRING,
    env_specific=True,
)

SNOWFLAKE_DATABASE = SettingDefinition(
    name="state_backend.snowflake.database",
    label="Snowflake Database",
    description="Snowflake database name",
    kind=SettingKind.STRING,
    env_specific=True,
)

SNOWFLAKE_SCHEMA = SettingDefinition(
    name="state_backend.snowflake.schema",
    label="Snowflake Schema",
    description="Snowflake schema name",
    kind=SettingKind.STRING,
    default="PUBLIC",
    env_specific=True,
)

SNOWFLAKE_ROLE = SettingDefinition(
    name="state_backend.snowflake.role",
    label="Snowflake Role",
    description="Snowflake role to use",
    kind=SettingKind.STRING,
    env_specific=True,
)


class SnowflakeStateStoreManager(StateStoreManager):
    """State backend for Snowflake."""

    label: str = "Snowflake"
    table_name: str = "meltano_state"
    lock_table_name: str = "meltano_state_locks"

    def __init__(
        self,
        uri: str,
        *,
        account: str | None = None,
        user: str | None = None,
        password: str | None = None,
        warehouse: str | None = None,
        database: str | None = None,
        schema: str | None = None,
        role: str | None = None,
        **kwargs: t.Any,
    ):
        """Initialize the SnowflakeStateStoreManager.

        Args:
            uri: The state backend URI
            account: Snowflake account identifier
            user: Snowflake username
            password: Snowflake password
            warehouse: Snowflake compute warehouse
            database: Snowflake database name
            schema: Snowflake schema name (default: PUBLIC)
            role: Optional Snowflake role to use
            kwargs: Additional keyword args to pass to parent
        """
        super().__init__(**kwargs)
        with requires_snowflake_connector():
            self.uri = uri
            parsed = urlparse(uri)

            # Extract connection details from URI and parameters
            self.account = account or parsed.hostname
            if not self.account:
                msg = "Snowflake account is required"
                raise MissingStateBackendSettingsError(msg)

            self.user = user or parsed.username
            if not self.user:
                msg = "Snowflake user is required"
                raise MissingStateBackendSettingsError(msg)

            self.password = password or parsed.password
            if not self.password:
                msg = "Snowflake password is required"
                raise MissingStateBackendSettingsError(msg)

            self.warehouse = warehouse
            if not self.warehouse:
                msg = "Snowflake warehouse is required"
                raise MissingStateBackendSettingsError(msg)

            # Extract database from path
            path_parts = parsed.path.strip("/").split("/") if parsed.path else []
            self.database = database or (path_parts[0] if path_parts else None)
            if not self.database:
                msg = "Snowflake database is required"
                raise MissingStateBackendSettingsError(msg)

            self.schema = schema or (path_parts[1] if len(path_parts) > 1 else "PUBLIC")
            self.role = role

            self._ensure_tables()

    @cached_property
    def connection(self) -> SnowflakeConnection:
        """Get a Snowflake connection.

        Returns:
            A Snowflake connection object.
        """
        conn_params = {
            "account": self.account,
            "user": self.user,
            "password": self.password,
            "warehouse": self.warehouse,
            "database": self.database,
            "schema": self.schema,
        }
        if self.role:
            conn_params["role"] = self.role

        return snowflake.connector.connect(**conn_params)

    def _ensure_tables(self) -> None:
        """Ensure the state and lock tables exist."""
        with self.connection.cursor() as cursor:
            # Create state table
            cursor.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {self.database}.{self.schema}.{self.table_name} (
                    state_id VARCHAR PRIMARY KEY,
                    partial_state VARIANT,
                    completed_state VARIANT,
                    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
                )
                """  # noqa: E501
            )

            # Create lock table
            cursor.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {self.database}.{self.schema}.{self.lock_table_name} (
                    state_id VARCHAR PRIMARY KEY,
                    locked_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
                    lock_id VARCHAR
                )
                """  # noqa: E501
            )

    def set(self, state: MeltanoState) -> None:
        """Set the job state for the given state_id.

        Args:
            state: the state to set.
        """
        partial_json = json.dumps(state.partial_state) if state.partial_state else None
        completed_json = (
            json.dumps(state.completed_state) if state.completed_state else None
        )

        with self.connection.cursor() as cursor:
            cursor.execute(
                f"""
                MERGE INTO {self.database}.{self.schema}.{self.table_name} AS target
                USING (SELECT %s AS state_id, PARSE_JSON(%s) AS partial_state,
                       PARSE_JSON(%s) AS completed_state) AS source
                ON target.state_id = source.state_id
                WHEN MATCHED THEN
                    UPDATE SET
                        partial_state = source.partial_state,
                        completed_state = source.completed_state,
                        updated_at = CURRENT_TIMESTAMP()
                WHEN NOT MATCHED THEN
                    INSERT (state_id, partial_state, completed_state)
                    VALUES (source.state_id, source.partial_state, source.completed_state)
                """,  # noqa: E501, S608
                (state.state_id, partial_json, completed_json),
            )

    def get(self, state_id: str) -> MeltanoState | None:
        """Get the job state for the given state_id.

        Args:
            state_id: the name of the job to get state for.

        Returns:
            The current state for the given job
        """
        with self.connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT partial_state, completed_state
                FROM {self.database}.{self.schema}.{self.table_name}
                WHERE state_id = %s
                """,  # noqa: S608
                (state_id,),
            )
            row = cursor.fetchone()

            if not row:
                return None

            # Snowflake returns None for NULL VARIANT columns
            # but MeltanoState expects empty dicts
            # Additionally, VARIANT columns might return JSON strings that need parsing
            partial_state = row[0]
            completed_state = row[1]

            # Handle None values
            if partial_state is None:
                partial_state = {}
            # Parse JSON string if Snowflake returns string instead of dict
            elif isinstance(partial_state, str):
                partial_state = json.loads(partial_state)

            if completed_state is None:
                completed_state = {}
            # Parse JSON string if Snowflake returns string instead of dict
            elif isinstance(completed_state, str):
                completed_state = json.loads(completed_state)

            return MeltanoState(
                state_id=state_id,
                partial_state=partial_state,
                completed_state=completed_state,
            )

    def delete(self, state_id: str) -> None:
        """Delete state for the given state_id.

        Args:
            state_id: the state_id to clear state for
        """
        with self.connection.cursor() as cursor:
            cursor.execute(
                f"DELETE FROM {self.database}.{self.schema}.{self.table_name} WHERE state_id = %s",  # noqa: E501, S608
                (state_id,),
            )

    def clear_all(self) -> int:
        """Clear all states.

        Returns:
            The number of states cleared from the store.
        """
        with self.connection.cursor() as cursor:
            cursor.execute(
                f"SELECT COUNT(*) FROM {self.database}.{self.schema}.{self.table_name}"  # noqa: S608
            )
            count = cursor.fetchone()[0]
            cursor.execute(
                f"TRUNCATE TABLE {self.database}.{self.schema}.{self.table_name}"
            )
            return count

    def get_state_ids(self, pattern: str | None = None) -> Iterable[str]:
        """Get all state_ids available in this state store manager.

        Args:
            pattern: glob-style pattern to filter by

        Returns:
            An iterable of state_ids
        """
        with self.connection.cursor() as cursor:
            if pattern and pattern != "*":
                # Convert glob pattern to SQL LIKE pattern
                sql_pattern = pattern.replace("*", "%").replace("?", "_")
                cursor.execute(
                    f"SELECT state_id FROM {self.database}.{self.schema}.{self.table_name} WHERE state_id LIKE %s",  # noqa: E501, S608
                    (sql_pattern,),
                )
            else:
                cursor.execute(
                    f"SELECT state_id FROM {self.database}.{self.schema}.{self.table_name}"  # noqa: E501, S608
                )

            for row in cursor:
                yield row[0]

    @contextmanager
    def acquire_lock(
        self,
        state_id: str,
        *,
        retry_seconds: int = 1,
    ) -> Generator[None, None, None]:
        """Acquire a lock for the given job's state.

        Args:
            state_id: the state_id to lock
            retry_seconds: the number of seconds to wait before retrying

        Yields:
            None

        Raises:
            StateIDLockedError: if the lock cannot be acquired
        """
        import uuid

        lock_id = str(uuid.uuid4())
        max_retries = 30  # Maximum 30 seconds of retrying
        retries = 0

        while retries < max_retries:
            try:
                with self.connection.cursor() as cursor:
                    # Try to acquire lock
                    cursor.execute(
                        f"""
                        INSERT INTO {self.database}.{self.schema}.{self.lock_table_name} (state_id, lock_id)
                        VALUES (%s, %s)
                        """,  # noqa: E501, S608
                        (state_id, lock_id),
                    )
                    break
            except ProgrammingError as e:
                # Check if it's a unique constraint violation
                if "Duplicate key" in str(e):
                    retries += 1
                    if retries >= max_retries:
                        msg = f"Could not acquire lock for state_id: {state_id}"
                        raise StateIDLockedError(msg) from e
                    sleep(retry_seconds)
                else:
                    raise

        try:
            yield
        finally:
            # Release the lock
            with self.connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    DELETE FROM {self.database}.{self.schema}.{self.lock_table_name}
                    WHERE state_id = %s AND lock_id = %s
                    """,  # noqa: S608
                    (state_id, lock_id),
                )

            # Clean up old locks (older than 5 minutes)
            with self.connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    DELETE FROM {self.database}.{self.schema}.{self.lock_table_name}
                    WHERE locked_at < DATEADD(minute, -5, CURRENT_TIMESTAMP())
                    """  # noqa: S608
                )
