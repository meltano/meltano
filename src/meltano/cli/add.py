import os
import yaml
import json
import click
from urllib.parse import urlparse
from . import cli

EXTRACTOR = "extractor"
LOADER = "loader"

discovery_file = os.path.join(os.path.dirname(__file__), "discovery.json")
meltano_yml_file = os.path.join("./", "meltano.yml")
meltano_yml = yaml.load(open(meltano_yml_file))
discovery_json = json.load(open(discovery_file))

@cli.command()
@click.argument("plugin_type", type=click.Choice([EXTRACTOR, LOADER]))
@click.argument("plugin_name")
def add(plugin_type, plugin_name):
    EXTRACTORS = "extractors"
    LOADERS = "loaders"
    if plugin_type == EXTRACTOR:
        check_add_to_file(EXTRACTORS, plugin_name)
    else:
        check_add_to_file(LOADERS, plugin_name)

def check_add_to_file(plugin_type, name):
  extract_dict = meltano_yml.get(plugin_type)
  if not extract_dict:
    meltano_yml[plugin_type] = []
    extract_dict = meltano_yml.get(plugin_type)
  try:
    found_extractor = next((plugin for plugin in extract_dict if plugin["name"] == name))
    click.secho(f"{name} is already installed", fg="green")
    click.Abort()
  except Exception as e:
    found_plugin = (discovery_json.get(plugin_type).get(name))
    if found_plugin is not None:
      add_to_file(plugin_type, name)
    else:
      click.secho(f"{name.title()} is not supported", fg="red")
      click.Abort()

def add_to_file(section, name):
  meltano_yml[section].append({'name': name})
  with open(meltano_yml_file, "w") as f:
    f.write(yaml.dump(meltano_yml))
  click.secho(f"{name} added to your meltano.yml config", fg="green")