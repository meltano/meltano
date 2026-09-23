from __future__ import annotations

import typing as t
from datetime import datetime, timedelta, timezone

import pytest
import sqlalchemy as sa

from meltano.core.sqlalchemy import DateTimeUTC

if t.TYPE_CHECKING:
    import sys

    if sys.version_info >= (3, 13):
        from collections.abc import Generator
    else:
        from typing_extensions import Generator


class TestSQLAlchemyModels:
    @pytest.fixture
    def engine(self) -> Generator[sa.Engine]:
        engine = sa.create_engine("sqlite:///:memory:")
        try:
            yield engine
        finally:
            engine.dispose()

    @pytest.fixture
    def table(self, engine: sa.Engine) -> sa.Table:
        metadata = sa.MetaData()
        test = sa.Table(
            "test",
            metadata,
            sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
            sa.Column("created_at", DateTimeUTC, nullable=True),
        )
        metadata.create_all(engine)
        return test

    @pytest.mark.parametrize(
        ("inserted", "expected"),
        (
            pytest.param(None, None, id="None"),
            pytest.param(
                datetime(2021, 1, 1, 12),  # noqa: DTZ001
                datetime(2021, 1, 1, 12, tzinfo=timezone.utc),
                id="naive",
            ),
            pytest.param(
                datetime(2021, 1, 1, 12, tzinfo=timezone.utc),
                datetime(2021, 1, 1, 12, tzinfo=timezone.utc),
                id="aware",
            ),
            pytest.param(
                datetime(2021, 1, 1, 12, tzinfo=timezone(timedelta(hours=-5))),
                datetime(2021, 1, 1, 17, tzinfo=timezone.utc),
                id="eastern",
            ),
        ),
    )
    def test_datetime_utc_model(
        self,
        engine: sa.Engine,
        table: sa.Table,
        inserted: datetime | None,
        expected: datetime | None,
    ) -> None:
        select_stmt = table.select()
        insert_stmt = table.insert().values(created_at=inserted)

        with engine.connect() as conn:
            conn.execute(insert_stmt)

            result = conn.execute(select_stmt).mappings().fetchone()
            assert result is not None
            assert result["created_at"] == expected
