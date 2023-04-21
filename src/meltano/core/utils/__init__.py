"""Defines helpers for the core codebase."""


from __future__ import annotations

import asyncio
import collections
import functools
import hashlib
import logging
import math
import os
import platform
import re
import sys
import traceback
import typing as t
import unicodedata
from contextlib import suppress
from copy import copy, deepcopy
from datetime import date, datetime, time
from enum import IntEnum
from functools import reduce
from operator import setitem
from pathlib import Path

import flatten_dict
from requests.auth import HTTPBasicAuth

if sys.version_info >= (3, 8):
    from typing import Protocol, runtime_checkable
else:
    from typing_extensions import Protocol, runtime_checkable

from meltano.core.error import MeltanoError

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
    """An element is not found."""

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
    """Run decorated Click commands with `asyncio.run`.

    Args:
        func: The function to run asynchronously.

    Returns:
        A function which runs the given function asynchronously.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):  # noqa: WPS430
        return asyncio.run(func(*args, **kwargs))

    return wrapper


# from https://github.com/jonathanj/compose/blob/master/compose.py
def compose(*fs: t.Callable[[t.Any], t.Any]):
    """Create a composition of unary functions.

    Args:
        fs: Unary functions to compose.

    Examples:
        ```python
        compose(f, g)(x) == f(g(x))
        ```

    Returns:
        The composition of the provided unary functions, which itself is a
        unary function.
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
        >>> a = {'f' :{'all_rows': {'pass': 'dog', 'n': '1'}}}
        >>> b = {'f' :{'all_rows': {'fail': 'cat', 'n': '5'}}}
        >>> merge(b, a) == {'f': {'all_rows': {'pass': 'dog', 'fail': 'cat', 'n': '5'}}}
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


def are_similar_types(left, right):
    return isinstance(left, type(right)) or isinstance(right, type(left))


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
        (not are_similar_types(cursor[tail], value)) and force  # noqa: WPS516
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


def to_env_var(*xs: str) -> str:
    """Convert a list of strings to an environment variable name.

    Args:
        *xs: the strings to convert

    Returns:
        The environment variable name.

    Examples:
        >>> to_env_var("foo", "bar")
        'FOO_BAR'
        >>> to_env_var("foo", "bar", "baz")
        'FOO_BAR_BAZ'
        >>> to_env_var("foo.bar")
        'FOO_BAR'
    """
    return "_".join(re.sub("[^A-Za-z0-9]", "_", x).upper() for x in xs if x)


def flatten(d: dict, reducer: str | t.Callable = "tuple", **kwargs):
    """Flatten a dictionary with `dot` and `env_var` reducers.

    Wrapper arround `flatten_dict.flatten`.

    Args:
        d: the dict to flatten
        reducer: the reducer to flatten with
        **kwargs: additional kwargs to pass to flatten_dict.flatten

    Returns:
        the flattened dict
    """
    if reducer == "dot":
        reducer = lambda *xs: xs[1] if xs[0] is None else ".".join(xs)  # noqa: E731
    if reducer == "env_var":
        reducer = to_env_var

    return flatten_dict.flatten(d, reducer, **kwargs)


def compact(xs: t.Iterable) -> t.Iterable:
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


def truthy(val: str) -> bool:
    return str(val).lower() in TRUTHY


@t.overload
def coerce_datetime(d: None) -> None:
    ...  # noqa: WPS428


@t.overload
def coerce_datetime(d: datetime) -> datetime:
    ...  # noqa: WPS428


@t.overload
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

    return d if isinstance(d, datetime) else datetime.combine(d, time())


@t.overload
def iso8601_datetime(d: None) -> None:
    ...  # noqa: WPS428


@t.overload
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
        with suppress(ValueError):
            return coerce_datetime(datetime.strptime(d, format_string))
    raise ValueError(f"{d} is not a valid UTC date.")


class _GetItemProtocol(Protocol):
    def __getitem__(self, key: str) -> str:
        ...  # noqa: WPS428


_G = t.TypeVar("_G", bound=_GetItemProtocol)


def find_named(xs: t.Iterable[_G], name: str, obj_type: type | None = None) -> _G:
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
        enabled = kwargs.pop("make_dirs", True)

        path = func(*args, **kwargs)

        if not enabled:
            return path

        # if there is an extension, only create the base dir
        _, ext = os.path.splitext(path)
        os.makedirs(os.path.dirname(path) if ext else path, exist_ok=True)
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

    for cursor, key in reversed(cursors):
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
    """A referenced environment variable is not set."""

    def __init__(self, env_var: str):
        """Initialize the error.

        Args:
            env_var: The unset environment variable name.
        """
        self.env_var = env_var

        reason = f"Environment variable '{env_var}' referenced but not set"
        instruction = "Make sure the environment variable is set"
        super().__init__(reason, instruction)


ENV_VAR_PATTERN = re.compile(
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

Expandable = t.TypeVar("Expandable", str, t.Mapping[str, "Expandable"])


class EnvVarMissingBehavior(IntEnum):
    """The behavior that should be employed when expanding a missing env var."""

    use_empty_str = 0
    raise_exception = 1
    ignore = 2


def expand_env_vars(
    raw_value: Expandable,
    env: t.Mapping[str, str],
    *,
    if_missing: EnvVarMissingBehavior = EnvVarMissingBehavior.use_empty_str,
    flat: bool = False,
) -> Expandable:
    """Expand/interpolate provided env vars into a string or env mapping.

    By default, attempting to expand an env var which is not defined in the
    provided env dict will result in it being replaced with the empty string.

    Args:
        raw_value: A string or env mapping in which env vars will be expanded.
        env: The env vars to use for the expansion of `raw_value`.
        if_missing: The behavior to employ if an env var in `raw_value` is not
            set in `env`.
        flat: Whether the `raw_value` has a flat structure. Ignored if
            `raw_value` is not a mapping. Otherwise it controls whether this
            function will process nested levels within `raw_value`. Defaults to
            `False` for backwards-compatibility. Setting to `True` is recommend
            for performance, safety, and cleanliness reasons.

    Raises:
        EnvironmentVariableNotSetError: Attempted to expand an env var that was not
            defined in the provided env dict, and `if_missing` was
            `EnvVarMissingBehavior.raise_exception`.

    Returns:
        The string or env dict with env vars expanded. For backwards
        compatibility, if anything other than an `str` or mapping is provided
        as the `raw_value`, it is returned unchanged.
    """  # noqa: DAR402
    if_missing = EnvVarMissingBehavior(if_missing)

    if not isinstance(raw_value, (str, t.Mapping)):
        return raw_value

    def replacer(match: re.Match) -> str:
        # The variable can be in either group
        var = next(var for var in match.groups() if var)
        try:
            val = str(env[var])
        except KeyError as ex:
            logger.debug(
                f"Variable '${var}' is not set in the provided env dictionary.",
            )
            if if_missing == EnvVarMissingBehavior.raise_exception:
                raise EnvironmentVariableNotSetError(var) from ex
            elif if_missing == EnvVarMissingBehavior.ignore:
                return f"${{{var}}}"
            return ""
        if not val:
            logger.debug(f"Variable '${var}' is empty.")
        return val

    return _expand_env_vars(raw_value, replacer, flat)


# Separate inner-function for `expand_env_vars` for performance reasons. Like
# this the `replacer` function closure only needs to be created once when
# `raw_value` is a dict, as opposed to once per key-value pair.
def _expand_env_vars(
    raw_value: Expandable,
    replacer: t.Callable[[re.Match], str],
    flat: bool,
) -> Expandable:
    if isinstance(raw_value, t.Mapping):
        if flat:
            return {k: ENV_VAR_PATTERN.sub(replacer, v) for k, v in raw_value.items()}
        return {
            k: _expand_env_vars(v, replacer, flat)
            if isinstance(v, (str, t.Mapping))
            else v
            for k, v in raw_value.items()
        }
    return ENV_VAR_PATTERN.sub(replacer, raw_value)


T = t.TypeVar("T")


def uniques_in(original: t.Sequence[T]) -> list[T]:
    """Get unique elements from an iterable while preserving order.

    Args:
        original: A sequence from which only the unique values will be returned.

    Returns:
        A list of unique values from the provided sequence in the order they appeared.
    """
    return list(collections.OrderedDict.fromkeys(original))


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
    """Get the exception with its traceback formatted as it would have been printed.

    Args:
        exception: The exception value to be turned into a string.

    Returns:
        A string that shows the exception object as it would have been printed
        had it been raised and not caught.
    """
    return "".join(
        traceback.format_exception(type(exception), exception, exception.__traceback__),
    )


def safe_hasattr(obj: t.Any, name: str) -> bool:
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
    """Get the truth value of the `NO_COLOR` environment variable.

    Returns:
        Whether the `NO_COLOR` environment variable is set to a truthy value.
    """
    return get_boolean_env_var("NO_COLOR")


class MergeStrategy(t.NamedTuple):
    """Strategy to be used when merging instances of a type.

    The first value of this tuple, `applicable_for_instance_of`, is a type or
    tuple of types for which the behavior (see below) should apply. An
    `isinstance` check is performed on each yet-unprocessed value using these
    types.

    The second value of this tuple, `behavior`, is a function which is provided
    the dictionary being merged into, the key into that dictionary that is
    being affected, the value for which
    `isinstance(value, applicable_for_instance_of)` was true, and the tuple of
    merge strategies in use (provided to enable recursion by calling
    `deep_merge`).

    If the behavior function returns `NotImplemented` then it will be skipped,
    and later items in the tuple of merge strategies will be tried instead.
    """

    applicable_for_instance_of: type | tuple[type, ...]
    behavior: t.Callable[
        [t.MutableMapping[str, t.Any], str, t.Any, tuple[MergeStrategy, ...] | None],
        None,
    ]


@runtime_checkable
class Extendable(Protocol):
    """A type protocol for types which have an `extend` method."""

    def extend(self, x: t.Any) -> None:
        """Extend the current instance with another value.

        Args:
            x: A value to extend this instance with.
        """


default_deep_merge_strategies: tuple[MergeStrategy, ...] = (
    MergeStrategy(
        t.Mapping,
        lambda x, k, v, s: setitem(
            x,
            k,
            _deep_merge(x.setdefault(k, v.__class__()), v, strategies=s),
        ),
    ),
    MergeStrategy(
        Extendable,
        lambda x, k, v, _: x.setdefault(k, v.__class__()).extend(v),
    ),
    MergeStrategy(object, lambda x, k, v, _: setitem(x, k, v)),
)


TMapping = t.TypeVar("TMapping", bound=t.Mapping)


def deep_merge(
    *data: TMapping,
    strategies: tuple[MergeStrategy, ...] = default_deep_merge_strategies,
) -> TMapping:
    """Merge multiple mappings at depth.

    Args:
        data: The mappings.
        strategies: A tuple of merge strategies, which are pairs of
            `(applicable type, behavior function)`. Each type will be tried in
            order until one passes an `isinstance` check for the value being
            merged, then the associated behavior function will be called to
            perform the merge. Refer to the documentation for `MergeStrategy`
            for more details. By default, the merge strategies will merge
            mappings with a recursive deep merge, objects with an `extend`
            method (e.g. `lists`) using the `extend` method, and all other
            objects with `setitem(dict_being_merged_into, key, value)`.

    Returns:
        The merged mapping.
    """
    return reduce(lambda a, b: _deep_merge(a, b, strategies), data)


def _deep_merge(a, b, strategies):
    base: TMapping = copy(a)
    for key, value in b.items():
        for applicable_types, behavior in strategies:
            if (
                isinstance(value, applicable_types)
                and behavior(base, key, value, strategies) is not NotImplemented
            ):
                break
    return base


def remove_suffix(string: str, suffix: str) -> str:
    """Remove suffix from string.

    Compatible with Python 3.8

    Args:
        string: the string to remove suffix from
        suffix: the suffix to remove

    Returns:
        The changed string
    """
    if sys.version_info >= (3, 9):
        return string.removesuffix(suffix)
    elif string.endswith(suffix):
        return string[: -len(suffix)]
    return string


_filename_restriction_pattern = re.compile(r"[^\w.-]")
_reserved_windows_filenames = frozenset(
    (
        "AUX",
        "COM1",
        "COM2",
        "COM3",
        "COM4",
        "CON",
        "LPT1",
        "LPT2",
        "LPT3",
        "NUL",
        "PRN",
    ),
)
_sanitize_filename_transformations = (
    # Normalize unicode data in the string:
    lambda x: unicodedata.normalize("NFKD", x),
    # Limit the string to ASCII characters:
    lambda x: x.encode("ascii", "ignore").decode("ascii"),
    # Replace each path separator with a space:
    lambda x: x.replace(os.path.sep, " "),
    lambda x: x.replace(os.path.altsep, " ") if os.path.altsep else x,
    # Replace each whitespace character with an underscore:
    lambda x: "_".join(x.split()),
    # Limit the string to alphanumeric characters, underscores, hyphens, and dots:
    lambda x: _filename_restriction_pattern.sub("", x),
    # Remove Remove illegal character combination `._` from front and back:
    lambda x: x.strip("._"),
    # Add a leading `_` if necessary to avoid conflict with reserved Windows filenames:
    lambda x: f"_{x}"
    if platform.system() == "Windows"
    and x
    and x.split(".")[0].upper() in _reserved_windows_filenames
    else x,
)


def sanitize_filename(filename: str) -> str:
    """Sanitize `filename` in a consistent cross-platform way.

    Args:
        filename: The name of the file to sanitize - not the full path.

    Returns:
        The provided filename after a series of santitization steps. It will
        only contain ASCII characters. If necessary on Windows, the filename
        will be prefixed by an underscore to avoid conflict with reserved
        Windows file names.
    """
    return functools.reduce(
        lambda x, y: y(x),  # noqa: WPS442
        _sanitize_filename_transformations,
        filename,
    )
