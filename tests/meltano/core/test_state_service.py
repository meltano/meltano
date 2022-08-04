from __future__ import annotations

import json
import platform

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

    def test_get_state(self, state_service, state_ids_with_expected_states):
        for (state_id, expected_state) in state_ids_with_expected_states:
            assert state_service.get_state(state_id) == expected_state

    def test_list_state(self, state_service, state_ids_with_expected_states):
        assert state_service.list_state() == {
            state_id: expected_state
            for (state_id, expected_state) in state_ids_with_expected_states
        }

    def test_add_state(self, state_service, payloads):
        mock_state_id = "nonexistent"
        state_service.add_state(
            mock_state_id, json.dumps(payloads.mock_state_payloads[0])
        )
        assert state_service.get_state(mock_state_id) == payloads.mock_state_payloads[0]

    def test_set_state(self, job_history_session, jobs, payloads, state_service):
        if platform.system() == "Windows":
            pytest.xfail(
                "Doesn't pass on windows, this is currently being tracked here https://github.com/meltano/meltano/issues/3444"
            )

        for job in jobs:
            for state in payloads.mock_state_payloads:
                state_service.set_state(job.job_name, json.dumps(state))
                assert state_service.get_state(job.job_name) == state

    def test_clear_state(self, job_history_session, jobs, payloads, state_service):
        for job in jobs:
            state_service.clear_state(job.job_name)
            assert state_service.get_state(job.job_name) == payloads.mock_empty_payload

    def test_merge_state(self, job_history_session, jobs, state_service):
        job_pairs = []
        for idx in range(0, len(jobs) - 1, 2):
            job_pairs.append((jobs[idx], jobs[idx + 1]))
        for (job_src, job_dst) in job_pairs:
            state_src = state_service.get_state(job_src.job_name)
            state_dst = state_service.get_state(job_dst.job_name)
            merged_dst = merge(state_src, state_dst)
            state_service.merge_state(job_src.job_name, job_dst.job_name)
            assert merged_dst == state_service.get_state(job_dst.job_name)

    def test_copy(self, state_ids, state_service):
        state_id_pairs = []
        for idx in range(0, len(state_ids) - 1, 2):
            state_id_pairs.append((state_ids[idx], state_ids[idx + 1]))
        for (state_id_src, state_id_dst) in state_id_pairs:
            state_src = state_service.get_state(state_id_src)
            state_service.copy_state(state_id_src, state_id_dst)
            assert state_service.get_state(state_id_dst) == state_src

    def test_move(self, state_ids, state_service):
        state_id_pairs = []
        for idx in range(0, len(state_ids) - 1, 2):
            state_id_pairs.append((state_ids[idx], state_ids[idx + 1]))
        for (state_id_src, state_id_dst) in state_id_pairs:
            state_src = state_service.get_state(state_id_src)
            state_service.move_state(state_id_src, state_id_dst)
            assert not state_service.get_state(state_id_src)
            assert state_service.get_state(state_id_dst) == state_src
