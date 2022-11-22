"""AWS KMS encryption key implementation."""

from __future__ import annotations

from meltano.core.encryption.base import EncryptionKey


class AwsKmsEncryptionKey(EncryptionKey):
    """AWS KMS encryption key implementation."""

    scheme = "awskms"

    def __init__(self, file: str):
        """Initialize the encryption key.

        Args:
            file: The file containing the encryption key.
        """
        self.file = file
