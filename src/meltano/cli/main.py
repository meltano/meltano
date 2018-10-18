import shutil
import os
import click
import yaml, json

from meltano.support.utils import setup_logging
from .params import db_options

EXTRACTORS = "extractors"
LOADERS = "loaders"

discovery_file = os.path.join(os.path.dirname(__file__), "discovery.json")
discovery_json = json.load(open(discovery_file))

@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    setup_logging()
    if ctx.invoked_subcommand is None:
      install()

def install():
    meltano_yml_file = os.path.join("./", "meltano.yml")
    meltano_yml = yaml.load(open(meltano_yml_file))
    click.secho('Updating from meltano.yml', fg="green")
    extractors = meltano_yml.get(EXTRACTORS)
    loaders = meltano_yml.get(LOADERS)
    cache_plugins(EXTRACTORS, cache_plugin_url(EXTRACTORS, extractors))
    cache_plugins(LOADERS, cache_plugin_url(LOADERS, loaders))

def cache_plugin_url(plugin_type, plugins_definitions):
  for plugin in plugins_definitions:
    url = ""
    if plugin.get('url') is None:
      plugin_type_discovery_dict = discovery_json.get(plugin_type)
      plugin_name = plugin.get('name')
      if plugin_name is None:
        raise click.ClickException(f'Meltano.yml file error: All {plugin_type} must have at least a name field')
      yield plugin_type_discovery_dict.get(plugin_name)
    else:
      yield plugin.get('url')

def cache_plugins(plugin_type, plugin_urls):
  meltano_hidden_dir = os.path.join("./", ".meltano", plugin_type)
  shutil.rmtree(meltano_hidden_dir)
  os.makedirs(meltano_hidden_dir, exist_ok=True)


