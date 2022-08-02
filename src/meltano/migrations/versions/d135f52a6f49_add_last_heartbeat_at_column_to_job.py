"""Add `last_heartbeat_at` column to `job` table.

Revision ID: d135f52a6f49
Revises: e4fbabc3fed6
Create Date: 2021-01-14 12:45:55.821947

"""
import sqlalchemy as sa
from alembic import op

from meltano.migrations.utils.dialect_typing import (
    datetime_for_dialect,
    get_dialect_name,
)

# revision identifiers, used by Alembic.
revision = "d135f52a6f49"
down_revision = "e4fbabc3fed6"
branch_labels = None
depends_on = None


def upgrade():
    dialect_name = get_dialect_name()
    datetime_type = datetime_for_dialect(dialect_name)

    op.add_column("job", sa.Column("last_heartbeat_at", datetime_type, nullable=True))


def downgrade():
    op.drop_column("user", "last_heartbeat_at")
