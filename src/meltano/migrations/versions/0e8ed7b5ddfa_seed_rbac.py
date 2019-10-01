"""Seed RBAC

Revision ID: 0e8ed7b5ddfa
Revises: 6ef30ab7b8e5
Create Date: 2019-10-01 12:27:10.660804

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0e8ed7b5ddfa"
down_revision = "6ef30ab7b8e5"
branch_labels = None
depends_on = None


def upgrade():
    Role = sa.table(
        "role",
        sa.Column("id", sa.Integer, nullable=False, primary_key=True),
        sa.Column("name", sa.String(80)),
        sa.Column("description", sa.String, nullable=True),
    )

    RolePermissions = sa.table(
        "role_permissions",
        sa.Column("id", sa.Integer, nullable=False, primary_key=True),
        sa.Column("role_id", sa.Integer),
        sa.Column("type", sa.String),
        sa.Column("context", sa.String, nullable=True),
    )

    op.bulk_insert(
        Role,
        [
            {"id": 0, "name": "admin", "description": "Meltano Admin"},
            {"id": 1, "name": "regular", "description": "Meltano User"},
        ],
    )

    op.bulk_insert(
        RolePermissions,
        [
            {"role_id": 0, "type": "view:design", "context": "*"},
            {"role_id": 0, "type": "view:reports", "context": "*"},
            {"role_id": 0, "type": "modify:acl", "context": "*"},
        ],
    )


def downgrade():
    pass
