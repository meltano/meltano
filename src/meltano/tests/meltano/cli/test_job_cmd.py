from __future__ import annotations

import json

import mock
import pytest

from asserts import assert_cli_runner
from meltano.cli import cli


class TestCliJob:
    def test_job_add(self, session, project, cli_runner, task_sets_service):
        # singular task with job
        with mock.patch(
            "meltano.cli.job.TaskSetsService", return_value=task_sets_service
        ), mock.patch("meltano.cli.job._validate_tasks", return_value=True):
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

    def test_job_set(self, session, project, cli_runner, task_sets_service):
        # singular task with job
        with mock.patch(
            "meltano.cli.job.TaskSetsService", return_value=task_sets_service
        ), mock.patch("meltano.cli.job._validate_tasks", return_value=True):
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

    @pytest.mark.order(after="test_job_add")
    def test_job_remove(self, session, project, cli_runner, task_sets_service):
        # singular task with job
        with mock.patch(
            "meltano.cli.job.TaskSetsService", return_value=task_sets_service
        ), mock.patch("meltano.cli.job._validate_tasks", return_value=True):
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

    def test_job_list(self, session, project, cli_runner, task_sets_service):
        # singular task with job
        with mock.patch(
            "meltano.cli.job.TaskSetsService", return_value=task_sets_service
        ), mock.patch("meltano.cli.job._validate_tasks", return_value=True):

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
                cli, ["job", "list", "--format=json", "job-list-mock"]
            )
            assert_cli_runner(res)
            output = json.loads(res.output)
            assert output["job_name"] == "job-list-mock"
            assert output["tasks"] == ["tap-mock target-mock"]
