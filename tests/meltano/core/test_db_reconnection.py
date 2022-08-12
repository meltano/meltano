from __future__ import annotations

import pytest
from mock import Mock
from sqlalchemy.exc import OperationalError

from meltano.core.db import connect


class TestConnectionRetries:
    def test_ping_failure(self):
        engine_mock = Mock()

        # check if OperationalError is raised if a connection can't be made
        engine_mock.connect.side_effect = OperationalError(
            "test_error", "test_error", "test_error"
        )
        with pytest.raises(OperationalError):
            connect(engine=engine_mock, max_retries=3, retry_timeout=0.1)

        assert engine_mock.connect.call_count == 4

        # check reconnect on second call to `engine.connect`
        engine_mock.reset_mock()
        engine_mock.connect.side_effect = [
            OperationalError("test_error", "test_error", "test_error"),
            None,
        ]

        connect(engine=engine_mock, max_retries=3, retry_timeout=0.1)
        assert engine_mock.connect.call_count == 2
