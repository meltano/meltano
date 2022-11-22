from __future__ import annotations

from urllib.parse import ParseResult

from meltano.core.encryption import FernetEncryptionKey, get_key


class TestEncryptionApi:
    def test_get_key(self, fernet_uri: ParseResult):
        key = get_key(fernet_uri.geturl())

        assert isinstance(key, FernetEncryptionKey)
        assert key.scheme == "fernet"
