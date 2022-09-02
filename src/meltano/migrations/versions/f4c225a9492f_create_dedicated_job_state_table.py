"""Create dedicated job_state table

Revision ID: f4c225a9492f
Revises: 5b43800443d1
Create Date: 2022-09-02 09:44:05.581824

"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.ext.mutable import MutableDict

from meltano.core.sqlalchemy import JSONEncodedDict
from meltano.migrations import JSONEncodedDict
from meltano.migrations.utils.dialect_typing import (
    datetime_for_dialect,
    get_dialect_name,
    max_string_length_for_dialect,
)

# revision identifiers, used by Alembic.
revision = "f4c225a9492f"
down_revision = "5b43800443d1"
branch_labels = None
depends_on = None


def upgrade():
    # Create state table
    dialect_name = get_dialect_name()
    datetime_type = datetime_for_dialect(dialect_name)
    max_string_length = max_string_length_for_dialect(dialect_name)
    op.create_table(
        "state",
        sa.Column("job_name", sa.String(max_string_length)),
        sa.Column(
            "partial_state",
            MutableDict.as_mutable(JSONEncodedDict(max_string_length)),
        ),
        sa.Column(
            "completed_state",
            MutableDict.as_mutable(JSONEncodedDict(max_string_length)),
        ),
        sa.Column(
            "updated_at",
            sa.types.TIMESTAMP,
            server_default=sa.func.now(),
            onupdate=sa.func.current_timestamp(),
        ),
        sa.PrimaryKeyConstraint("job_name"),
        sa.UniqueConstraint("job_name"),
    )


def downgrade():
    # Remove job_state table
    op.drop_table("state")
