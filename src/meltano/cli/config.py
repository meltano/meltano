import click
from . import cli
from .params import project, db_options

from meltano.core.db import project_engine
from meltano.core.project import Project
from meltano.core.config_service import ConfigService
from meltano.core.plugin.settings_service import PluginSettingsService

@cli.command()
@project
@click.argument("plugin_name")
@db_options
def config(project, plugin_name, engine_uri):
    config = ConfigService(project)
    plugin = config.get_plugin(plugin_name)

    _, Session = project_engine(project, engine_uri, default=True)
    session = Session()
    try:
        settings = PluginSettingsService(session, project, plugin)
        print(settings.as_config())
    finally:
        session.close()
