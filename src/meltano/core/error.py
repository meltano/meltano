import functools
import logging

from enum import Enum


class ExitCode(int, Enum):
    OK = 0
    FAIL = 1
    NO_RETRY = 2


class Error(Exception):
    """Base exception for ELT errors."""

    def exit_code(self):
        return ExitCode.FAIL


class ExtractError(Error):
    """Error in the extraction process, like API errors."""

    def exit_code(self):
        return ExitCode.NO_RETRY


class SubprocessError(Exception):
    """Happens when subprocess exits with a resultcode != 0"""

    def __init__(self, message: str, process):
        self.process = process
        super().__init__(message)


class PluginInstallError(SubprocessError):
    """Happens when a plugin fails to install."""

    pass


class PluginInstallWarning(Exception):
    """Happens when a plugin optional optional step fails to install."""

    pass


def aggregate(error_cls):
    class Aggregate(error_cls):
        """Aggregate multiple sub-exceptions."""

        def __init__(self, exceptions: []):
            self.exceptions = exceptions

        def __str__(self):
            return "\n".join((str(e) for e in self.exceptions))

    if error_cls != Exception:
        error_cls.Aggregate = Aggregate

    return error_cls


AggregateError = aggregate(Exception)


@aggregate
class ImportError(Error):
    """
    Error in the import process, the data cannot be processed.
    """

    def __init__(self, entry):
        self.entry = entry


@aggregate
class SchemaError(Error):
    """Base exception for schema errors."""


@aggregate
class InapplicableChangeError(SchemaError):
    """Raise for inapplicable schema changes."""

    def exit_code(self):
        return ExitCode.NO_RETRY


# TODO: use as a context manager instead
class ExceptionAggregator:
    def __init__(self, etype):
        self.success = []
        self.failures = []
        self.etype = etype

    def recognize_exception(self, e) -> bool:
        return self.etype == type(e)

    def call(self, callable, *args, **kwargs):
        params = (args, kwargs)
        try:
            ret = callable(*args, **kwargs)
            self.success.append(params)
            return ret
        except Exception as e:
            if self.recognize_exception(e):
                self.failures.append((e, params))
            else:
                raise e

    def raise_aggregate(self):
        aggregate_type = AggregateError

        if hasattr(self.etype, "Aggregate"):
            aggregate_type = self.etype.Aggregate

        if len(self.failures):
            exceptions = [f[0] for f in self.failures]
            raise aggregate_type(exceptions)


def with_error_exit_code(main):
    @functools.wraps(main)
    def f(*args, **kwargs):
        try:
            main(*args, **kwargs)
        except Error as err:
            logging.error(str(err))
            exit(err.exit_code())
        except Exception as e:
            logging.error(str(e))
            raise e

    return f
