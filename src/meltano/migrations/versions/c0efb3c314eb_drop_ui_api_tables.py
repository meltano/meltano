"""Drop UI/API tables that are no longer used.

These tables (user, role, roles_users, role_permissions, oauth, embed_tokens,
subscriptions) were only used by the Meltano UI/API which has been removed.

Revision ID: c0efb3c314eb
Revises: 6828cc5b1a4f
Create Date: 2025-12-15 12:00:00.000000

"""

from __future__ import annotations

from alembic import op

# revision identifiers, used by Alembic.
revision = "c0efb3c314eb"
down_revision = "6828cc5b1a4f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Drop redundant UI/API tables if they exist."""
    # Drop tables in correct order (respecting foreign key constraints)
    # Drop child tables first, then parent tables
    op.drop_table("roles_users", if_exists=True)
    op.drop_table("role_permissions", if_exists=True)
    op.drop_table("oauth", if_exists=True)
    op.drop_table("embed_tokens", if_exists=True)
    op.drop_table("subscriptions", if_exists=True)
    op.drop_table("role", if_exists=True)
    op.drop_index("ix_user_username", table_name="user", if_exists=True)
    op.drop_table("user", if_exists=True)


def downgrade() -> None:
    """No-op.

    We're not interested in recreating these tables.
    """
