"""Container specification."""

from __future__ import annotations

import shlex
from collections import defaultdict
from typing import Any

from meltano.core.behavior.canonical import Canonical
from meltano.core.utils import expand_env_vars


def env_mapping_to_docker(mapping: dict[str, Any]) -> list[str]:
    """Convert a dictionary of environment variables to the <ENVVAR>=<VALUE> form.

    Args:
        mapping: Dictionary of environment variables.

    Returns:
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
        """Create a new container specification.

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
        """Build a container configuration dictionary.

        Args:
            additional_env: Extend container environment with this mapping.

        Returns:
            Dictionary with container config.
        """
        env = {}

        if additional_env:
            env.update(additional_env)

        env.update(self.env)
        env_config = env_mapping_to_docker(env)

        volumes = [expand_env_vars(bind, env) for bind in self.volumes]

        exposed_ports = {}
        port_bindings = defaultdict(list)

        for host_port, container_port in self.ports.items():
            exposed_ports[container_port] = {}
            port_bindings[container_port].append(
                {
                    "HostPort": host_port,
                    "HostIP": "0.0.0.0",  # noqa: S104. Binding to all interfaces is OK.
                }
            )

        return {
            "Cmd": shlex.split(self.command) if self.command else None,
            "Image": self.image,
            "Entrypoint": self.entrypoint,
            "Env": env_config,
            "ExposedPorts": exposed_ports,
            "HostConfig": {
                "PortBindings": port_bindings,
                "Binds": volumes,
            },
        }
