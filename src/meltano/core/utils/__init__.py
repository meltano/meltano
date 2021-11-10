"""Defines helpers for the core codebase."""
import asyncio
import base64
import functools
import logging
import math
import os
import re
import sys
from collections import OrderedDict
from contextlib import suppress
from copy import deepcopy
from datetime import date, datetime, time
from pathlib import Path
from typing import Callable, Dict, Iterable, Optional, Union

import flatten_dict
from requests.auth import HTTPBasicAuth

logger = logging.getLogger(__name__)

TRUTHY = ("true", "1", "yes", "on")
REGEX_EMAIL = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"


try:
    # asyncio.Task.all_tasks() is fully moved to asyncio.all_tasks() starting
    # with Python 3.9. Also applies to current_task.
    asyncio_all_tasks = asyncio.all_tasks
except AttributeError:
    asyncio_all_tasks = asyncio.Task.all_tasks


class NotFound(Exception):
    """Occurs when an element is not found."""

    def __init__(self, name, obj_type=None):
        """Create a new exception."""
        if obj_type is None:
            super().__init__(f"{name} was not found.")
        else:
            super().__init__(f"{obj_type.__name__} '{name}' was not found.")


def run_async(coro):
    """Run coroutine and handle event loop and cleanup."""
    # Taken from https://stackoverflow.com/a/58532304
    # and inspired by Python 3.7's `asyncio.run`
    future = asyncio.ensure_future(coro)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(future)
    try:
        if future.exception():
            raise future.exception()

        return future.result()
    except asyncio.CancelledError:
        pass
    finally:
        all_tasks = asyncio.gather(*asyncio_all_tasks(loop), return_exceptions=True)
        all_tasks.cancel()
        with suppress(asyncio.CancelledError):
            loop.run_until_complete(all_tasks)
        loop.run_until_complete(loop.shutdown_asyncgens())


def click_run_async(func):
    """Small decorator to allow click invoked functions to leverage run_async and be declared as async."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):  # noqa: WPS430
        return run_async(func(*args, **kwargs))

    return wrapper


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
    return functools.reduce(lambda f, g: lambda x: f(g(x)), compact(fs), lambda x: x)


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
    s = re.sub(r"\W", "", s)

    # "some___articles_title__"
    # "some   articles title  "
    s = s.replace("_", " ")

    # "some   articles title  "
    # "some articles title "
    s = re.sub(r"\s+", " ", s)

    # "some articles title "
    # "some articles title"
    s = s.strip()

    # "some articles title"
    # "some-articles-title"
    s = s.replace(" ", "-")

    return s


def get_basic_auth(user, token):
    return HTTPBasicAuth(user, token)


def pop_all(keys, d: dict):
    return dict(map(lambda k: (k, d.pop(k)), keys))


def get_all(keys, d: dict, default=None):
    return dict(map(lambda k: (k, d.get(k, default)), keys))


# Taken from https://stackoverflow.com/a/20666342
def merge(source, destination):
    """
    >>> a = { 'first' : { 'all_rows' : { 'pass' : 'dog', 'number' : '1' } } }
    >>> b = { 'first' : { 'all_rows' : { 'fail' : 'cat', 'number' : '5' } } }
    >>> merge(b, a) == { 'first' : { 'all_rows' : { 'pass' : 'dog', 'fail' : 'cat', 'number' : '5' } } }
    True
    """
    for key, value in source.items():
        if isinstance(value, dict):
            # get node or create one
            node = destination.setdefault(key, {})
            merge(value, node)
        else:
            destination[key] = value

    return destination


def nest(d: dict, path: str, value={}, maxsplit=-1, force=False):
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
    if isinstance(path, str):
        path = path.split(".", maxsplit=maxsplit)

    *initial, tail = path

    # create the list of dicts
    cursor = d
    for key in initial:
        if key not in cursor or (not isinstance(cursor[key], dict) and force):
            cursor[key] = {}

        cursor = cursor[key]

    if not tail in cursor or (type(cursor[tail]) is not type(value) and force):
        # We need to copy the value to make sure
        # the `value` parameter is not mutated.
        cursor[tail] = deepcopy(value)

    return cursor[tail]


def nest_object(flat_object):
    obj = {}
    for key, value in flat_object.items():
        nest(obj, key, value)
    return obj


def to_env_var(*xs):
    xs = [re.sub("[^A-Za-z0-9]", "_", x).upper() for x in xs if x]
    return "_".join(xs)


def flatten(d: Dict, reducer: Union[str, Callable] = "tuple", **kwargs):
    """Wrapper arround `flatten_dict.flatten` that adds `dot` and `env_var` reducers."""

    def dot_reducer(*xs):
        if xs[0] is None:
            return xs[1]
        else:
            return ".".join(xs)

    if reducer == "dot":
        reducer = dot_reducer
    if reducer == "env_var":
        reducer = to_env_var

    return flatten_dict.flatten(d, reducer, **kwargs)


def compact(xs: Iterable) -> Iterable:
    return (x for x in xs if x is not None)


def file_has_data(file: Union[Path, str]):
    file = Path(file)  # ensure it is a Path object
    return file.exists() and file.stat().st_size > 0


def identity(x):
    return x


def noop(*_args, **_kwargs):
    pass


def map_dict(f: Callable, d: Dict):
    for k, v in d.items():
        yield k, f(v)


def truthy(val: str) -> bool:
    return str(val).lower() in TRUTHY


def coerce_datetime(d: Union[date, datetime]) -> Optional[datetime]:
    """Adds a `time` component to `d` if such a component is missing."""
    if d is None:
        return None

    if isinstance(d, datetime):
        return d

    return datetime.combine(d, time())


def iso8601_datetime(d: str) -> Optional[datetime]:
    if d is None:
        return None

    isoformats = [
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ]

    for format in isoformats:
        try:
            return coerce_datetime(datetime.strptime(d, format))
        except ValueError:
            pass

    raise ValueError(f"{d} is not a valid UTC date.")


def find_named(xs: Iterable[dict], name: str, obj_type: type = None) -> dict:
    """Find an object by its 'name' key.

    Args:
        xs: Some iterable of objects against which that name should be matched.
        name: Used to match against the input objects.
        obj_type: Object type used for generating the exception message.

    Returns:
        The first item matched, if any. Otherwise raises an exception.

    Raises:
        NotFound: If an object with the given name was not found.
    """
    try:
        return next(x for x in xs if x["name"] == name)
    except StopIteration as stop:
        raise NotFound(name, obj_type) from stop


def makedirs(func):
    @functools.wraps(func)
    def decorate(*args, **kwargs):

        enabled = kwargs.get("make_dirs", True)

        path = func(*args, **kwargs)

        if not enabled:
            return path

        # if there is an extension, only create the base dir
        _, ext = os.path.splitext(path)
        if ext:
            dir = os.path.dirname(path)
        else:
            dir = path

        os.makedirs(dir, exist_ok=True)
        return path

    return decorate


def is_email_valid(value: str):
    return re.match(REGEX_EMAIL, value)


def pop_at_path(d, path, default=None):
    if isinstance(path, str):
        path = path.split(".")

    *initial, tail = path

    cursor = d
    cursors = []
    for key in initial:
        cursors.append((cursor, key))

        try:
            cursor = cursor[key]
        except KeyError:
            return default

    popped = cursor.pop(tail, default)

    for (cursor, key) in reversed(cursors):
        if len(cursor[key]) == 0:
            cursor.pop(key, None)

    return popped


def set_at_path(d, path, value):
    if isinstance(path, str):
        path = path.split(".")

    *initial, tail = path

    final = nest(d, initial, force=True) if initial else d
    final[tail] = value


def expand_env_vars(raw_value, env: Dict):
    if not isinstance(raw_value, str):
        return raw_value

    # find viable substitutions
    var_matcher = re.compile(
        r"""
        \$  # starts with a '$'
        (?:
            {(\w+)} # ${VAR}
            |
            ([A-Z][A-Z0-9_]*) # $VAR
        )
        """,
        re.VERBOSE,
    )

    def subst(match) -> str:
        try:
            # the variable can be in either group
            var = next(var for var in match.groups() if var)
            val = str(env[var])

            if not val:
                logger.debug(f"Variable '${var}' is empty.")

            return val
        except KeyError as e:
            logger.debug(f"Variable '${var}' is missing from the environment.")
            return None

    fullmatch = re.fullmatch(var_matcher, raw_value)
    if fullmatch:
        # If the entire value is an env var reference, return None if it isn't set
        return subst(fullmatch)

    return re.sub(var_matcher, subst, raw_value)


def uniques_in(original):
    return list(OrderedDict.fromkeys(original))


# https://gist.github.com/cbwar/d2dfbc19b140bd599daccbe0fe925597#gistcomment-2845059
def human_size(num, suffix="B"):
    """Return human-readable file size."""
    magnitude = int(math.floor(math.log(num, 1024)))
    val = num / math.pow(1024, magnitude)

    if magnitude == 0:
        return f"{val:.0f} bytes"
    if magnitude > 7:
        return f"{val:.1f}Yi{suffix}"

    prefix = ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"][magnitude]
    return f"{val:3.1f}{prefix}{suffix}"
