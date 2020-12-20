from meltano.core.db import check_db_connection
from unittest.mock import call, Mock
from sqlalchemy.exc import OperationalError
import pytest


class TestConnectionRetries:
    def test_ping_failure(self):
        engine = Mock()

        # check if OperationalError is raised if a connection can't be made
        engine.connect.side_effect = OperationalError(
            "test_error", 
            "test_error", "test_error"
        )
        with pytest.raises(OperationalError):
            check_db_connection(engine, 3, 0.1)

        # check reconnect on second call to `engine.connect`
        engine.reset_mock()
        engine.connect.side_effect = [
            OperationalError("test_error", "test_error", "test_error"),
            None,
        ]
        check_db_connection(engine, 3, 0.1)
        calls = [call.connect(), call.connect()]
        engine.assert_has_calls(calls, any_order=True)
        