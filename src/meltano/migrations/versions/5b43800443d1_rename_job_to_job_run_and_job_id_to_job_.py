"""Rename job to job_run and job_id to job_name

Revision ID: 5b43800443d1
Revises: 13e8639c6d2b
Create Date: 2022-06-29 14:28:51.673195

"""
import sqlalchemy as sa
from alembic import op

from meltano.migrations.utils.dialect_typing import (
    get_dialect_name,
    max_string_length_for_dialect,
)

# revision identifiers, used by Alembic.
revision = "5b43800443d1"
down_revision = "13e8639c6d2b"
branch_labels = None
depends_on = None


def upgrade():
    dialect_name = get_dialect_name()
    max_string_length = max_string_length_for_dialect(dialect_name)

    op.alter_column(
        "job",
        "job_id",
        new_column_name="job_name",
        existing_type=sa.types.String(max_string_length),
    )
    op.rename_table("job", "runs")


def downgrade():
    dialect_name = get_dialect_name()
    max_string_length = max_string_length_for_dialect(dialect_name)

    op.rename_table("runs", "job")
    op.alter_column(
        "job",
        "job_name",
        new_column_name="job_id",
        existing_type=sa.types.String(max_string_length),
    )
