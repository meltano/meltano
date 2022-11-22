from __future__ import annotations

from urllib.parse import ParseResult

from meltano.core.encryption.fernet import FernetEncryptionKey


class TestFernet:
    def test_encrypt_decrypt(self, fernet_uri: ParseResult):
        fernet_key = FernetEncryptionKey.from_uri(fernet_uri)

        data = "Hello, World!"
        encrypted = fernet_key.encrypt(data)
        decrypted = fernet_key.decrypt(encrypted)

        assert data == decrypted
