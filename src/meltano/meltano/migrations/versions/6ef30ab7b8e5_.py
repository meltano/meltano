"""Create meltano.api tables

Revision ID: 6ef30ab7b8e5
Revises: b4c05e463b53
Create Date: 2019-07-23 16:09:20.192447

"""
import sqlalchemy as sa
from alembic import op

from meltano.migrations.utils.dialect_typing import (
    datetime_for_dialect,
    get_dialect_name,
    max_string_length_for_dialect,
)

# revision identifiers, used by Alembic.
revision = "6ef30ab7b8e5"
down_revision = "b4c05e463b53"
branch_labels = None
depends_on = None


def upgrade():
    dialect_name = get_dialect_name()
    datetime_type = datetime_for_dialect(dialect_name)
    max_string_length = max_string_length_for_dialect(dialect_name)

    op.create_table(
        "user",
        sa.Column("id", sa.Integer, nullable=False),
        sa.Column("username", sa.String(255)),
        sa.Column("email", sa.String(255)),
        sa.Column("password", sa.String(255)),
        sa.Column("active", sa.Boolean),
        sa.Column("confirmed_at", datetime_type, nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_user_username", "user", ["username"], unique=1)

    op.create_table(
        "role",
        sa.Column("id", sa.Integer, nullable=False),
        sa.Column("name", sa.String(80)),
        sa.Column("description", sa.String(255), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "roles_users",
        sa.Column("id", sa.Integer, nullable=False),
        sa.Column("user_id", sa.Integer),
        sa.Column("role_id", sa.Integer),
        sa.ForeignKeyConstraint(["role_id"], ["role.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "role_permissions",
        sa.Column("id", sa.Integer, nullable=False),
        sa.Column("role_id", sa.Integer),
        sa.Column("type", sa.String(max_string_length)),
        sa.Column("context", sa.String(max_string_length), nullable=True),
        sa.ForeignKeyConstraint(["role_id"], ["role.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "oauth",
        sa.Column("id", sa.Integer, nullable=False),
        sa.Column("user_id", sa.Integer),
        sa.Column("provider_id", sa.String(255)),
        sa.Column("provider_user_id", sa.Integer, nullable=True),
        sa.Column("access_token", sa.String(255)),
        sa.Column("created_at", datetime_type, nullable=True),
        sa.Column("id_token", sa.String(max_string_length)),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("roles_users")
    op.drop_table("role_permissions")
    op.drop_table("role")
    op.drop_index("ix_user_username", table_name="user")
    op.drop_table("user")
    op.drop_table("oauth")
