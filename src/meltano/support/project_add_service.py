import os
import json
import yaml

from .project import Project


class PluginNotSupportedException(Exception):
    pass


class MissingPluginException(Exception):
    pass


class ProjectAddService:
    EXTRACTOR = "extractor"
    LOADER = "loader"

    def __init__(self, project: Project,
                 plugin_type=None,
                 plugin_name=None):
        self.project = project
        self.plugin_type = plugin_type
        self.plugin_name = plugin_name

        self.discovery_file = os.path.join(os.path.dirname(__file__), "discovery.json")
        self.discovery_json = json.load(open(self.discovery_file))

        try:
            self.meltano_yml = yaml.load(open(self.project.meltanofile)) or {}
        except Exception as e:
            self.project.meltanofile.open("a").close()
            self.meltano_yml = yaml.load(open(self.project.meltanofile)) or {}
            
        if self.plugin_type:
            self.url = self.discovery_json.get(self.plugin_type, {}).get(self.plugin_name)

    def add(self):
        if not self.plugin_name or not self.plugin_type:
            raise MissingPluginException("Plugin type or plugin name is not set")

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

        except Exception as e:
            if self.url is not None:
                self.add_to_file()
            else:
                raise PluginNotSupportedException()

    def add_to_file(self):
        self.meltano_yml[self.plugin_type].append(
            {"name": self.plugin_name, "url": self.url}
        )
        with open(self.project.meltanofile, "w") as f:
            f.write(yaml.dump(self.meltano_yml))
