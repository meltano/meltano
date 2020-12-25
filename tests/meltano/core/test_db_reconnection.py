from unittest.mock import Mock, call

import pytest
from meltano.core.db import check_db_connection
from sqlalchemy.exc import OperationalError


class TestConnectionRetries:
    def test_ping_failure(self):
        engine = Mock()

        # check if OperationalError is raised if a connection can't be made
        engine.connect.side_effect = OperationalError(
            "test_error", "test_error", "test_error"
        )
        with pytest.raises(OperationalError):
            check_db_connection(engine=engine, max_retries=3, retry_timeout=0.1)

        calls = [call.connect() * 4]
        engine.assert_has_calls(calls, any_order=True)

        # check reconnect on second call to `engine.connect`
        engine.reset_mock()
        engine.connect.side_effect = [
            OperationalError("test_error", "test_error", "test_error"),
            None,
        ]

        check_db_connection(engine=engine, max_retries=3, retry_timeout=0.1)
        calls = [call.connect(), call.connect()]
        engine.assert_has_calls(calls, any_order=True)
