"""add_login_audit_columns

Revision ID: a3e2b0a4937d
Revises: 53e97221d99f
Create Date: 2020-01-09 14:23:56.880364

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a3e2b0a4937d"
down_revision = "53e97221d99f"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("user", sa.Column("last_login_at", sa.DateTime(), nullable=True))
    op.add_column("user", sa.Column("login_count", sa.Integer, default=0))


def downgrade():
    op.drop_column("user", "last_login_at")
    op.drop_column("user", "login_count")
