import functools
from flask import current_app

from meltano.core.utils import truthy


HTTP_KILLSWITCH_CODE = 499


def readonly_killswitch(f):
    @functools.wraps(f)
    def _decorated(*args, **kwargs):
        if current_app.config["MELTANO_READONLY"]:
            return (
                "Meltano is currently running in read-only mode.",
                HTTP_KILLSWITCH_CODE,
            )

        return f(*args, **kwargs)

    return _decorated
