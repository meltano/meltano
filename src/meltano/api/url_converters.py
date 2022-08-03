from __future__ import annotations

from werkzeug.routing import PathConverter

from meltano.core.plugin import PluginRef


class PluginRefConverter(PathConverter):
    def to_url(self, value):
        return "/".join([value.type, value.name])

    def to_python(self, value):
        return PluginRef(*value.split("/"))
