"""ensure user.login_count default value

Revision ID: 990c0665f3ce
Revises: a3e2b0a4937d
Create Date: 2020-01-15 15:58:25.416129

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import column, table

# revision identifiers, used by Alembic.
revision = "990c0665f3ce"
down_revision = "a3e2b0a4937d"
branch_labels = None
depends_on = None


def upgrade():
    # update the existing Users
    user = table("user", column("login_count", sa.Integer))
    connection = op.get_bind()

    connection.execute(
        user.update().where(user.c.login_count == None).values({"login_count": 0})
    )


def downgrade():
    pass
