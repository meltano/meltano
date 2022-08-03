"""The Meltano REPL."""

from __future__ import annotations

import click

from meltano.cli.cli import cli
from meltano.cli.params import database_uri_option
from meltano.cli.utils import InstrumentedCmd


@cli.command(cls=InstrumentedCmd, hidden=True)
@database_uri_option
@click.pass_context
def repl(ctx: click.Context):
    """Start the Meltano REPL."""
    try:
        import IPython
    except ImportError as ex:
        click.secho("The 'ipython' package must be installed to use the REPL", fg="red")
        raise click.Abort from ex

    from traitlets.config import Config

    # First create a config object from the traitlets library
    config = Config()

    config.InteractiveShellApp.extensions = ["autoreload"]
    config.InteractiveShellApp.exec_lines = [
        r'print("\nBooting import Meltano REPL\n")',
        "from meltano.core.project import Project",
        "from meltano.core.project_settings_service import ProjectSettingsService",
        "from meltano.core.project_plugins_service import ProjectPluginsService",
        "from meltano.core.plugin.settings_service import PluginSettingsService",
        "from meltano.core.db import project_engine",
        "project = Project.find()",
        "settings_service = ProjectSettingsService(project)",
        "_, Session = project_engine(project, default=True)",
        "session = Session()",
        "%autoreload 2",  # noqa: WPS323
    ]
    # config.InteractiveShell.colors = 'LightBG'  # noqa: E800
    config.InteractiveShell.confirm_exit = False
    config.TerminalIPythonApp.display_banner = True

    # Now we start ipython with our configuration
    IPython.start_ipython(argv=[], config=config)
