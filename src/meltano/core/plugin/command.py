from typing import Optional

from meltano.core.behavior.canonical import Canonical


class Command(Canonical):
    """This class represents stored command arguments for plugins."""

    def __init__(self, args: str, description: Optional[str] = None):
        super().__init__(args=args, description=description)

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
