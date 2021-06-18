import json
import logging
import os

from meltano.core.behavior.hookable import hook
from meltano.core.db import project_engine
from meltano.core.plugin import BasePlugin
from meltano.core.project import Project
from meltano.core.utils import nest_object


class SingerPlugin(BasePlugin):
    def process_config(self, flat_config):
        non_null_config = {k: v for k, v in flat_config.items() if v is not None}
        processed_config = nest_object(non_null_config)
        # Result at this point will contain duplicate entries for nested config
        # options. We need to pop those redundant entries recursively.

        def _pop_non_leaf_keys(nested_config: dict) -> None:  # noqa: WPS430
            """Recursively pop dictionary entries with '.' in their keys."""
            for key, val in list(nested_config.items()):
                if "." in key:
                    nested_config.pop(key)
                elif isinstance(val, dict):  # noqa: WPS220
                    _pop_non_leaf_keys(val)

        _pop_non_leaf_keys(processed_config)
        return processed_config

    @hook("before_configure")
    def before_configure(self, invoker, session):
        config_path = invoker.files["config"]
        with open(config_path, "w") as config_file:
            config = invoker.plugin_config_processed
            json.dump(config, config_file, indent=2)

        logging.debug(f"Created configuration at {config_path}")

    @hook("before_cleanup")
    def before_cleanup(self, invoker):
        config_path = invoker.files["config"]
        config_path.unlink()
        logging.debug(f"Deleted configuration at {config_path}")
