import re
import os
import yaml


class DatabaseAddService:
    def __init__(self):
        self.env_file = os.path.join("./", ".meltano")

    def env_param(self, name, upper=True):
        s = re.sub(r"[^\w\s]", "", name)
        s = re.sub(r"\s+", "_", s)
        return s.upper() if upper else s.lower()

    def get_env_file_path(self, **kwargs):
        return os.path.join(self.env_file, f".database_{kwargs['root_name'].lower()}.yml")

    def add_additional_kwargs(self, **kwargs):
        root_name = self.env_param(kwargs["name"])
        kwargs["root_name"] = root_name
        kwargs["name"] = self.env_param(kwargs["name"], False)
        return kwargs

    def add(self, **kwargs):
        kwargs = self.add_additional_kwargs(**kwargs)

        with open(self.get_env_file_path(**kwargs), "w") as f:
            f.write(yaml.dump(kwargs))
