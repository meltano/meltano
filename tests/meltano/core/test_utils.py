import pytest

from meltano.core.utils import nest, pop_at_path, set_at_path, setting_env


def test_nest():
    subject = {}

    b = nest(subject, "a.b")
    b["val"] = 1
    assert b == {"val": 1}

    c = nest(subject, "a.b.c")
    c["val"] = 2
    assert b == {"val": 1, "c": {"val": 2}}

    arr = nest(subject, "a.list", value=[])

    VALUE = {"value": 1}
    val = nest(subject, "a.value", value=VALUE)

    assert subject["a"]["b"] is b
    assert subject["a"]["b"]["c"] is c
    assert isinstance(arr, list)
    # make sure it is a copy
    assert val == VALUE and not val is VALUE


def test_pop_at_path():
    subject = {}
    pop_at_path(subject, "a.b.c")
    assert subject == {}

    subject = {"a": {"b": {"c": "value"}}}
    pop_at_path(subject, "a.b.c")
    assert subject == {}

    subject = {"a": {"b.c": "value"}}
    pop_at_path(subject, ["a", "b.c"])
    assert subject == {}

    subject = {"a": {"b": {"c": "value", "d": "value"}, "e": "value"}}
    pop_at_path(subject, "a.b.c")
    assert subject == {"a": {"b": {"d": "value"}, "e": "value"}}

    pop_at_path(subject, "a.b.d")
    assert subject == {"a": {"e": "value"}}

    pop_at_path(subject, "a.e")
    assert subject == {}

def test_setting_env():
    assert setting_env("namespace", "env") == "NAMESPACE_ENV"
    assert setting_env("namespace", "env", env_from_file=True) == "NAMESPACE_ENV_FILE"
    assert setting_env(defined_env="FOO_BAR", env_from_file=False) == "FOO_BAR"
    assert setting_env(defined_env="FOO_BAR", env_from_file=True) == "FOO_BAR_FILE"

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

