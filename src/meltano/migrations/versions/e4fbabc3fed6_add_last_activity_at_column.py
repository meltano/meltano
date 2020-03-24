"""add last activity at column

Revision ID: e4fbabc3fed6
Revises: 367228df6a43
Create Date: 2020-03-24 15:53:54.142685

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e4fbabc3fed6"
down_revision = "367228df6a43"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("user", sa.Column("last_activity_at", sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column("user", "last_activity_at")
