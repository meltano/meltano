import os
import json
import yaml


class PluginNotSupportedException(Exception):
    pass


class ProjectMissingYMLFileException(Exception):
    pass


class ProjectAddService:
    EXTRACTOR = "extractor"
    LOADER = "loader"

    def __init__(self, plugin_type, plugin_name):
        self.plugin_type = plugin_type
        self.plugin_name = plugin_name

        self.discovery_file = os.path.join(os.path.dirname(__file__), "discovery.json")
        self.discovery_json = json.load(open(self.discovery_file))
        self.meltano_yml_file = os.path.join("./", "meltano.yml")

        try:
            self.meltano_yml = yaml.load(open(self.meltano_yml_file)) or {}
        except Exception as e:
            raise ProjectMissingYMLFileException()
        self.url = self.discovery_json.get(self.plugin_type).get(self.plugin_name)

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

        except Exception as e:
            if self.url is not None:
                self.add_to_file()
                return True
            else:
                raise PluginNotSupportedException()

    def add_to_file(self):
        self.meltano_yml[self.plugin_type].append(
            {"name": self.plugin_name, "url": self.url}
        )
        with open(self.meltano_yml_file, "w") as f:
            f.write(yaml.dump(self.meltano_yml))
