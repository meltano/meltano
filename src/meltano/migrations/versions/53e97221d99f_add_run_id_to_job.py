"""Add run_id to Job.

Revision ID: 53e97221d99f
Revises: 6ef30ab7b8e5
Create Date: 2019-10-10 13:12:55.147164

"""

from __future__ import annotations

import uuid

import sqlalchemy as sa
import sqlalchemy.orm
from alembic import op

from meltano.migrations import GUID

# revision identifiers, used by Alembic.
revision = "53e97221d99f"
down_revision = "6ef30ab7b8e5"
branch_labels = None
depends_on = None

Session = sa.orm.sessionmaker(future=True)


def upgrade() -> None:
    op.add_column("job", sa.Column("run_id", GUID))

    metadata = sa.MetaData()
    session = Session(bind=op.get_bind())
    Job = sa.Table("job", metadata, autoload_with=op.get_bind())  # noqa: N806

    for job in session.query(Job):
        job.run_id = uuid.uuid4()

    session.commit()


def downgrade() -> None:
    op.drop_column("job", "run_id")
