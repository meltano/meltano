from __future__ import annotations

from collections import OrderedDict

import pytest  # noqa: F401

from meltano.core.utils import (
    EnvVarMissingBehavior,
    expand_env_vars,
    flatten,
    nest,
    pop_at_path,
    set_at_path,
)


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

    new_b = nest(subject, "a.b", "not_a_dict", force=True)
    assert new_b == "not_a_dict"
    assert subject == {"a": {"b": "not_a_dict", "list": [], "value": {"value": 1}}}

    # make sure existing values aren't cleared when `value=None` and `force=True`
    _ = nest(subject, "a.b", OrderedDict({"d": "d_value"}), force=True)  # noqa: WPS122
    assert subject == {
        "a": {"b": OrderedDict({"d": "d_value"}), "list": [], "value": {"value": 1}}
    }
    similar_b = nest(subject, "a.b", force=True)
    assert similar_b == OrderedDict({"d": "d_value"})
    assert subject == {
        "a": {"b": OrderedDict({"d": "d_value"}), "list": [], "value": {"value": 1}}
    }


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


def test_expand_env_vars():
    env = {"ENV_VAR": "substituted"}
    assert expand_env_vars("${ENV_VAR}_suffix", env) == "substituted_suffix"
    assert expand_env_vars("prefix_${ENV_VAR}", env) == "prefix_substituted"
    assert (
        expand_env_vars("prefix_${ENV_VAR}_suffix", env) == "prefix_substituted_suffix"
    )
    assert expand_env_vars("${ENV_VAR}", env) == "substituted"
    assert expand_env_vars("$ENV_VAR", env) == "substituted"

    assert expand_env_vars("$ENV_VAR", {}) == ""
    assert (
        expand_env_vars("$ENV_VAR", {}, if_missing=EnvVarMissingBehavior.ignore)
        == "${ENV_VAR}"
    )
    assert (
        expand_env_vars("${ENV_VAR}", {}, if_missing=EnvVarMissingBehavior.ignore)
        == "${ENV_VAR}"
    )
    assert (
        expand_env_vars(
            "prefix-${ENV_VAR}-suffix", {}, if_missing=EnvVarMissingBehavior.ignore
        )
        == "prefix-${ENV_VAR}-suffix"
    )


def test_expand_env_vars_nested():
    input_dict = {
        "some_key": 12,
        "some_var": "${ENV_VAR_1}",
        "nested": {
            "${THIS_DOES_NOT_EXPAND}": "another_val",
            "another_layer": {"nested_var": "${ENV_VAR_2}"},
        },
        "another_top_level_var": "${ENV_VAR_2}",
    }
    env = {"ENV_VAR_1": "substituted_1", "ENV_VAR_2": "substituted_2"}

    expected_output = {
        "some_key": 12,
        "some_var": "substituted_1",
        "nested": {
            "${THIS_DOES_NOT_EXPAND}": "another_val",
            "another_layer": {"nested_var": "substituted_2"},
        },
        "another_top_level_var": "substituted_2",
    }

    assert expand_env_vars(input_dict, env) == expected_output
