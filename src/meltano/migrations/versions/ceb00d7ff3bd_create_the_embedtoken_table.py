"""Create the EmbedToken table

Revision ID: ceb00d7ff3bd
Revises: 990c0665f3ce
Create Date: 2020-01-27 09:59:36.427138

"""
import sqlalchemy as sa
from alembic import op

from meltano.migrations.utils.dialect_typing import (
    datetime_for_dialect,
    get_dialect_name,
    max_string_length_for_dialect,
)

# revision identifiers, used by Alembic.
revision = "ceb00d7ff3bd"
down_revision = "990c0665f3ce"
branch_labels = None
depends_on = None


def upgrade():
    dialect_name = get_dialect_name()
    datetime_type = datetime_for_dialect(dialect_name)
    max_string_length = max_string_length_for_dialect(dialect_name)

    op.create_table(
        "embed_tokens",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("token", sa.String(64), unique=True),
        sa.Column("resource_id", sa.String(max_string_length), nullable=False),
        sa.Column("created_at", datetime_type),
    )


def downgrade():
    op.drop_table("embed_tokens")
