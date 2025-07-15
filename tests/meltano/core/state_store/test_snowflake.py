from __future__ import annotations

import json
from unittest import mock

import pytest

from meltano.core.state_store import MeltanoState
from meltano.core.state_store.base import (
    MissingStateBackendSettingsError,
    StateIDLockedError,
)
from meltano.core.state_store.snowflake import (
    MissingSnowflakeConnectorError,
    SnowflakeStateStoreManager,
)

# Remove direct import to avoid uv.lock dependency issues
SnowflakeConnection = None


class TestSnowflakeStateStoreManager:
    @pytest.fixture
    def mock_connection(self):
        """Mock Snowflake connection."""
        with mock.patch("snowflake.connector.connect") as mock_connect:
            mock_conn = mock.Mock()
            mock_cursor = mock.Mock()

            # Mock the context manager for cursor
            mock_cursor_context = mock.Mock()
            mock_cursor_context.__enter__ = mock.Mock(return_value=mock_cursor)
            mock_cursor_context.__exit__ = mock.Mock(return_value=None)
            mock_conn.cursor.return_value = mock_cursor_context

            mock_connect.return_value = mock_conn
            yield mock_conn, mock_cursor

    @pytest.fixture
    def subject(
        self,
        mock_connection: tuple[mock.Mock, mock.Mock],
    ) -> tuple[SnowflakeStateStoreManager, mock.Mock]:
        """Create SnowflakeStateStoreManager instance with mocked connection."""
        mock_conn, mock_cursor = mock_connection

        # Mock the SNOWFLAKE_INSTALLED check to avoid import issues
        with mock.patch("meltano.core.state_store.snowflake.SNOWFLAKE_INSTALLED", True):  # noqa: FBT003
            manager = SnowflakeStateStoreManager(
                uri="snowflake://testuser:testpass@testaccount/testdb/testschema",
                account="testaccount",
                user="testuser",
                password="testpass",  # noqa: S106
                warehouse="testwarehouse",
                database="testdb",
                schema="testschema",
            )
        # Replace the cached connection with our mock
        manager._connection = mock_conn
        return manager, mock_cursor

    def test_missing_snowflake_connector(self):
        """Test error when snowflake-connector-python is not installed."""
        with (
            mock.patch(
                "meltano.core.state_store.snowflake.SNOWFLAKE_INSTALLED",
                False,  # noqa: FBT003
            ),
            pytest.raises(MissingSnowflakeConnectorError),
        ):
            SnowflakeStateStoreManager(
                uri="snowflake://test@account/db",
                account="account",
                user="test",
                password="pass",  # noqa: S106
                warehouse="warehouse",
            )

    def test_set_state(
        self,
        subject: tuple[SnowflakeStateStoreManager, mock.Mock],
    ):
        """Test setting state."""
        manager, mock_cursor = subject

        # Test setting new state
        state = MeltanoState(
            state_id="test_job",
            partial_state={"singer_state": {"partial": 1}},
            completed_state={"singer_state": {"complete": 1}},
        )
        manager.set(state)

        # Verify MERGE query was executed with fully qualified table name
        mock_cursor.execute.assert_called()
        call_args = mock_cursor.execute.call_args
        assert "MERGE INTO testdb.testschema.meltano_state" in call_args[0][0]
        assert call_args[0][1] == (
            "test_job",
            json.dumps({"singer_state": {"partial": 1}}),
            json.dumps({"singer_state": {"complete": 1}}),
        )

    def test_get_state(
        self,
        subject: tuple[SnowflakeStateStoreManager, mock.Mock],
    ):
        """Test getting state."""
        manager, mock_cursor = subject

        # Mock cursor response - Snowflake VARIANT columns return Python dicts
        mock_cursor.fetchone.return_value = (
            {"singer_state": {"partial": 1}},
            {"singer_state": {"complete": 1}},
        )

        # Get state
        state = manager.get("test_job")

        # Verify query with fully qualified table name
        mock_cursor.execute.assert_called()
        call_args = mock_cursor.execute.call_args
        assert "FROM testdb.testschema.meltano_state" in call_args[0][0]
        assert call_args[0][1] == ("test_job",)

        # Verify returned state
        assert state.state_id == "test_job"
        assert state.partial_state == {"singer_state": {"partial": 1}}
        assert state.completed_state == {"singer_state": {"complete": 1}}

    def test_get_state_with_json_strings(
        self,
        subject: tuple[SnowflakeStateStoreManager, mock.Mock],
    ):
        """Test getting state when Snowflake returns JSON strings."""
        manager, mock_cursor = subject

        # Mock cursor response with JSON strings (as Snowflake might return)
        mock_cursor.fetchone.return_value = (
            '{"singer_state": {"partial": 1}}',
            '{"singer_state": {"complete": 1}}',
        )

        # Get state
        state = manager.get("test_job")

        # Verify returned state is properly parsed
        assert state.state_id == "test_job"
        assert state.partial_state == {"singer_state": {"partial": 1}}
        assert state.completed_state == {"singer_state": {"complete": 1}}

    def test_get_state_with_null_values(
        self,
        subject: tuple[SnowflakeStateStoreManager, mock.Mock],
    ):
        """Test getting state with NULL VARIANT columns."""
        manager, mock_cursor = subject

        # Mock cursor response with None values
        mock_cursor.fetchone.return_value = (
            None,
            '{"singer_state": {"complete": 1}}',
        )

        # Get state
        state = manager.get("test_job")

        # Verify returned state handles None correctly
        assert state.state_id == "test_job"
        assert state.partial_state == {}
        assert state.completed_state == {"singer_state": {"complete": 1}}

    def test_get_state_not_found(
        self,
        subject: tuple[SnowflakeStateStoreManager, mock.Mock],
    ):
        """Test getting state that doesn't exist."""
        manager, mock_cursor = subject

        # Mock cursor response
        mock_cursor.fetchone.return_value = None

        # Get state
        state = manager.get("nonexistent")

        # Verify it returns None
        assert state is None

    def test_get_state_with_none_values(
        self,
        subject: tuple[SnowflakeStateStoreManager, mock.Mock],
    ):
        """Test getting state with None values (NULL in Snowflake)."""
        manager, mock_cursor = subject

        # Mock cursor response with None values
        mock_cursor.fetchone.return_value = (None, None)

        # Get state
        state = manager.get("test_job")

        # Verify returned state has empty dicts for None values
        assert state.state_id == "test_job"
        assert state.partial_state == {}
        assert state.completed_state == {}

    def test_delete_state(
        self,
        subject: tuple[SnowflakeStateStoreManager, mock.Mock],
    ):
        """Test deleting state."""
        manager, mock_cursor = subject

        # Delete state
        manager.delete("test_job")

        # Verify DELETE query with fully qualified table name
        mock_cursor.execute.assert_called()
        call_args = mock_cursor.execute.call_args
        assert "DELETE FROM testdb.testschema.meltano_state" in call_args[0][0]
        assert call_args[0][1] == ("test_job",)

    def test_get_state_ids(
        self,
        subject: tuple[SnowflakeStateStoreManager, mock.Mock],
    ):
        """Test getting all state IDs."""
        manager, mock_cursor = subject

        # Mock cursor response - need to make cursor itself iterable
        mock_cursor.__iter__ = mock.Mock(
            return_value=iter([("job1",), ("job2",), ("job3",)])
        )

        # Get state IDs
        state_ids = list(manager.get_state_ids())

        # Verify query with fully qualified table name (skip table creation calls)
        select_calls = [
            call
            for call in mock_cursor.execute.call_args_list
            if "SELECT state_id FROM" in call[0][0]
        ]
        assert len(select_calls) == 1
        assert (
            "SELECT state_id FROM testdb.testschema.meltano_state"
            in select_calls[0][0][0]
        )

        # Verify returned IDs
        assert state_ids == ["job1", "job2", "job3"]

    def test_get_state_ids_with_pattern(
        self,
        subject: tuple[SnowflakeStateStoreManager, mock.Mock],
    ):
        """Test getting state IDs with pattern."""
        manager, mock_cursor = subject

        # Mock cursor response - need to make cursor itself iterable
        mock_cursor.__iter__ = mock.Mock(
            return_value=iter([("test_job_1",), ("test_job_2",)])
        )

        # Get state IDs with pattern
        state_ids = list(manager.get_state_ids("test_*"))

        # Verify query with LIKE and fully qualified table name (skip table creation calls)  # noqa: E501
        select_calls = [
            call
            for call in mock_cursor.execute.call_args_list
            if "SELECT state_id FROM" in call[0][0]
        ]
        assert len(select_calls) == 1
        assert (
            "SELECT state_id FROM testdb.testschema.meltano_state WHERE state_id LIKE"
            in select_calls[0][0][0]
        )
        assert select_calls[0][0][1] == ("test_%",)

        # Verify returned IDs
        assert state_ids == ["test_job_1", "test_job_2"]

    def test_clear_all(
        self,
        subject: tuple[SnowflakeStateStoreManager, mock.Mock],
    ):
        """Test clearing all states."""
        manager, mock_cursor = subject

        # Mock count query response
        mock_cursor.fetchone.return_value = (5,)

        # Clear all
        count = manager.clear_all()

        # Verify queries with fully qualified table names (skip table creation calls)
        count_calls = [
            call
            for call in mock_cursor.execute.call_args_list
            if "SELECT COUNT(*)" in call[0][0]
        ]
        truncate_calls = [
            call
            for call in mock_cursor.execute.call_args_list
            if "TRUNCATE TABLE" in call[0][0]
        ]

        assert len(count_calls) == 1
        assert len(truncate_calls) == 1
        assert (
            "SELECT COUNT(*) FROM testdb.testschema.meltano_state"
            in count_calls[0][0][0]
        )
        assert (
            "TRUNCATE TABLE testdb.testschema.meltano_state" in truncate_calls[0][0][0]
        )

        # Verify returned count
        assert count == 5

    def test_acquire_lock(
        self,
        subject: tuple[SnowflakeStateStoreManager, mock.Mock],
    ):
        """Test acquiring and releasing lock."""
        manager, mock_cursor = subject

        # Test successful lock acquisition
        with manager.acquire_lock("test_job", retry_seconds=0):
            # Verify INSERT query for lock with fully qualified table name (skip table creation calls)  # noqa: E501
            insert_calls = [
                call
                for call in mock_cursor.execute.call_args_list
                if "INSERT INTO" in call[0][0] and "meltano_state_locks" in call[0][0]
            ]
            assert len(insert_calls) >= 1
            assert (
                "INSERT INTO testdb.testschema.meltano_state_locks"
                in insert_calls[0][0][0]
            )

        # Verify DELETE queries for lock release and cleanup with fully qualified table names  # noqa: E501
        delete_calls = [
            call
            for call in mock_cursor.execute.call_args_list
            if "DELETE FROM testdb.testschema.meltano_state_locks" in call[0][0]
        ]
        assert len(delete_calls) >= 1

    def test_acquire_lock_retry(
        self,
        subject: tuple[SnowflakeStateStoreManager, mock.Mock],
    ):
        """Test lock retry mechanism."""
        manager, mock_cursor = subject

        # Create a mock exception that mimics ProgrammingError
        mock_programming_error = Exception("Duplicate key")

        # Mock lock conflict on first attempt, success on second
        mock_cursor.execute.side_effect = [
            mock_programming_error,  # First attempt fails
            None,  # Success on second attempt
            None,  # Lock release
            None,  # Lock cleanup
        ]

        # Mock the ProgrammingError class used in the implementation
        with (
            mock.patch(
                "meltano.core.state_store.snowflake.ProgrammingError",
                Exception,
            ),
            manager.acquire_lock("test_job", retry_seconds=0.1),
        ):
            pass

        # Verify it retried
        assert mock_cursor.execute.call_count >= 2

    def test_snowflake_not_installed(self):
        """Test ImportError when snowflake-connector is not installed (line 31-32)."""
        # This tests the ImportError path in lines 31-32
        with (
            mock.patch(
                "meltano.core.state_store.snowflake.SNOWFLAKE_INSTALLED",
                False,  # noqa: FBT003
            ),
            pytest.raises(MissingSnowflakeConnectorError),
        ):
            SnowflakeStateStoreManager(
                uri="snowflake://test@account/db",
                account="account",
                user="test",
                password="pass",  # noqa: S106
                warehouse="warehouse",
            )

    def test_missing_account_validation(self):
        """Test missing account validation (lines 165-166)."""
        with (
            mock.patch("meltano.core.state_store.snowflake.SNOWFLAKE_INSTALLED", True),  # noqa: FBT003
            pytest.raises(
                MissingStateBackendSettingsError, match="Snowflake account is required"
            ),
        ):
            SnowflakeStateStoreManager(
                uri="snowflake://user:pass@/db",  # No account in hostname
                user="test",
                password="pass",  # noqa: S106
                warehouse="warehouse",
                database="db",
            )

    def test_missing_user_validation(self):
        """Test missing user validation (lines 170-171)."""
        with (
            mock.patch("meltano.core.state_store.snowflake.SNOWFLAKE_INSTALLED", True),  # noqa: FBT003
            pytest.raises(
                MissingStateBackendSettingsError, match="Snowflake user is required"
            ),
        ):
            SnowflakeStateStoreManager(
                uri="snowflake://account/db",  # No user in URI
                account="account",
                password="pass",  # noqa: S106
                warehouse="warehouse",
                database="db",
            )

    def test_missing_password_validation(self):
        """Test missing password validation (lines 175-176)."""
        with (
            mock.patch("meltano.core.state_store.snowflake.SNOWFLAKE_INSTALLED", True),  # noqa: FBT003
            pytest.raises(
                MissingStateBackendSettingsError, match="Snowflake password is required"
            ),
        ):
            SnowflakeStateStoreManager(
                uri="snowflake://user@account/db",  # No password in URI
                account="account",
                user="test",
                warehouse="warehouse",
                database="db",
            )

    def test_missing_warehouse_validation(self):
        """Test missing warehouse validation (lines 180-181)."""
        with (
            mock.patch("meltano.core.state_store.snowflake.SNOWFLAKE_INSTALLED", True),  # noqa: FBT003
            pytest.raises(
                MissingStateBackendSettingsError,
                match="Snowflake warehouse is required",
            ),
        ):
            SnowflakeStateStoreManager(
                uri="snowflake://user:pass@account/db",
                account="account",
                user="test",
                password="pass",  # noqa: S106
                database="db",
                # No warehouse parameter
            )

    def test_missing_database_validation(self):
        """Test missing database validation (lines 187-188)."""
        with (
            mock.patch("meltano.core.state_store.snowflake.SNOWFLAKE_INSTALLED", True),  # noqa: FBT003
            pytest.raises(
                MissingStateBackendSettingsError, match="Snowflake database is required"
            ),
        ):
            SnowflakeStateStoreManager(
                uri="snowflake://user:pass@account/",  # No database in path
                account="account",
                user="test",
                password="pass",  # noqa: S106
                warehouse="warehouse",
                # No database parameter
            )

    def test_connection_with_role(self):
        """Test connection creation with role (line 211)."""
        # Mock snowflake.connector.connect directly during manager creation
        with (
            mock.patch("meltano.core.state_store.snowflake.SNOWFLAKE_INSTALLED", True),  # noqa: FBT003
            mock.patch("snowflake.connector.connect") as mock_connect,
        ):
            mock_conn = mock.Mock()
            mock_cursor = mock.Mock()
            mock_cursor_context = mock.Mock()
            mock_cursor_context.__enter__ = mock.Mock(return_value=mock_cursor)
            mock_cursor_context.__exit__ = mock.Mock(return_value=None)
            mock_conn.cursor.return_value = mock_cursor_context
            mock_connect.return_value = mock_conn

            manager = SnowflakeStateStoreManager(
                uri="snowflake://testuser:testpass@testaccount/testdb/testschema",
                account="testaccount",
                user="testuser",
                password="testpass",  # noqa: S106
                warehouse="testwarehouse",
                database="testdb",
                schema="testschema",
                role="testrole",  # This triggers line 211
            )

            # Access the connection property to trigger the connection
            _ = manager.connection

            # Verify role was included in connection params
            mock_connect.assert_called_with(
                account="testaccount",
                user="testuser",
                password="testpass",  # noqa: S106
                warehouse="testwarehouse",
                database="testdb",
                schema="testschema",
                role="testrole",
            )

    def test_acquire_lock_max_retries_exceeded(
        self,
        subject: tuple[SnowflakeStateStoreManager, mock.Mock],
    ):
        """Test lock acquisition with max retries exceeded (lines 414-415)."""
        manager, mock_cursor = subject

        # Create a mock exception that mimics ProgrammingError with duplicate key
        mock_programming_error = Exception("Duplicate key")

        # Mock lock conflict on all attempts
        mock_cursor.execute.side_effect = mock_programming_error

        # Mock the ProgrammingError class used in the implementation
        with (
            mock.patch(
                "meltano.core.state_store.snowflake.ProgrammingError",
                Exception,
            ),
            pytest.raises(
                StateIDLockedError,
                match="Could not acquire lock for state_id: test_job",
            ),
            manager.acquire_lock("test_job", retry_seconds=0.01),
        ):
            pass

    def test_acquire_lock_other_programming_error(
        self,
        subject: tuple[SnowflakeStateStoreManager, mock.Mock],
    ):
        """Test lock acquisition with non-duplicate key ProgrammingError (line 418)."""
        manager, mock_cursor = subject

        # Create a mock exception that mimics ProgrammingError but not duplicate key
        mock_programming_error = Exception("Some other error")

        # Mock lock conflict on first attempt
        mock_cursor.execute.side_effect = mock_programming_error

        # Mock the ProgrammingError class used in the implementation
        with (
            mock.patch(
                "meltano.core.state_store.snowflake.ProgrammingError",
                Exception,
            ),
            pytest.raises(Exception, match="Some other error"),
            manager.acquire_lock("test_job", retry_seconds=0.01),
        ):
            pass
