"""Create meltano.api tables

Revision ID: 6ef30ab7b8e5
Revises: b4c05e463b53
Create Date: 2019-07-23 16:09:20.192447

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "6ef30ab7b8e5"
down_revision = "b4c05e463b53"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "user",
        sa.Column("id", sa.Integer, nullable=False),
        sa.Column("username", sa.String, nullable=True),
        sa.Column("email", sa.String, nullable=True),
        sa.Column("password", sa.String, nullable=True),
        sa.Column("active", sa.Boolean, nullable=True),
        sa.Column("confirmed_at", sa.DateTime, nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_user_username", "user", ["username"], unique=1)

    op.create_table(
        "role",
        sa.Column("id", sa.Integer, nullable=False),
        sa.Column("name", sa.String(80), nullable=True),
        sa.Column("description", sa.String, nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "roles_users",
        sa.Column("id", sa.Integer, nullable=False),
        sa.Column("user_id", sa.Integer, nullable=True),
        sa.Column("role_id", sa.Integer, nullable=True),
        sa.ForeignKeyConstraint(["role_id"], ["role.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "role_permissions",
        sa.Column("id", sa.Integer, nullable=False),
        sa.Column("role_id", sa.Integer, nullable=True),
        sa.Column("type", sa.String, nullable=True),
        sa.Column("context", sa.String, nullable=True),
        sa.ForeignKeyConstraint(["role_id"], ["role.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "oauth",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("provider_id", sa.String(length=255), nullable=True),
        sa.Column("provider_user_id", sa.String(length=255), nullable=True),
        sa.Column("access_token", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("id_token", sa.String(), nullable=True),
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
