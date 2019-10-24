import datetime
import glob
import logging
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Union, Optional

from meltano.core.project import Project
from meltano.core.utils import slugify, makedirs


class MissingJobLogException(Exception):
    """Occurs when JobLoggingService can not find a requested log."""

    pass


class JobLoggingService:
    def __init__(self, project: Project):
        self.project = project

    @makedirs
    def elt_dir(self, job_id, run_id, *joinpaths):
        return self.project.job_dir(job_id, str(run_id), *joinpaths)

    @contextmanager
    def create_log(self, job_id, run_id, file_name="elt.log"):
        """
        Open a new log file for logging and yield it.

        Log will be created inside the elt_dir, which is .meltano/run/elt/:job_id/:run_id
        """
        log_file_name = self.elt_dir(job_id, run_id, file_name)

        try:
            log_file = open(log_file_name, "w")
        except (OSError, IOError) as err:
            # Don't stop the Job running if you can not open the log file
            # for writting: just return /dev/null
            logging.error(
                f"Could open log file {log_file_name} for writting. Using /dev/null"
            )
            log_file = open(os.devnull, "w")

        try:
            yield log_file
        finally:
            log_file.close()

    def get_latest_log(self, job_id):
        """
        Get the contents of the most recent log for any ELT job
         that run with the provided job_id
        """
        try:
            latest_log = next(iter(self.get_all_logs(job_id)))
            with latest_log.open() as f:
                return f.read()
        except StopIteration:
            raise MissingJobLogException(
                f"Could not find any log for job with id '{job_id}'"
            )
        except FileNotFoundError:
            raise MissingJobLogException(
                f"Cannot log for job with id '{job_id}': '{latest_log}' is missing."
            )

    def get_all_logs(self, job_id):
        """
        Get all the log files for any ELT job that run with the provided job_id

        The result is ordered so that the most recent is first on the list
        """
        log_files = list(self.project.job_dir(job_id).glob("**/*.log"))
        log_files.sort(key=os.path.getctime, reverse=True)

        return log_files
