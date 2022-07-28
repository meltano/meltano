"""Add Subscription

Revision ID: 87d9638f6ac6
Revises: 23ea52e6d784
Create Date: 2020-02-17 16:03:27.765240

"""
import sqlalchemy as sa
from alembic import op

from meltano.migrations import GUID
from meltano.migrations.utils.dialect_typing import (
    datetime_for_dialect,
    get_dialect_name,
)

# revision identifiers, used by Alembic.
revision = "87d9638f6ac6"
down_revision = "23ea52e6d784"
branch_labels = None
depends_on = None


def upgrade():
    dialect_name = get_dialect_name()
    datetime_type = datetime_for_dialect(dialect_name)

    op.create_table(
        "subscriptions",
        sa.Column("id", GUID, primary_key=True),
        sa.Column("recipient", sa.String(255), nullable=False),
        sa.Column("event_type", sa.String(255), nullable=False),
        sa.Column("source_type", sa.String(255), nullable=True),
        sa.Column("source_id", sa.String(255), nullable=True),
        sa.Column("created_at", datetime_type),
        sa.UniqueConstraint("recipient", "event_type", "source_type", "source_id"),
    )


def downgrade():
    op.drop_table("subscriptions")
