"""`BlockSet` metaclass and related components."""

from __future__ import annotations

import typing as t
from abc import ABCMeta, abstractmethod

if t.TYPE_CHECKING:
    from meltano.core.block.ioblock import IOBlock

_T = t.TypeVar("_T", bound="IOBlock")


class BlockSetValidationError(Exception):
    """Base exception when a block in a BlockSet violates the sets requirements."""

    def __init__(self, error: str, message: str = "block violates set requirements"):
        """Initialize exception for when plugin violates the BlockSet requirements.

        Args:
            error: The error.
            message: The message.
        """
        super().__init__(f"{message}: {error}")


class BlockSet(t.Generic[_T], metaclass=ABCMeta):
    """Currently the only complex block set is our `ExtractLoadBlocks` type.

    Theoretically, this is the bare minimum that we need to run and terminate
    (i.e. early abort) a block set. So anything implementing a `run`,
    `terminate`, and `validate_set` method currently satisfies the `BlockSet`
    interface.
    """

    blocks: tuple[_T, ...]

    @abstractmethod
    async def run(self) -> None:
        """Do whatever a BlockSet is designed to do."""
        raise NotImplementedError

    @abstractmethod
    async def terminate(self, *, graceful: bool = True) -> t.NoReturn:
        """Terminate a currently executing BlockSet.

        Args:
            graceful: Whether the BlockSet should try to gracefully quit.
        """
        raise NotImplementedError

    @abstractmethod
    def validate_set(self) -> None:
        """Validate a block set to ensure its valid and runnable.

        Raises:
            BlockSetValidationError: on validation failure
        """
        raise NotImplementedError
