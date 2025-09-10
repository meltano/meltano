from __future__ import annotations

import platform
import typing as t

import pytest

from meltano.core.constants import STATE_ID_COMPONENT_DELIMITER
from meltano.core.environment import (
    Environment,
    EnvironmentNameContainsStateIdDelimiterError,
)
from meltano.core.environment_service import EnvironmentAlreadyExistsError
from meltano.core.utils import NotFound

if t.TYPE_CHECKING:
    from meltano.core.environment_service import EnvironmentService


class TestEnvironmentService:
    @pytest.fixture
    def subject(self, environment_service):
        return environment_service

    @pytest.fixture
    def environment(self, environment_service: EnvironmentService) -> Environment:
        return environment_service.add("test-environment")

    @pytest.mark.order(0)
    def test_add_environment(self, subject: EnvironmentService) -> None:
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
            match=r"An Environment named 'environment_0' already exists.",
        ):
            subject.add_environment(environments[3])

    @pytest.mark.order(1)
    def test_remove_environment(
        self,
        subject: EnvironmentService,
        environment: Environment,
    ) -> None:
        assert subject.list_environments() == [environment]
        subject.remove(environment.name)
        assert not subject.list_environments()

        with pytest.raises(
            NotFound,
            match="Environment 'i-do-not-exist' was not found",
        ):
            subject.remove("i-do-not-exist")

    @pytest.mark.order(2)
    def test_list_environments(
        self,
        subject: EnvironmentService,
    ) -> None:
        if platform.system() == "Windows":
            pytest.xfail(
                "Fails on Windows: https://github.com/meltano/meltano/issues/3444",
            )
        new_environment = subject.add("new-environment")
        assert subject.list_environments() == [new_environment]

    def test_add_name_contains_state_id_component_delimiter(
        self,
        subject: EnvironmentService,
    ) -> None:
        with pytest.raises(EnvironmentNameContainsStateIdDelimiterError):
            subject.add(f"test{STATE_ID_COMPONENT_DELIMITER}")
