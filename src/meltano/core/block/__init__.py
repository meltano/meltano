from typing import Protocol


class BlockSetValidationError(Exception):
    def __init__(self, error: str, message: str = "block violates set requirements"):
        super().__init__(f"{message}: {error}")


class BlockSet(Protocol):
    """Right now the only complex block set is out ExtractLoadBlocks type. So just defining BlockSet as a protocol for
    now. Once we implement additional complex block sets it'll be more evident on what the BlockSet class might look
    like long term.

    Theoretically, the bare minimum that we need to run and terminate (i.e. early abort) a block set. So anything
    implementing a run(), terminate(), and validate_set() method currently satisfies the BlockSet interface.
    """

    async def run(self) -> None:
        """Do whatever a BlockSet is designed to do."""
        pass

    async def terminate(self, graceful: bool = True) -> bool:
        """Terminate a currently executing BlockSet.

        Args:
            graceful: Whether or not the BlockSet should try to gracefully quit.
        Returns:
            Whether or not the BlockSet terminated successfully.
        """
        pass

    def validate_set(self) -> None:  # TODO: probably not required long term
        """Validate a block set to ensure its valid and runable.

        Raises: BlockSetValidationError on validation failure
        """
        pass  # or raise BlockSetValidationError
