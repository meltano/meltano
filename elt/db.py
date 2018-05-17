import psycopg2
import os

db_config_keys = [
    "host",
    "port",
    "user",
    "password",
    "database",
]


class DB:
    db_config = {
        'host': os.getenv('PG_ADDRESS', 'localhost'),
        'port': os.getenv('PG_PORT', 5432),
        'user': os.getenv('PG_USERNAME', os.getenv('USER')),
        'password': os.getenv('PG_PASSWORD'),
        'database': os.getenv('PG_DATABASE'),
    }
    connection_class = psycopg2.extensions.connection
    _connection = None

    @classmethod
    def setup(self, open_persistent=False, **kwargs):
        self.db_config.update({k: kwargs[k] for k in db_config_keys if k in kwargs})
        # self._engine = create_engine(self.engine_uri())
        self._connection = self.connect()

    @classmethod
    def connect(self):
        if self._connection is not None:
            return self._connection

        return psycopg2.connect(**self.db_config,
                                connection_factory=self.connection_class)

    @classmethod
    def open(self):
        return db_open()

    @classmethod
    def engine_uri():
       return "postgresql://{username}:{password}@{host}:{port}/{database}".format(**self.db_config)

    @classmethod
    def set_connection_class(self, cls):
        self.connection_class = cls

    @classmethod
    def close(self):
        if self.connection is not None:
            self.connection.close()

class db_open:
    def __enter__(self):
        self.connection = DB.connect()
        return self.connection

    def __exit__(self, ex_type, ex_value, traceback):
        if ex_value is None:
            self.connection.commit()
        else:
            self.connection.rollback()
