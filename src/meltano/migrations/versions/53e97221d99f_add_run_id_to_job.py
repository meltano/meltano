"""Add run_id to Job

Revision ID: 53e97221d99f
Revises: 6ef30ab7b8e5
Create Date: 2019-10-10 13:12:55.147164

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy.types as types
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import UUID
import uuid


class GUID(types.TypeDecorator):
    """Platform-independent GUID type

    Uses PostgreSQL's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.

    Reference: https://docs.sqlalchemy.org/en/13/core/custom_types.html#backend-agnostic-guid-type
    """

    impl = types.CHAR

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(types.CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == "postgresql":
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).int
            else:
                # hexstring
                return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value


# revision identifiers, used by Alembic.
revision = "53e97221d99f"
down_revision = "6ef30ab7b8e5"
branch_labels = None
depends_on = None
Session = sa.orm.sessionmaker()


def upgrade():
    op.add_column("job", sa.Column("run_id", GUID))

    metadata = sa.MetaData(bind=op.get_bind())
    session = Session(bind=op.get_bind())
    Job = sa.Table("job", metadata, autoload=True)

    for job in session.query(Job):
        job.run_id = uuid.uuid4()

    session.commit()


def downgrade():
    op.drop_column("job", "run_id")
