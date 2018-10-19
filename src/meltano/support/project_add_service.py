import os
import click
import json
import yaml

class ProjectAddService:
    EXTRACTOR = "extractor"
    LOADER = "loader"

    def __init__(self, plugin_type, plugin_name):

        self.plugin_type = plugin_type
        self.plugin_name = plugin_name
        self.plugin_type_key = f"{self.plugin_type}s"

        self.discovery_file = os.path.join(os.path.dirname(__file__), "discovery.json")
        self.discovery_json = json.load(open(self.discovery_file))

        self.meltano_yml_file = os.path.join("./", "meltano.yml")
        self.meltano_yml = yaml.load(open(self.meltano_yml_file)) or {}

        self.url = self.discovery_json.get(self.plugin_type_key).get(self.plugin_name)

    def add(self):
        extract_dict = self.meltano_yml.get(self.plugin_type)
        if not extract_dict:
            self.meltano_yml[self.plugin_type] = []
            extract_dict = self.meltano_yml.get(self.plugin_type)

        try:
            found_extractor = next(
                (
                    plugin
                    for plugin in extract_dict
                    if plugin["name"] == self.plugin_name
                )
            )
            click.secho(f"{self.plugin_name} is already installed", fg="green")
            click.Abort()
        except Exception:
            if self.url is not None:
                self.add_to_file()
            else:
                click.secho(f"{self.plugin_name} is not supported", fg="red")
                click.Abort()

    def add_to_file(self):
        self.meltano_yml[self.plugin_type].append(
            {"name": self.plugin_name, "url": self.url}
        )
        with open(self.meltano_yml_file, "w") as f:
            f.write(yaml.dump(self.meltano_yml))
        click.secho(f"{self.plugin_name} added to your meltano.yml config", fg="green")
