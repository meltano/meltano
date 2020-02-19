"""Add Subscription

Revision ID: 87d9638f6ac6
Revises: 23ea52e6d784
Create Date: 2020-02-17 16:03:27.765240

"""
from alembic import op
import sqlalchemy as sa

from meltano.migrations import GUID

# revision identifiers, used by Alembic.
revision = "87d9638f6ac6"
down_revision = "23ea52e6d784"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "subscriptions",
        sa.Column("id", GUID, primary_key=True),
        sa.Column("recipient", sa.String(), nullable=False),
        sa.Column("event_type", sa.String(), nullable=False),
        sa.Column("source_type", sa.String(), nullable=True),
        sa.Column("source_id", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime),
        sa.UniqueConstraint("recipient", "event_type", "source_type", "source_id"),
    )


def downgrade():
    op.drop_table("subscriptions")
