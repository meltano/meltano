import datetime
import glob
import logging
import os

from contextlib import contextmanager

from meltano.core.project import Project
from meltano.core.utils import slugify

MAX_LOGS_PER_JOB_ID = 10


class MissingJobLogException(Exception):
    pass


class JobLoggingService:
    def __init__(self, project: Project):
        self.project = project

        try:
            self.max_logs_per_job_id = int(os.getenv("MELTANO_MAX_LOGS_PER_JOB_ID"))
            if self.max_logs_per_job_id < 1:
                self.max_logs_per_job_id = MAX_LOGS_PER_JOB_ID
        except Exception:
            self.max_logs_per_job_id = MAX_LOGS_PER_JOB_ID

    @contextmanager
    def create_log(self, job_id: str):
        """
        Open a new log file for logging and yield it
        Store all logs for a Job under: .meltano/run/logs/job_id/
        Support multiple (and even concurent) elt runs for the same job_id
         by creating a log per run that includes the current timestamp
         YYYYMMDD-HHMMSS-mmmmmm.log
        """
        log_file_name = self.project.run_dir(
            "logs",
            slugify(job_id),
            f"elt_{datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')}.log",
        )

        try:
            log_file = open(log_file_name, "w")
        except (OSError, IOError) as err:
            # Don't stop the Job running if you can not open the log file
            # for writting: just return /dev/null
            logging.error(
                f"Could open log file {log_file_name} for writting. Using /dev/null"
            )
            log_file = open(os.devnull, "w")

        yield log_file

        log_file.close()

        # When we are done, clean old logs so that we do not keep
        # too many logs for the same job_id
        self.clean_old_logs(job_id)

    def get_latest_log(self, job_id: str):
        """
        Get the contents of the most recent log for any ELT job
         that run with the provided job_id
        """
        log_files = self.project.run_dir("logs", slugify(job_id)).glob("*.log")
        latest_log = max(log_files, key=os.path.getctime)

        try:
            with open(latest_log, "r") as f:
                log = f.read()

            return log
        except FileNotFoundError:
            raise MissingJobLogException(
                f"Log File {latest_log} for job with id {job_id} not found"
            )

    def get_all_logs(self, job_id: str):
        """
        Get all the log files for any ELT job that run with the provided job_id

        The result is ordered so that the most recent is first on the list
        """
        log_files = list(self.project.run_dir("logs", slugify(job_id)).glob("*.log"))
        log_files.sort(key=os.path.getctime, reverse=True)

        return log_files

    def clean_old_logs(self, job_id: str):
        """
        Only keep self.max_logs_per_job_id logs per job_id
        """
        all_logs = self.get_all_logs(job_id)

        for log in all_logs[self.max_logs_per_job_id :]:
            try:
                os.remove(log)
            except OSError:
                pass
