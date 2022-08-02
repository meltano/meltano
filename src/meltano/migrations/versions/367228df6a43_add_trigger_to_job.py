"""Add 'trigger' to Job

Revision ID: 367228df6a43
Revises: 87d9638f6ac6
Create Date: 2020-02-19 14:40:30.229756

"""
import sqlalchemy as sa
from alembic import op

from meltano.migrations.utils.dialect_typing import (
    get_dialect_name,
    max_string_length_for_dialect,
)

# revision identifiers, used by Alembic.
revision = "367228df6a43"
down_revision = "87d9638f6ac6"
branch_labels = None
depends_on = None


def upgrade():
    dialect_name = get_dialect_name()
    max_string_length = max_string_length_for_dialect(dialect_name)

    op.add_column("job", sa.Column("trigger", sa.String(max_string_length)))


def downgrade():
    op.drop_column("job", "trigger")
