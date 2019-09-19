import logging
import sys

from .utils import remove_ansi_escape_sequences


class OutputLogger(object):
    """
    Context manager that takes over stdout and stderr and redirects anything
     sent there to a log file as also to the real stdout and stderr

    It also resets the handlers of the root logger to point to the newly set
     stderr, so that logging messages are also send to the log file
     even if it is not specified by the logger of a particular module.
    """

    def __init__(self, filename):
        # Don't append, just log the last run for the same job_id
        self.file = open(filename, "w")
        self.stdout = sys.stdout
        self.stderr = sys.stderr

        self.log_handlers = logging.getLogger().handlers

    def __enter__(self):
        # assign seld to stdout so that everything pass through the OutputLogger
        sys.stdout = self

        # We have to use a second class for logging to stderr as there is no
        #  way to differentiate the messages if we set everything to self.
        # We also don't want to assign the stderr to stdout as it would mess
        #  with the data sent through the Tap | Target pipe
        sys.stderr = LogStderrManager(self.file, self.stderr)

        stdlog = logging.StreamHandler(sys.stderr)
        logging.getLogger().handlers = [stdlog]

    def __exit__(self, exc_type, exc_value, tb):
        sys.stdout = self.stdout
        sys.stderr = self.stderr
        logging.getLogger().handlers = self.log_handlers

        self.flush()
        self.file.close()

    def write(self, data):
        self.stdout.write(data)

        self.file.write(remove_ansi_escape_sequences(data))
        # always flush the file to keep it up to date with stdout
        self.file.flush()

    def flush(self):
        self.stdout.flush()
        self.stderr.flush()
        self.file.flush()


class LogStderrManager(object):
    def __init__(self, file, stderr):
        self.file = file
        self.stderr = stderr

    def write(self, data):
        self.stderr.write(data)
        self.file.write(remove_ansi_escape_sequences(data))
        self.file.flush()

    def flush(self):
        self.file.flush()
        self.stderr.flush()
