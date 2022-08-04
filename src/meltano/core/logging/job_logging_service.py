from __future__ import annotations

import logging
import os
from contextlib import contextmanager

from meltano.core.project import Project
from meltano.core.utils import makedirs, slugify

MAX_FILE_SIZE = 2097152  # 2MB max


class MissingJobLogException(Exception):
    """Occurs when `JobLoggingService` can not find a requested log."""


class SizeThresholdJobLogException(Exception):
    """Occurs when a Job log exceeds the `MAX_FILE_SIZE`."""


class JobLoggingService:
    def __init__(self, project: Project):
        self.project = project

    @makedirs
    def logs_dir(self, state_id, *joinpaths):
        return self.project.job_logs_dir(state_id, *joinpaths)

    def generate_log_name(
        self, state_id: str, run_id: str, file_name: str = "elt.log"
    ) -> str:
        """Generate an internal etl log path and name."""
        return self.logs_dir(state_id, str(run_id), file_name)

    @contextmanager
    def create_log(self, state_id, run_id, file_name="elt.log"):
        """Open a new log file for logging and yield it.

        Log will be created inside the logs_dir, which is `.meltano/logs/elt/:state_id/:run_id`
        """
        log_file_name = self.generate_log_name(state_id, run_id, file_name)

        try:
            with open(log_file_name, "w") as log_file:
                yield log_file
        except OSError:
            # Don't stop the Job running if you can not open the log file
            # for writting: just return /dev/null
            logging.error(
                f"Could open log file {log_file_name!r} for writting. Using `/dev/null`"
            )
            with open(os.devnull, "w") as log_file:
                yield log_file

    def get_latest_log(self, state_id):
        """Get the contents of the most recent log for any ELT job that ran with the provided `state_id`."""
        try:
            latest_log = next(iter(self.get_all_logs(state_id)))

            if latest_log.stat().st_size > MAX_FILE_SIZE:
                raise SizeThresholdJobLogException(
                    f"The log file size exceeds '{MAX_FILE_SIZE}'"
                )

            with latest_log.open() as f:
                return f.read()
        except StopIteration:
            raise MissingJobLogException(
                f"Could not find any log for job with id '{state_id}'"
            )
        except FileNotFoundError:
            raise MissingJobLogException(
                f"Cannot log for job with id '{state_id}': '{latest_log}' is missing."
            )

    def get_downloadable_log(self, state_id):
        """Get the `*.log` file of the most recent log for any ELT job that ran with the provided `state_id`."""
        try:
            latest_log = next(iter(self.get_all_logs(state_id)))
            return str(latest_log.resolve())
        except StopIteration:
            raise MissingJobLogException(
                f"Could not find any log for job with id '{state_id}'"
            )
        except FileNotFoundError:
            raise MissingJobLogException(
                f"Cannot log for job with id '{state_id}': '{latest_log}' is missing."
            )

    def get_all_logs(self, state_id):
        """Get all the log files for any ELT job that ran with the provided `state_id`.

        The result is ordered so that the most recent is first on the list.
        """
        log_files = []
        for logs_dir in self.logs_dirs(state_id):
            log_files.extend(list(logs_dir.glob("**/*.log")))

        log_files.sort(key=lambda path: os.stat(path).st_ctime_ns, reverse=True)

        return log_files

    def delete_all_logs(self, state_id):
        """Delete all the log files for any ELT job that ran with the provided `state_id`."""
        for log_path in self.get_all_logs(state_id):
            log_path.unlink()

    def legacy_logs_dir(self, state_id, *joinpaths):
        job_dir = self.project.run_dir("elt").joinpath(slugify(state_id), *joinpaths)
        return job_dir if job_dir.exists() else None

    def logs_dirs(self, state_id, *joinpaths):
        logs_dir = self.logs_dir(state_id, *joinpaths)
        legacy_logs_dir = self.legacy_logs_dir(state_id, *joinpaths)

        dirs = [logs_dir]
        if legacy_logs_dir:
            dirs.append(legacy_logs_dir)

        return dirs
