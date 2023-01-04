from __future__ import annotations

from contextlib import nullcontext

import pytest
from mock import Mock

from meltano.core.db import (
    MeltanoDatabaseCompatibilityError,
    check_database_compatibility,
)


class TestDatabaseCompatibility:
    @pytest.mark.parametrize(
        ("dialect", "version", "expected"),
        [
            pytest.param(
                "sqlite",
                (3, 25, 0),
                pytest.raises(
                    MeltanoDatabaseCompatibilityError,
                    match=(
                        "Detected SQLite 3.25.0, but Meltano requires at least 3.25.1. "
                        "Upgrade your database to be compatible with Meltano or use a "
                        "different database."
                    ),
                ),
                id="sqlite-3.25.0",
            ),
            pytest.param("sqlite", (3, 25, 1), nullcontext(), id="sqlite-3.25.1"),
            pytest.param("sqlite", (3, 26, 0), nullcontext(), id="sqlite-3.26.0"),
            pytest.param("postgresql", (9, 6, 0), nullcontext(), id="postgresql-9.6.0"),
            pytest.param(
                "postgresql",
                (10, 0, 0),
                nullcontext(),
                id="postgresql-10.0.0",
            ),
        ],
    )
    def test_db_compatibility(self, dialect, version, expected):
        engine_mock = Mock()
        engine_mock.dialect.name = dialect
        engine_mock.dialect.server_version_info = version

        with expected:
            check_database_compatibility(engine_mock)
