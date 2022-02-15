"""Container specification."""

from __future__ import annotations

import shlex
from typing import Any

from meltano.core.behavior.canonical import Canonical


def env_mapping_to_docker(mapping: dict[str, Any]) -> list[str]:
    """Convert a dictionary of environment variables to the <ENVVAR>=<VALUE> form.

    Args:
        mapping: Dictionary of environment variables.

    Return:
        A list of <ENVVAR>=<VALUE> expression.

    >>> env_mapping_to_docker({"MY_VAR": "my_value", "DBT_TARGET": "postgres"})
    ['MY_VAR=my_value', 'DBT_TARGET=postgres']
    """
    return [f"{var}={value}" for var, value in mapping.items()]


class ContainerSpec(Canonical):
    """Container model for commands."""

    def __init__(
        self,
        image: str,
        *,
        command: str | None = None,
        entrypoint: str | None = None,
        ports: dict[str, str] | None = None,
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
        self.ports = ports or {}
        self.volumes = volumes or []
        self.env = env or {}

    def get_docker_config(self, *, additional_env: dict = None) -> dict:
        """Build a container configuration dictionary."""
        env_config = []

        if self.env:
            env_config.extend(env_mapping_to_docker(self.env))

        if additional_env:
            env_config.extend(env_mapping_to_docker(additional_env))

        return {
            "Cmd": shlex.split(self.command) if self.command else None,
            "Image": self.image,
            "Env": env_config,
            "HostConfig": {
                "PortBindings": {
                    container_port: [{"HostPort": host_port}]
                    for host_port, container_port in self.ports.items()
                },
                "Binds": self.volumes,
            },
        }
