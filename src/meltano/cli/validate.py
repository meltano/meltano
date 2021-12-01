"""Validation command."""

import asyncio
import sys
from typing import List, Tuple, TypeVar

import click
import structlog
from meltano.cli.utils import propagate_stop_signals
from meltano.core.db import project_engine
from meltano.core.plugin_invoker import PluginInvoker, invoker_factory
from meltano.core.project import Project
from meltano.core.project_plugins_service import ProjectPluginsService
from meltano.core.utils import run_async
from sqlalchemy.orm.session import sessionmaker

from . import cli
from .params import pass_project

logger = structlog.getLogger(__name__)
T = TypeVar("T")  # noqa: WPS111


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
    plugins_service = ProjectPluginsService(project)
    _, session_maker = project_engine(project)
    session = session_maker()

    # All tests for all plugins
    if all_tests:
        tasks = []
        plugins = plugins_service.plugins()
        for project_plugin in plugins:
            invoker = invoker_factory(
                project, project_plugin, plugins_service=plugins_service
            )
            tasks.append(_test_plugin(invoker, session, *project_plugin.test_commands))

        exit_codes = _flatten(run_async(asyncio.gather(*tasks)))
        sys.exit(1 if any(exit_codes) else 0)

    if not plugin_tests:
        click.secho("No plugin tests were selected", fg="yellow")

    # Test specific plugins
    tasks = []
    for plugin_test in plugin_tests:
        try:
            plugin_name, test_name = plugin_test.split(":")
        except ValueError:
            plugin_name, test_name = plugin_test, None

        plugin = plugins_service.find_plugin(plugin_name, configurable=True)
        invoker = invoker_factory(project, plugin, plugins_service=plugins_service)

        tests = (test_name,) if test_name else tuple(plugin.test_commands)
        tasks.append(_test_plugin(invoker, session, *tests))

    exit_codes = _flatten(run_async(asyncio.gather(*tasks)))
    sys.exit(1 if any(exit_codes) else 0)


async def _test_plugin(
    invoker: PluginInvoker,
    session: sessionmaker,
    *tests: str,
) -> List[int]:
    """Run all tests for a plugin."""
    async with invoker.prepared(session):
        return await asyncio.gather(
            *(_invoke_command(invoker, command) for command in tests)
        )


async def _invoke_command(invoker: PluginInvoker, command: str) -> int:
    """Invoke a single plugin command."""
    handle = await invoker.invoke_async(command=command)
    with propagate_stop_signals(handle):
        exit_code = await handle.wait()

    return exit_code


def _flatten(top: List[List[T]]) -> List[T]:
    """Flatten a one-level nested list.

    Example:
    >>> _flatten([[0, 1, 1], [0, 0]])
    [0, 1, 1, 0, 0]
    """
    return [value for nested in top for value in nested]
