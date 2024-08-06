"""THIS IS A NO-OP.

IT EXISTS ONLY TO PREVENT USERS WHO APPLIED THIS MIGRATION
FROM ENDING UP WITH AN ORPHANED alembic_version IN THEIR DB.

Revision ID: f4c225a9492f
Revises: 5b43800443d1
Create Date: 2022-09-02 09:44:05.581824

"""

from __future__ import annotations

# revision identifiers, used by Alembic.
revision = "f4c225a9492f"
down_revision = "5b43800443d1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
