from __future__ import annotations

import typing as t
from dataclasses import dataclass
from textwrap import dedent

import pytest
from sqlalchemy import create_engine

from meltano.core.migration_service import MigrationError, MigrationService

if t.TYPE_CHECKING:
    import sys
    from pathlib import Path

    from sqlalchemy import Engine

    if sys.version_info >= (3, 13):
        from collections.abc import Generator
    else:
        from typing_extensions import Generator


MIGRATION_TEMPLATE = """
revision = {revision}
down_revision = {down_revision}

def upgrade() -> None: ...
def downgrade() -> None: ...
"""


@dataclass
class Migration:
    revision: str
    down_revision: str
    path: Path


def _generate_migrations(
    migration_directory: Path, *, count: int = 3
) -> list[Migration]:
    env_py = migration_directory / "env.py"
    env_py.write_text("")

    versions_directory = migration_directory / "versions"
    versions_directory.mkdir(exist_ok=True)
    migrations: list[Migration] = []
    down_revision: str = "None"
    for i in range(count):
        migration = Migration(
            revision=f'"00000000000{i}"',
            down_revision=down_revision,
            path=versions_directory / f"00000000000{i}_migration_{i}.py",
        )
        migration.path.write_text(
            MIGRATION_TEMPLATE.format(
                revision=migration.revision,
                down_revision=migration.down_revision,
            )
        )
        migrations.append(migration)
        down_revision = migration.revision

    return migrations


class TestMigrationService:
    @pytest.fixture
    def engine(self) -> Generator[Engine]:
        engine = create_engine("sqlite:///:memory:")
        try:
            yield engine
        finally:
            engine.dispose()

    def test_upgrade(self, engine: Engine, tmp_path: Path) -> None:
        lock_path = tmp_path / "db.lock"

        migrations = _generate_migrations(tmp_path)
        lock_path.write_text(migrations[-1].revision)

        migration_service = MigrationService(
            engine=engine,
            lock_path=lock_path,
            migration_directory=tmp_path,
        )
        migration_service.upgrade()

    def test_upgrade_without_lock(self, engine: Engine, tmp_path: Path) -> None:
        lock_path = tmp_path / "db.lock"

        migration_service = MigrationService(
            engine=engine,
            lock_path=lock_path,
            migration_directory=tmp_path,
        )
        with pytest.raises(
            MigrationError,
            match=r"Cannot upgrade the system database, revision lock not found.",
        ):
            migration_service.upgrade()

    def test_upgrade_error(self, engine: Engine, tmp_path: Path) -> None:
        lock_path = tmp_path / "db.lock"

        migrations = _generate_migrations(tmp_path)
        lock_path.write_text(migrations[-2].revision)

        migrations[-1].path.write_text(
            dedent(f"""\
            revision = {migrations[-1].revision}
            down_revision = {migrations[-1].down_revision}

            1/0

            def upgrade() -> None: ...
            def downgrade() -> None: ...
            """)
        )

        migration_service = MigrationService(
            engine=engine,
            lock_path=lock_path,
            migration_directory=tmp_path,
        )
        with pytest.raises(
            MigrationError,
            match=r"Cannot upgrade the system database. It might be corrupted.*",
        ) as exc:
            migration_service.upgrade()

        assert isinstance(exc.value.__cause__, ZeroDivisionError)
