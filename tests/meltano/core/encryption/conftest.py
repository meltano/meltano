from __future__ import annotations

from urllib.parse import ParseResult

import pytest
from cryptography.fernet import Fernet


@pytest.fixture(scope="session")
def fernet_uri() -> ParseResult:
    key = Fernet.generate_key().decode()
    return ParseResult(
        scheme="fernet",
        netloc=key,
        path="",
        params="",
        query="",
        fragment="",
    )
