"""Test container commands."""

import pytest

from meltano.core.container.container_service import ContainerService
from meltano.core.container.container_spec import ContainerSpec


@pytest.fixture
def spec() -> ContainerSpec:
    return ContainerSpec(
        "lightdash/lightdash",
        ports={"8080": "8000"},
    )


class TestContainerService:
    def test_docker_config(self, spec: ContainerSpec):
        config = spec.get_docker_config()
        assert config == {
            "Cmd": None,
            "Image": "lightdash/lightdash",
            "Env": [],
            "HostConfig": {
                "PortBindings": {
                    "8000": [{"HostPort": "8080"}],
                },
                "Binds": [],
            },
        }
