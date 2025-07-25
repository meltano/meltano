"""Tests for the logs CLI commands."""

from __future__ import annotations

import json
import typing as t
import uuid
from datetime import datetime, timezone
from unittest import mock

import pytest

from meltano.cli import logs
from meltano.core.db import project_engine
from meltano.core.job import Job, State
from meltano.core.logging.job_logging_service import JobLoggingService

if t.TYPE_CHECKING:
    from fixtures.cli import MeltanoCliRunner
    from meltano.core.project import Project


@pytest.fixture
def create_test_job(project: Project):
    """Create a test job with logs."""

    def _create(
        job_name: str = "tap-gitlab target-postgres",
        state: State = State.SUCCESS,
        run_id: str | None = None,
        log_content: str = "Test log content\nLine 2\nLine 3",
    ) -> Job:
        if run_id is None:
            run_id = str(uuid.uuid4())

        # Create job in database
        job = Job(
            job_name=job_name,
            state=state,
            run_id=run_id,
            started_at=datetime.now(timezone.utc),
        )

        if state in (State.SUCCESS, State.FAIL):
            job.ended_at = datetime.now(timezone.utc)

        _, make_session = project_engine(project)
        with make_session() as session:
            job.save(session)

        # Create log file
        job_logging_service = JobLoggingService(project)
        log_path = job_logging_service.generate_log_name(job_name, run_id)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text(log_content)

        return job

    return _create


class TestLogsShow:
    """Test the logs show command."""

    def test_show_latest_log(
        self,
        project: Project,
        cli_runner: MeltanoCliRunner,
        create_test_job,
    ):
        """Test showing the latest log for a job."""
        job = create_test_job(log_content="Latest log content\nWith multiple lines")

        result = cli_runner.invoke(logs.show, [job.job_name])

        assert result.exit_code == 0
        assert "Latest log content" in result.output
        assert "With multiple lines" in result.output
        assert f"Job: {job.job_name}" in result.output
        assert f"Run ID: {job.run_id}" in result.output
        assert "State: SUCCESS" in result.output

    def test_show_specific_run(
        self,
        project: Project,
        cli_runner: MeltanoCliRunner,
        create_test_job,
    ):
        """Test showing log for a specific run ID."""
        # Create multiple runs
        job1 = create_test_job(log_content="First run log")
        job2 = create_test_job(log_content="Second run log")

        # Show specific run
        result = cli_runner.invoke(
            logs.show,
            [job1.job_name, "--run-id", str(job1.run_id)],
        )

        assert result.exit_code == 0
        assert "First run log" in result.output
        assert "Second run log" not in result.output

    def test_list_runs(
        self,
        project: Project,
        cli_runner: MeltanoCliRunner,
        create_test_job,
    ):
        """Test listing available runs for a job."""
        # Create multiple runs with different states
        job1 = create_test_job(state=State.SUCCESS)
        job2 = create_test_job(state=State.FAIL)
        job3 = create_test_job(state=State.RUNNING)

        result = cli_runner.invoke(logs.show, [job1.job_name, "--list"])

        assert result.exit_code == 0
        assert f"Runs for job '{job1.job_name}':" in result.output
        assert str(job1.run_id) in result.output
        assert str(job2.run_id) in result.output
        assert str(job3.run_id) in result.output
        assert "✓" in result.output  # Success marker
        assert "✗" in result.output  # Fail marker
        assert "→" in result.output  # Running marker

    def test_list_runs_json_format(
        self,
        project: Project,
        cli_runner: MeltanoCliRunner,
        create_test_job,
    ):
        """Test listing runs in JSON format."""
        job = create_test_job()

        result = cli_runner.invoke(
            logs.show,
            [job.job_name, "--list", "--format", "json"],
        )

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["job_name"] == job.job_name
        assert len(data["runs"]) == 1
        assert data["runs"][0]["run_id"] == str(job.run_id)
        assert data["runs"][0]["state"] == "SUCCESS"

    def test_tail_option(
        self,
        project: Project,
        cli_runner: MeltanoCliRunner,
        create_test_job,
    ):
        """Test showing last N lines with --tail."""
        log_content = "\n".join([f"Line {i}" for i in range(1, 101)])
        job = create_test_job(log_content=log_content)

        result = cli_runner.invoke(logs.show, [job.job_name, "--tail", "5"])

        assert result.exit_code == 0
        assert "Line 96" in result.output
        assert "Line 97" in result.output
        assert "Line 98" in result.output
        assert "Line 99" in result.output
        assert "Line 100" in result.output
        assert "Line 95" not in result.output

    def test_no_logs_found(
        self,
        project: Project,
        cli_runner: MeltanoCliRunner,
    ):
        """Test error when no logs are found."""
        result = cli_runner.invoke(logs.show, ["non-existent-job"])

        assert result.exit_code == 1
        assert "No logs found for job 'non-existent-job'" in result.output

    def test_no_runs_found(
        self,
        project: Project,
        cli_runner: MeltanoCliRunner,
    ):
        """Test error when no runs are found for list."""
        result = cli_runner.invoke(logs.show, ["non-existent-job", "--list"])

        assert result.exit_code == 1
        assert "No runs found for job 'non-existent-job'" in result.output

    def test_missing_run_id(
        self,
        project: Project,
        cli_runner: MeltanoCliRunner,
        create_test_job,
    ):
        """Test error when specific run ID is not found."""
        job = create_test_job()
        fake_run_id = str(uuid.uuid4())

        result = cli_runner.invoke(
            logs.show,
            [job.job_name, "--run-id", fake_run_id],
        )

        assert result.exit_code == 1
        assert (
            f"Log file not found for job '{job.job_name}' with run ID '{fake_run_id}'"
            in result.output
        )

    def test_large_log_confirmation(
        self,
        project: Project,
        cli_runner: MeltanoCliRunner,
        create_test_job,
    ):
        """Test confirmation prompt for large log files."""
        # Create a log larger than 2MB
        large_content = "x" * (2 * 1024 * 1024 + 1)
        job = create_test_job(log_content=large_content)

        # Test declining confirmation
        result = cli_runner.invoke(logs.show, [job.job_name], input="n\n")

        assert result.exit_code == 0
        assert "Log file is large" in result.output
        assert "Do you want to display it anyway?" in result.output
        assert "Log file path:" in result.output

        # Test accepting confirmation
        result = cli_runner.invoke(logs.show, [job.job_name], input="y\n")

        assert result.exit_code == 0
        assert "Log file is large" in result.output
        # The large content would be displayed

    def test_json_format_with_log_display(
        self,
        project: Project,
        cli_runner: MeltanoCliRunner,
        create_test_job,
    ):
        """Test JSON format for job info when showing logs."""
        job = create_test_job()

        result = cli_runner.invoke(
            logs.show,
            [job.job_name, "--format", "json"],
        )

        assert result.exit_code == 0
        # Job info should be in JSON format
        lines = result.output.strip().split("\n")
        # Find the JSON block (before the log content)
        json_end = None
        for i, line in enumerate(lines):
            if line == "}":
                json_end = i
                break

        assert json_end is not None
        json_str = "\n".join(lines[: json_end + 1])
        data = json.loads(json_str)
        assert data["job_name"] == job.job_name
        assert data["run_id"] == str(job.run_id)
        assert data["state"] == "SUCCESS"

    def test_legacy_log_location(
        self,
        project: Project,
        cli_runner: MeltanoCliRunner,
        create_test_job,
    ):
        """Test reading logs from legacy location."""
        # This would require mocking the legacy_logs_dir method
        # to return a valid path and creating logs there
        # Placeholder for legacy log test
