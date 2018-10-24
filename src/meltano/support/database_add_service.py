import re
import os
import yaml


class DatabaseAddService:
    def __init__(self):
        self.meltano_secret_dir = os.path.join("./", ".meltano")

    def environmentalize(self, name, upper=True):
        s = re.sub(r"[^\w\s]", "", name)
        s = re.sub(r"\s+", "_", s)
        return s.upper() if upper else s.lower()

    def get_db_vars_file_path(self, **kwargs):
        return os.path.join(
            self.meltano_secret_dir, f".database_{kwargs['root_name'].lower()}.yml"
        )

    def add_additional_kwargs(self, **kwargs):
        root_name = self.environmentalize(kwargs["name"])
        kwargs["root_name"] = root_name
        kwargs["name"] = self.environmentalize(kwargs["name"], False)
        return kwargs

    def add(self, **kwargs):
        kwargs = self.add_additional_kwargs(**kwargs)

        with open(self.get_db_vars_file_path(**kwargs), "w") as f:
            f.write(yaml.dump(kwargs))
