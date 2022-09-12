from __future__ import annotations

import pytest

from meltano.core.job_state import JobState
from meltano.core.state_store import DBStateStoreManager


class TestDBStateStoreManager:
    @pytest.fixture
    def subject(self, session):
        # TODO: populate a bunch of mock state
        mock_state = JobState(
            job_name="mock_job",
            partial_state={
                "singer_state_1": "mock_partial_state_1",
                "singer_state_2": "mock_partial_state_1",
            },
            completed_state={
                "singer_state_1": "mock_partial_state_0",
                "singer_state_3": "mock_partial_state_3",
            },
        )
        session.add(mock_state)
        session.commit()
        return DBStateStoreManager(session=session)

    def test_get_state(self, subject: DBStateStoreManager):
        assert subject.get("mock_job") == {
            "singer_state_1": "mock_partial_state_1",
            "singer_state_2": "mock_partial_state_1",
            "singer_state_3": "mock_partial_state_3",
        }

    def test_set_state(self, subject: DBStateStoreManager):
        ...
