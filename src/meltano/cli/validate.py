"""Validation command."""

from __future__ import annotations

import asyncio
import shutil
import sys
from typing import Iterable

import click
import structlog
from sqlalchemy.orm.session import sessionmaker

from meltano.cli import activate_environment, cli
from meltano.cli.params import pass_project
from meltano.cli.utils import InstrumentedCmd, propagate_stop_signals
from meltano.core.db import project_engine
from meltano.core.project import Project
from meltano.core.validation_service import ValidationOutcome, ValidationsRunner

logger = structlog.getLogger(__name__)

TEST_LINE_LENGTH = 60


def write_sep_line(title: str, sepchar: str, **kwargs):
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

    async def run_test(self, name: str) -> int:
        """Run a test command.

        Args:
            name: Test command name to invoke.

        Returns:
            Exit code for the plugin invocation.
        """
        write_sep_line(f"{self.plugin_name}:{name}", "=", bold=True)
        handle = await self.invoker.invoke_async(command=name)
        with propagate_stop_signals(handle):
            exit_code = await handle.wait()
        return exit_code


@cli.command(cls=InstrumentedCmd, short_help="Run validations using plugins' tests.")
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
@click.pass_context
def test(
    ctx: click.Context,
    project: Project,
    all_tests: bool,
    plugin_tests: tuple[str] = (),
):
    """
    Run validations using plugins' tests.

    \b\nRead more at https://docs.meltano.com/reference/command-line-interface#test
    """
    activate_environment(ctx, project)
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

    exit_codes = asyncio.run(_run_plugin_tests(session, collected.values()))
    click.echo()
    _report_and_exit(exit_codes)


async def _run_plugin_tests(
    session: sessionmaker,
    runners: Iterable[ValidationsRunner],
) -> dict[str, dict[str, int]]:
    return {runner.plugin_name: await runner.run_all(session) for runner in runners}


def _report_and_exit(results: dict[str, dict[str, int]]):
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
        + f"{passed_count} test(s) successful. {failed_count} test(s) failed."
    )

    write_sep_line(message, "=", fg=("red" if exit_code else "green"))

    sys.exit(exit_code)
