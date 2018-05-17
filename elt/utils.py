import sys
import psycopg2
import logging

from functools import reduce


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
