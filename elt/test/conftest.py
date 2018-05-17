import os
import pytest
import psycopg2
import psycopg2.sql as sql
import logging

from elt.db import DB

class NoCommitConnection(psycopg2.extensions.connection):
    def commit(self):
        print("db.commit() bypass for pytest")


@pytest.fixture(scope='session')
def db_setup(request):
    args = {
        'database': "pytest",
        'host': os.getenv("PG_ADDRESS"),
        'port': os.getenv("PG_PORT", 5432),
        'user': os.getenv("PG_USERNAME"),
        'password': os.getenv("PG_PASSWORD"),
    }
    DB.set_connection_class(NoCommitConnection)
    DB.setup(**args)

@pytest.fixture()
def db(request, db_setup):
    connection = DB.connect()

    def teardown():
        connection.rollback()

    request.addfinalizer(teardown)
    return connection
