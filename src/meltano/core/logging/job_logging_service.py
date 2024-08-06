from __future__ import annotations  # noqa: D100

import os
import typing as t
from contextlib import contextmanager

import structlog

from meltano.core.utils import makedirs, slugify

if t.TYPE_CHECKING:
    from pathlib import Path

    from meltano.core.project import Project

logger = structlog.stdlib.get_logger(__name__)
MAX_FILE_SIZE = 2097152  # 2MB max


class MissingJobLogException(Exception):
    """Occurs when `JobLoggingService` can not find a requested log."""


class SizeThresholdJobLogException(Exception):
    """A Job log exceeds the `MAX_FILE_SIZE`."""


class JobLoggingService:  # noqa: D101
    def __init__(self, project: Project):  # noqa: D107
        self.project = project

    @makedirs
    def logs_dir(self, state_id, *joinpaths, make_dirs: bool = True):  # noqa: ANN001, ANN002, ANN201
        """Return the logs directory for a given state_id.

        Args:
            state_id: The state ID for the logs.
            joinpaths: Additional paths to join to the logs directory.
            make_dirs: Whether to create the directory if it does not exist.

        Returns:
            The logs directory for the given state ID.
        """
        return self.project.job_logs_dir(state_id, *joinpaths, make_dirs=make_dirs)

    def generate_log_name(
        self,
        state_id: str,
        run_id: str,
        file_name: str = "elt.log",
    ) -> Path:
        """Generate an internal etl log path and name.

        Args:
            state_id: The state ID for the log.
            run_id: The run ID for the log.
            file_name: The name of the log file.

        Returns:
            The full path to the log file.
        """
        return self.logs_dir(state_id, str(run_id), file_name)

    @contextmanager
    def create_log(self, state_id, run_id, file_name="elt.log"):  # noqa: ANN001, ANN201
        """Open a new log file for logging and yield it.

        Log will be created inside the logs_dir, which is
        `.meltano/logs/elt/:state_id/:run_id`
        """
        log_file_name = self.generate_log_name(state_id, run_id, file_name)

        try:
            with log_file_name.open("w") as log_file:
                yield log_file
        except OSError:
            # Don't stop the Job running if you can not open the log file
            # for writing: just return /dev/null
            logger.error(
                f"Could open log file {log_file_name!r} for writing. "  # noqa: G004
                "Using `/dev/null`",
            )
            with open(os.devnull, "w") as log_file:  # noqa: PTH123
                yield log_file

    def get_latest_log(self, state_id) -> str:  # noqa: ANN001
        """Get the latest log.

        Args:
            state_id: The state ID for the log.

        Returns:
            The contents of the most recent log for any ELT job that ran with
            the provided `state_id`.
        """
        try:
            latest_log = next(iter(self.get_all_logs(state_id)))

            if latest_log.stat().st_size > MAX_FILE_SIZE:
                raise SizeThresholdJobLogException(
                    f"The log file size exceeds '{MAX_FILE_SIZE}'",  # noqa: EM102
                )

            with latest_log.open() as f:
                return f.read()
        except StopIteration:
            raise MissingJobLogException(
                f"Could not find any log for job with ID '{state_id}'",  # noqa: EM102
            ) from None
        except FileNotFoundError as ex:
            raise MissingJobLogException(
                f"Cannot log for job with ID '{state_id}': '{latest_log}' is missing.",  # noqa: EM102
            ) from ex

    def get_downloadable_log(self, state_id):  # noqa: ANN001, ANN201
        """Get the `*.log` file of the most recent log for any ELT job that ran with the provided `state_id`."""  # noqa: E501
        try:
            latest_log = next(iter(self.get_all_logs(state_id)))
            return str(latest_log.resolve())
        except StopIteration:
            raise MissingJobLogException(
                f"Could not find any log for job with ID '{state_id}'",  # noqa: EM102
            ) from None
        except FileNotFoundError as ex:
            raise MissingJobLogException(
                f"Cannot log for job with ID '{state_id}': '{latest_log}' is missing.",  # noqa: EM102
            ) from ex

    def get_all_logs(self, state_id):  # noqa: ANN001, ANN201
        """Get all the log files for any ELT job that ran with the provided `state_id`.

        The result is ordered so that the most recent is first on the list.
        """
        return sorted(
            [
                log_file
                for logs_dir in self.logs_dirs(state_id)
                for log_file in logs_dir.glob("**/*.log")
            ],
            key=lambda path: path.stat().st_ctime_ns,
            reverse=True,
        )

    def delete_all_logs(self, state_id) -> None:  # noqa: ANN001
        """Delete all the logs for any ELT job that ran with the provided `state_id`.

        Args:
            state_id: The state ID for which all log files should be deleted.
        """
        for log_path in self.get_all_logs(state_id):
            log_path.unlink()

    def legacy_logs_dir(self, state_id, *joinpaths):  # noqa: ANN001, ANN002, ANN201, D102
        job_dir = self.project.run_dir("elt").joinpath(slugify(state_id), *joinpaths)
        return job_dir if job_dir.exists() else None

    def logs_dirs(self, state_id, *joinpaths):  # noqa: ANN001, ANN002, ANN201, D102
        logs_dir = self.logs_dir(state_id, *joinpaths)
        legacy_logs_dir = self.legacy_logs_dir(state_id, *joinpaths)

        dirs = [logs_dir]
        if legacy_logs_dir:
            dirs.append(legacy_logs_dir)

        return dirs
