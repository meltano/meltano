"""Utilities for the Meltano API controller."""

from .errors import InvalidFileNameError


def enforce_secure_filename(filename: str) -> str:
    """Secure a filename by limiting to ASCII & removing/replacing bad characters.

    Parameters:
        filename: The filename to be secured.

    Raises:
        InvalidFileNameError: If the filename is empty after securing it.

    Returns:
        The secured non-empty filename.
    """
    from werkzeug.utils import secure_filename

    secured_filename = secure_filename(filename)
    if secured_filename == "":
        raise InvalidFileNameError(secured_filename)
    return secured_filename
