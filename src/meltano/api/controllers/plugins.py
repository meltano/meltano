from flask import request, jsonify, g

from meltano.core.error import PluginInstallError
from meltano.core.plugin_discovery_service import (
    PluginDiscoveryService,
    PluginNotFoundError,
)
from meltano.core.plugin import PluginType, ProjectPlugin
from meltano.core.project import Project
from meltano.core.project_add_service import ProjectAddService
from meltano.core.config_service import ConfigService
from meltano.core.plugin_install_service import (
    PluginInstallService,
    PluginInstallReason,
)
from flask_security import roles_required
from meltano.api.api_blueprint import APIBlueprint
from meltano.api.security.auth import block_if_readonly


def plugin_def_json(plugin_def):
    return {
        "name": plugin_def.name,
        "namespace": plugin_def.namespace,
        "hidden": plugin_def.hidden,
        "label": plugin_def.label,
        "logo_url": plugin_def.logo_url,
        "description": plugin_def.description,
        "variants": [
            {"name": v.name, "default": i == 0, "deprecated": v.deprecated}
            for i, v in enumerate(plugin_def.variants)
        ],
    }


pluginsBP = APIBlueprint("plugins", __name__)


@pluginsBP.errorhandler(PluginInstallError)
def _handle(ex):
    return (jsonify({"error": True, "code": str(ex)}), 502)


@pluginsBP.route("/all", methods=["GET"])
def all():
    project = Project.find()
    discovery = PluginDiscoveryService(project)

    all_plugins = {
        plugin_type: [plugin_def_json(plugin_def) for plugin_def in plugin_defs]
        for plugin_type, plugin_defs in discovery.plugins_by_type().items()
    }

    return jsonify(all_plugins)


@pluginsBP.route("/installed", methods=["GET"])
def installed():
    project = Project.find()
    config = ConfigService(project)
    discovery = PluginDiscoveryService(project)

    def plugin_json(plugin: ProjectPlugin):
        plugin_json = {"name": plugin.name}

        try:
            plugin_def = discovery.get_definition(plugin)

            plugin_json.update(plugin_def_json(plugin_def))

            plugin_json["variant"] = plugin_def.current_variant_name
            plugin_json["docs"] = plugin_def.docs
        except PluginNotFoundError:
            pass

        return plugin_json

    installed_plugins = {
        plugin_type: [plugin_json(plugin) for plugin in plugins]
        for plugin_type, plugins in config.plugins_by_type().items()
    }

    return jsonify(installed_plugins)


@pluginsBP.route("/add", methods=["POST"])
@block_if_readonly
def add():
    payload = request.get_json()
    plugin_type = PluginType(payload["plugin_type"])
    plugin_name = payload["name"]
    variant = payload.get("variant", None)

    project = Project.find()
    add_service = ProjectAddService(project)
    plugin = add_service.add(plugin_type, plugin_name, variant=variant)

    return jsonify(plugin.canonical())


@pluginsBP.route("/install/batch", methods=["POST"])
@block_if_readonly
def install_batch():
    payload = request.get_json()
    plugin_type = PluginType(payload["plugin_type"])
    plugin_name = payload["name"]

    project = Project.find()

    config_service = ConfigService(project)
    plugin = config_service.find_plugin(plugin_name, plugin_type=plugin_type)

    add_service = ProjectAddService(project)
    related_plugins = add_service.add_related(plugin)

    # We will install the plugins in reverse order, since dependencies
    # are listed after their dependents in `related_plugins`, but should
    # be installed first.
    related_plugins.reverse()

    install_service = PluginInstallService(project)
    install_status = install_service.install_plugins(
        related_plugins, reason=PluginInstallReason.ADD
    )

    for error in install_status["errors"]:
        raise PluginInstallError(error["message"])

    return jsonify([plugin.canonical() for plugin in related_plugins])


@pluginsBP.route("/install", methods=["POST"])
@block_if_readonly
def install():
    payload = request.get_json()
    plugin_type = PluginType(payload["plugin_type"])
    plugin_name = payload["name"]

    project = Project.find()

    config_service = ConfigService(project)
    plugin = config_service.find_plugin(plugin_name, plugin_type=plugin_type)

    install_service = PluginInstallService(project)
    install_service.install_plugin(plugin, reason=PluginInstallReason.ADD)

    return jsonify(plugin.canonical())
