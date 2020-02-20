"""Add 'trigger' to Job

Revision ID: 367228df6a43
Revises: 87d9638f6ac6
Create Date: 2020-02-19 14:40:30.229756

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "367228df6a43"
down_revision = "87d9638f6ac6"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("job", sa.Column("trigger", sa.String()))


def downgrade():
    op.drop_column("job", "trigger")
