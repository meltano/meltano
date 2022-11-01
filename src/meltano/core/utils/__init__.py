"""Defines helpers for the core codebase."""

from __future__ import annotations

import asyncio
import functools
import hashlib
import logging
import math
import os
import re
import sys
import traceback
from collections import OrderedDict
from copy import deepcopy
from datetime import date, datetime, time
from pathlib import Path
from typing import Any, Callable, Iterable, TypeVar, overload

import flatten_dict
from requests.auth import HTTPBasicAuth

from meltano.core.error import MeltanoError

logger = logging.getLogger(__name__)
T = TypeVar("T")

TRUTHY = ("true", "1", "yes", "on")
REGEX_EMAIL = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"


try:
    # asyncio.Task.all_tasks() is fully moved to asyncio.all_tasks() starting
    # with Python 3.9. Also applies to current_task.
    asyncio_all_tasks = asyncio.all_tasks
except AttributeError:
    asyncio_all_tasks = asyncio.Task.all_tasks

if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol


class NotFound(Exception):
    """Occurs when an element is not found."""

    def __init__(self, name, obj_type=None):
        """Create a new exception.

        Args:
            name: the name of the element that is not found
            obj_type: the type of element
        """
        if obj_type is None:
            super().__init__(f"{name} was not found.")
        else:
            super().__init__(f"{obj_type.__name__} '{name}' was not found.")


def click_run_async(func):
    """Small decorator to allow click invoked functions to leverage `asyncio.run` and be declared as async.

    Args:
        func: the function to run async

    Returns:
        A function which runs the given function async
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):  # noqa: WPS430
        return asyncio.run(func(*args, **kwargs))

    return wrapper


# from https://github.com/jonathanj/compose/blob/master/compose.py
def compose(*fs: Callable[[Any], Any]):
    """Create a composition of unary functions.

    Args:
        fs: Unary functions to compose.

    Examples:
        ```python
        compose(f, g)(x) == f(g(x))
        ```

    Returns:
        The composition of the provided unary functions, which itself is a unary function.
    """
    return functools.reduce(lambda f, g: lambda x: f(g(x)), compact(fs), lambda x: x)


# from http://www.dolphmathews.com/2012/09/slugify-string-in-python.html
def slugify(s):
    """Normalize strings into something URL-friendly.

    Args:
        s: the string to slugify

    Returns:
        The string as a slug

    >>> slugify("[Some] _ Article's Title--")
    'some-articles-title'
    """
    # "[Some] _ Article's Title--" -> "[some] _ article's title--"
    s = s.lower()

    # "[some] _ article's_title--" -> "[some]___article's_title__"
    for c in " -./":
        s = s.replace(c, "_")

    # "[some]___article's_title__" -> "some___articles_title__"
    s = re.sub(r"\W", "", s)

    # "some___articles_title__" -> "some   articles title  "
    s = s.replace("_", " ")

    # "some   articles title  " -> "some articles title "
    s = re.sub(r"\s+", " ", s)

    # "some articles title " -> "some articles title"
    s = s.strip()

    # "some articles title" -> "some-articles-title"
    return s.replace(" ", "-")


def get_basic_auth(user, token):
    return HTTPBasicAuth(user, token)


def pop_all(keys, d: dict):
    return {k: d.pop(k) for k in keys}


def get_all(keys, d: dict, default=None):
    return {k: d.get(k, default) for k in keys}


# Taken from https://stackoverflow.com/a/20666342
def merge(src, dest):
    """Merge both given dictionaries together at depth, modifying `dest` in-place.

    Args:
        src: A dictionary to merge into `dest`.
        dest: The dictionary that will be updated with the keys and values from
            `src` at depth.

    Examples:
        >>> a = { 'first' : { 'all_rows' : { 'pass' : 'dog', 'number' : '1' } } }
        >>> b = { 'first' : { 'all_rows' : { 'fail' : 'cat', 'number' : '5' } } }
        >>> merge(b, a) == { 'first' : { 'all_rows' : { 'pass' : 'dog', 'fail' : 'cat', 'number' : '5' } } }
        True

    Returns:
        The `dest` dictionary with the keys and values from `src` merged in.
    """
    for key, value in src.items():
        if isinstance(value, dict):
            # get node or create one
            node = dest.setdefault(key, {})
            merge(value, node)
        else:
            dest[key] = value

    return dest


def nest(d: dict, path: str, value=None, maxsplit=-1, force=False):  # noqa: WPS210
    """Create a hierarchical dictionary path and return the leaf dict.

    Args:
        d: the dictionary to operate on
        path: the dot-delimited path to operate on
        value: the value to set at the given path
        maxsplit: maximum number of splits to split path by
        force: if true, write an empty dict

    Returns:
        The leaf element of the dict

    Examples:
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
    """  # noqa: P102
    if value is None:
        value = {}

    if isinstance(path, str):
        path = path.split(".", maxsplit=maxsplit)

    *initial, tail = path

    # create the list of dicts
    cursor = d
    for key in initial:
        if key not in cursor or (not isinstance(cursor[key], dict) and force):
            cursor[key] = {}

        cursor = cursor[key]

    if tail not in cursor or (
        type(cursor[tail]) is not type(value) and force  # noqa: WPS516
    ):
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


def flatten(d: dict, reducer: str | Callable = "tuple", **kwargs):
    """Flatten a dictionary with `dot` and `env_var` reducers.

    Wrapper arround `flatten_dict.flatten`.

    Args:
        d: the dict to flatten
        reducer: the reducer to flatten with
        **kwargs: additional kwargs to pass to flatten_dict.flatten

    Returns:
        the flattened dict
    """

    def dot_reducer(*xs):
        if xs[0] is None:
            return xs[1]
        return ".".join(xs)

    if reducer == "dot":
        reducer = dot_reducer
    if reducer == "env_var":
        reducer = to_env_var

    return flatten_dict.flatten(d, reducer, **kwargs)


def compact(xs: Iterable) -> Iterable:
    """Remove None values from an iterable.

    Args:
        xs: the iterable to operate on

    Returns:
        The iterable with Nones removed
    """
    return (x for x in xs if x is not None)


def file_has_data(file: Path | str):
    file = Path(file)  # ensure it is a Path object
    return file.exists() and file.stat().st_size > 0


def identity(x):
    return x


def noop(*_args, **_kwargs):
    pass


def map_dict(f: Callable, d: dict):
    yield from ((k, f(v)) for k, v in d.items())


def truthy(val: str) -> bool:
    return str(val).lower() in TRUTHY


@overload
def coerce_datetime(d: None) -> None:
    ...  # noqa: WPS428


@overload
def coerce_datetime(d: datetime) -> datetime:
    ...  # noqa: WPS428


@overload
def coerce_datetime(d: date) -> datetime:
    ...  # noqa: WPS428


def coerce_datetime(d):
    """Add a `time` component to `d` if it is missing.

    Args:
        d: the date or datetime to add the time to

    Returns:
        The resulting datetime
    """
    if d is None:
        return None

    if isinstance(d, datetime):
        return d

    return datetime.combine(d, time())


@overload
def iso8601_datetime(d: None) -> None:
    ...  # noqa: WPS428


@overload
def iso8601_datetime(d: str) -> datetime:
    ...  # noqa: WPS428


def iso8601_datetime(d):
    if d is None:
        return None

    isoformats = [
        "%Y-%m-%dT%H:%M:%SZ",  # noqa: WPS323
        "%Y-%m-%dT%H:%M:%S",  # noqa: WPS323
        "%Y-%m-%d %H:%M:%S",  # noqa: WPS323
        "%Y-%m-%d",  # noqa: WPS323
    ]

    for format_string in isoformats:
        try:
            return coerce_datetime(datetime.strptime(d, format_string))
        except ValueError:
            pass

    raise ValueError(f"{d} is not a valid UTC date.")


class _GetItemProtocol(Protocol):
    def __getitem__(self, key: str) -> str:
        ...  # noqa: WPS428


_G = TypeVar("_G", bound=_GetItemProtocol)


def find_named(xs: Iterable[_G], name: str, obj_type: type = None) -> _G:
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
            directory = os.path.dirname(path)
        else:
            directory = path

        os.makedirs(directory, exist_ok=True)
        return path

    return decorate


def is_email_valid(value: str):
    return re.match(REGEX_EMAIL, value)


def pop_at_path(d, path, default=None):  # noqa: WPS210
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


class EnvironmentVariableNotSetError(MeltanoError):
    """Occurs when a referenced environment variable is not set."""

    def __init__(self, env_var: str):
        """Initialize the error.

        Args:
            env_var: The unset environment variable name.
        """
        self.env_var = env_var

        reason = f"Environment variable '{env_var}' referenced but not set"
        instruction = "Make sure the environment variable is set"
        super().__init__(reason, instruction)


def expand_env_vars(raw_value, env: dict, raise_if_missing: bool = False):
    if isinstance(raw_value, dict):
        return {
            key: expand_env_vars(val, env, raise_if_missing)
            for key, val in raw_value.items()
        }
    elif not isinstance(raw_value, str):
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
                if raise_if_missing:
                    raise EnvironmentVariableNotSetError(var)
            return val
        except KeyError as e:
            if raise_if_missing:
                raise EnvironmentVariableNotSetError(e.args[0])
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
    """Return human-readable file size.

    Args:
        num: the number to convert
        suffix: the suffix to append to the resulting file size

    Returns:
        File size in human-readable format
    """
    magnitude = int(math.floor(math.log(num, 1024)))
    val = num / math.pow(1024, magnitude)

    if magnitude == 0:
        return f"{val:.0f} bytes"
    if magnitude > 7:
        return f"{val:.1f}Yi{suffix}"

    prefix = ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"][magnitude]
    return f"{val:3.1f}{prefix}{suffix}"


def hash_sha256(value: str | bytes) -> str:
    """Get the sha256 hash of a string.

    Args:
        value: the string value to hash.

    Returns:
        The hashed value of the given string.

    Raises:
        ValueError: If we are blindly passed a value that is None.
    """
    if value is None:
        raise ValueError("Cannot hash None.")
    if isinstance(value, str):
        value = value.encode()
    return hashlib.sha256(value).hexdigest()


def format_exception(exception: BaseException) -> str:
    """Get the exception with its traceback in the standard format it would have been printed with.

    Args:
        exception: The exception value to be turned into a string.

    Returns:
        A string that shows the exception object as it would have been printed had it been raised
        and not caught.
    """
    return "".join(
        traceback.format_exception(type(exception), exception, exception.__traceback__)
    )


def safe_hasattr(obj: Any, name: str) -> bool:
    """Safely checks if an object has a given attribute.

    This is a hacky workaround for the fact that `hasattr` is not allowed by WPS.

    Args:
        obj: The object to check.
        name: The name of the attribute to check.

    Returns:
        True if the object has the attribute, False otherwise.
    """
    try:
        getattr(obj, name)
    except AttributeError:
        return False
    return True


def strtobool(val: str) -> bool:
    """Convert a string representation of truth to true (1) or false (0).

    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.

    Case is ignored in string comparisons.

    Re-implemented from distutils.util.strtobool to avoid importing distutils.

    Args:
        val: The string to convert to a boolean.

    Returns:
        True if the string represents a truthy value, False otherwise.

    Raises:
        ValueError: If the string is not a valid representation of a boolean.
    """
    val = val.lower()
    if val in {"y", "yes", "t", "true", "on", "1"}:
        return True
    elif val in {"n", "no", "f", "false", "off", "0"}:
        return False

    raise ValueError(f"invalid truth value {val!r}")


def get_boolean_env_var(env_var: str, default: bool = False) -> bool:
    """Get the value of an environment variable as a boolean.

    Args:
        env_var: The name of the environment variable.
        default: The default value to return if the environment variable is not set.

    Returns:
        The value of the environment variable as a boolean.
    """
    try:
        return strtobool(os.getenv(env_var, str(default)))
    except ValueError:
        return default


def get_no_color_flag() -> bool:
    """Get the value of the NO_COLOR environment variable.

    Returns:
        True if the NO_COLOR environment variable is set to a truthy value, False otherwise.
    """
    return get_boolean_env_var("NO_COLOR")
