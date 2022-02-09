"""Container specification."""

from __future__ import annotations

from typing import Any

from meltano.core.behavior.canonical import Canonical


class ContainerSpec(Canonical):
    """Container model for commands."""

    def __init__(
        self,
        image: str,
        *,
        command: str | None = None,
        entrypoint: str | None = None,
        ports: list[str] | None = None,
        volumes: list[str] | None = None,
        env: dict[str, Any] | None = None,
    ):
        """A container specification.

        Args:
            image: Container image.
            command: Command to run the container with.
            entrypoint: Overwrite the default `ENTRYPOINT` of the image.
            ports: Bind these ports.
            volumes: Bind mount these volumes.
            env: Environment variables.
        """
        super().__init__()

        self.image = image
        self.command = command
        self.entrypoint = entrypoint
        self.ports = ports or []
        self.volumes = volumes or []
        self.env = env or {}
