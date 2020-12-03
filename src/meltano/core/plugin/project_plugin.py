import copy
import logging
from typing import Optional

from meltano.core.setting_definition import SettingDefinition
from meltano.core.utils import flatten, uniques_in

from .base import PluginDefinition, PluginRef, PluginType, Variant
from .factory import base_plugin_factory

logger = logging.getLogger(__name__)


class CyclicInheritanceError(Exception):
    def __init__(self, plugin: "ProjectPlugin", ancestor: "ProjectPlugin"):
        self.plugin = plugin
        self.ancestor = ancestor

        super().__init__(
            f"{plugin.type.descriptor.capitalize()} '{plugin.name}' cannot inherit from '{ancestor.name}', which itself inherits from '{plugin.name}'."
        )


class ProjectPlugin(PluginRef):
    def __init__(
        self,
        plugin_type: PluginType,
        name: str,
        inherit_from: Optional[str] = None,
        namespace: Optional[str] = None,
        variant: Optional[str] = None,
        pip_url: Optional[str] = None,
        config: Optional[dict] = {},
        **extras,
    ):
        super().__init__(plugin_type, name)

        # Attributes will be listed in meltano.yml in the order they are set on self:
        self.inherit_from = (
            inherit_from if inherit_from and inherit_from != name else None
        )

        # If a custom definition is provided, its properties will come before all others in meltano.yml
        self.custom_definition = None
        self._flattened.add("custom_definition")

        self._parent = None
        if not self.inherit_from and namespace:
            # When not explicitly inheriting, a namespace indicates an embedded custom plugin definition
            self.custom_definition = PluginDefinition(
                plugin_type, name, namespace, variant=variant, pip_url=pip_url, **extras
            )

            # Any properties considered "extra" by the embedded plugin definition
            # should be considered extras of the project plugin, since they are
            # the current values, not default values.
            extras = self.custom_definition.extras
            self.custom_definition.extras = {}

            # Typically, the parent is set from ProjectPluginsService.current_plugins,
            # where we have access to the discoverable plugin definitions coming from
            # PluginDiscoveryService, but here we can set the parent directly.
            self.parent = base_plugin_factory(self.custom_definition, variant)

        # These properties are also set on the parent, but can be overridden
        self.namespace = namespace
        self.set_presentation_attrs(extras)
        self.variant = variant
        self.pip_url = pip_url

        self._fallbacks.update(["logo_url", "description", "variant", "pip_url"])

        # If no variant is set, we fall back on the original one
        self._defaults["variant"] = lambda _: Variant.ORIGINAL_NAME

        if self.inherit_from:
            # When explicitly inheriting from a project plugin or discoverable definition,
            # derive default values from our own name
            self._defaults["namespace"] = lambda p: p.name.replace("-", "_")
            self._defaults["label"] = (
                lambda p: f"{p.parent.label}: {p.name}" if p.parent else p.name
            )
        else:
            # When shadowing a discoverable definition with the same name (no `inherit_from`),
            # or an embedded custom definition (with `namespace`), fall back on parent's
            # values derived from its name instead
            self._fallbacks.update(["namespace", "label"])

        self.config = copy.deepcopy(config)
        self.extras = extras

        if "profiles" in extras:
            logger.warning(
                f"Plugin configuration profiles are no longer supported, ignoring `profiles` in '{name}' {plugin_type.descriptor} definition."
            )

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, new_parent):
        ancestor = new_parent
        while isinstance(ancestor, self.__class__):
            if ancestor == self:
                raise CyclicInheritanceError(self, ancestor)

            ancestor = ancestor.parent

        self._parent = new_parent
        self._fallback_to = new_parent

    @property
    def info(self):
        return {"name": self.name, "namespace": self.namespace, "variant": self.variant}

    @property
    def info_env(self):
        # MELTANO_EXTRACTOR_...
        return flatten({"meltano": {self.type.singular: self.info}}, "env_var")

    def env_prefixes(self, for_writing=False):
        prefixes = [self.name, self.namespace]

        if for_writing:
            prefixes.extend(self._parent.env_prefixes(for_writing=True))
            prefixes.append(f"meltano_{self.type.verb}"),  # MELTANO_EXTRACT_...

        return uniques_in(prefixes)

    @property
    def extra_config(self):
        return {f"_{k}": v for k, v in self.extras.items()}

    @property
    def config_with_extras(self):
        return {**self.config, **self.extra_config}

    @config_with_extras.setter
    def config_with_extras(self, new_config_with_extras):
        self.config.clear()
        self.extras.clear()

        for k, v in new_config_with_extras.items():
            if k.startswith("_"):
                self.extras[k[1:]] = v
            else:
                self.config[k] = v

    @property
    def settings(self):
        existing_settings = self._parent.settings
        return [
            *existing_settings,
            *SettingDefinition.from_missing(existing_settings, self.config),
        ]

    @property
    def extra_settings(self):
        existing_settings = self._parent.extra_settings
        return [
            *existing_settings,
            *SettingDefinition.from_missing(existing_settings, self.extra_config),
        ]

    @property
    def settings_with_extras(self):
        return [*self.settings, *self.extra_settings]

    def is_custom(self):
        return self.custom_definition is not None

    @property
    def is_shadowing(self):
        return not self.inherit_from
