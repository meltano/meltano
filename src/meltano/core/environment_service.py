"""Manager for Meltano project Environments."""

from __future__ import annotations

from meltano.core.environment import Environment
from meltano.core.project import Project

from .utils import find_named


class EnvironmentAlreadyExistsError(Exception):
    """Occurs when an environment already exists."""

    def __init__(self, environment: Environment):
        """Create a new exception.

        Args:
            environment: An Environment object.
        """
        self.environment = environment
        super().__init__(f"An Environment named '{environment.name}' already exists.")


class EnvironmentService:
    """Meltano Service to manage Environment instances."""

    def __init__(self, project: Project):
        """Create a new EnvironmentService for a Meltano Project.

        Args:
            project: A Meltano Project.
        """
        self.project = project

    def add(self, name) -> Environment:
        """Create a new Environment in `meltano.yml`.

        Args:
            name: Name for new Environment.

        Returns:
            The newly added Environment object.
        """
        return self.add_environment(Environment(name=name))

    def add_environment(self, environment: Environment):
        """Add an Environment object to `meltano.yml`.

        Args:
            environment: An instance of meltano.core.environment.Environment to add.

        Raises:
            EnvironmentAlreadyExistsError: If an Environment with the same name already exists.

        Returns:
            The newly added Environment.
        """
        with self.project.meltano_update() as meltano:
            # guard if it already exists
            # matching only by name works thanks to the `NameEq` mixin
            if environment in meltano.environments:
                raise EnvironmentAlreadyExistsError(environment=environment)

            meltano.environments.append(environment)

        return environment

    def list_environments(self) -> list[Environment]:
        """Enumerate existing Environments.

        Returns:
            A list of Environment objects.
        """
        return self.project.meltano.environments.copy()

    def remove(self, name: str) -> str:
        """Remove an Environment by name.

        Args:
            name: Name of the Environment that should be removed.

        Returns:
            The name of the removed Environment.
        """
        with self.project.meltano_update() as meltano:
            environment = find_named(
                self.list_environments(), name, obj_type=Environment
            )

            # find the schedules plugin config
            meltano.environments.remove(environment)

        return name
