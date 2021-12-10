from meltano.core.plugin import PluginRef
from werkzeug.routing import PathConverter


class PluginRefConverter(PathConverter):
    def to_url(self, value):
        return "/".join([value.type, value.name])

    def to_python(self, value):
        return PluginRef(*value.split("/"))
