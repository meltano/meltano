from __future__ import annotations

import json
import platform
import re
import typing as t
from unittest import mock

import pytest

from asserts import assert_cli_runner
from meltano.cli import cli, state
from meltano.core.state_service import InvalidJobStateError
from meltano.core.utils import merge

if t.TYPE_CHECKING:
    from pathlib import Path

    from click.testing import CliRunner, Result

    from fixtures.cli import MeltanoCliRunner
    from meltano.core.project import Project
    from meltano.core.state_service import StateService
    from tests.fixtures.core import Payloads

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
    def test_state_service_from_state_id_returns_none_non_convention(
        self,
        project: Project,
        state_id: str,
    ) -> None:
        assert state.state_service_from_state_id(project, state_id) is None

    @pytest.mark.parametrize("state_id", conventional_state_ids)
    def test_state_service_from_state_id_returns_state_service_convention(
        self,
        project: Project,
        state_id: str,
    ) -> None:
        with mock.patch(
            "meltano.cli.state.BlockParser",
            autospec=True,
        ) as mock_block_parser:
            state.state_service_from_state_id(project, state_id)
            args = state_id.split(":")[1].split("-to-")
            assert args in mock_block_parser.call_args.args

    @staticmethod
    def get_result_set(result: Result) -> set[str]:
        result_set = set(result.stdout.split("\n"))
        result_set.remove("")
        return result_set

    @staticmethod
    def invoke_with_state_service(
        cli_runner: CliRunner,
        state_service: StateService,
        args: list[str],
    ) -> Result:
        """Helper to invoke CLI with mocked StateService."""
        with mock.patch("meltano.cli.state.StateService", return_value=state_service):
            return cli_runner.invoke(cli, args)

    @pytest.mark.usefixtures("project")
    def test_list(
        self,
        state_ids: list[str],
        state_service: StateService,
        cli_runner: MeltanoCliRunner,
    ) -> None:
        result = self.invoke_with_state_service(
            cli_runner,
            state_service,
            ["state", "list"],
        )
        assert_cli_runner(result)
        assert self.get_result_set(result) == set(state_ids)

    @pytest.fixture
    def patterns_with_expected_results(
        self,
        state_ids: list[str],
    ) -> list[tuple[str, set[str]]]:
        return [
            (
                "test:*",
                set(
                    filter(
                        lambda state_id: state_id.startswith("test:"),
                        list(state_ids),
                    ),
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
                    ),
                ),
            ),
        ]

    def test_list_pattern(
        self,
        state_service: StateService,
        cli_runner: MeltanoCliRunner,
        patterns_with_expected_results: list[tuple[str, set[str]]],
    ) -> None:
        with mock.patch("meltano.cli.state.StateService", return_value=state_service):
            for pattern, expected_result in patterns_with_expected_results:
                result = cli_runner.invoke(cli, ["state", "list", "--pattern", pattern])
                assert_cli_runner(result)
                assert self.get_result_set(result) == expected_result

    def test_set_from_string(
        self,
        state_service: StateService,
        state_ids: list[str],
        payloads: Payloads,
        cli_runner: MeltanoCliRunner,
    ) -> None:
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
        self,
        tmp_path: Path,
        state_service: StateService,
        state_ids: list[str],
        payloads: Payloads,
        cli_runner: MeltanoCliRunner,
    ) -> None:
        with mock.patch("meltano.cli.state.StateService", return_value=state_service):
            for idx_i, state_id in enumerate(state_ids):
                for idx_j, state_payload in enumerate(payloads.mock_state_payloads):
                    filepath = tmp_path / f"state-file-{idx_i}-{idx_j}.json"
                    with filepath.open("w+") as state_file:
                        json.dump(state_payload, state_file)
                    result = cli_runner.invoke(
                        cli,
                        ["state", "set", "--force", state_id, "--input-file", filepath],
                    )
                    assert_cli_runner(result)
                    assert state_service.get_state(state_id) == state_payload

    def test_set_invalid_json(
        self,
        state_service: StateService,
        state_ids: list[str],
        cli_runner: MeltanoCliRunner,
    ) -> None:
        """Test that invalid JSON is rejected with a clear error message."""
        state_id = state_ids[0]
        invalid_json = "{ invalid json"

        with mock.patch("meltano.cli.state.StateService", return_value=state_service):
            result = cli_runner.invoke(
                cli,
                ["state", "set", "--force", state_id, invalid_json],
            )
            assert result.exit_code == 1
            assert "Invalid JSON provided" in result.stderr

    def test_set_empty_state_string(
        self,
        state_service: StateService,
        state_ids: list[str],
        cli_runner: MeltanoCliRunner,
        tmp_path: Path,
    ) -> None:
        """Test that empty string input for state is rejected with a clear message."""
        state_id = state_ids[0]
        filepath = tmp_path / "empty-state.json"
        filepath.write_text("")

        with mock.patch("meltano.cli.state.StateService", return_value=state_service):
            result = cli_runner.invoke(
                cli,
                ["state", "set", "--force", state_id, "--input-file", filepath],
            )
            assert result.exit_code == 1
            assert "Invalid JSON provided" in result.stderr

    def test_set_invalid_state_format(
        self,
        state_service: StateService,
        state_ids: list[str],
        cli_runner: MeltanoCliRunner,
    ) -> None:
        """Test that state without 'singer_state' key is rejected."""
        state_id = state_ids[0]
        invalid_state = {"invalid": "state"}

        with mock.patch("meltano.cli.state.StateService", return_value=state_service):
            result = cli_runner.invoke(
                cli,
                ["state", "set", "--force", state_id, json.dumps(invalid_state)],
            )
            assert result.exit_code == 1
            assert "Invalid state format" in result.stderr
            assert "singer_state" in result.stderr

    def test_set_nested_singer_state_key(
        self,
        state_service: StateService,
        state_ids: list[str],
        cli_runner: MeltanoCliRunner,
    ) -> None:
        """Test that state with nested 'singer_state' key is rejected."""
        state_id = state_ids[0]
        nested_state = {"outer": {"singer_state": {}}}

        with mock.patch("meltano.cli.state.StateService", return_value=state_service):
            result = cli_runner.invoke(
                cli,
                ["state", "set", "--force", state_id, json.dumps(nested_state)],
            )
            assert result.exit_code == 1
            assert "Invalid state format" in result.stderr
            assert "singer_state" in result.stderr

    def test_set_invalid_state_from_file(
        self,
        tmp_path: Path,
        state_service: StateService,
        state_ids: list[str],
        cli_runner: MeltanoCliRunner,
    ) -> None:
        """Test that invalid state from file is rejected."""
        state_id = state_ids[0]
        invalid_state = {"invalid": "state"}
        filepath = tmp_path / "invalid-state.json"

        with filepath.open("w") as state_file:
            json.dump(invalid_state, state_file)

        with mock.patch("meltano.cli.state.StateService", return_value=state_service):
            result = cli_runner.invoke(
                cli,
                ["state", "set", "--force", state_id, "--input-file", filepath],
            )
            assert result.exit_code == 1
            assert "Invalid state format" in result.stderr
            assert "singer_state" in result.stderr

    def test_set_no_validate_flag(
        self,
        state_service: StateService,
        state_ids: list[str],
        cli_runner: MeltanoCliRunner,
    ) -> None:
        """Test that --no-validate flag bypasses validation and emits warning."""
        state_id = state_ids[0]
        invalid_state = {"invalid": "state"}

        with mock.patch("meltano.cli.state.StateService", return_value=state_service):
            result = cli_runner.invoke(
                cli,
                [
                    "state",
                    "set",
                    "--force",
                    "--no-validate",
                    state_id,
                    json.dumps(invalid_state),
                ],
            )
            assert_cli_runner(result)
            # Check that a warning was logged
            assert "Skipping state validation" in result.stderr
            assert "Invalid state may cause issues" in result.stderr
            # Verify the invalid state was actually set
            assert state_service.get_state(state_id) == invalid_state

    def test_set_no_validate_from_file(
        self,
        tmp_path: Path,
        state_service: StateService,
        state_ids: list[str],
        cli_runner: MeltanoCliRunner,
    ) -> None:
        """Test that --no-validate works with --input-file."""
        state_id = state_ids[0]
        invalid_state = {"invalid": "state"}
        filepath = tmp_path / "invalid-state.json"

        with filepath.open("w") as state_file:
            json.dump(invalid_state, state_file)

        with mock.patch("meltano.cli.state.StateService", return_value=state_service):
            result = cli_runner.invoke(
                cli,
                [
                    "state",
                    "set",
                    "--force",
                    "--no-validate",
                    state_id,
                    "--input-file",
                    filepath,
                ],
            )
            assert_cli_runner(result)
            # Check that a warning was logged
            assert "Skipping state validation" in result.stderr
            # Verify the invalid state was actually set
            assert state_service.get_state(state_id) == invalid_state

    def test_merge_from_string(
        self,
        state_service: StateService,
        state_ids: list[str],
        cli_runner: MeltanoCliRunner,
    ) -> None:
        with mock.patch("meltano.cli.state.StateService", return_value=state_service):
            job_pairs = [
                (state_ids[idx], state_ids[idx + 1])
                for idx in range(0, len(state_ids) - 1, 2)
            ]
            for job_src, job_dst in job_pairs:
                job_src_state = state_service.get_state(job_src)
                job_dst_state = state_service.get_state(job_dst)
                result = cli_runner.invoke(
                    cli,
                    ["state", "merge", job_dst, json.dumps(job_src_state)],
                )
                assert_cli_runner(result)
                assert state_service.get_state(job_dst) == merge(
                    job_src_state,
                    job_dst_state,
                )

    @pytest.mark.usefixtures("payloads")
    def test_merge_from_file(
        self,
        tmp_path: Path,
        state_service: StateService,
        state_ids: list[str],
        cli_runner: MeltanoCliRunner,
    ) -> None:
        if platform.system() == "Windows":
            pytest.xfail(
                "Fails on Windows: https://github.com/meltano/meltano/issues/3444",
            )
        with mock.patch("meltano.cli.state.StateService", return_value=state_service):
            job_pairs = [
                (state_ids[idx], state_ids[idx + 1])
                for idx in range(0, len(state_ids) - 1, 2)
            ]
            for job_src, job_dst in job_pairs:
                job_src_state = state_service.get_state(job_src)
                job_dst_state = state_service.get_state(job_dst)
                filepath = tmp_path / f"{job_src}-{job_dst}"
                with filepath.open("w+") as state_file:
                    json.dump(job_src_state, state_file)
                result = cli_runner.invoke(
                    cli,
                    ["state", "merge", job_dst, "--input-file", filepath],
                )
                assert_cli_runner(result)
                assert state_service.get_state(job_dst) == merge(
                    job_src_state,
                    job_dst_state,
                )

    def test_merge_from_job(
        self,
        state_service: StateService,
        state_ids: list[str],
        cli_runner: MeltanoCliRunner,
    ) -> None:
        with mock.patch("meltano.cli.state.StateService", return_value=state_service):
            job_pairs = [
                (state_ids[idx], state_ids[idx + 1])
                for idx in range(0, len(state_ids) - 1, 2)
            ]
            for job_src, job_dst in job_pairs:
                job_state_src = state_service.get_state(job_src)
                job_state_dst = state_service.get_state(job_dst)
                merged_state = merge(job_state_src, job_state_dst)
                result = cli_runner.invoke(
                    cli,
                    ["state", "merge", "--from-state-id", job_src, job_dst],
                )
                assert_cli_runner(result)
                assert state_service.get_state(job_dst) == merged_state

    def test_copy_over_existing(
        self,
        state_service: StateService,
        state_ids: list[str],
        cli_runner: MeltanoCliRunner,
    ) -> None:
        with mock.patch("meltano.cli.state.StateService", return_value=state_service):
            job_pairs = [
                (state_ids[idx], state_ids[idx + 1])
                for idx in range(0, len(state_ids) - 1, 2)
            ]
            for job_src, job_dst in job_pairs:
                job_src_state = state_service.get_state(job_src)
                result = cli_runner.invoke(
                    cli,
                    ["state", "copy", job_src, job_dst, "--force"],
                )
                assert_cli_runner(result)
                assert state_service.get_state(job_dst) == job_src_state

    def test_copy_to_new(
        self,
        state_service: StateService,
        state_ids: list[str],
        cli_runner: MeltanoCliRunner,
    ) -> None:
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

    def test_move(
        self,
        state_service: StateService,
        state_ids: list[str],
        cli_runner: MeltanoCliRunner,
    ) -> None:
        with mock.patch("meltano.cli.state.StateService", return_value=state_service):
            job_pairs = [
                (state_ids[idx], state_ids[idx + 1])
                for idx in range(0, len(state_ids) - 1, 2)
            ]
            for job_src, job_dst in job_pairs:
                job_src_state = state_service.get_state(job_src)
                result = cli_runner.invoke(
                    cli,
                    ["state", "move", job_src, job_dst, "--force"],
                )
                assert_cli_runner(result)
                assert not state_service.get_state(job_src)
                assert state_service.get_state(job_dst) == job_src_state

    def test_get(
        self,
        state_service: StateService,
        cli_runner: MeltanoCliRunner,
        state_ids_with_expected_states: list[tuple[str, dict]],
    ) -> None:
        with mock.patch("meltano.cli.state.StateService", return_value=state_service):
            for state_id, expected_state in state_ids_with_expected_states:
                result = cli_runner.invoke(cli, ["state", "get", state_id])
                assert_cli_runner(result)
                assert json.loads(result.stdout) == expected_state

    def test_get_default_format_is_compact(
        self,
        state_service: StateService,
        cli_runner: MeltanoCliRunner,
        state_ids_with_expected_states: list[tuple[str, dict]],
    ) -> None:
        """Test that default output format is compact (single-line JSON)."""
        with mock.patch("meltano.cli.state.StateService", return_value=state_service):
            for state_id, expected_state in state_ids_with_expected_states:
                result = cli_runner.invoke(cli, ["state", "get", state_id])
                assert_cli_runner(result)
                # Compact JSON should not contain newlines except the trailing one
                assert result.stdout.count("\n") == 1
                # Should not contain spaces after separators
                assert ": " not in result.stdout
                assert ", " not in result.stdout
                # Should still be valid JSON
                assert json.loads(result.stdout) == expected_state

    def test_get_format_json_option(
        self,
        state_service: StateService,
        cli_runner: MeltanoCliRunner,
        state_ids_with_expected_states: list[tuple[str, dict]],
    ) -> None:
        """Test that --format json explicitly produces compact output."""
        with mock.patch("meltano.cli.state.StateService", return_value=state_service):
            for state_id, expected_state in state_ids_with_expected_states:
                result = cli_runner.invoke(
                    cli,
                    ["state", "get", state_id, "--format", "json"],
                )
                assert_cli_runner(result)
                # Compact JSON should not contain newlines except the trailing one
                assert result.stdout.count("\n") == 1
                # Should use compact separators
                assert ": " not in result.stdout
                assert ", " not in result.stdout
                # Should still be valid JSON
                assert json.loads(result.stdout) == expected_state

    def test_get_format_pretty_option(
        self,
        state_service: StateService,
        cli_runner: MeltanoCliRunner,
        state_ids_with_expected_states: list[tuple[str, dict]],
    ) -> None:
        """Test that --format pretty produces human-readable indented output."""
        with mock.patch("meltano.cli.state.StateService", return_value=state_service):
            for state_id, expected_state in state_ids_with_expected_states:
                result = cli_runner.invoke(
                    cli,
                    ["state", "get", state_id, "--format", "pretty"],
                )
                assert_cli_runner(result)
                # Pretty JSON should contain multiple newlines (more than just trailing)
                assert result.stdout.count("\n") > 1
                # Should be valid JSON
                assert json.loads(result.stdout) == expected_state

    def test_get_set_roundtrip(
        self,
        state_service: StateService,
        cli_runner: MeltanoCliRunner,
        state_ids: list[str],
    ) -> None:
        """Test that output from 'state get' can be directly used in 'state set'."""
        with mock.patch("meltano.cli.state.StateService", return_value=state_service):
            for state_id in state_ids:
                # Get the current state
                get_result = cli_runner.invoke(cli, ["state", "get", state_id])
                assert_cli_runner(get_result)

                # Use the output directly in set command for a new state ID
                new_state_id = f"{state_id}-roundtrip-test"
                set_result = cli_runner.invoke(
                    cli,
                    [
                        "state",
                        "set",
                        "--force",
                        new_state_id,
                        get_result.stdout.strip(),
                    ],
                )
                assert_cli_runner(set_result)

                # Verify the new state matches the original
                original_state = state_service.get_state(state_id)
                copied_state = state_service.get_state(new_state_id)
                assert copied_state == original_state

    def test_clear(
        self,
        state_service: StateService,
        cli_runner: MeltanoCliRunner,
        state_ids: list[str],
    ) -> None:
        with mock.patch("meltano.cli.state.StateService", return_value=state_service):
            for state_id in state_ids:
                result = cli_runner.invoke(cli, ["state", "clear", "--force", state_id])
                assert_cli_runner(result)
                job_state = state_service.get_state(state_id)
                assert (not job_state) or (not job_state.get("singer_state"))

    def test_clear_all(
        self,
        state_service: StateService,
        cli_runner: CliRunner,
    ) -> None:
        with mock.patch("meltano.cli.state.StateService", return_value=state_service):
            assert len(state_service.list_state()) > 0
            result = cli_runner.invoke(
                cli,
                ["state", "clear", "--force", "--all"],
            )
            assert_cli_runner(result)
            pattern = r"[1-9] state\(s\) were successfully cleared"
            assert re.search(pattern, result.stderr) is not None
            assert len(state_service.list_state()) == 0

    @pytest.mark.parametrize(
        "args",
        (
            pytest.param(("my-state-id", "--all"), id="both"),
            pytest.param((), id="neither"),
        ),
    )
    def test_clear_all_conflict_error(
        self,
        state_service: StateService,
        cli_runner: CliRunner,
        args: tuple[str, ...],
    ) -> None:
        with mock.patch("meltano.cli.state.StateService", return_value=state_service):
            assert len(state_service.list_state()) > 0
            result = cli_runner.invoke(cli, ["state", "clear", "--force", *args])
            assert result.exit_code == 2

            message = "A state ID or the --all flag must be provided, but not both"
            assert message in result.stderr

    def test_clear_prompt(
        self,
        state_service: StateService,
        cli_runner: MeltanoCliRunner,
        state_ids: list[str],
    ) -> None:
        with mock.patch("meltano.cli.state.StateService", return_value=state_service):
            for state_id in state_ids:
                result = cli_runner.invoke(cli, ["state", "clear", state_id], input="n")
                assert result.exit_code == 1

                job_state = state_service.get_state(state_id)
                assert "singer_state" in job_state

                result = cli_runner.invoke(cli, ["state", "clear", state_id], input="y")
                assert_cli_runner(result)

                job_state = state_service.get_state(state_id)
                assert (not job_state) or (not job_state.get("singer_state"))

    def test_edit_existing_state(
        self,
        state_service: StateService,
        cli_runner: MeltanoCliRunner,
        state_ids: list[str],
    ) -> None:
        """Test editing an existing state."""
        state_id = state_ids[0]
        original_state: dict[str, dict] = state_service.get_state(state_id)

        modified_state = original_state.copy()
        modified_state["singer_state"].setdefault("bookmarks", {})
        modified_state["singer_state"]["bookmarks"]["new_stream"] = {"version": 1}

        edited_content = json.dumps(modified_state, indent=2)

        with mock.patch("click.edit", return_value=edited_content) as mock_edit:
            result = self.invoke_with_state_service(
                cli_runner,
                state_service,
                ["state", "edit", "--force", state_id],
            )
            assert_cli_runner(result)
            mock_edit.assert_called_once()

            updated_state = state_service.get_state(state_id)
            assert updated_state == modified_state
            assert "new_stream" in updated_state["singer_state"]["bookmarks"]

    def test_edit_new_state(
        self,
        state_service: StateService,
        cli_runner: MeltanoCliRunner,
    ) -> None:
        """Test editing a non-existent state creates a new one."""
        state_id = "new-state-id"
        new_state: dict[str, dict] = {"singer_state": {"bookmarks": {}}}
        edited_content = json.dumps(new_state, indent=2)

        with mock.patch("click.edit", return_value=edited_content) as mock_edit:
            result = self.invoke_with_state_service(
                cli_runner,
                state_service,
                ["state", "edit", "--force", state_id],
            )
            assert_cli_runner(result)
            mock_edit.assert_called_once()

            created_state = state_service.get_state(state_id)
            assert created_state == new_state

    def test_edit_cancelled(
        self,
        state_service: StateService,
        cli_runner: MeltanoCliRunner,
        state_ids: list[str],
    ) -> None:
        """Test cancelling edit operation."""
        state_id = state_ids[0]
        original_state = state_service.get_state(state_id)

        with mock.patch("click.edit", return_value=None) as mock_edit:
            result = self.invoke_with_state_service(
                cli_runner,
                state_service,
                ["state", "edit", "--force", state_id],
            )
            assert_cli_runner(result)
            mock_edit.assert_called_once()

            current_state = state_service.get_state(state_id)
            assert current_state == original_state

    def test_edit_no_changes(
        self,
        state_service: StateService,
        cli_runner: MeltanoCliRunner,
        state_ids: list[str],
    ) -> None:
        """Test editing with no changes."""
        state_id = state_ids[0]
        original_state = state_service.get_state(state_id)
        original_content = json.dumps(original_state, indent=2)

        with mock.patch("click.edit", return_value=original_content) as mock_edit:
            result = self.invoke_with_state_service(
                cli_runner,
                state_service,
                ["state", "edit", "--force", state_id],
            )
            assert_cli_runner(result)
            mock_edit.assert_called_once()

            current_state = state_service.get_state(state_id)
            assert current_state == original_state

    def test_edit_semantic_no_changes(
        self,
        state_service: StateService,
        cli_runner: MeltanoCliRunner,
        state_ids: list[str],
    ) -> None:
        """Test semantically identical but differently formatted JSON as no change."""
        state_id = state_ids[0]
        original_state = state_service.get_state(state_id)

        # Create differently formatted but semantically identical JSON
        compact_content = json.dumps(original_state, separators=(",", ":"))

        with mock.patch("click.edit", return_value=compact_content) as mock_edit:
            result = self.invoke_with_state_service(
                cli_runner,
                state_service,
                ["state", "edit", "--force", state_id],
            )
            assert_cli_runner(result)
            mock_edit.assert_called_once()

            # Verify state was not changed
            current_state = state_service.get_state(state_id)
            assert current_state == original_state

    def test_edit_invalid_json(
        self,
        state_service: StateService,
        cli_runner: MeltanoCliRunner,
        state_ids: list[str],
    ) -> None:
        """Test editing with invalid JSON."""
        state_id = state_ids[0]
        invalid_json = "{ invalid json"

        with mock.patch("click.edit", return_value=invalid_json) as mock_edit:
            result = self.invoke_with_state_service(
                cli_runner,
                state_service,
                ["state", "edit", "--force", state_id],
            )
            assert result.exit_code == 1
            mock_edit.assert_called_once()

            assert isinstance(result.exception, json.JSONDecodeError)

    def test_edit_invalid_state_format(
        self,
        state_service: StateService,
        cli_runner: MeltanoCliRunner,
        state_ids: list[str],
    ) -> None:
        """Test editing with invalid state format."""
        state_id = state_ids[0]
        invalid_state = {"invalid": "state"}
        edited_content = json.dumps(invalid_state, indent=2)

        with mock.patch("click.edit", return_value=edited_content) as mock_edit:
            result = self.invoke_with_state_service(
                cli_runner,
                state_service,
                ["state", "edit", "--force", state_id],
            )
            assert result.exit_code == 1
            mock_edit.assert_called_once()

            assert isinstance(result.exception, InvalidJobStateError)

    def test_edit_empty_content(
        self,
        state_service: StateService,
        cli_runner: MeltanoCliRunner,
        state_ids: list[str],
    ) -> None:
        """Test editing with empty content."""
        state_id = state_ids[0]
        original_state = state_service.get_state(state_id)

        with mock.patch("click.edit", return_value="   \n  ") as mock_edit:
            result = self.invoke_with_state_service(
                cli_runner,
                state_service,
                ["state", "edit", "--force", state_id],
            )
            assert_cli_runner(result)
            mock_edit.assert_called_once()

            current_state = state_service.get_state(state_id)
            assert current_state == original_state

    def test_edit_prompt_confirmation(
        self,
        state_service: StateService,
        cli_runner: MeltanoCliRunner,
        state_ids: list[str],
    ) -> None:
        """Test the confirmation prompt when editing."""
        state_id = state_ids[0]
        original_state = state_service.get_state(state_id)

        with mock.patch("meltano.cli.state.StateService", return_value=state_service):
            result = cli_runner.invoke(cli, ["state", "edit", state_id], input="n")
        assert result.exit_code == 1

        current_state = state_service.get_state(state_id)
        assert current_state == original_state
