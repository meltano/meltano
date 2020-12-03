import logging
import copy
from typing import Dict
from typing import Optional

from meltano.core.behavior.hookable import HookObject
from .base import PluginRef, PluginType, PluginDefinition

logger = logging.getLogger(__name__)


class ProjectPlugin(HookObject, PluginRef):
    def __init__(
        self,
        plugin_type: PluginType,
        name: str,
        namespace: Optional[str] = None,
        custom_definition: Optional["PluginDefinition"] = None,
        variant: Optional[str] = None,
        pip_url: Optional[str] = None,
        config: Optional[dict] = {},
        **extras,
    ):
        if namespace:
            custom_definition = PluginDefinition(
                plugin_type, name, namespace, variant=variant, pip_url=pip_url, **extras
            )
            extras = {}

        if custom_definition:
            # Any properties considered "extra" by the embedded plugin definition
            # should be considered extras of the project plugin, since they are
            # the current values, not default values.
            extras = {**custom_definition.extras, **extras}
            custom_definition.extras = {}

        if "profiles" in extras:
            logger.warning(
                f"Plugin configuration profiles are no longer supported, ignoring `profiles` in '{name}' {plugin_type.descriptor} definition."
            )

        super().__init__(
            plugin_type,
            name,
            # Attributes will be listed in meltano.yml in this order:
            custom_definition=custom_definition,
            variant=variant,
            pip_url=pip_url,
            config=copy.deepcopy(config),
            extras=extras,
        )

        self._flattened.add("custom_definition")

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

    def is_custom(self):
        return self.custom_definition is not None
