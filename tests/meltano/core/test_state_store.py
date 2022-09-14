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
            job_name="mock_state_with_only_partial", partial_state=partial_state
        )
        mock_state_with_only_complete = JobState(
            job_name="mock_state_with_only_complete", completed_state=complete_state
        )

        subject.set(
            mock_state_with_only_partial.job_name, json.dumps(partial_state), False
        )
        assert subject.get(mock_state_with_only_partial.job_name) == partial_state

        subject.set(
            mock_state_with_only_complete.job_name, json.dumps(complete_state), True
        )
        assert subject.get(mock_state_with_only_complete.job_name) == complete_state

        subject.set(
            mock_state_with_only_complete.job_name, json.dumps(partial_state), False
        )
        assert subject.get(mock_state_with_only_complete.job_name) == merge(
            partial_state, complete_state
        )

        subject.set(
            mock_state_with_only_complete.job_name,
            json.dumps(overwritten_complete),
            True,
        )

        assert (
            subject.get(mock_state_with_only_complete.job_name) == overwritten_complete
        )

        subject.set(
            mock_state_with_only_partial.job_name,
            json.dumps(overwritten_partial),
            False,
        )
        assert subject.get(mock_state_with_only_partial.job_name) == overwritten_partial

        subject.set(
            mock_state_with_only_partial.job_name, json.dumps(second_partial), False
        )
        assert subject.get(mock_state_with_only_partial.job_name) == merge(
            overwritten_partial, second_partial
        )

    def test_get_job_names(self, subject: DBStateStoreManager, state_ids_with_jobs):
        assert set(subject.get_job_names()) == set(state_ids_with_jobs.keys())
