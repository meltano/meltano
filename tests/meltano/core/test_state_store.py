from __future__ import annotations

import json

import pytest

from meltano.core.job_state import JobState
from meltano.core.state_store import DBStateStoreManager
from meltano.core.utils import merge


class TestDBStateStoreManager:
    @pytest.fixture
    def subject(self, job_history_session, state_ids_with_jobs):
        return DBStateStoreManager(session=job_history_session)

    def test_get_state(
        self, subject: DBStateStoreManager, state_ids_with_expected_states
    ):
        for (state_id, expected_state) in state_ids_with_expected_states:
            assert subject.get(state_id) == expected_state

    def test_set_state(self, subject: DBStateStoreManager):
        partial_state = {"singer_state": {"partial": 1}}
        complete_state = {"singer_state": {"complete": 1}}
        overwritten_partial = {"singer_state": {"partial": "overwritten"}}
        overwritten_complete = {"singer_state": {"complete": "overwritten"}}
        second_partial = {"singer_state": {"partial_2": 2}}

        mock_state_with_only_partial = JobState(
            state_id="mock_state_with_only_partial", partial_state=partial_state
        )
        mock_state_with_only_complete = JobState(
            state_id="mock_state_with_only_complete", completed_state=complete_state
        )

        subject.set(
            mock_state_with_only_partial.state_id, json.dumps(partial_state), False
        )
        assert subject.get(mock_state_with_only_partial.state_id) == partial_state

        subject.set(
            mock_state_with_only_complete.state_id, json.dumps(complete_state), True
        )
        assert subject.get(mock_state_with_only_complete.state_id) == complete_state

        subject.set(
            mock_state_with_only_complete.state_id, json.dumps(partial_state), False
        )
        assert subject.get(mock_state_with_only_complete.state_id) == merge(
            partial_state, complete_state
        )

        subject.set(
            mock_state_with_only_complete.state_id,
            json.dumps(overwritten_complete),
            True,
        )

        assert (
            subject.get(mock_state_with_only_complete.state_id) == overwritten_complete
        )

        subject.set(
            mock_state_with_only_partial.state_id,
            json.dumps(overwritten_partial),
            False,
        )
        assert subject.get(mock_state_with_only_partial.state_id) == overwritten_partial

        subject.set(
            mock_state_with_only_partial.state_id, json.dumps(second_partial), False
        )
        assert subject.get(mock_state_with_only_partial.state_id) == merge(
            overwritten_partial, second_partial
        )

    def test_get_state_ids(self, subject: DBStateStoreManager, state_ids_with_jobs):
        assert set(subject.get_state_ids()) == set(state_ids_with_jobs.keys())
