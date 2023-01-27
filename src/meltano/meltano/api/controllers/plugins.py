"""API Plugin Management Blue Print."""

from __future__ import annotations

import asyncio
import logging

from flask import jsonify, request

from meltano.api.api_blueprint import APIBlueprint
from meltano.api.security.auth import block_if_readonly
from meltano.core.error import PluginInstallError
from meltano.core.plugin import PluginType
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.plugin_discovery_service import (
    PluginDiscoveryService,
    PluginNotFoundError,
)
from meltano.core.plugin_install_service import (
    PluginInstallReason,
    PluginInstallService,
)
from meltano.core.project import Project
from meltano.core.project_add_service import ProjectAddService
from meltano.core.project_plugins_service import ProjectPluginsService


def plugin_def_json(plugin_def):
    """Convert plugin defenition to json.

    Args:
        plugin_def: Plugin definition

    Returns:
        JSON of the plugin's definition
    """
    return {
        "name": plugin_def.name,
        "namespace": plugin_def.namespace,
        "hidden": plugin_def.hidden,
        "label": plugin_def.label,
        "logo_url": plugin_def.logo_url,
        "description": plugin_def.description,
        "variants": [
            {
                "name": v.name,  # noqa: WPS111
                "default": i == 0,  # noqa: WPS111
                "deprecated": v.deprecated,
            }
            for i, v in enumerate(plugin_def.variants)  # noqa: WPS111
        ],
    }


plugins_bp = APIBlueprint("plugins", __name__)  # noqa: N816


@plugins_bp.errorhandler(PluginInstallError)
def _handle(ex):
    return (jsonify({"error": True, "code": str(ex)}), 502)


@plugins_bp.route("/all", methods=["GET"])  # noqa: WPS125
def all():
    """Plugins found by the PluginDiscoveryService.

    Returns:
        Json containing all the discovered plugins.
    """
    project = Project.find()
    discovery = PluginDiscoveryService(project)

    all_plugins = {
        plugin_type: [plugin_def_json(plugin_def) for plugin_def in plugin_defs]
        for plugin_type, plugin_defs in discovery.plugins_by_type().items()
    }

    return jsonify(all_plugins)


@plugins_bp.route("/installed", methods=["GET"])
def installed():
    """All plugins installed in the project.

    Returns:
        Json of all installed plugins.
    """
    project = Project.find()
    plugins_service = ProjectPluginsService(project)

    def _plugin_json(plugin: ProjectPlugin):
        plugin_json = {"name": plugin.name}

        try:
            plugin_json.update(plugin_def_json(plugin))

            plugin_json["variant"] = plugin.variant
            plugin_json["docs"] = plugin.docs
        except PluginNotFoundError:
            pass

        return plugin_json

    installed_plugins = {
        plugin_type: [_plugin_json(plugin) for plugin in plugins]
        for plugin_type, plugins in plugins_service.plugins_by_type().items()
    }

    return jsonify(installed_plugins)


@plugins_bp.route("/add", methods=["POST"])
@block_if_readonly
def add():
    """Add Plugin the the project file.

    Returns:
        JSON of the plugin information added.
    """
    payload = request.get_json()
    plugin_type = PluginType(payload["plugin_type"])
    plugin_name = payload["name"]
    variant = payload.get("variant", None)

    project = Project.find()
    add_service = ProjectAddService(project)
    plugin = add_service.add(plugin_type, plugin_name, variant=variant)

    return jsonify(plugin.canonical())


@plugins_bp.route("/install/batch", methods=["POST"])
@block_if_readonly
def install_batch():  # noqa: WPS210
    """Install multiple plugins at once.

    Raises:
        PluginInstallError: Plugin insatllation error message.

    Returns:
        JSON cotaining all plugins installed.
    """
    payload = request.get_json()
    project = Project.find()

    plugins_service = ProjectPluginsService(project)
    plugin = plugins_service.find_plugin(
        payload["name"], plugin_type=PluginType(payload["plugin_type"])
    )

    add_service = ProjectAddService(project, plugins_service=plugins_service)
    required_plugins = add_service.add_required(plugin)

    # This was added to assist api_worker threads
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        logging.debug("/plugins/install/batch no asyncio event loop detected")
        asyncio.set_event_loop(asyncio.new_event_loop())

    install_service = PluginInstallService(project, plugins_service=plugins_service)
    install_results = install_service.install_plugins(
        required_plugins, reason=PluginInstallReason.ADD
    )

    for result in install_results:
        if not result.successful:
            raise PluginInstallError(result.message)

    return jsonify([plugin.canonical() for plugin in required_plugins])


@plugins_bp.route("/install", methods=["POST"])
@block_if_readonly
def install():
    """Install a plugin.

    Returns:
        JSON containing the plugin installed.
    """
    payload = request.get_json()
    plugin_type = PluginType(payload["plugin_type"])
    plugin_name = payload["name"]

    project = Project.find()

    plugins_service = ProjectPluginsService(project)
    plugin = plugins_service.find_plugin(plugin_name, plugin_type=plugin_type)

    # This was added to assist api_worker threads
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        logging.debug("/plugins/install no asyncio event loop detected")
        asyncio.set_event_loop(asyncio.new_event_loop())

    install_service = PluginInstallService(project, plugins_service=plugins_service)
    install_service.install_plugin(plugin, reason=PluginInstallReason.ADD)

    return jsonify(plugin.canonical())
