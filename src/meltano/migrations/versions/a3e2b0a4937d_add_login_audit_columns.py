"""add_login_audit_columns

Revision ID: a3e2b0a4937d
Revises: 53e97221d99f
Create Date: 2020-01-09 14:23:56.880364

"""  # noqa: INP001, I002, D415
import sqlalchemy as sa
from alembic import op

from meltano.migrations.utils.dialect_typing import (
    datetime_for_dialect,
    get_dialect_name,
)

# revision identifiers, used by Alembic.
revision = "a3e2b0a4937d"
down_revision = "53e97221d99f"
branch_labels = None
depends_on = None


def upgrade():  # noqa: ANN201
    dialect_name = get_dialect_name()
    datetime_type = datetime_for_dialect(dialect_name)

    op.add_column("user", sa.Column("last_login_at", datetime_type, nullable=True))
    op.add_column("user", sa.Column("login_count", sa.Integer, default=0))


def downgrade():  # noqa: ANN201
    op.drop_column("user", "last_login_at")
    op.drop_column("user", "login_count")
