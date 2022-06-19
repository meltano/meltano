import werkzeug.utils

from .errors import InvalidFileNameError


def enforce_secure_filename(string: str):
    name = werkzeug.utils.secure_filename(string)
    if name == "":
        raise InvalidFileNameError(name)
    return name
