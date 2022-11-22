"""Fernet encryption key implementation."""

from __future__ import annotations

from urllib.parse import ParseResult

from cryptography import fernet

from meltano.core.encryption.base import EncryptionKey


class FernetEncryptionKey(EncryptionKey):
    """Fernet encryption key implementation."""

    scheme = "fernet"

    def __init__(self, key: str):
        """Initialize the encryption key.

        Args:
            key: The encryption key.
        """
        self.value = fernet.MultiFernet([fernet.Fernet(k) for k in key.split(",")])

    @classmethod
    def from_uri(
        cls: type[FernetEncryptionKey],
        key_uri: ParseResult,
    ) -> FernetEncryptionKey:
        """Initialize the encryption key from a URI.

        Args:
            key_uri: The URI of the encryption key.

        Returns:
            The encryption key.
        """
        return cls(key_uri.netloc)

    def encrypt(self, data: str) -> str:
        """Encrypt data.

        Args:
            data: The data to encrypt.

        Returns:
            The encrypted data.
        """
        return self.value.encrypt(data.encode()).decode()

    def decrypt(self, data: str) -> str:
        """Decrypt data.

        Args:
            data: The data to decrypt.

        Returns:
            The decrypted data.
        """
        return self.value.decrypt(data).decode()
