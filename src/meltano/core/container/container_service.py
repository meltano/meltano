"""Container management."""

from __future__ import annotations

from .container_spec import ContainerSpec


class ContainerService:
    def __init__(self, spec: ContainerSpec):
        self.spec = spec

    def build_command(self) -> list[str]:
        result = ["docker", "run", "--rm"]

        for port_mapping in self.spec.ports:
            result.extend(["-p", port_mapping])

        for volume_mapping in self.spec.volumes:
            result.extend(["-v", volume_mapping])

        for env_var, value in self.spec.env.items():
            result.extend(["-e", f"{env_var}={value}"])

        if self.spec.entrypoint:
            result.extend(["--entrypoint", self.spec.entrypoint])

        result.extend(["--name", "todo"])

        # Detached mode
        # result.append("-d")

        result.append(self.spec.image)

        if self.spec.command:
            result.append(self.spec.command)

        return result
