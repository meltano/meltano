import os
import pytest
import psycopg2

from elt.utils import db_open


@pytest.fixture(scope='session')
def db_args(request):
    return {
        'database': "pytest",
        'host': os.getenv("PG_ADDRESS"),
        'port': os.getenv("PG_PORT", 5432),
        'user': os.getenv("PG_USERNAME"),
        'password': os.getenv("PG_PASSWORD"),
    }


@pytest.fixture()
def dbcursor(request, db_args):
    connection = psycopg2.connect(**db_args, )
    transaction = connection.cursor()

    def teardown():
        connection.close()

    request.addfinalizer(teardown)

    return transaction
