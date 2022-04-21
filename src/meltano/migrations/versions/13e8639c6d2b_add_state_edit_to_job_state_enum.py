"""add_state_edit_to_job_state_enum

Revision ID: 13e8639c6d2b
Revises: d135f52a6f49
Create Date: 2022-04-21 09:35:35.435614

"""
from enum import Enum

import sqlalchemy as sa
from alembic import op
from sqlalchemy.ext.mutable import MutableDict

from meltano.migrations import IntFlag, JSONEncodedDict

# revision identifiers, used by Alembic.
revision = "13e8639c6d2b"
down_revision = "d135f52a6f49"
branch_labels = None
depends_on = None


class OldState(Enum):
    IDLE = (0, ("RUNNING", "FAIL"))
    RUNNING = (1, ("SUCCESS", "FAIL"))
    SUCCESS = (2, ())
    FAIL = (3, ("RUNNING",))
    DEAD = (4, ())


# from `src/meltano/core/job.py`
class NewState(Enum):
    IDLE = (0, ("RUNNING", "FAIL"))
    RUNNING = (1, ("SUCCESS", "FAIL"))
    SUCCESS = (2, ())
    FAIL = (3, ("RUNNING",))
    DEAD = (4, ())
    STATE_EDIT = (5, ())


columns = [
    "id",
    "job_id",
    "state",
    "started_at",
    "ended_at",
    "payload",
    "payload_flags",
    "last_heartbeat_at",
]
get_jobs_query = f"SELECT {', '.join(columns[1:])} FROM job"

table_args = [
    "job_new",
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("job_id", sa.String),
    sa.Column("state", sa.Enum(NewState, name="job_state_with_state_edit")),
    sa.Column("started_at", sa.DateTime),
    sa.Column("ended_at", sa.DateTime),
    sa.Column("payload", MutableDict.as_mutable(JSONEncodedDict)),
    sa.Column("payload_flags", IntFlag, default=0),
    sa.Column("last_heartbeat_at", sa.DateTime(), nullable=True),
]


def upgrade():
    jobs_table = sa.sql.table(*table_args)
    op.create_table(*table_args)

    conn = op.get_bind()

    result = conn.execute(get_jobs_query)

    jobs = result.fetchall()

    job_dicts = [
        {columns[1:][jdx]: job[jdx] for jdx in range(len(job))} for job in jobs
    ]

    op.bulk_insert(jobs_table, job_dicts)

    op.drop_table("job")
    op.rename_table("job_new", "job")


def downgrade():

    table_args[3] = sa.Column("state", sa.Enum(OldState, name="job_state"))
    op.create_table(*table_args)
    jobs_table = sa.sql.table(*table_args)

    conn = op.get_bind()

    result = conn.execute(get_jobs_query)

    jobs = result.fetchall()

    job_dicts = [
        {columns[1:][jdx]: job[jdx] for jdx in range(len(job))}
        for job in jobs
        if job[columns.index("state")] != NewState.STATE_EDIT
    ]

    op.bulk_insert(jobs_table, job_dicts)

    op.drop_table("job")
    op.rename_table("job_new", "job")
