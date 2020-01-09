"""Create meltano.core base tables

Revision ID: b4c05e463b53
Revises: 6f28844bcd3c
Create Date: 2019-07-23 16:05:29.073296

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.ext.mutable import MutableDict
from meltano.migrations import JSONEncodedDict, IntFlag
from enum import Enum


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
    op.create_table(
        "job",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("job_id", sa.String),
        sa.Column("state", sa.Enum(State, name="job_state")),
        sa.Column("started_at", sa.DateTime),
        sa.Column("ended_at", sa.DateTime),
        sa.Column("payload", MutableDict.as_mutable(JSONEncodedDict)),
        sa.Column("payload_flags", IntFlag, default=0),
    )

    op.create_table(
        "plugin_settings",
        sa.Column("label", sa.String(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("namespace", sa.String(), nullable=True),
        sa.Column("value", sa.PickleType(), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("name", "namespace"),
    )


def downgrade():
    op.drop_table("job")
    op.drop_table("plugin_settings")
