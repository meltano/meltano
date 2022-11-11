from __future__ import annotations

import json

import pytest

from meltano.core.job_state import JobState
from meltano.core.state_store import DBStateStoreManager


class TestDBStateStoreManager:
    @pytest.fixture
    def subject(self, job_history_session, state_ids_with_jobs):
        return DBStateStoreManager(session=job_history_session)

    def test_get_state(
        self, subject: DBStateStoreManager, state_ids_with_expected_states
    ):
        for (state_id, expected_state) in state_ids_with_expected_states:
            assert json.loads(subject.get(state_id).json_merged()) == expected_state

    def test_set_state(self, subject: DBStateStoreManager):

        # New partial is set
        partial_only = JobState(
            state_id="partial_only", partial_state={"singer_state": {"partial": 1}}
        )
        subject.set(partial_only)
        assert subject.get(partial_only.state_id) == partial_only

        # Partial merges onto existing partial
        new_partial = JobState(
            state_id="partial_only", partial_state={"singer_state": {"partial": 2}}
        )
        subject.set(new_partial)
        assert subject.get(partial_only.state_id) == new_partial

        # New complete is set
        complete_only = JobState(
            state_id="complete_only", completed_state={"singer_state": {"complete": 1}}
        )
        subject.set(complete_only)
        assert subject.get(complete_only.state_id) == complete_only

        # Complete overwrites partial
        new_complete = JobState(
            state_id="partial_only", completed_state={"singer_state": {"complete": 1}}
        )
        subject.set(new_complete)
        assert subject.get(partial_only.state_id) == new_complete

        # Complete overwrites complete
        new_complete_overwritten = JobState(
            state_id="complete_only", completed_state={"singer_state": {"complete": 1}}
        )
        subject.set(new_complete_overwritten)
        assert subject.get(complete_only.state_id) == new_complete_overwritten

        # Partial merges onto complete
        complete_with_partial = JobState(
            state_id="complete_only", partial_state={"singer_state": {"partial": 1}}
        )
        subject.set(complete_with_partial)
        assert subject.get(complete_only.state_id) == JobState(
            state_id="complete_only",
            partial_state={"singer_state": {"partial": 1}},
            completed_state={"singer_state": {"complete": 1}},
        )

    def test_get_state_ids(self, subject: DBStateStoreManager, state_ids_with_jobs):
        assert set(subject.get_state_ids()) == set(state_ids_with_jobs.keys())
