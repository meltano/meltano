from __future__ import annotations

import pytest

from meltano.api.models import db as _db


@pytest.fixture(autouse=True)
def session(app, connection):
    # attach it to our test app
    _db.app = app

    # create a new session upon our auto-rollback
    # connection
    _db.session = _db.create_scoped_session(options={"bind": connection, "binds": {}})

    try:
        yield _db.session
    finally:
        _db.session.remove()
