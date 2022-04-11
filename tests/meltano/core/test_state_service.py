import itertools
import json
from collections import namedtuple
from datetime import datetime, timedelta

import pytest

from meltano.core.block.extract_load import generate_job_id
from meltano.core.job import Job, Payload, State
from meltano.core.state_service import InvalidJobStateError, StateService
from meltano.core.utils import merge

# TODO: Do this with mocks
MockNameOnlyEnv = namedtuple("MockNameOnlyEnv", "name")
MockEnvOnlyProject = namedtuple("MockEnvOnlyProject", "active_environment")
MockStringIDOnlyBlock = namedtuple("MockStringIDOnlyBlock", "string_id")

num_params = 10
mock_state_payloads = [
    {"singer_state": {f"bookmark-{j}": j + i for i in range(num_params)}}
    for j in range(num_params)
]
mock_error_payload = {"error": "failed"}
mock_empty_payload = {}


def create_job_id(description: str, env: str = "test") -> str:
    return f"{env}:tap-{description}-to-target-{description}"


single_incomplete_job_id = create_job_id("single-incomplete")
single_complete_job_id = create_job_id("single-complete")
multiple_incompletes_job_id = create_job_id("multiple-incompletes")
multiple_completes_job_id = create_job_id("multiple-completes")
single_complete_then_multiple_incompletes_job_id = create_job_id(
    "single-complete-then-multiple-incompletes"
)
single_incomplete_then_multiple_completes_job_id = create_job_id(
    "single-incomplete-then-multiple-completes"
)
complete_job_args = dict(state=State.SUCCESS, payload_flags=Payload.STATE)
incomplete_job_args = dict(state=State.FAIL, payload_flags=Payload.INCOMPLETE_STATE)


class TestStateService:
    @pytest.fixture
    def mock_time(self):
        def _mock_time():
            for i in itertools.count():
                yield datetime(2022, 1, 1) + timedelta(hours=i)

        return _mock_time()

    @staticmethod
    def get_state_from_payload(payload):
        return payload.get("singer_state") or payload

    @pytest.fixture
    def job_ids_with_jobs(self, mock_time):
        jobs = {
            single_incomplete_job_id: [
                Job(
                    job_id=single_incomplete_job_id,
                    **incomplete_job_args,
                    payload=mock_state_payloads[0],
                )
            ],
            single_complete_job_id: [
                Job(
                    job_id=single_complete_job_id,
                    payload=mock_state_payloads[0],
                    **complete_job_args,
                )
            ],
            multiple_incompletes_job_id: [
                Job(
                    job_id=multiple_incompletes_job_id,
                    **incomplete_job_args,
                    payload=payload,
                )
                for payload in mock_state_payloads
            ],
            multiple_completes_job_id: [
                Job(
                    job_id=multiple_completes_job_id,
                    payload=payload,
                    **complete_job_args,
                )
                for payload in mock_state_payloads
            ],
            single_complete_then_multiple_incompletes_job_id: [
                Job(
                    job_id=single_complete_then_multiple_incompletes_job_id,
                    payload=mock_state_payloads[0],
                    **complete_job_args,
                )
            ]
            + [
                Job(
                    job_id=single_complete_then_multiple_incompletes_job_id,
                    payload=payload,
                    **incomplete_job_args,
                )
                for payload in mock_state_payloads[1:]
            ],
            single_incomplete_then_multiple_completes_job_id: [
                Job(
                    job_id=single_incomplete_then_multiple_completes_job_id,
                    payload=mock_state_payloads[0],
                    **incomplete_job_args,
                )
            ]
            + [
                Job(
                    job_id=single_incomplete_then_multiple_completes_job_id,
                    payload=payload,
                    **complete_job_args,
                )
                for payload in mock_state_payloads[1:]
            ],
        }
        for job_list in jobs.values():
            for job in job_list:
                job.started_at = next(mock_time)
                job.ended_at = next(mock_time)
        return jobs

    @pytest.fixture
    def jobs(self, job_ids_with_jobs):
        return [job for job_list in job_ids_with_jobs.values() for job in job_list]

    @pytest.fixture
    def job_ids_with_expected_states(self, job_ids_with_jobs):
        final_state = {}
        for state in mock_state_payloads:
            merge(state, final_state)
        expectations = {
            single_complete_job_id: self.get_state_from_payload(mock_state_payloads[0]),
            single_incomplete_job_id: mock_empty_payload,
        }
        for job_id in job_ids_with_jobs.keys():
            if job_id not in [single_complete_job_id, single_incomplete_job_id]:
                expectations[job_id] = final_state
        return expectations.items()

    @pytest.fixture
    def job_history_session(self, jobs, session):
        for job in jobs:
            job.save(session)
        yield session

    @pytest.fixture
    def state_service(self, job_history_session):
        return StateService(session=job_history_session)

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
            k: self.get_state_from_payload(v) for (k, v) in job_ids_with_expected_states
        }

    def test_add_state(self, state_service):
        mock_job_id = "nonexistent"
        state_service.add_state(mock_job_id, json.dumps(mock_state_payloads[0]))
        assert (
            state_service.get_state(mock_job_id)
            == mock_state_payloads[0]["singer_state"]
        )

    def test_set_state(self, job_history_session, jobs, state_service):
        for job in jobs:
            for state in mock_state_payloads:
                state_service.set_state(job.job_id, json.dumps(state))
                assert state_service.get_state(
                    job.job_id
                ) == self.get_state_from_payload(state)

    def test_clear_state(self, job_history_session, jobs, state_service):
        for job in jobs:
            state_service.clear_state(job.job_id)
            assert state_service.get_state(job.job_id) == mock_empty_payload
