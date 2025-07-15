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

if t.TYPE_CHECKING:
    from snowflake.connector import SnowflakeConnection


class TestSnowflakeStateStoreManager:
    @pytest.fixture
    def mock_connection(self):
        """Mock Snowflake connection."""
        with mock.patch("snowflake.connector.connect") as mock_connect:
            mock_conn = mock.Mock(spec=SnowflakeConnection)
            mock_cursor = mock.Mock()
            mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
            mock_conn.cursor.return_value.__exit__.return_value = None
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

        # Verify MERGE query was executed
        mock_cursor.execute.assert_called()
        call_args = mock_cursor.execute.call_args
        assert "MERGE INTO" in call_args[0][0]
        assert call_args[0][1] == (
            "test_job",
            json.dumps({"singer_state": {"partial": 1}}),
            json.dumps({"singer_state": {"complete": 1}}),
        )

    def test_get_state(self, subject):
        """Test getting state."""
        manager, mock_cursor = subject

        # Mock cursor response
        mock_cursor.fetchone.return_value = (
            {"singer_state": {"partial": 1}},
            {"singer_state": {"complete": 1}},
        )

        # Get state
        state = manager.get("test_job")

        # Verify query
        mock_cursor.execute.assert_called()
        call_args = mock_cursor.execute.call_args
        assert "SELECT partial_state, completed_state" in call_args[0][0]
        assert call_args[0][1] == ("test_job",)

        # Verify returned state
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

    def test_delete_state(self, subject):
        """Test deleting state."""
        manager, mock_cursor = subject

        # Delete state
        manager.delete("test_job")

        # Verify DELETE query
        mock_cursor.execute.assert_called()
        call_args = mock_cursor.execute.call_args
        assert "DELETE FROM" in call_args[0][0]
        assert call_args[0][1] == ("test_job",)

    def test_get_state_ids(self, subject):
        """Test getting all state IDs."""
        manager, mock_cursor = subject

        # Mock cursor response
        mock_cursor.__iter__.return_value = iter([("job1",), ("job2",), ("job3",)])

        # Get state IDs
        state_ids = list(manager.get_state_ids())

        # Verify query
        mock_cursor.execute.assert_called()
        call_args = mock_cursor.execute.call_args
        assert "SELECT state_id FROM" in call_args[0][0]

        # Verify returned IDs
        assert state_ids == ["job1", "job2", "job3"]

    def test_get_state_ids_with_pattern(self, subject):
        """Test getting state IDs with pattern."""
        manager, mock_cursor = subject

        # Mock cursor response
        mock_cursor.__iter__.return_value = iter([("test_job_1",), ("test_job_2",)])

        # Get state IDs with pattern
        state_ids = list(manager.get_state_ids("test_*"))

        # Verify query with LIKE
        mock_cursor.execute.assert_called()
        call_args = mock_cursor.execute.call_args
        assert "WHERE state_id LIKE" in call_args[0][0]
        assert call_args[0][1] == ("test_%",)

        # Verify returned IDs
        assert state_ids == ["test_job_1", "test_job_2"]

    def test_clear_all(self, subject):
        """Test clearing all states."""
        manager, mock_cursor = subject

        # Mock count query response
        mock_cursor.fetchone.return_value = (5,)

        # Clear all
        count = manager.clear_all()

        # Verify queries
        assert mock_cursor.execute.call_count == 2
        calls = mock_cursor.execute.call_args_list
        assert "SELECT COUNT(*)" in calls[0][0][0]
        assert "TRUNCATE TABLE" in calls[1][0][0]

        # Verify returned count
        assert count == 5

    def test_acquire_lock(self, subject):
        """Test acquiring and releasing lock."""
        manager, mock_cursor = subject

        # Test successful lock acquisition
        with manager.acquire_lock("test_job", retry_seconds=0):
            # Verify INSERT query for lock
            assert mock_cursor.execute.call_count >= 1
            insert_call = mock_cursor.execute.call_args_list[0]
            assert "INSERT INTO" in insert_call[0][0]
            assert "meltano_state_locks" in insert_call[0][0]

        # Verify DELETE queries for lock release and cleanup
        delete_calls = [
            call
            for call in mock_cursor.execute.call_args_list
            if "DELETE FROM" in call[0][0]
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
