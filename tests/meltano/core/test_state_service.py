import json

import pytest

from meltano.core.state_service import InvalidJobStateError


class TestStateService:
    def test_validate_state(self, state_service):
        with pytest.raises(json.decoder.JSONDecodeError):
            state_service.validate_state("bad state")
        with pytest.raises(InvalidJobStateError):
            state_service.validate_state('{"root key not singer_state": {}}')
        assert (
            state_service.validate_state(
                '{"singer_state": {"bookmarks": {"mock-stream": "mock-value"}}}'
            )
            is None
        )

    def test_get_state(self, state_service, job_ids_with_expected_states):
        for (job_id, expected_state) in job_ids_with_expected_states:
            assert state_service.get_state(job_id) == expected_state

    def test_list_state(self, state_service, job_ids_with_expected_states):
        assert state_service.list_state() == {
            job_id: expected_state
            for (job_id, expected_state) in job_ids_with_expected_states
        }

    def test_add_state(self, state_service, payloads):
        mock_job_id = "nonexistent"
        state_service.add_state(
            mock_job_id, json.dumps(payloads.mock_state_payloads[0])
        )
        assert (
            state_service.get_state(mock_job_id)
            == payloads.mock_state_payloads[0]["singer_state"]
        )

    def test_set_state(self, job_history_session, jobs, payloads, state_service):
        for job in jobs:
            for state in payloads.mock_state_payloads:
                state_service.set_state(job.job_id, json.dumps(state))
                assert state_service.get_state(job.job_id) == state["singer_state"]

    def test_clear_state(self, job_history_session, jobs, payloads, state_service):
        for job in jobs:
            state_service.clear_state(job.job_id)
            assert state_service.get_state(job.job_id) == payloads.mock_empty_payload
