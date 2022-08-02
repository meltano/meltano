"""Create meltano.core base tables

Revision ID: b4c05e463b53
Revises: 6f28844bcd3c
Create Date: 2019-07-23 16:05:29.073296

"""
from enum import Enum

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.mssql import DATETIME2
from sqlalchemy.ext.mutable import MutableDict

from meltano.migrations import IntFlag, JSONEncodedDict
from meltano.migrations.utils.dialect_typing import (
    datetime_for_dialect,
    get_dialect_name,
    max_string_length_for_dialect,
)

# revision identifiers, used by Alembic.
revision = "b4c05e463b53"
down_revision = None
branch_labels = None
depends_on = None


# from `src/meltano/core/job.py`
class State(Enum):
    IDLE = (0, ("RUNNING", "FAIL"))
    RUNNING = (1, ("SUCCESS", "FAIL"))
    SUCCESS = (2, ())
    FAIL = (3, ("RUNNING",))
    DEAD = (4, ())


def upgrade():
    dialect_name = get_dialect_name()
    datetime_type = datetime_for_dialect(dialect_name)
    max_string_length = max_string_length_for_dialect(dialect_name)

    op.create_table(
        "job",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("job_id", sa.String(max_string_length)),
        sa.Column("state", sa.Enum(State, name="job_state")),
        sa.Column("started_at", datetime_type),
        sa.Column("ended_at", datetime_type),
        sa.Column(
            "payload", MutableDict.as_mutable(JSONEncodedDict(max_string_length))
        ),
        sa.Column("payload_flags", IntFlag, default=0),
    )

    op.create_table(
        "plugin_settings",
        sa.Column("label", datetime_type, nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("namespace", sa.String(255), nullable=True),
        sa.Column("value", sa.PickleType(), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("name", "namespace"),
    )


def downgrade():
    op.drop_table("job")
    op.drop_table("plugin_settings")
