from __future__ import annotations

import json
import os
import platform
import sys

import mock
import pytest

from asserts import assert_cli_runner
from meltano.cli import cli, state
from meltano.core.utils import merge

unconventional_state_ids = [
    "unconventional",
    "dev:tap-and-target",
    "tap-mock-to-target-mock",
    "staging:",
    "staging:tap-mock-to-",
    "dev:-to-target-mock",
    "dev:tap-to-target:",
    "dev:tap-to-target:suffix:",
]

conventional_state_ids = [
    "dev:tap-mock-to-target-mock",
    "dev:tap-mock-to-target-mock:suffix",
    "staging:mock-to-mock",
]


class TestCliState:
    @pytest.mark.parametrize("state_id", unconventional_state_ids)
    def test_state_service_from_state_id_returns_none_non_convention(  # noqa: WPS118
        self, project, state_id
    ):
        assert state.state_service_from_state_id(project, state_id) is None

    @pytest.mark.parametrize("state_id", conventional_state_ids)
    def test_state_service_from_state_id_returns_state_service_convention(  # noqa: WPS118
        self, project, state_id
    ):
        with mock.patch(
            "meltano.cli.state.BlockParser",
            autospec=True,
        ) as mock_block_parser:
            state.state_service_from_state_id(project, state_id)
            args = state_id.split(":")[1].split("-to-")
            if sys.version_info >= (3, 8):
                assert args in mock_block_parser.call_args.args
            else:
                assert args in mock_block_parser.call_args[0]

    @staticmethod
    def get_result_set(result):
        result_set = set(result.stdout.split("\n"))
        result_set.remove("")
        return result_set

    def test_list(self, project, state_ids, state_service, cli_runner):
        with mock.patch("meltano.cli.state.StateService", return_value=state_service):
            result = cli_runner.invoke(cli, ["state", "list"])
        assert_cli_runner(result)
        assert self.get_result_set(result) == set(state_ids)

    @pytest.fixture
    def patterns_with_expected_results(self, state_ids):
        return [
            (
                "test:*",
                set(
                    filter(
                        lambda state_id: state_id.startswith("test:"), list(state_ids)
                    )
                ),
            ),
            ("*-to-*", set(state_ids)),
            ("multiple-complete", set()),
            (
                "*multiple-complete",
                set(
                    filter(
                        lambda state_id: state_id.endswith("multiple-complete"),
                        list(state_ids),
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

    def test_set_from_string(self, state_service, state_ids, payloads, cli_runner):
        with mock.patch("meltano.cli.state.StateService", return_value=state_service):
            for state_id in state_ids:
                for state_payload in payloads.mock_state_payloads:
                    result = cli_runner.invoke(
                        cli,
                        [
                            "state",
                            "set",
                            "--force",
                            state_id,
                            json.dumps(state_payload),
                        ],
                    )
                    assert_cli_runner(result)
                    assert state_service.get_state(state_id) == state_payload

    def test_set_from_file(
        self, tmp_path, state_service, state_ids, payloads, cli_runner
    ):
        with mock.patch("meltano.cli.state.StateService", return_value=state_service):
            for idx_i, state_id in enumerate(state_ids):
                for idx_j, state_payload in enumerate(payloads.mock_state_payloads):
                    filepath = os.path.join(
                        tmp_path, f"state-file-{idx_i}-{idx_j}.json"
                    )
                    with open(filepath, "w+") as state_file:
                        json.dump(state_payload, state_file)
                    result = cli_runner.invoke(
                        cli,
                        ["state", "set", "--force", state_id, "--input-file", filepath],
                    )
                    assert_cli_runner(result)
                    assert state_service.get_state(state_id) == state_payload

    def test_merge_from_string(self, state_service, state_ids, cli_runner):
        with mock.patch("meltano.cli.state.StateService", return_value=state_service):
            job_pairs = []
            for idx in range(0, len(state_ids) - 1, 2):
                job_pairs.append((state_ids[idx], state_ids[idx + 1]))
            for (job_src, job_dst) in job_pairs:
                job_src_state = state_service.get_state(job_src)
                job_dst_state = state_service.get_state(job_dst)
                result = cli_runner.invoke(
                    cli,
                    [
                        "state",
                        "merge",
                        job_dst,
                        json.dumps(job_src_state),
                    ],
                )
                assert_cli_runner(result)
                assert state_service.get_state(job_dst) == merge(
                    job_src_state, job_dst_state
                )

    def test_merge_from_file(
        self, tmp_path, state_service, state_ids, payloads, cli_runner
    ):
        if platform.system() == "Windows":
            pytest.xfail(
                "Doesn't pass on windows, this is currently being tracked here https://github.com/meltano/meltano/issues/3444"
            )
        with mock.patch("meltano.cli.state.StateService", return_value=state_service):
            job_pairs = []
            for idx in range(0, len(state_ids) - 1, 2):
                job_pairs.append((state_ids[idx], state_ids[idx + 1]))
            for (job_src, job_dst) in job_pairs:
                job_src_state = state_service.get_state(job_src)
                job_dst_state = state_service.get_state(job_dst)
                filepath = os.path.join(tmp_path, f"{job_src}-{job_dst}")
                with open(filepath, "w+") as state_file:
                    json.dump(job_src_state, state_file)
                result = cli_runner.invoke(
                    cli,
                    ["state", "merge", job_dst, "--input-file", filepath],
                )
                assert_cli_runner(result)
                assert state_service.get_state(job_dst) == merge(
                    job_src_state, job_dst_state
                )

    def test_merge_from_job(self, state_service, state_ids, cli_runner):
        with mock.patch("meltano.cli.state.StateService", return_value=state_service):
            job_pairs = []
            for idx in range(0, len(state_ids) - 1, 2):
                job_pairs.append((state_ids[idx], state_ids[idx + 1]))
            for (job_src, job_dst) in job_pairs:
                job_state_src = state_service.get_state(job_src)
                job_state_dst = state_service.get_state(job_dst)
                merged_state = merge(job_state_src, job_state_dst)
                result = cli_runner.invoke(
                    cli, ["state", "merge", "--from-state-id", job_src, job_dst]
                )
                assert_cli_runner(result)
                assert state_service.get_state(job_dst) == merged_state

    def test_copy_over_existing(self, state_service, state_ids, cli_runner):
        with mock.patch("meltano.cli.state.StateService", return_value=state_service):
            job_pairs = []
            for idx in range(0, len(state_ids) - 1, 2):
                job_pairs.append((state_ids[idx], state_ids[idx + 1]))
            for (job_src, job_dst) in job_pairs:
                job_src_state = state_service.get_state(job_src)
                result = cli_runner.invoke(
                    cli,
                    ["state", "copy", job_src, job_dst, "--force"],
                )
                assert_cli_runner(result)
                assert state_service.get_state(job_dst) == job_src_state

    def test_copy_to_new(self, state_service, state_ids, cli_runner):
        with mock.patch("meltano.cli.state.StateService", return_value=state_service):
            for job_src_id in state_ids:
                job_src_state = state_service.get_state(job_src_id)
                job_dst_id = f"{job_src_id}-test-copy"
                result = cli_runner.invoke(
                    cli,
                    ["state", "copy", job_src_id, job_dst_id, "--force"],
                )
                assert_cli_runner(result)
                assert state_service.get_state(job_dst_id) == job_src_state

    def test_move(self, state_service, state_ids, cli_runner):
        with mock.patch("meltano.cli.state.StateService", return_value=state_service):
            job_pairs = []
            for idx in range(0, len(state_ids) - 1, 2):
                job_pairs.append((state_ids[idx], state_ids[idx + 1]))
            for (job_src, job_dst) in job_pairs:
                job_src_state = state_service.get_state(job_src)
                result = cli_runner.invoke(
                    cli,
                    ["state", "move", job_src, job_dst, "--force"],
                )
                assert_cli_runner(result)
                assert not state_service.get_state(job_src)
                assert state_service.get_state(job_dst) == job_src_state

    def test_get(self, state_service, cli_runner, state_ids_with_expected_states):
        with mock.patch("meltano.cli.state.StateService", return_value=state_service):
            for (state_id, expected_state) in state_ids_with_expected_states:
                result = cli_runner.invoke(cli, ["state", "get", state_id])
                assert_cli_runner(result)
                assert json.loads(result.stdout) == expected_state

    def test_clear(self, state_service, cli_runner, state_ids):
        with mock.patch("meltano.cli.state.StateService", return_value=state_service):
            for state_id in state_ids:
                result = cli_runner.invoke(cli, ["state", "clear", "--force", state_id])
                assert_cli_runner(result)
                job_state = state_service.get_state(state_id)
                assert (not job_state) or (not job_state.get("singer_state"))
