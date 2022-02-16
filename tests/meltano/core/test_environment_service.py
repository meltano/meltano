import pytest

from meltano.core.environment import Environment
from meltano.core.environment_service import (
    EnvironmentAlreadyExistsError,
    EnvironmentService,
)
from meltano.core.utils import NotFound


class TestEnvironmentService:
    @pytest.fixture()
    def subject(self, environment_service):
        return environment_service

    @pytest.fixture()
    def environment(self, environment_service: EnvironmentService) -> Environment:
        return environment_service.add("test-environment")

    def test_add_environment(self, subject: EnvironmentService):
        count = 10
        environments = [Environment(f"environment_{idx}") for idx in range(count)]
        for environment in environments:
            subject.add_environment(environment)

        # default environments are added to initialised projects
        default_environments = [
            Environment(name) for name in ("dev", "staging", "prod")
        ]
        environments = default_environments + environments

        assert subject.list_environments() == environments

        with pytest.raises(
            EnvironmentAlreadyExistsError,
            match="An Environment named 'environment_0' already exists.",
        ):
            subject.add_environment(environments[3])

    def test_remove_environment(
        self,
        subject: EnvironmentService,
        environment: Environment,
    ):
        assert subject.list_environments() == [environment]
        subject.remove(environment.name)
        assert not subject.list_environments()

        with pytest.raises(
            NotFound,
            match="Environment 'i-do-not-exist' was not found",
        ):
            subject.remove("i-do-not-exist")

    def test_list_environments(
        self,
        subject: EnvironmentService,
    ):
        new_environment = subject.add("new-environment")
        assert subject.list_environments() == [new_environment]
