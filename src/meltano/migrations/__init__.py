from __future__ import annotations

from pathlib import Path

import meltano.core.sqlalchemy as types

MIGRATION_DIR = Path(__path__[0])
LOCK_PATH = MIGRATION_DIR.joinpath("db.lock")


# Exposing the types here enable us to create versioned
# version for migrations purpose. For instance, if one
# of these types change in `meltano.core`, we would then
# create a version for this type for all migrations that
# would follow.
GUID = types.GUID
JSONEncodedDict = types.JSONEncodedDict
IntFlag = types.IntFlag
