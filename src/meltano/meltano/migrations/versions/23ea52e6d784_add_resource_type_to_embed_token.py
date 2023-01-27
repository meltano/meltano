"""add resource type to embed token

Revision ID: 23ea52e6d784
Revises: ceb00d7ff3bd
Create Date: 2020-02-12 09:29:31.592426

"""
import sqlalchemy as sa
import sqlalchemy.orm
from alembic import op

from meltano.migrations.utils.dialect_typing import (
    get_dialect_name,
    max_string_length_for_dialect,
)

# revision identifiers, used by Alembic.
revision = "23ea52e6d784"
down_revision = "ceb00d7ff3bd"
branch_labels = None
depends_on = None

Session = sa.orm.sessionmaker()


def upgrade():
    dialect_name = get_dialect_name()
    max_string_length = max_string_length_for_dialect(dialect_name)

    op.add_column(
        "embed_tokens", sa.Column("resource_type", sa.String(max_string_length))
    )

    metadata = sa.MetaData(bind=op.get_bind())
    Embed_Tokens = sa.Table("embed_tokens", metadata, autoload=True)
    op.execute(Embed_Tokens.update().values({"resource_type": "report"}))


def downgrade():
    op.drop_column("embed_tokens", "resource_type")
