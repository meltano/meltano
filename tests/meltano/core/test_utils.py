import hashlib
from traceback import print_exc
from uuid import uuid4

from meltano.core.utils import (
    flatten,
    format_exception,
    hash_sha256,
    nest,
    pop_at_path,
    set_at_path,
)
from meltano.core.utils.singleton import SingletonMeta


def test_nest():
    subject = {}

    one_deep = nest(subject, "a.b")
    one_deep["val"] = 1
    assert one_deep == {"val": 1}

    two_deep = nest(subject, "a.b.c")
    two_deep["val"] = 2
    assert one_deep == {"val": 1, "c": {"val": 2}}

    arr = nest(subject, "a.list", value=[])

    start_value = {"value": 1}
    val = nest(subject, "a.value", value=start_value)

    assert subject["a"]["b"] is one_deep
    assert subject["a"]["b"]["c"] is two_deep
    assert isinstance(arr, list)
    # make sure it is a copy
    assert val == start_value and val is not start_value


def test_pop_at_path():
    subject = {}
    pop_at_path(subject, "a.b.c")
    assert not subject

    subject = {"a": {"b": {"c": "value"}}}
    pop_at_path(subject, "a.b.c")
    assert not subject

    subject = {"a": {"b.c": "value"}}
    pop_at_path(subject, ["a", "b.c"])
    assert not subject

    subject = {"a": {"b": {"c": "value", "d": "value"}, "e": "value"}}
    pop_at_path(subject, "a.b.c")
    assert subject == {"a": {"b": {"d": "value"}, "e": "value"}}

    pop_at_path(subject, "a.b.d")
    assert subject == {"a": {"e": "value"}}

    pop_at_path(subject, "a.e")
    assert not subject


def test_set_at_path():
    subject = {}

    set_at_path(subject, "a.b.c", "value")
    assert subject == {"a": {"b": {"c": "value"}}}

    set_at_path(subject, "a.b.d", "value")
    assert subject == {"a": {"b": {"c": "value", "d": "value"}}}

    set_at_path(subject, "a.b", "value")
    assert subject == {"a": {"b": "value"}}

    set_at_path(subject, "a.b", "newvalue")
    assert subject == {"a": {"b": "newvalue"}}

    set_at_path(subject, "a.b.c", "value")
    assert subject == {"a": {"b": {"c": "value"}}}

    set_at_path(subject, ["a", "d.e"], "value")
    assert subject == {"a": {"b": {"c": "value"}, "d.e": "value"}}


def test_flatten():
    example_config = {"_update": {"orchestrate/dags/meltano.py": False}}
    expected_flat = {"_update.orchestrate/dags/meltano.py": False}
    result = flatten(example_config, "dot")
    assert result == expected_flat


def test_hash_sha256():
    for _ in range(10):
        random_string = str(uuid4())
        assert (
            hash_sha256(random_string)
            == hashlib.sha256(random_string.encode()).hexdigest()
        )


def test_format_exception(capsys):
    def inner_function():
        try:
            assert 2 + 2 == 5
        except AssertionError as ex_1:
            raise ValueError("bad value") from ex_1

    try:
        inner_function()
    except ValueError as ex_2:
        print_exc()
        formatted_exception = format_exception(ex_2)

    _, err = capsys.readouterr()
    assert formatted_exception == err


def test_singleton():
    class SingletonTestClass(metaclass=SingletonMeta):
        """A class whose metaclass is `SingletonMeta`."""

    assert SingletonTestClass() is SingletonTestClass()
