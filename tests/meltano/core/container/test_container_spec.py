"""Test container commands."""

from collections import defaultdict

import pytest

from meltano.core.container.container_spec import ContainerSpec


@pytest.fixture
def spec() -> ContainerSpec:
    return ContainerSpec(
        "lightdash/lightdash",
        ports={"8080": "8000"},
    )


class TestContainerService:
    @pytest.mark.asyncio
    async def test_docker_config(self, spec: ContainerSpec):
        """Check Docker container config from container spec."""
        config = spec.get_docker_config()
        assert config == {
            "Cmd": None,
            "Image": "lightdash/lightdash",
            "Env": [],
            "ExposedPorts": {"8000": {}},
            "HostConfig": {
                "PortBindings": defaultdict(
                    list,
                    {
                        "8000": [
                            {"HostPort": "8080", "HostIP": "0.0.0.0"}  # noqa: S104
                        ],
                    },
                ),
                "Binds": [],
            },
        }
