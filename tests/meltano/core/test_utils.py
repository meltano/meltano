from __future__ import annotations

import pytest

from meltano.core.utils import (
    EnvVarMissingBehavior,
    expand_env_vars,
    flatten,
    makedirs,
    nest,
    pop_at_path,
    set_at_path,
    uuid7,
)


def test_nest() -> None:
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
    assert val == start_value
    assert val is not start_value

    new_b = nest(subject, "a.b", "not_a_dict", force=True)
    assert new_b == "not_a_dict"
    assert subject == {"a": {"b": "not_a_dict", "list": [], "value": {"value": 1}}}

    # make sure existing values aren't cleared when `value=None` and `force=True`
    _ = nest(subject, "a.b", {"d": "d_value"}, force=True)
    assert subject == {
        "a": {"b": {"d": "d_value"}, "list": [], "value": {"value": 1}},
    }
    similar_b = nest(subject, "a.b", force=True)
    assert similar_b == {"d": "d_value"}
    assert subject == {
        "a": {"b": {"d": "d_value"}, "list": [], "value": {"value": 1}},
    }


def test_pop_at_path() -> None:
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


def test_set_at_path() -> None:
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


def test_flatten() -> None:
    # Test dot flatten
    example_config = {"_update": {"orchestrate/dags/meltano.py": False}}
    expected_flat = {"_update.orchestrate/dags/meltano.py": False}
    result = flatten(example_config, "dot")

    # Test env var flatten
    example_config = {"_update": {"orchestrate/dags/meltano.py": False}}
    expected_flat = {"_UPDATE_ORCHESTRATE_DAGS_MELTANO_PY": False}
    result = flatten(example_config, "env_var")

    # Test tuple flatten
    example_config = {"_update": {"orchestrate/dags/meltano.py": False}}
    expected_flat = {("_update", "orchestrate/dags/meltano.py"): False}
    result = flatten(example_config, "tuple")
    assert result == expected_flat


def test_unflatten() -> None:
    from meltano.core.utils import unflatten

    # Test basic dot notation unflatten (matches original flatten_dict behavior)
    flat_config = {"_update.orchestrate/dags/meltano.py": False}
    # Note: The dot in ".py" is also split, matching original flatten_dict behavior
    expected_nested = {"_update": {"orchestrate/dags/meltano": {"py": False}}}
    result = unflatten(flat_config, "dot")
    assert result == expected_nested

    # Test multiple levels
    flat_config = {"a.b.c": 1, "a.b.d": 2, "a.e": 3}
    expected_nested = {"a": {"b": {"c": 1, "d": 2}, "e": 3}}
    result = unflatten(flat_config, "dot")
    assert result == expected_nested

    # Test that flatten and unflatten are inverses
    original = {"foo": {"bar": {"baz": "value"}}}
    flattened = flatten(original, "dot")
    unflattened = unflatten(flattened, "dot")
    assert unflattened == original

    # Test tuple unflatten
    flat_config = {("_update", "orchestrate/dags/meltano.py"): False}
    expected_nested = {"_update": {"orchestrate/dags/meltano.py": False}}
    result = unflatten(flat_config, "tuple")
    assert result == expected_nested

    # Test custom reducer
    def custom_reducer(key: str) -> tuple[str, ...]:
        return tuple(key.split("_")) if isinstance(key, str) else (key,)

    flat_config = {"a_b_c": 1, "a_b_d": 2, "a_e": 3}
    expected_nested = {"a": {"b": {"c": 1, "d": 2}, "e": 3}}
    result = unflatten(flat_config, custom_reducer)
    assert result == expected_nested


@pytest.mark.parametrize(
    ("input_value", "env", "kwargs", "expected_output"),
    (
        pytest.param(
            "${ENV_VAR}_suffix",
            {"ENV_VAR": "substituted"},
            {},
            "substituted_suffix",
            id="suffix",
        ),
        pytest.param(
            "prefix_${ENV_VAR}",
            {"ENV_VAR": "substituted"},
            {},
            "prefix_substituted",
            id="prefix",
        ),
        pytest.param(
            "prefix_${ENV_VAR}_suffix",
            {"ENV_VAR": "substituted"},
            {},
            "prefix_substituted_suffix",
            id="prefix-and-suffix",
        ),
        pytest.param(
            "${ENV_VAR}",
            {"ENV_VAR": "substituted"},
            {},
            "substituted",
            id="curly-braces",
        ),
        pytest.param(
            "$ENV_VAR",
            {"ENV_VAR": "substituted"},
            {},
            "substituted",
            id="no-curly-braces",
        ),
        pytest.param(
            "$ENV_VAR",
            {},
            {},
            "",
            id="no-match-use-empty-string",
        ),
        pytest.param(
            "$ENV_VAR",
            {},
            {"if_missing": EnvVarMissingBehavior.ignore},
            "$ENV_VAR",
            id="no-match-ignore",
        ),
        pytest.param(
            "${ENV_VAR}",
            {},
            {"if_missing": EnvVarMissingBehavior.ignore},
            "${ENV_VAR}",
            id="no-match-ignore-curly-braces",
        ),
        pytest.param(
            "prefix-${ENV_VAR}-suffix",
            {},
            {"if_missing": EnvVarMissingBehavior.ignore},
            "prefix-${ENV_VAR}-suffix",
            id="no-match-prefix-and-suffix-ignore",
        ),
        pytest.param(
            "MY_DB\\$TableName",
            {},
            {},
            "MY_DB$TableName",
            id="escape",
        ),
    ),
)
def test_expand_env_vars(input_value, env, kwargs, expected_output) -> None:
    assert expand_env_vars(input_value, env, **kwargs) == expected_output


def test_expand_env_vars_nested() -> None:
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
def test_expand_env_vars_array_nested(input_array, env, expected_output) -> None:
    assert expand_env_vars(input_array, env) == expected_output


def test_makedirs_decorator(tmp_path) -> None:
    def root(*paths):
        return tmp_path.joinpath(*paths)

    @makedirs
    def hierarchy(*ranks, make_dirs: bool = True):  # noqa: ARG001
        return root(*ranks)

    @makedirs
    def species(genus_name, species_name, *, make_dirs: bool = True):
        return hierarchy(genus_name, species_name, make_dirs=make_dirs)

    cat = species("felis", "catus")
    assert cat.exists()

    wolf = species("canis", "lupus", make_dirs=False)
    assert not wolf.exists()


def test_uuidv7() -> None:
    """Test UUIDv7 generation and properties."""
    import time
    import uuid

    # Generate multiple UUIDs
    uuid1 = uuid7()
    time.sleep(0.001)  # Wait 1ms to ensure different timestamps
    uuid2 = uuid7()

    # Test that they are valid UUIDs
    assert isinstance(uuid1, uuid.UUID)
    assert isinstance(uuid2, uuid.UUID)

    # Test that they have version 7
    assert uuid1.version == 7
    assert uuid2.version == 7

    # Test that they are time-ordered (lexicographically sortable)
    assert str(uuid1) < str(uuid2)

    # Test that they are different
    assert uuid1 != uuid2

    # Test timestamp encoding (first 48 bits should be timestamp)
    uuid1_bytes = uuid1.bytes
    uuid2_bytes = uuid2.bytes

    # Extract timestamps from first 6 bytes
    timestamp1 = int.from_bytes(uuid1_bytes[:6], byteorder="big")
    timestamp2 = int.from_bytes(uuid2_bytes[:6], byteorder="big")

    # timestamp2 should be greater than timestamp1
    assert timestamp2 > timestamp1


def test_uuidv7_time_ordering() -> None:
    """Test that UUIDv7s generated in sequence are time-ordered."""
    import time

    uuids = []
    for _ in range(10):
        uuids.append(uuid7())
        time.sleep(0.001)

    # Convert to strings and verify they are in ascending order
    uuid_strings = [str(u) for u in uuids]
    assert uuid_strings == sorted(uuid_strings)
