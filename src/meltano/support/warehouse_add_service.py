import re
import os


class WarehouseAddService:
    def __init__(self):
        self.env_file = os.path.join("./", ".env")

    def env_param(self, name, upper=True):
        s = re.sub(r"[^\w\s]", "", name)
        s = re.sub(r"\s+", "_", s)
        return s.upper() if upper else s.lower()

    def header_conf(self, root_name):
        return f"### {root_name}_CONFIGURATION"

    def footer_conf(self, root_name):
        return f"### {root_name}_END_CONFIGURATION"

    def content_replace(self, **kwargs):
        content = self.read_conf()
        regex = re.compile(
            fr"{kwargs['header']}(.*){kwargs['footer']}", re.MULTILINE | re.DOTALL
        )
        result = re.search(regex, content)
        if result is None:
            return f"{self.env_contents(**kwargs)}\n{content}"
        else:
            return content.replace(result.group(0), self.env_contents(**kwargs))

    def env_contents(self, **kwargs):
        return """\
{header}
{root_name}="{name}"
{root_name}_HOST="{host}"
{root_name}_DATABASE="{database}"
{root_name}_SCHEMA="{schema}"
{root_name}_USERNAME="{username}"
{root_name}_PASSWORD="{password}"
{footer}
        """.format(
            **kwargs
        )

    def add_additional_kwargs(self, **kwargs):
        root_name = self.env_param(kwargs["name"])
        kwargs["root_name"] = root_name
        kwargs["header"] = self.header_conf(root_name)
        kwargs["footer"] = self.footer_conf(root_name)
        kwargs["name"] = self.env_param(kwargs["name"], False)
        return kwargs

    def read_conf(self):
        return open(self.env_file, "r").read()

    def add(self, **kwargs):
        kwargs = self.add_additional_kwargs(**kwargs)
        contents = self.content_replace(**kwargs)
        with open(self.env_file, "w") as f:
            f.write(contents)
