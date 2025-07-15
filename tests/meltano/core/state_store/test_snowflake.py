from __future__ import annotations

import json
import typing as t
from unittest import mock

import pytest

from meltano.core.state_store import MeltanoState
from meltano.core.state_store.snowflake import (
    MissingSnowflakeConnectorError,
    SnowflakeStateStoreManager,
)

try:
    from snowflake.connector import SnowflakeConnection
except ImportError:
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
    def subject(self, mock_connection):
        """Create SnowflakeStateStoreManager instance with mocked connection."""
        mock_conn, mock_cursor = mock_connection
        manager = SnowflakeStateStoreManager(
            uri="snowflake://testuser:testpass@testaccount/testdb/testschema",
            account="testaccount",
            user="testuser",
            password="testpass",
            warehouse="testwarehouse",
            database="testdb",
            schema="testschema",
        )
        # Replace the cached connection with our mock
        manager._connection = mock_conn
        return manager, mock_cursor

    def test_missing_snowflake_connector(self):
        """Test error when snowflake-connector-python is not installed."""
        with mock.patch(
            "meltano.core.state_store.snowflake.SNOWFLAKE_INSTALLED",
            False,
        ):
            with pytest.raises(MissingSnowflakeConnectorError):
                SnowflakeStateStoreManager(
                    uri="snowflake://test@account/db",
                    account="account",
                    user="test",
                    password="pass",
                    warehouse="warehouse",
                )

    def test_set_state(self, subject):
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

    def test_get_state(self, subject):
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

    def test_get_state_with_json_strings(self, subject):
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

    def test_get_state_with_null_values(self, subject):
        """Test getting state with NULL VARIANT columns."""
        manager, mock_cursor = subject

        # Mock cursor response with None values
        mock_cursor.fetchone.return_value = (None, '{"singer_state": {"complete": 1}}')

        # Get state
        state = manager.get("test_job")

        # Verify returned state handles None correctly
        assert state.state_id == "test_job"
        assert state.partial_state == {}
        assert state.completed_state == {"singer_state": {"complete": 1}}

    def test_get_state_with_json_strings(self, subject):
        """Test getting state when Snowflake returns JSON strings."""
        manager, mock_cursor = subject

        # Mock cursor response - sometimes Snowflake might return JSON strings
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

    def test_get_state_not_found(self, subject):
        """Test getting state that doesn't exist."""
        manager, mock_cursor = subject

        # Mock cursor response
        mock_cursor.fetchone.return_value = None

        # Get state
        state = manager.get("nonexistent")

        # Verify it returns None
        assert state is None

    def test_get_state_with_none_values(self, subject):
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

    def test_delete_state(self, subject):
        """Test deleting state."""
        manager, mock_cursor = subject

        # Delete state
        manager.delete("test_job")

        # Verify DELETE query with fully qualified table name
        mock_cursor.execute.assert_called()
        call_args = mock_cursor.execute.call_args
        assert "DELETE FROM testdb.testschema.meltano_state" in call_args[0][0]
        assert call_args[0][1] == ("test_job",)

    def test_get_state_ids(self, subject):
        """Test getting all state IDs."""
        manager, mock_cursor = subject

        # Mock cursor response - need to make cursor itself iterable
        mock_cursor.__iter__ = mock.Mock(return_value=iter([("job1",), ("job2",), ("job3",)]))

        # Get state IDs
        state_ids = list(manager.get_state_ids())

        # Verify query with fully qualified table name (skip table creation calls)
        select_calls = [call for call in mock_cursor.execute.call_args_list if "SELECT state_id FROM" in call[0][0]]
        assert len(select_calls) == 1
        assert "SELECT state_id FROM testdb.testschema.meltano_state" in select_calls[0][0][0]

        # Verify returned IDs
        assert state_ids == ["job1", "job2", "job3"]

    def test_get_state_ids_with_pattern(self, subject):
        """Test getting state IDs with pattern."""
        manager, mock_cursor = subject

        # Mock cursor response - need to make cursor itself iterable
        mock_cursor.__iter__ = mock.Mock(return_value=iter([("test_job_1",), ("test_job_2",)]))

        # Get state IDs with pattern
        state_ids = list(manager.get_state_ids("test_*"))

        # Verify query with LIKE and fully qualified table name (skip table creation calls)
        select_calls = [call for call in mock_cursor.execute.call_args_list if "SELECT state_id FROM" in call[0][0]]
        assert len(select_calls) == 1
        assert "SELECT state_id FROM testdb.testschema.meltano_state WHERE state_id LIKE" in select_calls[0][0][0]
        assert select_calls[0][0][1] == ("test_%",)

        # Verify returned IDs
        assert state_ids == ["test_job_1", "test_job_2"]

    def test_clear_all(self, subject):
        """Test clearing all states."""
        manager, mock_cursor = subject

        # Mock count query response
        mock_cursor.fetchone.return_value = (5,)

        # Clear all
        count = manager.clear_all()

        # Verify queries with fully qualified table names (skip table creation calls)
        count_calls = [call for call in mock_cursor.execute.call_args_list if "SELECT COUNT(*)" in call[0][0]]
        truncate_calls = [call for call in mock_cursor.execute.call_args_list if "TRUNCATE TABLE" in call[0][0]]
        
        assert len(count_calls) == 1
        assert len(truncate_calls) == 1
        assert "SELECT COUNT(*) FROM testdb.testschema.meltano_state" in count_calls[0][0][0]
        assert "TRUNCATE TABLE testdb.testschema.meltano_state" in truncate_calls[0][0][0]

        # Verify returned count
        assert count == 5

    def test_acquire_lock(self, subject):
        """Test acquiring and releasing lock."""
        manager, mock_cursor = subject

        # Test successful lock acquisition
        with manager.acquire_lock("test_job", retry_seconds=0):
            # Verify INSERT query for lock with fully qualified table name (skip table creation calls)
            insert_calls = [call for call in mock_cursor.execute.call_args_list if "INSERT INTO" in call[0][0] and "meltano_state_locks" in call[0][0]]
            assert len(insert_calls) >= 1
            assert "INSERT INTO testdb.testschema.meltano_state_locks" in insert_calls[0][0][0]

        # Verify DELETE queries for lock release and cleanup with fully qualified table names
        delete_calls = [
            call
            for call in mock_cursor.execute.call_args_list
            if "DELETE FROM testdb.testschema.meltano_state_locks" in call[0][0]
        ]
        assert len(delete_calls) >= 1

    def test_acquire_lock_retry(self, subject):
        """Test lock retry mechanism."""
        manager, mock_cursor = subject

        # Mock lock conflict on first attempt, success on second
        mock_cursor.execute.side_effect = [
            mock.Mock(
                side_effect=mock.Mock(
                    __class__=type(
                        "ProgrammingError",
                        (Exception,),
                        {},
                    ),
                    args=("Duplicate key",),
                )
            ),
            None,  # Success on second attempt
            None,  # Lock release
            None,  # Lock cleanup
        ]

        # Import the actual exception for isinstance check
        with mock.patch(
            "meltano.core.state_store.snowflake.ProgrammingError",
            Exception,
        ):
            with manager.acquire_lock("test_job", retry_seconds=0.1):
                pass

        # Verify it retried
        assert mock_cursor.execute.call_count >= 2
