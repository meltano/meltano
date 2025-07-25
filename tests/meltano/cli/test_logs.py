"""Tests for the logs CLI commands."""

from __future__ import annotations

import json
import typing as t
import uuid
from datetime import datetime, timezone

import pytest

from meltano.cli import cli
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

        result = cli_runner.invoke(cli, ["logs", "show", str(job.run_id)])

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
        create_test_job(log_content="Second run log")

        # Show specific run
        result = cli_runner.invoke(
            cli,
            ["logs", "show", str(job1.run_id)],
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

        result = cli_runner.invoke(cli, ["logs", "list"])

        assert result.exit_code == 0
        assert "Recent job runs" in result.output
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
            cli,
            ["logs", "list", "--format", "json"],
        )

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "runs" in data
        assert len(data["runs"]) >= 1
        run_ids = [run["log_id"] for run in data["runs"]]
        assert str(job.run_id) in run_ids

    def test_tail_option(
        self,
        project: Project,
        cli_runner: MeltanoCliRunner,
        create_test_job,
    ):
        """Test showing last N lines with --tail."""
        log_content = "\n".join([f"Line {i}" for i in range(1, 101)])
        job = create_test_job(log_content=log_content)

        result = cli_runner.invoke(
            cli, ["logs", "show", str(job.run_id), "--tail", "5"]
        )

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
        fake_uuid = str(uuid.uuid4())
        result = cli_runner.invoke(cli, ["logs", "show", fake_uuid])

        assert result.exit_code == 1
        assert f"No job found with log ID '{fake_uuid}'" in result.output

    def test_no_runs_found(
        self,
        project: Project,
        cli_runner: MeltanoCliRunner,
    ):
        """Test when no runs are found for list."""
        # Clear any existing jobs by testing with empty DB
        result = cli_runner.invoke(cli, ["logs", "list"])

        # Should succeed but show no runs message
        assert result.exit_code == 0
        assert "No job runs found." in result.output

    def test_missing_run_id(
        self,
        project: Project,
        cli_runner: MeltanoCliRunner,
        create_test_job,
    ):
        """Test error when specific run ID is not found."""
        fake_run_id = str(uuid.uuid4())

        result = cli_runner.invoke(
            cli,
            ["logs", "show", fake_run_id],
        )

        assert result.exit_code == 1
        assert f"No job found with log ID '{fake_run_id}'" in result.output

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
        result = cli_runner.invoke(cli, ["logs", "show", str(job.run_id)], input="n\n")

        assert result.exit_code == 0
        assert "Log file is large" in result.output
        assert "Do you want to display it anyway?" in result.output
        assert "Log file path:" in result.output

        # Test accepting confirmation
        result = cli_runner.invoke(cli, ["logs", "show", str(job.run_id)], input="y\n")

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
            cli,
            ["logs", "show", str(job.run_id), "--format", "json"],
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
