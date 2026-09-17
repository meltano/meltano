"""Plugin management CLI."""

from __future__ import annotations

import json
import re
import typing as t
from dataclasses import asdict, dataclass
from importlib.metadata import distributions

import click
from packaging.requirements import InvalidRequirement, Requirement
from packaging.utils import canonicalize_name
from rich.box import SIMPLE_HEAD
from rich.console import Console
from rich.table import Table

from meltano.cli.params import pass_project
from meltano.cli.utils import (
    CliEnvironmentBehavior,
    InstrumentedGroup,
    PartialInstrumentedCmd,
)
from meltano.core.venv_service import VirtualEnv

if t.TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path

    from meltano.core.plugin.project_plugin import ProjectPlugin
    from meltano.core.project import Project

# Shown in place of a value that could not be determined.
UNKNOWN = "-"

# Shown in place of the version of a plugin that has no virtual environment.
NOT_INSTALLED = "[yellow](not installed)[/yellow]"

# Marks a plugin that carries its own definition in `meltano.yml`.
CUSTOM = "\u2713"

# The tool prefix of a VCS `pip install` argument, e.g. the 'git+' of
# 'git+https://github.com/MeltanoLabs/tap-github.git'.
_VCS_PREFIX = re.compile(r"^(?:git|hg|svn|bzr)\+")


def _requirement_name(pip_url: str | None) -> str | None:
    """Get the distribution name from a `pip install` argument.

    Args:
        pip_url: The `pip install` argument, if any.

    Returns:
        The distribution name, or `None` if the argument names no
        distribution, as a VCS URL and a local path do not.
    """
    if not pip_url:
        return None

    try:
        return Requirement(pip_url).name
    except InvalidRequirement:
        return None


def _vcs_url(pip_url: str) -> str | None:
    """Get the repository URL from a VCS `pip install` argument.

    Args:
        pip_url: The `pip install` argument.

    Returns:
        The URL without its tool prefix, revision, and fragment, or `None` if
        the argument does not install from a version control system.
    """
    if not _VCS_PREFIX.match(pip_url):
        return None

    url = _VCS_PREFIX.sub("", pip_url.strip()).split("#", 1)[0]

    # The revision follows the last '/', so an '@' before it belongs to
    # credentials, as in 'https://user:token@github.com/org/repo.git'.
    head, separator, tail = url.rpartition("/")
    return head + separator + tail.split("@", 1)[0]


def _direct_url_revision(site_packages: Path, pip_url: str) -> str | None:
    """Get the revision that a plugin was installed from a repository at.

    `pip` records the URL it installed from, and the revision it was asked
    for, in a `direct_url.json` file, as described by PEP 610. The
    distribution name cannot be read from a VCS `pip_url`, so the URL is what
    identifies the distribution here.

    Args:
        site_packages: The site-packages directory to search.
        pip_url: The `pip install` argument of the plugin.

    Returns:
        The requested revision, or `None` if there is none to report.
    """
    if (url := _vcs_url(pip_url)) is None:
        return None

    for dist in distributions(path=[str(site_packages)]):
        if (recorded := dist.read_text("direct_url.json")) is None:
            continue

        try:
            direct_url = json.loads(recorded)
        except ValueError:
            continue

        if direct_url.get("url") == url:
            return direct_url.get("vcs_info", {}).get("requested_revision")

    return None


def _site_packages_dir(venv: VirtualEnv) -> Path | None:
    """Find the site-packages directory of a virtual environment.

    `VirtualEnv.site_packages_dir` names the directory after the interpreter
    that Meltano itself runs on, so it is not used here.

    Args:
        venv: The virtual environment.

    Returns:
        The site-packages directory, or `None` if there is not exactly one.
    """
    # Windows puts the directory straight under the lib directory. Every other
    # platform puts it under the name of the version that created the
    # environment, which is not necessarily the one Meltano runs on.
    for pattern in ("site-packages", "python*/site-packages"):
        if found := sorted(venv.lib_dir.glob(pattern)):
            return found[0]

    return None


def _installed_version(venv: VirtualEnv, plugin: ProjectPlugin) -> str | None:
    """Get the version of the distribution a plugin was installed from.

    Args:
        venv: The plugin's virtual environment.
        plugin: The plugin.

    Returns:
        The installed version, or `None` if it could not be determined.
    """
    if (site_packages := _site_packages_dir(venv)) is None:
        return None

    if plugin.pip_url and (
        revision := _direct_url_revision(site_packages, plugin.pip_url)
    ):
        return revision

    names = {plugin.name, plugin.plugin_dir_name, _requirement_name(plugin.pip_url)}
    candidates = {canonicalize_name(name) for name in names if name}

    for dist in distributions(path=[str(site_packages)]):
        if dist.name and canonicalize_name(dist.name) in candidates:
            return dist.version

    return None


@dataclass(frozen=True)
class PluginListing:
    """A plugin in the project, and what is known about its installation."""

    name: str
    type: str
    variant: str | None
    version: str | None
    installed: bool
    custom: bool
    pip_url: str | None
    inherit_from: str | None

    @classmethod
    def from_plugin(cls, project: Project, plugin: ProjectPlugin) -> PluginListing:
        """Describe a plugin of the project.

        Args:
            project: The Meltano project.
            plugin: The plugin to describe.

        Returns:
            The plugin listing.
        """
        # Inheriting plugins share their parent's virtual environment unless
        # they install something different, which `plugin_dir_name` accounts
        # for. Mappings resolve to their mapper this way too.
        venv = VirtualEnv(
            project.dirs.venvs(plugin.type, plugin.plugin_dir_name, make_dirs=False),
        )
        # The fingerprint is written once `pip install` has returned, so an
        # environment created for an install that then failed has an
        # interpreter but no fingerprint.
        installed = venv.read_fingerprint() is not None
        return cls(
            name=plugin.name,
            type=plugin.type.descriptor,
            variant=plugin.variant,
            version=_installed_version(venv, plugin) if installed else None,
            installed=installed,
            custom=plugin.is_custom(),
            pip_url=plugin.pip_url,
            inherit_from=plugin.inherit_from,
        )


def _render_table(listings: Iterable[PluginListing]) -> None:
    """Print the plugins as a table.

    Args:
        listings: The plugins to print.
    """
    table = Table(box=SIMPLE_HEAD, pad_edge=False)
    table.add_column("TYPE", style="cyan", no_wrap=True)
    table.add_column("NAME", style="bold", overflow="fold")
    table.add_column("VARIANT", overflow="fold")
    table.add_column("VERSION", overflow="fold")
    table.add_column("CUSTOM", justify="center")

    for listing in listings:
        table.add_row(
            listing.type,
            listing.name,
            listing.variant or UNKNOWN,
            (listing.version or UNKNOWN) if listing.installed else NOT_INSTALLED,
            CUSTOM if listing.custom else "",
        )

    Console().print(table)


@click.group(
    cls=InstrumentedGroup,
    name="plugin",
    short_help="Manage project plugins.",
    environment_behavior=CliEnvironmentBehavior.environment_optional_use_default,
)
def plugin() -> None:
    """Manage the plugins in your Meltano project.

    Read more at https://docs.meltano.com/reference/command-line-interface#plugin
    """


@plugin.command(
    cls=PartialInstrumentedCmd,
    name="list",
    short_help="List the plugins in your project.",
)
@click.option(
    "--format",
    "list_format",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format.",
)
@pass_project()
def list_plugins(project: Project, *, list_format: str) -> None:
    """List the plugins in your project.

    Read more at https://docs.meltano.com/reference/command-line-interface#plugin
    """
    listings = [
        PluginListing.from_plugin(project, project_plugin)
        for project_plugin in project.plugins.plugins()
        # A mapping is configuration for its mapper, not a separate
        # installation, and is yielded under the mapper's own name.
        if not project_plugin.is_mapping()
    ]
    if list_format == "json":
        click.echo(json.dumps([asdict(listing) for listing in listings], indent=2))
        return

    if listings:
        _render_table(listings)
        return

    click.secho("No plugins are defined in this project.", fg="yellow")
    click.echo("Add one with 'meltano add'.")
