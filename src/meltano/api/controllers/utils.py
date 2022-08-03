from __future__ import annotations

from werkzeug.utils import secure_filename

from .errors import InvalidFileNameError


def enforce_secure_filename(string: str):
    name = secure_filename(string)
    if name == "":
        raise InvalidFileNameError(name)
    return name
