from __future__ import annotations

import contextlib
import os
import typing as t
from collections import OrderedDict

import pytest  # noqa: F401

from meltano.core import utils

if t.TYPE_CHECKING:
    from pathlib import Path


def test_nest():
    subject = {}

    one_deep = utils.nest(subject, "a.b")
    one_deep["val"] = 1
    assert one_deep == {"val": 1}

    two_deep = utils.nest(subject, "a.b.c")
    two_deep["val"] = 2
    assert one_deep == {"val": 1, "c": {"val": 2}}

    arr = utils.nest(subject, "a.list", value=[])

    start_value = {"value": 1}
    val = utils.nest(subject, "a.value", value=start_value)

    assert subject["a"]["b"] is one_deep
    assert subject["a"]["b"]["c"] is two_deep
    assert isinstance(arr, list)
    # make sure it is a copy
    assert val == start_value
    assert val is not start_value

    new_b = utils.nest(subject, "a.b", "not_a_dict", force=True)
    assert new_b == "not_a_dict"
    assert subject == {"a": {"b": "not_a_dict", "list": [], "value": {"value": 1}}}

    # make sure existing values aren't cleared when `value=None` and `force=True`
    _ = utils.nest(subject, "a.b", OrderedDict({"d": "d_value"}), force=True)  # noqa: WPS122
    assert subject == {
        "a": {"b": OrderedDict({"d": "d_value"}), "list": [], "value": {"value": 1}},
    }
    similar_b = utils.nest(subject, "a.b", force=True)
    assert similar_b == OrderedDict({"d": "d_value"})
    assert subject == {
        "a": {"b": OrderedDict({"d": "d_value"}), "list": [], "value": {"value": 1}},
    }


def test_pop_at_path():
    subject = {}
    utils.pop_at_path(subject, "a.b.c")
    assert not subject

    subject = {"a": {"b": {"c": "value"}}}
    utils.pop_at_path(subject, "a.b.c")
    assert not subject

    subject = {"a": {"b.c": "value"}}
    utils.pop_at_path(subject, ["a", "b.c"])
    assert not subject

    subject = {"a": {"b": {"c": "value", "d": "value"}, "e": "value"}}
    utils.pop_at_path(subject, "a.b.c")
    assert subject == {"a": {"b": {"d": "value"}, "e": "value"}}

    utils.pop_at_path(subject, "a.b.d")
    assert subject == {"a": {"e": "value"}}

    utils.pop_at_path(subject, "a.e")
    assert not subject


def test_set_at_path():
    subject = {}

    utils.set_at_path(subject, "a.b.c", "value")
    assert subject == {"a": {"b": {"c": "value"}}}

    utils.set_at_path(subject, "a.b.d", "value")
    assert subject == {"a": {"b": {"c": "value", "d": "value"}}}

    utils.set_at_path(subject, "a.b", "value")
    assert subject == {"a": {"b": "value"}}

    utils.set_at_path(subject, "a.b", "newvalue")
    assert subject == {"a": {"b": "newvalue"}}

    utils.set_at_path(subject, "a.b.c", "value")
    assert subject == {"a": {"b": {"c": "value"}}}

    utils.set_at_path(subject, ["a", "d.e"], "value")
    assert subject == {"a": {"b": {"c": "value"}, "d.e": "value"}}


def test_flatten():
    example_config = {"_update": {"orchestrate/dags/meltano.py": False}}
    expected_flat = {"_update.orchestrate/dags/meltano.py": False}
    result = utils.flatten(example_config, "dot")
    assert result == expected_flat


def test_expand_env_vars():
    env = {"ENV_VAR": "substituted"}
    assert utils.expand_env_vars("${ENV_VAR}_suffix", env) == "substituted_suffix"
    assert utils.expand_env_vars("prefix_${ENV_VAR}", env) == "prefix_substituted"
    assert (
        utils.expand_env_vars("prefix_${ENV_VAR}_suffix", env)
        == "prefix_substituted_suffix"
    )
    assert utils.expand_env_vars("${ENV_VAR}", env) == "substituted"
    assert utils.expand_env_vars("$ENV_VAR", env) == "substituted"

    assert utils.expand_env_vars("$ENV_VAR", {}) == ""
    assert (
        utils.expand_env_vars(
            "$ENV_VAR", {}, if_missing=utils.EnvVarMissingBehavior.ignore
        )
        == "${ENV_VAR}"
    )
    assert (
        utils.expand_env_vars(
            "${ENV_VAR}", {}, if_missing=utils.EnvVarMissingBehavior.ignore
        )
        == "${ENV_VAR}"
    )
    assert (
        utils.expand_env_vars(
            "prefix-${ENV_VAR}-suffix",
            {},
            if_missing=utils.EnvVarMissingBehavior.ignore,
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

    assert utils.expand_env_vars(input_dict, env) == expected_output


@pytest.mark.parametrize(
    ("input_array", "env", "expected_output"),
    (
        pytest.param(
            [
                {"some_key": "${ENV_VAR_1}"},
                {"some_key": "${ENV_VAR_2}"},
            ],
            {"ENV_VAR_1": "substituted_1", "ENV_VAR_2": "substituted_2"},
            [
                {"some_key": "substituted_1"},
                {"some_key": "substituted_2"},
            ],
            id="array-of-flat-dicts",
        ),
        pytest.param(
            [
                {
                    "some_key": [
                        {
                            "some_key": "${ENV_VAR_1}",
                            "another_key": "${ENV_VAR_2}",
                        },
                    ],
                },
            ],
            {"ENV_VAR_1": "substituted_1", "ENV_VAR_2": "substituted_2"},
            [
                {
                    "some_key": [
                        {
                            "some_key": "substituted_1",
                            "another_key": "substituted_2",
                        },
                    ],
                },
            ],
            id="array-of-nested-dicts",
        ),
        pytest.param(
            [
                "${ENV_VAR_1}",
                "${ENV_VAR_2}",
            ],
            {"ENV_VAR_1": "substituted_1", "ENV_VAR_2": "substituted_2"},
            [
                "substituted_1",
                "substituted_2",
            ],
            id="flat-array",
        ),
    ),
)
def test_expand_env_vars_array_nested(input_array, env, expected_output):
    assert utils.expand_env_vars(input_array, env) == expected_output


def test_remove_suffix():
    assert utils.remove_suffix("a_string", "ing") == "a_str"
    assert utils.remove_suffix("a_string", "in") == "a_string"
    assert utils.remove_suffix("a_string", "gni") == "a_string"


def test_makedirs_decorator(tmp_path):
    def root(*paths):
        return tmp_path.joinpath(*paths)

    @utils.makedirs
    def hierarchy(*ranks, make_dirs: bool = True):  # noqa: ARG001
        return root(*ranks)

    @utils.makedirs
    def species(genus_name, species_name, make_dirs: bool = True):  # noqa: ARG001
        return hierarchy(genus_name, species_name, make_dirs=make_dirs)

    cat = species("felis", "catus")
    assert cat.exists()

    wolf = species("canis", "lupus", make_dirs=False)
    assert not wolf.exists()


def test_atomic_write(tmp_path: Path):
    """The file should be written atomically."""
    fname = tmp_path.joinpath("ha")

    # Test write
    with utils.atomic_write(fname) as f:
        f.write("hoho")

    assert fname.read_text() == "hoho"
    assert len(os.listdir(tmp_path)) == 1

    # Test overwrite
    with utils.atomic_write(fname) as f:
        f.write("harhar")

    assert fname.read_text() == "harhar"
    assert len(os.listdir(tmp_path)) == 1


def test_atomic_write_teardown(tmp_path: Path):
    """If the context manager raises an exception, nothing should be written."""  # noqa: DAR401
    fname = tmp_path.joinpath("ha")
    with contextlib.suppress(RuntimeError), utils.atomic_write(fname):
        raise RuntimeError("boom")  # noqa: EM101

    assert not os.listdir(tmp_path)


def test_atomic_write_replace_simultaneously_created_file(tmp_path: Path):
    """If the file is created simultaneously, it should be replaced by the first writer."""  # noqa: E501
    fname = tmp_path.joinpath("ha")
    with utils.atomic_write(fname) as f:
        f.write("hoho")
        fname.write_text("harhar")
        assert fname.read_text() == "harhar"

    assert fname.read_text() == "hoho"
    assert len(os.listdir(tmp_path)) == 1
