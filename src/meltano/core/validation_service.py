"""Class for invoking plugin validations."""

from __future__ import annotations

from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import TypeVar

from sqlalchemy.orm.session import sessionmaker

from meltano.core.plugin import PluginType
from meltano.core.plugin_invoker import PluginInvoker, invoker_factory
from meltano.core.project import Project
from meltano.core.project_plugins_service import ProjectPluginsService

EXIT_CODE_OK = 0

T = TypeVar("T")  # noqa: WPS111


class ValidationOutcome(str, Enum):
    """Data validation outcome options."""

    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"

    @property
    def color(self) -> str:
        """Return terminal color for this outcome.

        Returns:
            The string name of a color for this outcome.
        """
        return "green" if self == self.SUCCESS else "red"

    @classmethod
    def from_exit_code(cls, exit_code: int):
        """Create validation outcome from an exit code.

        Args:
            exit_code: Exit code of this of this outcome.

        Returns:
            A string name of this outcome ("SUCCESS or "FAILURE")
        """
        return cls.SUCCESS if exit_code == EXIT_CODE_OK else cls.FAILURE


class ValidationsRunner(metaclass=ABCMeta):
    """Class to collect all validations defined for a plugin."""

    def __init__(
        self,
        invoker: PluginInvoker,
        tests_selection: dict[str, bool],
    ) -> None:
        """Create a validators runner for a plugin.

        Args:
            invoker: PluginInvoker to be used with this ValidationsRunner.
            tests_selection: Dict of selected tests.
        """
        self.invoker = invoker
        self.tests_selection = tests_selection

    @property
    def plugin_name(self) -> str:
        """Get underlying plugin name.

        Returns:
            The name of the plugin to run.
        """
        return self.invoker.plugin.name

    def select_test(self, name: str) -> None:
        """Mark a single test as selected.

        Args:
            name: Test (command) name.

        Raises:
            KeyError: If plugin test is not defined.
        """
        try:
            self.tests_selection[name] = True
        except KeyError as exc:
            raise KeyError(
                f"Plugin {self.plugin_name} does not have a test named '{name}'"
            ) from exc

    def select_all(self) -> None:
        """Mark all plugin validators as selected."""
        for name in self.tests_selection.keys():
            self.tests_selection[name] = True

    async def run_all(self, session: sessionmaker) -> dict[str, int]:
        """Run all validators defined in a plugin.

        Args:
            session: A SQLAlchemy ORM session.

        Returns:
            A mapping of validator names to exit codes.
        """
        if not self.tests_selection:
            return {}

        results = {}
        async with self.invoker.prepared(session):
            for name, selected in self.tests_selection.items():
                if selected:
                    results[name] = await self.run_test(name)
        return results

    @classmethod
    def collect(
        cls: type[T],
        project: Project,
        select_all: bool = True,
    ) -> dict[str, T]:
        """Collect all tests for CLI invocation.

        Args:
            project: A Meltano project object.
            select_all: Flag to select all validations by default.

        Returns:
            A mapping of plugin names to validation runners.
        """
        plugins_service = ProjectPluginsService(project)
        return {
            plugin.name: cls(
                invoker=invoker_factory(
                    project, plugin, plugins_service=plugins_service
                ),
                tests_selection={
                    test_name: select_all for test_name in plugin.test_commands
                },
            )
            for plugin in plugins_service.plugins()
            if plugin.type is not PluginType.FILES
        }

    @abstractmethod
    async def run_test(self, name: str):
        """Run a test command.

        Args:
            name: Test name.
        """
        raise NotImplementedError
