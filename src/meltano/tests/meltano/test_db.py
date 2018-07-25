from meltano.common.db import DB


def test_connect():
    db_conn = DB.connect()
    assert(db_conn)
