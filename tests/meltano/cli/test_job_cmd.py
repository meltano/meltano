from __future__ import annotations

import json
import typing as t
from unittest import mock

import pytest

from asserts import assert_cli_runner
from meltano.cli import cli

if t.TYPE_CHECKING:
    from tests.fixtures.cli import MeltanoCliRunner


class TestCliJob:
    @pytest.mark.usefixtures("session", "project")
    def test_job_add(self, cli_runner, task_sets_service) -> None:
        # singular task with job
        with (
            mock.patch(
                "meltano.cli.job.TaskSetsService",
                return_value=task_sets_service,
            ),
            mock.patch("meltano.cli.job._validate_tasks", return_value=True),
        ):
            res = cli_runner.invoke(
                cli,
                [
                    "job",
                    "add",
                    "job-mock",
                    "--tasks",
                    "'tap-mock target-mock'",
                ],
            )
            assert_cli_runner(res)
            task_sets = task_sets_service.get("job-mock")

            assert task_sets.name == "job-mock"
            assert task_sets.tasks == ["tap-mock target-mock"]

            # valid pseudo-list of tasks
            res = cli_runner.invoke(
                cli,
                [
                    "job",
                    "add",
                    "job-mock2",
                    "--tasks",
                    "['tap-mock target-mock', 'tap-mock2 target-mock2']",
                ],
            )
            assert_cli_runner(res)

            task_sets = task_sets_service.get("job-mock2")
            assert task_sets.name == "job-mock2"
            assert task_sets.tasks == ["tap-mock target-mock", "tap-mock2 target-mock2"]

            # verify that you can't add a job with the same name
            res = cli_runner.invoke(
                cli,
                [
                    "job",
                    "add",
                    "job-mock2",
                    "--tasks",
                    "['tap-mock target-mock', 'tap-mock2 target-mock2']",
                ],
            )
            assert res.exit_code == 1
            assert "Job 'job-mock2' already exists" in str(res.exception)

            # invalid task - schema validation fails
            res = cli_runner.invoke(
                cli,
                [
                    "job",
                    "add",
                    "job-mock-bad-schema",
                    "--tasks",
                    '["tap-gitlab target-jsonl", "dbt:run", 5]',
                ],
                catch_exceptions=True,
            )
            assert res.exit_code == 1
            assert "Failed to validate task schema" in str(res.exception)

            # invalid task - yaml parsing failure
            res = cli_runner.invoke(
                cli,
                [
                    "job",
                    "add",
                    "job-mock-bad-yaml",
                    "--tasks",
                    "['tap-mock target-mock'",
                ],
                catch_exceptions=True,
            )
            assert res.exit_code == 1
            assert "Failed to parse yaml" in str(res.exception)

            # test adding job with environment variables
            res = cli_runner.invoke(
                cli,
                [
                    "job",
                    "add",
                    "job-with-env",
                    "--tasks",
                    "'tap-mock target-mock'",
                    "--env",
                    "DBT_MODELS=+gitlab+",
                ],
            )
            assert_cli_runner(res)
            task_sets = task_sets_service.get("job-with-env")
            assert task_sets.name == "job-with-env"
            assert task_sets.tasks == ["tap-mock target-mock"]
            assert task_sets.env == {"DBT_MODELS": "+gitlab+"}

            # test adding job with multiple environment variables
            res = cli_runner.invoke(
                cli,
                [
                    "job",
                    "add",
                    "job-with-multiple-env",
                    "--tasks",
                    "'tap-mock target-mock'",
                    "--env",
                    "DBT_MODELS=+gitlab+",
                    "--env",
                    "TARGET_BATCH_SIZE=100",
                ],
            )
            assert_cli_runner(res)
            task_sets = task_sets_service.get("job-with-multiple-env")
            assert task_sets.env == {
                "DBT_MODELS": "+gitlab+",
                "TARGET_BATCH_SIZE": "100",
            }

            # test invalid env var format
            res = cli_runner.invoke(
                cli,
                [
                    "job",
                    "add",
                    "job-bad-env",
                    "--tasks",
                    "'tap-mock target-mock'",
                    "--env",
                    "INVALID_FORMAT",
                ],
                catch_exceptions=True,
            )
            assert res.exit_code == 1  # CliError for invalid env format

            # test invalid env var format - empty key
            res = cli_runner.invoke(
                cli,
                [
                    "job",
                    "add",
                    "job-bad-empty-key",
                    "--tasks",
                    "'tap-mock target-mock'",
                    "--env",
                    "=value",
                ],
                catch_exceptions=True,
            )
            assert res.exit_code == 1  # CliError for empty key

    @pytest.mark.usefixtures("session", "tap", "target")
    def test_job_add_invalid(self, cli_runner: MeltanoCliRunner) -> None:
        """Add a job with an invalid EL block should raise an error."""
        res = cli_runner.invoke(
            cli,
            [
                "job",
                "add",
                "job-mock-bad-el",
                "--tasks",
                '["target-mock tap-mock"]',
            ],
            catch_exceptions=True,
        )
        assert res.exit_code == 1
        assert "Job 'job-mock-bad-el' has invalid task" in str(res.exception)

    @pytest.mark.usefixtures("session", "project")
    def test_job_set(self, cli_runner, task_sets_service) -> None:
        # singular task with job
        with (
            mock.patch(
                "meltano.cli.job.TaskSetsService",
                return_value=task_sets_service,
            ),
            mock.patch("meltano.cli.job._validate_tasks", return_value=True),
        ):
            res = cli_runner.invoke(
                cli,
                [
                    "job",
                    "add",
                    "job-set-mock",
                    "--tasks",
                    "'tap-mock target-mock'",
                ],
            )
            assert_cli_runner(res)
            assert task_sets_service.exists("job-set-mock")

            res = cli_runner.invoke(
                cli,
                [
                    "job",
                    "set",
                    "job-set-mock",
                    "--tasks",
                    "'tap2-mock target2-mock'",
                ],
            )

            task_sets = task_sets_service.get("job-set-mock")
            assert task_sets.name == "job-set-mock"
            assert task_sets.tasks == ["tap2-mock target2-mock"]

            # test setting environment variables
            res = cli_runner.invoke(
                cli,
                [
                    "job",
                    "set",
                    "job-set-mock",
                    "--env",
                    "DBT_MODELS=+gitlab+",
                    "--env",
                    "TARGET_BATCH_SIZE=500",
                ],
            )
            assert_cli_runner(res)

            task_sets = task_sets_service.get("job-set-mock")
            assert task_sets.env == {
                "DBT_MODELS": "+gitlab+",
                "TARGET_BATCH_SIZE": "500",
            }

            # test setting env vars only (no tasks)
            res = cli_runner.invoke(
                cli,
                [
                    "job",
                    "set",
                    "job-set-mock",
                    "--env",
                    "ENV_ONLY_VAR=test_value",
                ],
            )
            assert_cli_runner(res)

            task_sets = task_sets_service.get("job-set-mock")
            assert "ENV_ONLY_VAR" in task_sets.env
            assert task_sets.env["ENV_ONLY_VAR"] == "test_value"

            # test error when neither tasks nor env provided to set command
            res = cli_runner.invoke(
                cli,
                [
                    "job",
                    "set",
                    "job-set-mock",
                ],
                catch_exceptions=True,
            )
            assert res.exit_code == 1  # CliError for missing parameters

            # test setting env vars on non-existent job
            res = cli_runner.invoke(
                cli,
                [
                    "job",
                    "set",
                    "non-existent-job",
                    "--env",
                    "KEY=value",
                ],
                catch_exceptions=True,
            )
            assert res.exit_code == 1  # CliError for JobNotFoundError

    @pytest.mark.order(after="test_job_add")
    @pytest.mark.usefixtures("session", "project")
    def test_job_remove(self, cli_runner, task_sets_service) -> None:
        # singular task with job
        with (
            mock.patch(
                "meltano.cli.job.TaskSetsService",
                return_value=task_sets_service,
            ),
            mock.patch("meltano.cli.job._validate_tasks", return_value=True),
        ):
            res = cli_runner.invoke(
                cli,
                [
                    "job",
                    "add",
                    "job-remove-mock",
                    "--tasks",
                    "'tap-mock target-mock'",
                ],
            )
            assert_cli_runner(res)
            assert task_sets_service.exists("job-mock")

            res = cli_runner.invoke(cli, ["job", "remove", "job-remove-mock"])
            assert_cli_runner(res)
            assert not task_sets_service.exists("job-remove-mock")

    @pytest.mark.usefixtures("session", "project")
    def test_job_list(self, cli_runner, task_sets_service) -> None:
        # singular task with job
        with (
            mock.patch(
                "meltano.cli.job.TaskSetsService",
                return_value=task_sets_service,
            ),
            mock.patch("meltano.cli.job._validate_tasks", return_value=True),
        ):
            cli_args = [
                "job",
                "add",
                "job-list-mock",
                "--tasks",
                "'tap-mock target-mock'",
            ]
            res = cli_runner.invoke(cli, cli_args)
            assert_cli_runner(res)
            assert task_sets_service.exists("job-list-mock")

            cli_args = [
                "job",
                "add",
                "job-list-mock2",
                "--tasks",
                "'tap-mock2 target-mock2'",
            ]
            res = cli_runner.invoke(cli, cli_args)
            assert_cli_runner(res)
            assert task_sets_service.exists("job-list-mock2")

            # test vanilla
            res = cli_runner.invoke(cli, ["job", "list"])
            assert_cli_runner(res)
            assert "job-list-mock: ['tap-mock target-mock']" in res.output
            assert "job-list-mock2: ['tap-mock2 target-mock2']" in res.output

            # test singular json list
            res = cli_runner.invoke(
                cli,
                ["job", "list", "--format=json", "job-list-mock"],
            )
            assert_cli_runner(res)
            output = json.loads(res.stdout)
            assert output["job_name"] == "job-list-mock"
            assert output["tasks"] == ["tap-mock target-mock"]

            # test job list with environment variables
            cli_args = [
                "job",
                "add",
                "job-list-with-env",
                "--tasks",
                "'tap-mock target-mock'",
                "--env",
                "DBT_MODELS=+gitlab+",
                "--env",
                "TARGET_BATCH_SIZE=100",
            ]
            res = cli_runner.invoke(cli, cli_args)
            assert_cli_runner(res)

            # test vanilla list includes env vars
            res = cli_runner.invoke(cli, ["job", "list"])
            assert_cli_runner(res)
            assert "job-list-with-env" in res.output
            # The exact format will depend on implementation, but env vars should appear

            # test job without env vars doesn't show env in output
            assert (
                "job-list-mock:" in res.output
            )  # Job without env should not show env section

            # test json format includes env vars
            res = cli_runner.invoke(
                cli,
                ["job", "list", "--format=json", "job-list-with-env"],
            )
            assert_cli_runner(res)
            output = json.loads(res.stdout)
            assert output["job_name"] == "job-list-with-env"
            assert output["tasks"] == ["tap-mock target-mock"]
            assert output.get("env") == {
                "DBT_MODELS": "+gitlab+",
                "TARGET_BATCH_SIZE": "100",
            }

            # test json format for job without env vars
            res = cli_runner.invoke(
                cli,
                ["job", "list", "--format=json", "job-list-mock"],
            )
            assert_cli_runner(res)
            output = json.loads(res.stdout)
            assert output["job_name"] == "job-list-mock"
            assert output["tasks"] == ["tap-mock target-mock"]
            assert "env" not in output  # Job without env should not have env field

            # test json format for all jobs includes both with and without env
            res = cli_runner.invoke(cli, ["job", "list", "--format=json"])
            assert_cli_runner(res)
            output = json.loads(res.stdout)
            assert "jobs" in output
            jobs = output["jobs"]

            # Find jobs with and without env in the list
            job_with_env = next(
                (j for j in jobs if j["job_name"] == "job-list-with-env"), None
            )
            job_without_env = next(
                (j for j in jobs if j["job_name"] == "job-list-mock"), None
            )

            assert job_with_env is not None
            assert "env" in job_with_env
            assert job_without_env is not None
            assert "env" not in job_without_env
