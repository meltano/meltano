"""Class for invoking plugin validations."""

from __future__ import annotations

import enum
import sys
import typing as t
from abc import ABCMeta, abstractmethod

from meltano.core.plugin import PluginType
from meltano.core.plugin_invoker import invoker_factory

if sys.version_info >= (3, 11):
    from enum import StrEnum
    from typing import Self  # noqa: ICN003
else:
    from backports.strenum import StrEnum
    from typing_extensions import Self


if t.TYPE_CHECKING:
    from sqlalchemy.orm.session import Session

    from meltano.core.plugin_invoker import PluginInvoker
    from meltano.core.project import Project

EXIT_CODE_OK = 0


class ValidationOutcome(StrEnum):
    """Data validation outcome options."""

    SUCCESS = enum.auto()
    FAILURE = enum.auto()

    @property
    def color(self) -> str:
        """Return terminal color for this outcome.

        Returns:
            The string name of a color for this outcome.
        """
        return "green" if self == ValidationOutcome.SUCCESS else "red"

    @classmethod
    def from_exit_code(cls, exit_code: int):  # noqa: ANN206
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
            raise KeyError(  # noqa: TRY003
                f"Plugin {self.plugin_name} does not have a test named '{name}'",  # noqa: EM102
            ) from exc

    def select_all(self) -> None:
        """Mark all plugin validators as selected."""
        for name in self.tests_selection:
            self.tests_selection[name] = True

    async def run_all(self, session: Session) -> dict[str, int]:
        """Run all validators defined in a plugin.

        Args:
            session: A SQLAlchemy ORM session.

        Returns:
            A mapping of validator names to exit codes.
        """
        if not self.tests_selection:
            return {}

        results = {}  # type: ignore[var-annotated]
        async with self.invoker.prepared(session):
            for name, selected in self.tests_selection.items():
                if selected:
                    results[name] = await self.run_test(name)
        return results

    @classmethod
    def collect(
        cls,
        project: Project,
        *,
        select_all: bool = True,
    ) -> dict[str, Self]:
        """Collect all tests for CLI invocation.

        Args:
            project: A Meltano project object.
            select_all: Flag to select all validations by default.

        Returns:
            A mapping of plugin names to validation runners.
        """
        return {
            plugin.name: cls(
                invoker=invoker_factory(project, plugin),
                tests_selection=dict.fromkeys(plugin.test_commands, select_all),
            )
            for plugin in project.plugins.plugins()
            if plugin.type is not PluginType.FILES
        }

    @abstractmethod
    async def run_test(self, name: str) -> t.NoReturn:
        """Run a test command.

        Args:
            name: Test name.
        """
        raise NotImplementedError
