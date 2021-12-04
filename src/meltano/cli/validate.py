"""Validation command."""

import sys
from typing import Dict, Iterable, Tuple, TypeVar

import click
import structlog
from meltano.cli.utils import propagate_stop_signals
from meltano.core.db import project_engine
from meltano.core.plugin_invoker import PluginInvoker, invoker_factory
from meltano.core.project import Project
from meltano.core.project_plugins_service import ProjectPluginsService
from meltano.core.utils import run_async
from meltano.core.validation_service import ValidationOutcome, ValidationsRunner
from sqlalchemy.orm.session import sessionmaker

from . import cli
from .params import pass_project

logger = structlog.getLogger(__name__)
T = TypeVar("T")  # noqa: WPS111

TEST_LINE_LENGTH = 60


class CommandLineValidator:
    """Validator that runs in the CLI."""

    def __init__(self, name: str, selected: bool = True) -> None:
        """Create a new CLI validator."""
        self.name = name
        self.selected = selected

    async def run_async(self, invoker: PluginInvoker):
        """Run this validation.

        Args:
            invoker: A plugin CLI invoker.

        Returns:
            Exit code for the plugin invocation.
        """
        handle = await invoker.invoke_async(command=self.name)
        with propagate_stop_signals(handle):
            exit_code = await handle.wait()
        return exit_code


@cli.command()
@click.option(
    "--all",
    "all_tests",
    is_flag=True,
    help="Run all defined tests in all plugins.",
)
@click.argument(
    "plugin_tests",
    default=None,
    required=False,
    nargs=-1,
)
@pass_project(migrate=True)
def test(
    project: Project,
    all_tests: bool,
    plugin_tests: Tuple[str] = (),
):
    """Run validations using plugins' tests."""
    _, session_maker = project_engine(project)
    session = session_maker()

    collected = collect_tests(project, select_all=all_tests)

    for plugin_test in plugin_tests:
        try:
            plugin_name, test_name = plugin_test.split(":")
        except ValueError:
            plugin_name, test_name = plugin_test, None

        if test_name:
            collected[plugin_name].select_test(test_name)
        else:
            collected[plugin_name].select_all()

    exit_codes = run_async(_run_plugin_tests(session, collected.values()))

    click.echo()
    _report_and_exit(exit_codes)


def collect_tests(
    project: Project,
    select_all: bool = True,
) -> Dict[str, ValidationsRunner]:
    """Collect all tests for CLI invocation.

    Args:
        project: A Meltano project object.
        select_all: Flag to select all validations by default.

    Returns:
        A mapping of plugin names to validation runners.
    """
    plugins_service = ProjectPluginsService(project)
    return {
        plugin.name: ValidationsRunner(
            invoker=invoker_factory(project, plugin, plugins_service=plugins_service),
            validators={
                test: CommandLineValidator(test, select_all)
                for test in plugin.test_commands
            },
        )
        for plugin in plugins_service.plugins()
    }


async def _run_plugin_tests(
    session: sessionmaker,
    runners: Iterable[ValidationsRunner],
) -> Dict[str, Dict[str, int]]:
    return {runner.plugin_name: await runner.run_all(session) for runner in runners}


def _report_and_exit(results: Dict[str, Dict[str, int]]):
    exit_code = 0
    failed_count = 0
    passed_count = 0

    for plugin_name, test_results in results.items():
        for test_name, test_exit_code in test_results.items():
            outcome = ValidationOutcome.from_exit_code(test_exit_code)
            if test_exit_code == 0:
                passed_count += 1
            else:
                exit_code = 1
                failed_count += 1
            styled_result = click.style(outcome, fg=outcome.color)
            plugin_test = click.style(f"{plugin_name}:{test_name}", bold=True)
            click.echo(f"{plugin_test.ljust(TEST_LINE_LENGTH, '.')} {styled_result}")

    message = "successfully" if failed_count == 0 else "with failures"

    click.echo(
        f"\nTesting completed {message}. "
        + f"{passed_count} tests successful. {failed_count} tests failed."
    )

    sys.exit(exit_code)
