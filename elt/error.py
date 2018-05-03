class Error(Exception):
    """Base exception for ELT errors."""


class ExtractError(Error):
    """
    Error in the extraction process, like API errors.
    """


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


class InapplicableChangeError(SchemaError):
    """Raise for inapplicable schema changes."""


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
        aggregate_type = self.etype.Aggregate if hasattr(self.etype, "Aggregate") else AggregateError

        if len(self.failures):
            exceptions = map(lambda f: f[0], self.failures)
            raise aggregate_type(exceptions)
