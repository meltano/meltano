from __future__ import annotations

import pytest

from meltano.core.encryption.base import EncryptionKey


class DummyEncryptionKey(EncryptionKey):
    scheme = "dummy"
    size = 16

    @classmethod
    def from_uri(cls, key_uri):
        return cls()

    def encrypt(self, data):
        padding = "*" * self.size
        return padding + data

    def decrypt(self, data):
        return data[self.size :]


class TestEncryptionABC:
    def test_missing_scheme(self):
        with pytest.raises(
            TypeError,
            match="EncryptionKey subclass .* must define a scheme",
        ):

            class _MissingScheme(EncryptionKey):
                pass

    def test_not_implemented(self):
        class NotImplementedEncryptionKey(EncryptionKey):
            scheme = "not_implemented"

        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            NotImplementedEncryptionKey()  # type: ignore

    def test_encrypt_decrypt(self):
        key = DummyEncryptionKey()
        data = "Hello, World!"
        encrypted = key.encrypt(data)
        decrypted = key.decrypt(encrypted)

        assert data == decrypted
