"""Create dedicated job_state table

Revision ID: f4c225a9492f
Revises: 5b43800443d1
Create Date: 2022-09-02 09:44:05.581824

"""
from __future__ import annotations

from alembic import op

# revision identifiers, used by Alembic.
revision = "f4c225a9492f"
down_revision = "5b43800443d1"
branch_labels = None
depends_on = None


def upgrade():
    # Create state table
    pass


def downgrade():
    # Remove job_state table
    # Job run history is still maintained, so no need to copy
    op.drop_table("state")
