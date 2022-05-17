import json

import pytest

from meltano.core.state_service import InvalidJobStateError
from meltano.core.utils import merge


class TestStateService:
    def test_validate_state(self, state_service):
        with pytest.raises(InvalidJobStateError):
            state_service.validate_state(
                json.loads('{"root key not singer_state": {}}')
            )
        assert (
            state_service.validate_state(
                json.loads(
                    '{"singer_state": {"bookmarks": {"mock-stream": "mock-value"}}}'
                )
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
        assert state_service.get_state(mock_job_id) == payloads.mock_state_payloads[0]

    def test_set_state(self, job_history_session, jobs, payloads, state_service):
        for job in jobs:
            for state in payloads.mock_state_payloads:
                state_service.set_state(job.job_id, json.dumps(state))
                assert state_service.get_state(job.job_id) == state

    def test_clear_state(self, job_history_session, jobs, payloads, state_service):
        for job in jobs:
            state_service.clear_state(job.job_id)
            assert state_service.get_state(job.job_id) == payloads.mock_empty_payload

    def test_merge_state(self, job_history_session, jobs, state_service):
        job_pairs = []
        for idx in range(0, len(jobs) - 1, 2):
            job_pairs.append((jobs[idx], jobs[idx + 1]))
        for (job_src, job_dst) in job_pairs:
            state_src = state_service.get_state(job_src.job_id)
            state_dst = state_service.get_state(job_dst.job_id)
            merged_dst = merge(state_src, state_dst)
            state_service.merge_state(job_src.job_id, job_dst.job_id)
            assert merged_dst == state_service.get_state(job_dst.job_id)

    def test_copy(self, job_ids, state_service):
        job_pairs = []
        for idx in range(0, len(job_ids) - 1, 2):
            job_pairs.append((job_ids[idx], job_ids[idx + 1]))
        for (job_src, job_dst) in job_pairs:
            state_src = state_service.get_state(job_src)
            state_service.copy_state(job_src, job_dst)
            assert state_service.get_state(job_dst) == state_src

    def test_move(self, job_ids, state_service):
        job_pairs = []
        for idx in range(0, len(job_ids) - 1, 2):
            job_pairs.append((job_ids[idx], job_ids[idx + 1]))
        for (job_src, job_dst) in job_pairs:
            state_src = state_service.get_state(job_src)
            state_service.move_state(job_src, job_dst)
            assert not state_service.get_state(job_src)
            assert state_service.get_state(job_dst) == state_src
