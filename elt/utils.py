import sys
import psycopg2
import logging

from functools import reduce


db_config_keys = [
    "host",
    "port",
    "user",
    "password",
    "database",
]


class db_open:
    def __init__(self, **kwargs):
        self.config = {k: kwargs[k] for k in db_config_keys}

    def __enter__(self, **kwargs):
        self.connection = psycopg2.connect(**self.config)
        return self.connection

    def __exit__(self, type, value, traceback):
        self.connection.close()


# from https://github.com/jonathanj/compose/blob/master/compose.py
def compose(*fs):
    """
    Create a function composition.
    :type *fs: ``iterable`` of 1-argument ``callable``s
    :param *fs: Iterable of 1-argument functions to compose, functions will be
        applied from last to first, in other words ``compose(f, g)(x) ==
        f(g(x))``.
    :return: I{callable} taking 1 argument.
    """
    return reduce(lambda f, g: lambda x: f(g(x)), fs, lambda x: x)


def setup_logging(args):
    logging.basicConfig(stream=sys.stdout,
                        format="[%(levelname)s][%(asctime)s] %(message)s",
                        level=int(args.log_level))
