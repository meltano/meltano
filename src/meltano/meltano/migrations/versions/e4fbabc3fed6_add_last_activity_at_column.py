"""add last activity at column

Revision ID: e4fbabc3fed6
Revises: 367228df6a43
Create Date: 2020-03-24 15:53:54.142685

"""
import sqlalchemy as sa
from alembic import op

from meltano.migrations.utils.dialect_typing import (
    datetime_for_dialect,
    get_dialect_name,
)

# revision identifiers, used by Alembic.
revision = "e4fbabc3fed6"
down_revision = "367228df6a43"
branch_labels = None
depends_on = None


def upgrade():
    dialect_name = get_dialect_name()
    datetime_type = datetime_for_dialect(dialect_name)

    op.add_column("user", sa.Column("last_activity_at", datetime_type, nullable=True))


def downgrade():
    op.drop_column("user", "last_activity_at")
