import base64
import re
import sys
import logging

from typing import Union
from requests.auth import HTTPBasicAuth
from functools import reduce
from pathlib import Path
from .db import DB


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


# from http://www.dolphmathews.com/2012/09/slugify-string-in-python.html
def slugify(s):
    """
    Simplifies ugly strings into something URL-friendly.
    >>> slugify("[Some] _ Article's Title--")
    'some-articles-title'
    """

    # "[Some] _ Article's Title--"
    # "[some] _ article's title--"
    s = s.lower()

    # "[some] _ article's_title--"
    # "[some]___article's_title__"
    for c in [" ", "-", ".", "/"]:
        s = s.replace(c, "_")

    # "[some]___article's_title__"
    # "some___articles_title__"
    s = re.sub("\W", "", s)

    # "some___articles_title__"
    # "some   articles title  "
    s = s.replace("_", " ")

    # "some   articles title  "
    # "some articles title "
    s = re.sub("\s+", " ", s)

    # "some articles title "
    # "some articles title"
    s = s.strip()

    # "some articles title"
    # "some-articles-title"
    s = s.replace(" ", "-")

    return s


def setup_db(args=None):
    if args is None:
        DB.setup()
    else:
        DB.setup(**vars(args))


def setup_logging(log_level=logging.INFO):
    logging.basicConfig(
        stream=sys.stderr,
        format="[%(threadName)10s][%(levelname)s][%(asctime)s] %(message)s",
        level=log_level,
    )


def get_basic_auth(user, token):
    return HTTPBasicAuth(user, token)


def pop_all(keys, d: dict):
    return dict(map(lambda k: (k, d.pop(k)), keys))


def get_all(keys, d: dict, default=None):
    return dict(map(lambda k: (k, d.get(k, default)), keys))


def nest(d: dict, path: str, value={}):
    """
    Create a hierarchical dictionary path and return the leaf dict.

    >>> d = dict()
    >>> test = nest(d, "foo.bar.test")
    >>> test
    {}
    >>> d
    {'foo': {'bar': {'test': {}}}}
    >>> test["a"] = 1
    >>> d
    {'foo': {'bar': {'test': {'a': 1}}}}
    >>> alist = nest(d, "foo.bar.list", value=[])
    >>> alist.append("works")
    >>> d
    {'foo': {'bar': {'test': {'a': 1}}, 'list': ["works"]}}

    """
    cursor = d

    # create the list of dicts
    for key in path.split("."):
        if key not in cursor:
            cursor[key] = value
        cursor = cursor[key]

    return cursor


def file_has_data(file: Union[Path, str]):
    file = Path(file)  # ensure it is a Path object
    return file.exists() and file.stat().st_size > 0


def decode_file_path_from_id(unique_id):
    return base64.b32decode(unique_id).decode("utf-8")


def encode_id_from_file_path(file_path):
    return base64.b32encode(bytes(file_path, "utf-8")).decode("utf-8")


def noop(*_args, **_kwargs):
    pass
