import json
import os
from unittest import mock

import pytest

from asserts import assert_cli_runner
from meltano.cli import cli, state
from meltano.core.utils import merge

unconventional_job_ids = [
    "unconventional",
    "dev:tap-and-target",
    "tap-mock-to-target-mock",
    "staging:",
    "staging:tap-mock-to-",
    "dev:-to-target-mock",
]

conventional_job_ids = ["dev:tap-mock-to-target-mock", "staging:mock-to-mock"]


class TestCliState:
    @pytest.mark.parametrize("job_id", unconventional_job_ids)
    def test_state_service_from_job_id_returns_none_non_convention(  # noqa: WPS118
        self, project, job_id
    ):
        assert state.state_service_from_job_id(project, job_id) is None

    @pytest.mark.parametrize("job_id", conventional_job_ids)
    def test_state_service_from_job_id_returns_state_service_convention(  # noqa: WPS118
        self, project, job_id
    ):
        with mock.patch(
            "meltano.cli.state.BlockParser",
            autospec=True,
        ) as mock_block_parser:
            state.state_service_from_job_id(project, job_id)
            assert (
                job_id.split(":")[1].split("-to-") in mock_block_parser.call_args.args
            )

    @staticmethod
    def get_result_set(result):
        result_set = set(result.stdout.split("\n"))
        result_set.remove("")
        return result_set

    def test_list(self, project, job_ids, state_service, cli_runner):
        with mock.patch("meltano.cli.state.StateService", return_value=state_service):
            result = cli_runner.invoke(cli, ["state", "list"])
        assert_cli_runner(result)
        assert self.get_result_set(result) == set(job_ids)

    @pytest.fixture
    def patterns_with_expected_results(self, job_ids):
        return [
            (
                "test:*",
                set(filter(lambda job_id: job_id.startswith("test:"), list(job_ids))),
            ),
            ("*-to-*", set(job_ids)),
            ("multiple-complete", set()),
            (
                "*multiple-complete",
                set(
                    filter(
                        lambda job_id: job_id.endswith("multiple-complete"),
                        list(job_ids),
                    )
                ),
            ),
        ]

    def test_list_pattern(
        self, state_service, cli_runner, patterns_with_expected_results
    ):
        with mock.patch("meltano.cli.state.StateService", return_value=state_service):
            for (pattern, expected_result) in patterns_with_expected_results:
                result = cli_runner.invoke(cli, ["state", "list", "--pattern", pattern])
                assert_cli_runner(result)
                assert self.get_result_set(result) == expected_result

    def test_set_from_string(self, state_service, job_ids, payloads, cli_runner):
        with mock.patch("meltano.cli.state.StateService", return_value=state_service):
            for job_id in job_ids:
                for state_payload in payloads.mock_state_payloads:
                    result = cli_runner.invoke(
                        cli,
                        [
                            "state",
                            "set",
                            "--force",
                            job_id,
                            "--state",
                            json.dumps(state_payload),
                        ],
                    )
                    assert_cli_runner(result)
                    assert (
                        state_service.get_state(job_id) == state_payload["singer_state"]
                    )

    def test_set_from_file(self, mkdtemp, state_service, job_ids, payloads, cli_runner):
        tmp_path = mkdtemp()
        with mock.patch("meltano.cli.state.StateService", return_value=state_service):
            for idx_i, job_id in enumerate(job_ids):
                for idx_j, state_payload in enumerate(payloads.mock_state_payloads):
                    filepath = os.path.join(
                        tmp_path, f"state-file-{idx_i}-{idx_j}.json"
                    )
                    with open(filepath, "w+") as state_file:
                        json.dump(state_payload, state_file)
                    result = cli_runner.invoke(
                        cli,
                        ["state", "set", "--force", job_id, "--input-file", filepath],
                    )
                    assert_cli_runner(result)
                    assert (
                        state_service.get_state(job_id) == state_payload["singer_state"]
                    )

    def test_merge_from_string(self, state_service, payloads, cli_runner):
        with mock.patch("meltano.cli.state.StateService", return_value=state_service):
            job_id = "nonexistent_job_id"
            result = cli_runner.invoke(
                cli,
                [
                    "state",
                    "merge",
                    job_id,
                    "--state",
                    json.dumps(payloads.mock_state_payloads[0]),
                ],
            )
            assert_cli_runner(result)
            assert (
                state_service.get_state(job_id)
                == payloads.mock_state_payloads[0]["singer_state"]
            )

    def test_merge_from_file(
        self, mkdtemp, state_service, job_ids, payloads, cli_runner
    ):
        tmp_path = mkdtemp()
        job_id = "nonexistent_job_id"
        with mock.patch("meltano.cli.state.StateService", return_value=state_service):
            filepath = os.path.join(tmp_path, "state-file-test-add-path.json")
            with open(filepath, "w+") as state_file:
                json.dump(payloads.mock_state_payloads[0], state_file)
            result = cli_runner.invoke(
                cli, ["state", "merge", job_id, "--input-file", filepath]
            )

            assert_cli_runner(result)
            assert (
                state_service.get_state(job_id)
                == payloads.mock_state_payloads[0]["singer_state"]
            )

    def test_merge_from_job(self, state_service, job_ids, cli_runner):
        with mock.patch("meltano.cli.state.StateService", return_value=state_service):
            job_pairs = []
            for idx in range(0, len(job_ids) - 1, 2):
                job_pairs.append((job_ids[idx], job_ids[idx + 1]))
            for (job_src, job_dst) in job_pairs:
                job_state_src = state_service.get_state(job_src)
                job_state_dst = state_service.get_state(job_dst)
                merged_state = merge(job_state_src, job_state_dst)
                result = cli_runner.invoke(
                    cli, ["state", "merge", "--from-job-id", job_src, job_dst]
                )
                assert_cli_runner(result)
                assert state_service.get_state(job_dst) == merged_state

    def test_get(self, state_service, cli_runner, job_ids_with_expected_states):
        with mock.patch("meltano.cli.state.StateService", return_value=state_service):
            for (job_id, expected_state) in job_ids_with_expected_states:
                result = cli_runner.invoke(cli, ["state", "get", job_id])
                assert_cli_runner(result)
                assert json.loads(result.stdout) == expected_state

    def test_clear(self, state_service, cli_runner, job_ids):
        with mock.patch("meltano.cli.state.StateService", return_value=state_service):
            for job_id in job_ids:
                result = cli_runner.invoke(cli, ["state", "clear", "--force", job_id])
                assert_cli_runner(result)
                job_state = state_service.get_state(job_id)
                assert (not job_state) or (not state.get("singer_state"))
