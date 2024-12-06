"""Stored command arguments for plugins."""

from __future__ import annotations

import shlex
import typing as t

from meltano.core.behavior.canonical import Canonical
from meltano.core.container.container_spec import ContainerSpec
from meltano.core.error import Error
from meltano.core.utils import expand_env_vars

if t.TYPE_CHECKING:
    from collections.abc import Mapping


class UndefinedEnvVarError(Error):
    """An environment variable is used as a command argument but is not set."""

    def __init__(self, command_name: str, var: str) -> None:
        """Initialize UndefinedEnvVarError.

        Args:
            command_name: Plugin command name.
            var: Environment variable name.
        """
        super().__init__(
            f"Command '{command_name}' referenced unset environment variable "
            f"'{var}' in an argument. Set the environment variable or update "
            "the command definition.",
        )


class Command(Canonical):
    """This class represents stored command arguments for plugins."""

    args: str
    description: str | None
    executable: str | None
    container_spec: ContainerSpec | None

    def __init__(
        self,
        args: str = "",
        description: str | None = None,
        executable: str | None = None,
        container_spec: dict | None = None,
    ):
        """Initialize a Command.

        Args:
            args: Command arguments.
            description: Command description.
            executable: Optional command executable.
            container_spec: Container specification for this command.
        """
        super().__init__(
            args=args,
            description=description,
            executable=executable,
        )
        self.container_spec = (
            ContainerSpec(**container_spec) if container_spec else None
        )

    def expanded_args(self, name: str, env: Mapping[str, str]) -> list[str]:
        """Replace any env var arguments with their values.

        Args:
            name: Command name.
            env: Mapping of environment variables to expand the command.

        Returns:
            List of expanded command parts.

        Raises:
            UndefinedEnvVarError: if an env var argument is not set
        """
        expanded = []
        for arg in shlex.split(self.args):
            if value := expand_env_vars(arg, env):
                expanded.append(value)

            else:
                raise UndefinedEnvVarError(name, arg)

        return expanded

    @classmethod
    def as_canonical(cls, target):  # noqa: ANN001, ANN206
        """Serialize the target command.

        Args:
            target: Target object type.

        Returns:
            Python object.
        """
        canonical = super().as_canonical(target)
        # if there are only args, flatten the object
        # to the short form
        if "args" in canonical and len(canonical) == 1:
            return canonical["args"]

        return canonical

    @classmethod
    def parse(cls, obj: str | dict) -> Command:
        """Deserialize data into a Command.

        Args:
            obj: Raw Python object.

        Returns:
            Command instance.
        """
        if isinstance(obj, str):
            # allow setting the arguments as the value
            # without a description
            return Command(args=obj)

        return super().parse(obj)

    @classmethod
    def parse_all(cls: type[Command], obj: dict | None) -> dict[str, Command]:
        """Deserialize commands data into a dict of Commands.

        Args:
            obj: Raw Python object.

        Returns:
            Mapping of command names to instances.
        """
        if obj is not None:
            return {name: Command.parse(cmd) for name, cmd in obj.items()}

        return {}
