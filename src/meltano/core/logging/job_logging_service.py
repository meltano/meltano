import datetime
import glob
import logging
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Union

from meltano.core.project import Project
from meltano.core.utils import slugify, makedirs


MAX_LOGS_PER_JOB_ID = 10


class MissingJobLogException(Exception):
    """Occurs when JobLoggingService can not find a requested log."""

    pass


class JobLoggingService:
    def __init__(self, project: Project, logs_dir: Union[str, Path] = None):
        self.project = project
        self.logs_dir = logs_dir or self.project.run_dir("logs")

        try:
            self.max_logs_per_job_id = int(os.getenv("MELTANO_MAX_LOGS_PER_JOB_ID"))
            if self.max_logs_per_job_id < 1:
                self.max_logs_per_job_id = MAX_LOGS_PER_JOB_ID
        except Exception:
            self.max_logs_per_job_id = MAX_LOGS_PER_JOB_ID

    @makedirs
    def run_dir(self, run_id, *joinpaths):
        return self.logs_dir.joinpath(str(run_id), *joinpaths)

    @contextmanager
    def create_log(self, run_id, file_name="elt.log"):
        """
        Open a new log file for logging and yield it
        Store all logs for a Job under: .meltano/run/logs/job_id/
        Support multiple (and even concurent) elt runs for the same job_id
         by creating a log per run that includes the current timestamp
         YYYYMMDD-HHMMSS-mmmmmm.log
        """
        log_file_name = self.run_dir(run_id, file_name)

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
        except Exception as err:
            raise err
        finally:
            log_file.close()

            # When we are done, clean old logs so that we do not keep
            # too many logs for the same job_id
            self.clean_old_logs()

    def get_latest_log(self):
        """
        Get the contents of the most recent log for any ELT job
         that run with the provided job_id
        """
        try:
            latest_log = next(iter(self.get_all_logs()))
            with latest_log.open() as f:
                log = f.read()

            return log
        except FileNotFoundError:
            raise MissingJobLogException(
                # f"Log File {latest_log} for job with id {job_id} not found"
            )
        except StopIteration:
            raise MissingJobLogException(
                # f"Could not find a log File for job with id {job_id}"
            )

    def get_all_logs(self):
        """
        Get all the log files for any ELT job that run with the provided job_id

        The result is ordered so that the most recent is first on the list
        """
        log_files = list(self.logs_dir.glob("**/*.log"))
        log_files.sort(key=os.path.getctime, reverse=True)

        return log_files

    def clean_old_logs(self):
        """
        Only keep self.max_logs_per_job_id logs per job_id
        """
        all_logs = self.get_all_logs()

        for log in all_logs[self.max_logs_per_job_id:]:
            try:
                log.unlink()
            except OSError:
                pass
