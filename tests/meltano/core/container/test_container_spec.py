"""Test container commands."""

import platform
from collections import defaultdict

import pytest

from meltano.core.container.container_spec import ContainerSpec


class TestContainerService:
    @pytest.mark.parametrize(
        "spec,payload",
        [
            (
                ContainerSpec(
                    "lightdash/lightdash",
                    ports={"8080": "8000"},
                ),
                {
                    "Cmd": None,
                    "Entrypoint": None,
                    "Image": "lightdash/lightdash",
                    "Env": [],
                    "ExposedPorts": {"8000": {}},
                    "HostConfig": {
                        "PortBindings": defaultdict(
                            list,
                            {
                                "8000": [
                                    {
                                        "HostPort": "8080",
                                        "HostIP": "0.0.0.0",  # noqa: S104v
                                    }
                                ],
                            },
                        ),
                        "Binds": [],
                    },
                },
            ),
            (
                ContainerSpec(
                    "lightdash/lightdash",
                    entrypoint="bash",
                ),
                {
                    "Cmd": None,
                    "Entrypoint": "bash",
                    "Image": "lightdash/lightdash",
                    "Env": [],
                    "ExposedPorts": {},
                    "HostConfig": {
                        "PortBindings": defaultdict(list, {}),
                        "Binds": [],
                    },
                },
            ),
        ],
        ids=["port-mapping", "custom-entrypoint"],
    )
    @pytest.mark.asyncio
    @pytest.mark.skipif(
        platform.system() == "Windows",
        reason="Doesn't pass on windows, this is currently being tracked here https://github.com/meltano/meltano/issues/3444",
    )
    async def test_docker_config(self, spec: ContainerSpec, payload: dict):
        """Check Docker container config from container spec."""
        config = spec.get_docker_config()
        assert config == payload
