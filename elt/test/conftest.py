import os
import pytest
import psycopg2
import psycopg2.sql as sql

from elt.db import DB

class NoCommitConnection(psycopg2.extensions.connection):
    def commit(self):
        pass


@pytest.fixture(scope='session')
def db_args(request):
    args = {
        'database': "pytest",
        'host': os.getenv("PG_ADDRESS"),
        'port': os.getenv("PG_PORT", 5432),
        'user': os.getenv("PG_USERNAME"),
        'password': os.getenv("PG_PASSWORD"),
    }
    DB.register(**args)
    DB.set_connection_class(NoCommitConnection)

@pytest.fixture()
def db(request, db_args):
    connection = DB.connect()

    def teardown():
        connection.close()

    request.addfinalizer(teardown)
    return connection
