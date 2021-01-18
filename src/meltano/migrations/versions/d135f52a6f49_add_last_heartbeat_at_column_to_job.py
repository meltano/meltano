"""Add `last_heartbeat_at` column to `job` table.

Revision ID: d135f52a6f49
Revises: e4fbabc3fed6
Create Date: 2021-01-14 12:45:55.821947

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "d135f52a6f49"
down_revision = "e4fbabc3fed6"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("job", sa.Column("last_heartbeat_at", sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column("user", "last_heartbeat_at")
