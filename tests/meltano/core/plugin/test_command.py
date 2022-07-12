from pathlib import Path

import pytest

from meltano.core.behavior.canonical import Canonical
from meltano.core.plugin.command import Command, UndefinedEnvVarError


class TestCommand:
    @pytest.fixture
    def commands(self):
        return {
            "foo": {
                "args": "foo",
                "description": "foo desc",
                "executable": "foo",
                "cwd": "path",
            },
            "bar": {"args": "bar"},
            "baz": "baz",
            "test": {"args": "--test", "description": "Run tests"},
        }

    def test_serialize(self, commands):

        assert Command.parse(commands["foo"]).args == "foo"
        assert Command.parse(commands["bar"]).args == "bar"
        assert Command.parse(commands["baz"]).args == "baz"
        assert Command.parse(commands["test"]).args == "--test"

        serialized = Command.parse_all(commands)
        assert serialized["foo"].args == "foo"
        assert serialized["foo"].description == "foo desc"
        assert serialized["foo"].executable == "foo"
        assert serialized["foo"].cwd == "path"
        assert serialized["bar"].args == "bar"
        assert serialized["bar"].description is None
        assert serialized["bar"].executable is None
        assert serialized["bar"].cwd is None
        assert serialized["baz"].args == "baz"
        assert serialized["baz"].description is None
        assert serialized["baz"].executable is None
        assert serialized["baz"].cwd is None
        assert serialized["test"].args == "--test"
        assert serialized["test"].description == "Run tests"
        assert serialized["test"].executable is None
        assert serialized["test"].cwd is None

    def test_deserialize(self, commands):
        serialized = Command.parse_all(commands)

        assert serialized["foo"].canonical() == commands["foo"]
        assert serialized["bar"].canonical() == "bar"
        assert serialized["baz"].canonical() == "baz"
        assert serialized["test"].canonical() == commands["test"]

        assert Canonical.as_canonical(serialized) == {**commands, "bar": "bar"}

    def test_expanded_args(self):
        expanded_args = Command.parse("some args --flag $ENV_VAR_ARG").expanded_args(
            name="cmd",
            env={
                "ENV_VAR_ARG": "env-var-arg",
            },
        )

        assert expanded_args == ["some", "args", "--flag", "env-var-arg"]

    def test_undefined_env_var(self):
        with pytest.raises(UndefinedEnvVarError):
            Command.parse("some args --flag $ENV_VAR_ARG").expanded_args(
                name="cmd",
                env={},
            )

    def test_expand_cwd(self, commands):
        foo = Command.parse(commands["foo"])
        bar = Command.parse(commands["bar"])

        assert foo.expand_cwd(env={}) == Path.cwd() / Path("path")
        assert foo.expand_cwd(env={}, root_dir=Path("/root")) == Path("/root/path")
        assert bar.expand_cwd(env={}) is None
