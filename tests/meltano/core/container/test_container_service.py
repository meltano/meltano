import pytest

from meltano.core.container.container_service import ContainerService
from meltano.core.container.container_spec import ContainerSpec


@pytest.fixture
def spec() -> ContainerSpec:
    return ContainerSpec(
        "lightdash/lightdash",
        ports=[
            "8080:8000",
        ],
    )


class TestContainerService:
    def test_build_command(self, spec: ContainerSpec):
        service = ContainerService(spec)
        assert service.build_command() == [
            "docker",
            "run",
            "--rm",
            "-p",
            "8080:8000",
            "--name",
            "todo",
            # "-d",
            "lightdash/lightdash",
        ]
