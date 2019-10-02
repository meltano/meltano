from pathlib import Path

# the `scripts/alembic_freeze.py` refers to these paths
# we need to make sure they match
MIGRATION_DIR = Path(__path__[0])
LOCK_PATH = MIGRATION_DIR.joinpath("db.lock")


from meltano.api.models.security import Role, RolePermissions
from meltano.core.db import project_engine


def seed(project):
    _, Session = project_engine(project)

    try:
        session = Session()

        if not session.query(Role).filter_by(name="admin").first():
            session.add(
                Role(
                    name="admin",
                    description="Meltano Admin",
                    permissions=[
                        RolePermissions(type="view:design", context="*"),
                        RolePermissions(type="view:reports", context="*"),
                        RolePermissions(type="modify:acl", context="*"),
                    ],
                )
            )

        if not session.query(Role).filter_by(name="regular").first():
            session.merge(Role(name="regular", description="Meltano User"))

        session.commit()
    finally:
        session.close()
