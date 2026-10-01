"""Add an index on runs job_name, state, and descending started_at.

Revision ID: e7d3a8c921f6
Revises: c0efb3c314eb
Create Date: 2026-10-01 00:00:00.000000

"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "e7d3a8c921f6"
down_revision = "c0efb3c314eb"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create an index for latest run lookups by job name and state."""
    if op.get_bind().dialect.name == "mssql":
        # SQL Server cannot index VARCHAR(MAX). The bounded columns keep the
        # combined key below its 1700-byte nonclustered index limit.
        for column_name, length in (("job_name", 1024), ("state", 64)):
            op.alter_column(
                "runs",
                column_name,
                type_=sa.String(length),
                existing_type=sa.String(),
                existing_nullable=True,
            )

    op.create_index(
        "ix_runs_job_state_started",
        "runs",
        ["job_name", "state", sa.column("started_at").desc()],
    )


def downgrade() -> None:
    """Remove the index and restore SQL Server's unbounded columns."""
    op.drop_index("ix_runs_job_state_started", table_name="runs")

    if op.get_bind().dialect.name == "mssql":
        for column_name, length in (("job_name", 1024), ("state", 64)):
            op.alter_column(
                "runs",
                column_name,
                type_=sa.String(),
                existing_type=sa.String(length),
                existing_nullable=True,
            )
