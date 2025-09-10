"""Validation command."""

from __future__ import annotations

import shutil
import sys
import typing as t

import click
import structlog

from meltano.cli.params import get_install_options, pass_project
from meltano.cli.utils import (
    CliEnvironmentBehavior,
    InstrumentedCmd,
    propagate_stop_signals,
)
from meltano.core.db import project_engine
from meltano.core.plugin_install_service import PluginInstallReason
from meltano.core.utils import run_async
from meltano.core.validation_service import ValidationOutcome, ValidationsRunner

if t.TYPE_CHECKING:
    from collections import abc

    from sqlalchemy.orm.session import Session

    from meltano.cli.params import InstallPlugins
    from meltano.core.project import Project

logger = structlog.getLogger(__name__)

TEST_LINE_LENGTH = 60

install, no_install, only_install = get_install_options(include_only_install=True)


def write_sep_line(title: str, sepchar: str, **kwargs) -> None:  # noqa: ANN003
    """Write a separator line in the terminal."""
    terminal_width, _ = shutil.get_terminal_size()
    char_count = (
        terminal_width - len(title) - 2  # Whitespace between sepchar and title
    ) // (2 * len(sepchar))
    char_count = max(char_count, 1)

    fill = sepchar * char_count
    line = f"\n{fill} {title} {fill}"

    if len(line) + len(sepchar.rstrip()) <= terminal_width:
        line += sepchar.rstrip()

    click.secho(line, **kwargs)


class CommandLineRunner(ValidationsRunner):
    """Validator that runs in the CLI."""

    async def run_test(self, name: str) -> int:  # type: ignore[override]
        """Run a test command.

        Args:
            name: Test command name to invoke.

        Returns:
            Exit code for the plugin invocation.
        """
        write_sep_line(f"{self.plugin_name}:{name}", "=", bold=True)
        handle = await self.invoker.invoke_async(command=name)
        with propagate_stop_signals(handle):
            return await handle.wait()


@click.command(
    cls=InstrumentedCmd,
    short_help="Run validations using plugins' tests.",
    environment_behavior=CliEnvironmentBehavior.environment_optional_use_default,
)
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
@install
@no_install
@only_install
@pass_project(migrate=True)
@run_async
async def test(
    project: Project,
    *,
    all_tests: bool,
    install_plugins: InstallPlugins,
    plugin_tests: tuple[str, ...],
) -> None:
    """Run validations using plugins' tests.

    \b
    Read more at https://docs.meltano.com/reference/command-line-interface#test
    """  # noqa: D301
    _, session_maker = project_engine(project)
    session = session_maker()

    collected = CommandLineRunner.collect(project, select_all=all_tests)

    for plugin_test in plugin_tests:
        try:
            plugin_name, test_name = plugin_test.split(":")
        except ValueError:
            plugin_name, test_name = plugin_test, None

        if test_name:
            collected[plugin_name].select_test(test_name)
        else:
            collected[plugin_name].select_all()

    await install_plugins(
        project,
        [c.invoker.plugin for c in collected.values() if c.tests_selection],
        reason=PluginInstallReason.AUTO,
    )

    exit_codes = await _run_plugin_tests(session, collected.values())
    click.echo()
    _report_and_exit(exit_codes)


async def _run_plugin_tests(
    session: Session,
    runners: abc.Iterable[ValidationsRunner],
) -> dict[str, dict[str, int]]:
    return {runner.plugin_name: await runner.run_all(session) for runner in runners}


def _report_and_exit(results: dict[str, dict[str, int]]) -> None:
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

    status = "successfully" if failed_count == 0 else "with failures"
    message = (
        f"Testing completed {status}. "
        f"{passed_count} test(s) successful. {failed_count} test(s) failed."
    )

    write_sep_line(message, "=", fg=("red" if exit_code else "green"))

    sys.exit(exit_code)
