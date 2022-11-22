"""Encryption API."""

from __future__ import annotations

from urllib.parse import urlparse

from meltano.core.encryption.base import EncryptionKey


class UnknownEncryptionSchemeError(Exception):
    """Raised when an unknown encryption scheme is encountered."""

    def __init__(self, scheme: str):
        """Initialize the exception.

        Args:
            scheme: The unknown encryption scheme.
        """
        super().__init__(f"Unknown encryption scheme: {scheme}")
        self.scheme = scheme


def get_key(key_uri: str) -> EncryptionKey:
    """Get an encryption key from a URI.

    Args:
        key_uri: The URI of the encryption key.

    Returns:
        The encryption key.

    Raises:
        UnknownEncryptionSchemeError: If the encryption scheme is not supported.
    """
    parsed_uri = urlparse(key_uri)
    try:
        return EncryptionKey.implementations[parsed_uri.scheme].from_uri(parsed_uri)
    except KeyError:
        raise UnknownEncryptionSchemeError(parsed_uri.scheme)
