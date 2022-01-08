"""This holds the actual BlockSet meta class as well as related components such as exceptions."""
from abc import ABCMeta, abstractmethod

from sqlalchemy.orm import Session


class BlockSetValidationError(Exception):
    """Base exception when a block in a BlockSet violates the sets requirements."""

    def __init__(self, error: str, message: str = "block violates set requirements"):
        """Initialize exception for when plugin violates the BlockSet requirements.

        Args:
            error: The error.
            message: The message.
        """
        super().__init__(f"{message}: {error}")


class BlockSet(metaclass=ABCMeta):
    """Currently the only complex block set is our ExtractLoadBlocks type.

    Theoretically, this is the bare minimum that we need to run and terminate (i.e. early abort) a block set. So anything
    implementing a run(), terminate(), and validate_set() method currently satisfies the BlockSet interface.
    """

    @abstractmethod
    async def run(self, session: Session) -> None:
        """Do whatever a BlockSet is designed to do."""
        raise NotImplementedError

    @abstractmethod
    async def terminate(self, graceful: bool = True) -> bool:
        """Terminate a currently executing BlockSet.

        Args:
            graceful: Whether or not the BlockSet should try to gracefully quit.
        Returns:
            Whether or not the BlockSet terminated successfully.
        """
        raise NotImplementedError

    @abstractmethod
    def validate_set(self) -> None:
        """Validate a block set to ensure its valid and runnable.

        Raises:
            BlockSetValidationError: on validation failure
        """
        raise NotImplementedError
