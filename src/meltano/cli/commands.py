"""The (lazy) commands that make up the top-level of the Meltano CLI.

This module defines the `LazyCommand` class, and registers each Meltano
sub-command/group (i.e. creates a `LazyCommand` instance for it).

To add a new top-level command or command group, it must be registered in this
module like the others. Any arguments that would normally be provided to the
`cli.command`/`cli.group` decorator must be provided to the initialization
method of the `LazyCommand` instead.

Then, in the `meltano.cli` sub-module that implements the new command/group,
you must decorate the function that implements the command/group with
`cli.commands.<command_name>`. This essentially connects the `LazyCommand`
instance to the actual implementation of the command.
"""

from __future__ import annotations

import inspect
from functools import update_wrapper
from importlib import import_module
from typing import Any, Callable

import click

from meltano.cli.cli import cli
from meltano.cli.utils import (
    InstrumentedCmd,
    InstrumentedDefaultGroup,
    InstrumentedGroup,
    PartialInstrumentedCmd,
)


class LazyCommand:
    """A lazy stand-in for a Click group/command that becomes real as needed.

    A `LazyCommand` instance is initialized with and stores some basic info that a group/command
    would have, such as its `name` and `short_help`. When an attribute which it doesn't have is
    accessed (i.e. by Click) the `LazyCommand` transparently replaces itself with a real
    group/command.

    Should be called as a decorator on the function defining the group/command instead of the
    regular top-level group/command decorator.
    """

    def __init__(
        self,
        *,
        name: str,
        short_help: str | None = None,
        hidden: bool = False,
        import_path: str | None = None,
        cls: type[click.BaseCommand] = InstrumentedCmd,  # noqa: WPS117
        **kwargs,
    ):
        """Initialize a `LazyCommand` instance.

        Parameters:
            name: The name of the group/command.
            short_help: The short help text for the group/command.
            hidden: Whether the group/command should be hidden (i.e. appear in help text and
                tab-completion).
            import_path: The module which implements the real version of this group/command which
                will be used to replace the `LazyCommand`. Defaults to `f"meltano.cli.{name}"`.
            cls: The class the real group/command that the `LazyCommand` will become.
        """
        # Attributes necessary to avoid prematurely loading the command:
        self.name = name
        self.hidden = hidden
        self.short_help = short_help or ""
        self.get_short_help_str = lambda *args, **kwargs: short_help or ""

        # Attributes necessary to load the command later, when needed:
        self._import_path = (
            f"meltano.cli.{name}" if import_path is None else import_path
        )
        self._kwargs = kwargs
        self._cls = cls  # noqa: WPS117

    def __call__(self, fn: Callable) -> LazyCommand:
        """Decorate the given function to transform it into this `LazyCommand` instance.

        Parameters:
            fn: The original (non-lazy) CLI group/command function, likely decorated by various
                standard Click decorators.

        Returns:
            The `LazyCommand` instance.
        """
        # Take what we need from the function object, then return the LazyCommand instance.
        update_wrapper(self, fn)
        self._kwargs.update(
            {
                "callback": fn,
                "params": list(reversed(getattr(fn, "__click_params__", []))),
                "help": inspect.getdoc(fn) if fn else "",
            }
        )
        return self

    def _activate(self):
        import_module(self._import_path)

        if not isinstance(self, LazyCommand):
            # It's possible for the above import to trigger (and complete) activation, so this
            # early-exit avoids double-activation in that case.
            return

        self.__class__ = self._cls
        self.__init__(
            self.name,
            short_help=self.short_help,
            **self._kwargs,
        )

    def __getattr__(self, key: str) -> Any:
        """Turn this instance into a real Click group/command, then get the requested attribute.

        Parameters:
            key: The name of the attribute that this instance lacked.

        Returns:
            The requested attribute from the real group/command object created from this instance.
        """
        self._activate()
        return getattr(self, key)


for command in (
    LazyCommand(
        name="add",
        short_help="Add a plugin to your project.",
        cls=PartialInstrumentedCmd,
    ),
    LazyCommand(
        name="config",
        short_help="Display Meltano or plugin configuration.",
        invoke_without_command=True,
        cls=InstrumentedGroup,
    ),
    LazyCommand(
        name="discover",
        import_path="meltano.cli.discovery",
        short_help="List the available plugins in Meltano Hub and their variants.",
    ),
    LazyCommand(
        name="dragon",
        short_help="Summon a dragon!",
    ),
    LazyCommand(
        name="elt",
        short_help="Run an ELT pipeline to Extract, Load, and Transform data.",
        cls=PartialInstrumentedCmd,
    ),
    LazyCommand(
        name="environment",
        short_help="Manage environments.",
        cls=InstrumentedGroup,
    ),
    LazyCommand(
        name="init",
        short_help="Create a new Meltano project.",
        import_path="meltano.cli.initialize",
    ),
    LazyCommand(
        name="install",
        short_help="Install project dependencies.",
        cls=PartialInstrumentedCmd,
    ),
    LazyCommand(
        name="invoke",
        short_help="Invoke a plugin.",
        context_settings={
            "ignore_unknown_options": True,
            "allow_interspersed_args": False,
        },
        cls=PartialInstrumentedCmd,
    ),
    LazyCommand(
        name="job",
        short_help="Manage jobs.",
        cls=InstrumentedGroup,
    ),
    LazyCommand(
        name="lock",
        short_help="Lock plugin definitions.",
        cls=PartialInstrumentedCmd,
    ),
    LazyCommand(
        name="remove",
        short_help="Remove plugins from your project.",
    ),
    LazyCommand(
        name="repl",
        hidden=True,
    ),
    LazyCommand(
        name="run",
        short_help="Run a set of plugins in series.",
        cls=PartialInstrumentedCmd,
    ),
    LazyCommand(
        name="schedule",
        short_help="Manage pipeline schedules.",
        cls=InstrumentedDefaultGroup,
        default="add",
    ),
    LazyCommand(
        name="schema",
        short_help="Manage system DB schema.",
        cls=InstrumentedGroup,
    ),
    LazyCommand(
        name="select",
        short_help="Manage extractor selection patterns.",
    ),
    LazyCommand(
        name="state",
        short_help="Manage Singer state.",
        cls=InstrumentedGroup,
    ),
    LazyCommand(
        name="test",
        import_path="meltano.cli.validate",
        short_help="Run validations using plugins' tests.",
    ),
    LazyCommand(
        name="ui",
        short_help="Start the Meltano UI webserver.",
        cls=InstrumentedDefaultGroup,
        default="start",
        default_if_no_args=True,
    ),
    LazyCommand(
        name="upgrade",
        short_help="Upgrade Meltano and your entire project to the latest version.",
        cls=InstrumentedDefaultGroup,
        default="all",
        default_if_no_args=True,
    ),
    LazyCommand(
        name="user",
        invoke_without_command=True,
        short_help="Manage Meltano user accounts.",
        cls=InstrumentedGroup,
    ),
):
    cli.add_command(command)
