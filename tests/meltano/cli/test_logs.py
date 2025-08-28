"""Tests for the logs CLI commands."""

from __future__ import annotations

import json
import typing as t
import uuid
from datetime import datetime, timezone
from unittest import mock

import pytest

from meltano.cli import cli
from meltano.cli.utils import CliError
from meltano.core.job import Job, State
from meltano.core.logging.job_logging_service import JobLoggingService

if t.TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from fixtures.cli import MeltanoCliRunner
    from meltano.core.project import Project


class JobFactory:
    """Factory for creating test jobs."""

    def __init__(self, project: Project):
        self.project = project

    def create(
        self,
        session: Session,
        job_name: str = "tap-gitlab target-postgres",
        state: State = State.SUCCESS,
        run_id: str | None = None,
        log_content: str = "Test log content\nLine 2\nLine 3",
    ) -> Job:
        run_id = run_id or str(uuid.uuid4())

        # Create job in database
        job = Job(
            job_name=job_name,
            state=state,
            run_id=run_id,
            started_at=datetime.now(timezone.utc),
        )

        if state in (State.SUCCESS, State.FAIL):
            job.ended_at = datetime.now(timezone.utc)

        job.save(session)

        # Create log file
        job_logging_service = JobLoggingService(self.project)
        log_path = job_logging_service.generate_log_name(job_name, run_id)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text(log_content)

        return job


@pytest.fixture
def job_factory(project: Project):
    """Create a test job with logs."""
    return JobFactory(project)


class TestLogsShow:
    """Test the logs show command."""

    def test_show_latest_log(
        self,
        session: Session,
        cli_runner: MeltanoCliRunner,
        job_factory: JobFactory,
    ):
        """Test showing the latest log for a job."""
        job = job_factory.create(
            session,
            log_content="Latest log content\nWith multiple lines",
        )

        with mock.patch(
            "meltano.cli.logs.project_engine",
            return_value=(None, lambda: session),
        ):
            result = cli_runner.invoke(cli, ["logs", "show", str(job.run_id)])

        assert result.exit_code == 0
        assert "Latest log content" in result.output
        assert "With multiple lines" in result.output
        assert f"Job: {job.job_name}" in result.output
        assert f"Run ID: {job.run_id}" in result.output
        assert "State: SUCCESS" in result.output

    def test_show_specific_run(
        self,
        session: Session,
        cli_runner: MeltanoCliRunner,
        job_factory: JobFactory,
    ):
        """Test showing log for a specific run ID."""
        # Create multiple runs
        job1 = job_factory.create(session, log_content="First run log")
        job_factory.create(session, log_content="Second run log")

        # Show specific run
        with mock.patch(
            "meltano.cli.logs.project_engine",
            return_value=(None, lambda: session),
        ):
            result = cli_runner.invoke(
                cli,
                ["logs", "show", str(job1.run_id)],
            )

        assert result.exit_code == 0
        assert "First run log" in result.output
        assert "Second run log" not in result.output

    def test_list_runs(
        self,
        session: Session,
        cli_runner: MeltanoCliRunner,
        job_factory: JobFactory,
    ):
        """Test listing available runs for a job."""
        # Create multiple runs with different states
        job1 = job_factory.create(session, state=State.SUCCESS)
        job2 = job_factory.create(session, state=State.FAIL)
        job3 = job_factory.create(session, state=State.RUNNING)

        with mock.patch(
            "meltano.cli.logs.project_engine",
            return_value=(None, lambda: session),
        ):
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
        session: Session,
        cli_runner: MeltanoCliRunner,
        job_factory: JobFactory,
    ):
        """Test listing runs in JSON format."""
        job = job_factory.create(session)

        with mock.patch(
            "meltano.cli.logs.project_engine",
            return_value=(None, lambda: session),
        ):
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
        session: Session,
        cli_runner: MeltanoCliRunner,
        job_factory: JobFactory,
    ):
        """Test showing last N lines with --tail."""
        log_content = "\n".join([f"Line {i}" for i in range(1, 101)])
        job = job_factory.create(session, log_content=log_content)

        with mock.patch(
            "meltano.cli.logs.project_engine",
            return_value=(None, lambda: session),
        ):
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
        session: Session,
        cli_runner: MeltanoCliRunner,
    ):
        """Test error when no logs are found."""
        job = Job(
            job_name="tap-gitlab target-postgres",
            state=State.SUCCESS,
            started_at=datetime.now(timezone.utc),
        )
        job.save(session)

        with mock.patch(
            "meltano.cli.logs.project_engine",
            return_value=(None, lambda: session),
        ):
            result = cli_runner.invoke(cli, ["logs", "show", str(job.run_id)])

        assert result.exit_code == 1
        exc = result.exception
        assert isinstance(exc, CliError)
        assert f"Log file not found for job run '{job.run_id}'" in exc.args[0]

    @pytest.mark.usefixtures("project")
    def test_no_runs_found(
        self,
        cli_runner: MeltanoCliRunner,
    ):
        """Test when no runs are found for list."""
        # Clear any existing jobs by testing with empty DB
        result = cli_runner.invoke(cli, ["logs", "list"])

        # Should succeed but show no runs message
        assert result.exit_code == 0
        assert "No job runs found." in result.output

    def test_missing_run_id(self, cli_runner: MeltanoCliRunner):
        """Test error when specific run ID is not found."""
        fake_run_id = str(uuid.uuid4())

        result = cli_runner.invoke(cli, ["logs", "show", fake_run_id])

        assert result.exit_code == 1
        exc = result.exception
        assert isinstance(exc, CliError)
        assert f"No job found with log ID '{fake_run_id}'" in exc.args[0]

    def test_large_log_confirmation(
        self,
        session: Session,
        cli_runner: MeltanoCliRunner,
        job_factory: JobFactory,
    ):
        """Test confirmation prompt for large log files."""
        # Create a log larger than 2MB
        large_content = "x" * (2 * 1024 * 1024 + 1)
        job = job_factory.create(session, log_content=large_content)

        # Test declining confirmation
        with mock.patch(
            "meltano.cli.logs.project_engine",
            return_value=(None, lambda: session),
        ):
            result = cli_runner.invoke(
                cli,
                ["logs", "show", str(job.run_id)],
                input="n\n",
            )

        assert result.exit_code == 0
        assert "Log file is large" in result.output
        assert "Do you want to display it anyway?" in result.output
        assert "Log file path:" in result.output

        # Test accepting confirmation
        with mock.patch(
            "meltano.cli.logs.project_engine",
            return_value=(None, lambda: session),
        ):
            result = cli_runner.invoke(
                cli,
                ["logs", "show", str(job.run_id)],
                input="y\n",
            )

        assert result.exit_code == 0
        assert "Log file is large" in result.output
        # The large content would be displayed

    def test_json_format_with_log_display(
        self,
        session: Session,
        cli_runner: MeltanoCliRunner,
        job_factory: JobFactory,
    ):
        """Test JSON format for job info when showing logs."""
        job = job_factory.create(session)

        with mock.patch(
            "meltano.cli.logs.project_engine",
            return_value=(None, lambda: session),
        ):
            result = cli_runner.invoke(
                cli,
                ["logs", "show", str(job.run_id), "--format", "json"],
            )

        assert result.exit_code == 0
        # Job info should be in JSON format
        lines = result.output.strip().split("\n")
        json_end = next((i for i, line in enumerate(lines) if line == "}"), None)
        assert json_end is not None
        json_str = "\n".join(lines[: json_end + 1])
        data = json.loads(json_str)
        assert data["job_name"] == job.job_name
        assert data["run_id"] == str(job.run_id)
        assert data["state"] == "SUCCESS"

    def test_legacy_log_location(
        self,
        cli_runner: MeltanoCliRunner,
        job_factory: JobFactory,
    ):
        """Test reading logs from legacy location."""
        # This would require mocking the legacy_logs_dir method
        # to return a valid path and creating logs there
        # Placeholder for legacy log test
