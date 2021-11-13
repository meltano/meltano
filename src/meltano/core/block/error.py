class BlockSetValidationError(Exception):
    """Base exception when a block in a BlockSet violates the sets requirements."""

    def __init__(self, error: str, message: str = "block violates set requirements"):
        """Initialize exception for when plugin violates the BlockSet requirements.

        Args:
            error: The error.
            message: The message.
        """

        super().__init__(f"{message}: {error}")
