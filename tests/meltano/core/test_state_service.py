import itertools
import json
from collections import namedtuple
from datetime import datetime, timedelta

import pytest

from meltano.core.block.extract_load import generate_job_id
from meltano.core.job import Job, Payload, State
from meltano.core.state_service import InvalidJobStateError, StateService
from meltano.core.utils import merge


class TestStateService:
    def test_validate_state(self, state_service):
        with pytest.raises(json.decoder.JSONDecodeError):
            state_service.validate_state("bad state")
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
            k: v for (k, v) in job_ids_with_expected_states
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
