"""Encryption for Meltano and plugins configuration."""

from __future__ import annotations

from meltano.core.encryption.api import get_key
from meltano.core.encryption.base import EncryptionKey
from meltano.core.encryption.fernet import FernetEncryptionKey

__all__ = ["get_key", "EncryptionKey", "FernetEncryptionKey"]
