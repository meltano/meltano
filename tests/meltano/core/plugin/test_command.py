from __future__ import annotations

import pytest

from meltano.core.behavior.canonical import Canonical
from meltano.core.plugin.command import Command, UndefinedEnvVarError


class TestCommand:
    @pytest.fixture
    def commands(self):
        return {
            "foo": {"args": "foo", "description": "foo desc", "executable": "foo"},
            "bar": {"args": "bar"},
            "baz": "baz",
            "test": {"args": "--test", "description": "Run tests"},
            "no_args": {
                "description": "No args command",
                "executable": "my-executable",
            },
        }

    def test_serialize(self, commands) -> None:
        assert Command.parse(commands["foo"]).args == "foo"
        assert Command.parse(commands["bar"]).args == "bar"
        assert Command.parse(commands["baz"]).args == "baz"
        assert Command.parse(commands["test"]).args == "--test"
        assert Command.parse(commands["no_args"]).args == ""

        serialized = Command.parse_all(commands)
        assert serialized["foo"].args == "foo"
        assert serialized["foo"].description == "foo desc"
        assert serialized["foo"].executable == "foo"
        assert serialized["bar"].args == "bar"
        assert serialized["bar"].description is None
        assert serialized["bar"].executable is None
        assert serialized["baz"].args == "baz"
        assert serialized["baz"].description is None
        assert serialized["baz"].executable is None
        assert serialized["test"].args == "--test"
        assert serialized["test"].description == "Run tests"
        assert serialized["test"].executable is None
        assert serialized["no_args"].args == ""
        assert serialized["no_args"].description == "No args command"
        assert serialized["no_args"].executable == "my-executable"

    def test_deserialize(self, commands) -> None:
        serialized = Command.parse_all(commands)

        assert serialized["foo"].canonical() == commands["foo"]
        assert serialized["bar"].canonical() == "bar"
        assert serialized["baz"].canonical() == "baz"
        assert serialized["test"].canonical() == commands["test"]
        assert serialized["no_args"].canonical() == commands["no_args"]

        assert Canonical.as_canonical(serialized) == {**commands, "bar": "bar"}

    def test_expanded_args(self) -> None:
        expanded_args = Command.parse("some args --flag $ENV_VAR_ARG").expanded_args(
            name="cmd",
            env={
                "ENV_VAR_ARG": "env-var-arg",
            },
        )

        assert expanded_args == ["some", "args", "--flag", "env-var-arg"]

    def test_undefined_env_var(self) -> None:
        with pytest.raises(UndefinedEnvVarError):
            Command.parse("some args --flag $ENV_VAR_ARG").expanded_args(
                name="cmd",
                env={},
            )
