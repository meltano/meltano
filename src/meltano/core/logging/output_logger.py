import click
import functools
import logging
import importlib
import sys

from .utils import remove_ansi_escape_sequences


# By default, click is automatically stripping ANSI color codes if the output
#  stream is not connected to a terminal (which is the case with OutputLogger).
# In order to force it to use colors, we have to add a `color=True` param to secho
# But this turns off autodetection, so we now have to be careful not to force
#  this for Windows or other unsupported platforms. Hence the check bellow:
if sys.platform.startswith(("linux", "darwin")):
    FORCE_COLOR = True
else:
    FORCE_COLOR = None


class OutputLogger(object):
    """
    Context manager that takes over stdout and stderr and redirects anything
     sent there to a log file as also to the real stdout and stderr

    It also resets the handlers of the root logger to point to the newly set
     stderr, so that logging messages are also send to the log file
     even if it is not specified by the logger of a particular module.
    """

    def __init__(self, file):
        # Don't append, just log the last run for the same job_id
        self.file = file
        self.stdout = sys.stdout
        self.stderr = sys.stderr

        self.log_handlers = logging.getLogger().handlers

    def __enter__(self):
        # assign the Tee class to stdout and stderr so that everything pass through it
        sys.stdout = Tee(self.file, self.stdout)
        sys.stderr = Tee(self.file, self.stderr)

        stdlog = logging.StreamHandler(sys.stderr)
        logging.getLogger().handlers = [stdlog]

        # monkeypatch `click.secho`, setting `color=FORCE_COLOR` by default
        click.secho = functools.partial(click.secho, color=FORCE_COLOR)

    def __exit__(self, exc_type, exc_value, tb):
        # log any Exception that caused this OutputLogger to exit prematurely
        if isinstance(exc_value, Exception):
            logging.exception(exc_value)

        sys.stdout.flush()
        sys.stderr.flush()

        sys.stdout = self.stdout
        sys.stderr = self.stderr
        logging.getLogger().handlers = self.log_handlers

        # revert back to the `click` implementation
        importlib.reload(click)


class Tee(object):
    """
    Simple Tee class to log anything written in a stream to a file
     and then also write it to the stream.
    """

    def __init__(self, file, stream):
        self.file = file
        self.stream = stream

    def write(self, data):
        self.stream.write(data)
        self.file.write(remove_ansi_escape_sequences(data))
        # always flush the file to keep it up to date with the stream
        self.file.flush()

    def flush(self):
        self.stream.flush()
        self.file.flush()
