from unittest.mock import Mock

import pytest
from sqlalchemy.exc import OperationalError

from meltano.core.db import check_db_connection


class TestConnectionRetries:
    def test_ping_failure(self):
        engine_mock = Mock()

        # check if OperationalError is raised if a connection can't be made
        engine_mock.connect.side_effect = OperationalError(
            "test_error", "test_error", "test_error"
        )
        with pytest.raises(OperationalError):
            check_db_connection(engine=engine_mock, max_retries=3, retry_timeout=0.1)

        assert engine_mock.connect.call_count == 4

        # check reconnect on second call to `engine.connect`
        engine_mock.reset_mock()
        engine_mock.connect.side_effect = [
            OperationalError("test_error", "test_error", "test_error"),
            None,
        ]

        check_db_connection(engine=engine_mock, max_retries=3, retry_timeout=0.1)
        assert engine_mock.connect.call_count == 2
