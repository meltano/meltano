import pytest  # noqa: F401

from meltano.core.utils import flatten, nest, pop_at_path, set_at_path


def test_nest():
    subject = {}

    one_deep = nest(subject, "a.b")
    one_deep["val"] = 1
    assert one_deep == {"val": 1}

    two_deep = nest(subject, "a.b.c")
    two_deep["val"] = 2
    assert two_deep == {"val": 1, "c": {"val": 2}}

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
