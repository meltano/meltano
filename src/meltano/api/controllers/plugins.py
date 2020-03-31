from itertools import groupby
from flask import request, jsonify, g

from meltano.core.error import PluginInstallError
from meltano.core.plugin_discovery_service import (
    PluginDiscoveryService,
    PluginNotFoundError,
)
from meltano.core.plugin import PluginType
from meltano.core.project import Project
from meltano.core.project_add_service import ProjectAddService
from meltano.core.config_service import ConfigService
from meltano.core.plugin_install_service import PluginInstallService
from flask_security import roles_required
from meltano.api.api_blueprint import APIBlueprint


pluginsBP = APIBlueprint("plugins", __name__)


@pluginsBP.errorhandler(PluginInstallError)
def _handle(ex):
    return (jsonify({"error": True, "code": str(ex)}), 502)


@pluginsBP.route("/all", methods=["GET"])
def all():
    project = Project.find()
    discovery = PluginDiscoveryService(project)
    ordered_plugins = {}

    for type, plugins in groupby(discovery.plugins(), key=lambda p: p.type):
        canonical_plugins = []
        for plugin in plugins:
            canonical_plugin = plugin.canonical()

            # let's remove all the settings related data
            canonical_plugin.pop("settings", None)
            canonical_plugin.pop("settings_group_validation", None)

            canonical_plugins.append(canonical_plugin)

        ordered_plugins[type] = canonical_plugins

    return jsonify(ordered_plugins)


@pluginsBP.route("/installed", methods=["GET"])
def installed():
    """Returns JSON of all installed plugins

    Fuses the discovery.yml data with meltano.yml data and sorts each type alphabetically by name
    """

    project = Project.find()
    config = ConfigService(project)
    discovery = PluginDiscoveryService(project)
    installed_plugins = {}

    # merge definitions
    for plugin in sorted(config.plugins(), key=lambda x: x.name):
        try:
            definition = discovery.find_plugin(plugin.type, plugin.name)
            merged_plugin_definition = {**definition.canonical(), **plugin.canonical()}
        except PluginNotFoundError:
            merged_plugin_definition = {**plugin.canonical()}

        merged_plugin_definition.pop("settings", None)
        merged_plugin_definition.pop("select", None)

        if not plugin.type in installed_plugins:
            installed_plugins[plugin.type] = []

        installed_plugins[plugin.type].append(merged_plugin_definition)

    return jsonify({**project.meltano.canonical(), "plugins": installed_plugins})


@pluginsBP.route("/add", methods=["POST"])
@roles_required("admin")
def add():
    payload = request.get_json()
    plugin_type = PluginType(payload["plugin_type"])
    plugin_name = payload["name"]

    project = Project.find()
    add_service = ProjectAddService(project)
    plugin = add_service.add(plugin_type, plugin_name)

    return jsonify(plugin.canonical())


@pluginsBP.route("/install/batch", methods=["POST"])
@roles_required("admin")
def install_batch():
    payload = request.get_json()
    plugin_type = PluginType(payload["plugin_type"])
    plugin_name = payload["name"]

    project = Project.find()

    # We use the DiscoveryService rather than the ConfigService because the
    # plugin may not actually be installed yet at this point.
    discovery = PluginDiscoveryService(project)
    plugin = discovery.find_plugin(plugin_type, plugin_name)

    add_service = ProjectAddService(project)
    related_plugins = add_service.add_related(plugin)

    install_service = PluginInstallService(project)
    install_service.install_plugins(related_plugins)

    return jsonify([plugin.canonical() for plugin in related_plugins])


@pluginsBP.route("/install", methods=["POST"])
@roles_required("admin")
def install():
    payload = request.get_json()
    plugin_type = PluginType(payload["plugin_type"])
    plugin_name = payload["name"]

    project = Project.find()

    config_service = ConfigService(project)
    plugin = config_service.find_plugin(plugin_name, plugin_type=plugin_type)

    install_service = PluginInstallService(project)
    install_service.install_plugin(plugin)

    return jsonify(plugin.canonical())
