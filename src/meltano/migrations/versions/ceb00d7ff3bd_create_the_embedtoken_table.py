"""Create the EmbedToken table

Revision ID: ceb00d7ff3bd
Revises: 990c0665f3ce
Create Date: 2020-01-27 09:59:36.427138

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "ceb00d7ff3bd"
down_revision = "990c0665f3ce"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "embed_tokens",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("token", sa.String(64), unique=True),
        sa.Column("resource_id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime),
    )


def downgrade():
    op.drop_table("embed_tokens")
