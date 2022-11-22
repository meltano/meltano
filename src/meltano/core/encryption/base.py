"""Encryption key base class."""

from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TypeVar
from urllib.parse import ParseResult

__all__ = ["EncryptionKey"]

_T = TypeVar("_T", bound="EncryptionKey")


class EncryptionKey(metaclass=ABCMeta):
    """ABC for encryption keys."""

    scheme: str
    implementations: dict[str, type[EncryptionKey]] = {}

    def __init_subclass__(cls, **kwargs: object) -> None:
        """Register the encryption key implementation.

        Args:
            kwargs: Additional keyword arguments.

        Raises:
            TypeError: If the encryption key implementation does not define a scheme.
        """
        super().__init_subclass__(**kwargs)

        if not hasattr(cls, "scheme"):  # noqa: WPS421
            raise TypeError(f"EncryptionKey subclass {cls} must define a scheme")

        cls.implementations[cls.scheme] = cls

    @staticmethod
    def is_encrypted(data: str) -> bool:
        """Check if data is encrypted.

        Args:
            data: The data to check.

        Returns:
            True if the data is encrypted, False otherwise.
        """
        return data.startswith("ENC(") and data.endswith(")")

    @staticmethod
    def prepare_encrypted(data: str) -> str:
        """Prepare encrypted data for decryption.

        Args:
            data: The data to prepare.

        Returns:
            The prepared data.
        """
        return data[4:-1]

    @classmethod
    @abstractmethod
    def from_uri(cls: type[_T], key_uri: ParseResult) -> _T:
        """Create an encryption key from a URI.

        Args:
            key_uri: The key URI to parse.

        Returns:
            The encryption key.
        """

    @abstractmethod
    def encrypt(self, data: str) -> str:
        """Encrypt data.

        Args:
            data: The data to encrypt.

        Returns:
            The encrypted data.
        """

    @abstractmethod
    def decrypt(self, data: str) -> str:
        """Decrypt data.

        Args:
            data: The data to decrypt.

        Returns:
            The decrypted data.
        """
