"""Stored command arguments for plugins."""
import shlex
from typing import Optional

from meltano.core.behavior.canonical import Canonical
from meltano.core.error import Error
from meltano.core.utils import expand_env_vars


class UndefinedEnvVarError(Error):
    """Occurs when an environment variable is used as a command argument but is not set."""

    def __init__(self, command_name, var):
        """Initialize UndefinedEnvVarError."""
        super().__init__(
            f"Command '{command_name}' referenced unset environment variable '{var}' in an argument. "
            + "Set the environment variable or update the command definition."
        )


class Command(Canonical):
    """This class represents stored command arguments for plugins."""

    def __init__(
        self,
        args: str,
        description: Optional[str] = None,
        executable: Optional[str] = None,
    ):
        """Initialize a Command."""
        super().__init__(args=args, description=description, executable=executable)

    def expanded_args(self, name, env):
        """
        Replace any env var arguments with their values.

        :raises UndefinedEnvVarError: if an env var argument is not set
        """
        expanded = []
        for arg in shlex.split(self.args):
            value = expand_env_vars(arg, env)
            if not value:
                raise UndefinedEnvVarError(name, arg)

            expanded.append(value)

        return expanded

    def canonical(self):
        """Serialize the command."""
        return Command.as_canonical(self)

    @classmethod
    def as_canonical(cls, target):
        """Serialize the target command."""
        canonical = super().as_canonical(target)
        # if there are only args, flatten the object
        # to the short form
        if "args" in canonical and len(canonical) == 1:
            return canonical["args"]

        return canonical

    @classmethod
    def parse(cls, obj):
        """Deserialize data into a Command."""
        if isinstance(obj, str):
            # allow setting the arguments as the value
            # without a description
            return Command(args=obj)

        return super().parse(obj)

    @classmethod
    def parse_all(cls, obj):
        """Deserialize commands data into a dict of Commands."""
        if isinstance(obj, dict):
            return {name: Command.parse(cmd) for name, cmd in obj.items()}

        if obj is None:
            return {}

        raise ValueError(f"Expected command to be a dict but was {type(obj)}")
