import os
import json
import yaml
import logging
import click
import re

from .project import Project
from .plugin import PluginType, Plugin
from .plugin.factory import plugin_factory
from .config_service import ConfigService
from .utils import setting_env


class ProjectAddCustomService:
    def __init__(self, project: Project, config_service: ConfigService = None):
        self.project = project
        self.config_service = config_service or ConfigService(project)

    def add(self, plugin_type: PluginType, plugin_name: str):
        click.secho(
            f"Adding new custom {plugin_type.descriptor} with name '{plugin_name}'...",
            fg="green",
        )
        click.echo()

        click.echo(
            f"Specify the plugin's {click.style('namespace', fg='blue')}, which will serve as the:"
        )
        click.echo("- prefix for configuration environment variables")
        click.echo("- identifier to find related/compatible plugins")
        if plugin_type == PluginType.EXTRACTORS:
            click.echo("- default value for the `schema` setting when used")
            click.echo("  with loader target-postgres or target-snowflake")
        elif plugin_type == PluginType.LOADERS:
            click.echo("- default value for the `target` setting when used")
            click.echo("  with transformer dbt")
        click.echo()
        if plugin_type == PluginType.LOADERS:
            default_namespace = re.sub(r"^.*target-", "", plugin_name)
            default_description = "plugin name without `target-` prefix"
        else:
            default_namespace = plugin_name.replace("-", "_")
            default_description = "plugin name with underscores instead of dashes"
        click.echo(f"Hit Return to accept the default: {default_description}")
        click.echo()

        namespace = click.prompt(
            click.style("(namespace)", fg="blue"), type=str, default=default_namespace
        )

        click.echo()
        click.echo(
            f"Specify the plugin's {click.style('`pip install` argument', fg='blue')}, for example:"
        )
        click.echo("- PyPI package name:")
        click.echo(f"\t{plugin_name}")
        click.echo("- VCS repository URL:")
        click.echo(f"\tgit+https://gitlab.com/meltano/{plugin_name}.git")
        click.echo("- local directory, in editable/development mode:")
        click.echo(f"\t-e extract/{plugin_name}")
        click.echo()
        click.echo("Default: plugin name as PyPI package name")
        click.echo()

        pip_url = click.prompt(
            click.style("(pip_url)", fg="blue"), type=str, default=plugin_name
        )

        click.echo()
        click.echo(f"Specify the package's {click.style('executable name', fg='blue')}")
        click.echo()
        click.echo("Default: package name derived from `pip_url`")
        click.echo()

        package_name, _ = os.path.splitext(os.path.basename(pip_url))
        executable = click.prompt(
            click.style("(executable)", fg="blue"), default=package_name
        )

        capabilities = []
        if plugin_type == PluginType.EXTRACTORS:
            click.echo()
            click.echo(
                f"Specify the tap's {click.style('supported Singer features', fg='blue')} (executable flags), for example:"
            )
            click.echo("\t`catalog`: supports the `--catalog` flag")
            click.echo("\t`discover`: supports the `--discover` flag")
            click.echo("\t`properties`: supports the `--properties` flag")
            click.echo("\t`state`: supports the `--state` flag")
            click.echo()
            click.echo(
                "To find out what features a tap supports, reference its documentation or try one"
            )
            click.echo(
                "of the tricks under https://meltano.com/docs/contributor-guide.html#how-to-test-a-tap."
            )
            click.echo()
            click.echo("Multiple capabilities can be separated using commas.")
            click.echo()
            click.echo("Default: no capabilities")
            click.echo()

            capabilities = click.prompt(
                click.style("(capabilities)", fg="blue"),
                type=list,
                default=[],
                value_proc=lambda value: [c.strip() for c in value.split(",")],
            )

        settings = []
        if plugin_type in (PluginType.EXTRACTORS, PluginType.LOADERS):
            singer_type = "tap" if plugin_type == PluginType.EXTRACTORS else "target"

            click.echo()
            click.echo(
                f"Specify the {singer_type}'s {click.style('supported settings', fg='blue')} (`config.json` keys)"
            )
            click.echo()
            click.echo("Nested properties can be represented using the `.` seperator,")
            click.echo('e.g. `auth.username` for `{ "auth": { "username": value } }`.')
            click.echo()
            click.echo(
                f"To find out what settings a {singer_type} supports, reference its documentation."
            )
            click.echo()
            click.echo("Multiple setting names (keys) can be separated using commas.")
            click.echo()
            click.echo("Default: no settings")
            click.echo()

            settings = click.prompt(
                click.style("(settings)", fg="blue"),
                type=list,
                default=[],
                value_proc=lambda value: [c.strip() for c in value.split(",")],
            )

        plugin = Plugin(
            plugin_type,
            plugin_name,
            namespace,
            pip_url=pip_url,
            executable=executable,
            capabilities=capabilities,
            settings=[
                {"name": name, "env": setting_env(namespace, name)} for name in settings
            ],
        )

        installed = plugin.as_installed(custom=True)
        return self.config_service.add_to_file(installed)

    def add_related(self, *args, **kwargs):
        return []
