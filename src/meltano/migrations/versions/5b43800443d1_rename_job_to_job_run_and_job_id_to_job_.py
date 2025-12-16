"""Rename job to job_run and job_id to job_name.

Revision ID: 5b43800443d1
Revises: 13e8639c6d2b
Create Date: 2022-06-29 14:28:51.673195

"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "5b43800443d1"
down_revision = "13e8639c6d2b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # MySQL requires existing_type for column renames
    op.alter_column(
        "job",
        "job_id",
        new_column_name="job_name",
        existing_type=sa.String(1024),
    )
    op.rename_table("job", "runs")


def downgrade() -> None:
    op.rename_table("runs", "job")
    # MySQL requires existing_type for column renames
    op.alter_column(
        "job",
        "job_name",
        new_column_name="job_id",
        existing_type=sa.String(1024),
    )
