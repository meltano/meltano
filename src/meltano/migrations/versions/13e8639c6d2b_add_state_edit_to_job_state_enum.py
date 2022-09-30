"""add_state_edit_to_job_state_enum

Revision ID: 13e8639c6d2b
Revises: d135f52a6f49
Create Date: 2022-04-21 09:35:35.435614

"""
from enum import Enum

import sqlalchemy as sa
from alembic import op

from meltano.migrations.utils.dialect_typing import (
    get_dialect_name,
    max_string_length_for_dialect,
)

# revision identifiers, used by Alembic.
revision = "13e8639c6d2b"
down_revision = "d135f52a6f49"
branch_labels = None
depends_on = None


# from core/job/job.py
class State(Enum):
    """Represents status of a Job."""

    IDLE = (0, ("RUNNING", "FAIL"))
    RUNNING = (1, ("SUCCESS", "FAIL"))
    SUCCESS = (2, ())
    FAIL = (3, ("RUNNING",))
    DEAD = (4, ())
    STATE_EDIT = (5, ())


def upgrade():
    dialect_name = get_dialect_name()
    max_string_length = max_string_length_for_dialect(dialect_name)

    conn = op.get_bind()
    # In sqlite, the field is already a varchar.
    # "ALTER COLUMN" statements are also not supported.
    if conn.dialect.name != "sqlite":
        op.alter_column(
            table_name="job",
            column_name="state",
            type_=sa.types.String(max_string_length),
            existing_type=sa.Enum(State, name="job_state"),
            existing_nullable=True,
        )

    # In postgresql, drop the created Enum type so that
    # downgrade() can re-create it.
    if conn.dialect.name == "postgresql":
        conn.execute("DROP TYPE job_state;")


def downgrade():
    conn = op.get_bind()
    # In sqlite, the field is already a varchar.
    # "ALTER COLUMN" statements are also not supported.
    if conn.dialect.name != "sqlite":
        op.alter_column(
            table_name="job",
            column_name="state",
            _type=sa.Enum(State, name="job_state"),
            existing_type=sa.types.String,
        )
