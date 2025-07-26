"""YAML style configuration management."""

from __future__ import annotations

import os
import typing as t
from dataclasses import dataclass, field
from pathlib import Path

from ruamel.yaml import YAML

if t.TYPE_CHECKING:
    from ruamel.yaml import CommentedMap


@dataclass
class YamlIndent:
    """YAML indentation configuration."""

    mapping: int = 2
    sequence: int = 4
    offset: int = 2

    def __post_init__(self) -> None:
        """Validate indentation values."""
        for name, value in [
            ("mapping", self.mapping),
            ("sequence", self.sequence),
            ("offset", self.offset),
        ]:
            if not isinstance(value, int) or not (1 <= value <= 10):
                msg = (
                    f"yaml.indent.{name} must be an integer between 1 and 10, "
                    f"got {value}"
                )
                raise ValueError(msg)


@dataclass
class YamlStyleConfig:
    """YAML style configuration."""

    indent: YamlIndent = field(default_factory=YamlIndent)
    width: int = 80
    preserve_quotes: bool = True
    compact_sequences: bool = False

    def __post_init__(self) -> None:
        """Validate configuration values."""
        if not isinstance(self.width, int) or not (40 <= self.width <= 200):
            msg = f"yaml.width must be an integer between 40 and 200, got {self.width}"
            raise ValueError(msg)

        if not isinstance(self.preserve_quotes, bool):
            msg = f"yaml.preserve_quotes must be a boolean, got {self.preserve_quotes}"
            raise ValueError(msg)

        if not isinstance(self.compact_sequences, bool):
            msg = f"yaml.compact_sequences must be a boolean, got {self.compact_sequences}"
            raise ValueError(msg)

    @classmethod
    def from_dict(cls, data: dict[str, t.Any]) -> YamlStyleConfig:
        """Create YamlStyleConfig from dictionary data."""
        indent_data = data.get("indent", {})
        indent = (
            YamlIndent(
                **{
                    k: v
                    for k, v in indent_data.items()
                    if k in {"mapping", "sequence", "offset"}
                }
            )
            if isinstance(indent_data, dict)
            else YamlIndent()
        )

        return cls(
            indent=indent,
            width=data.get("width", 80),
            preserve_quotes=data.get("preserve_quotes", True),
            compact_sequences=data.get("compact_sequences", False),
        )

    def merge(self, other: YamlStyleConfig) -> YamlStyleConfig:
        """Merge this configuration with another, giving precedence to the other."""
        return other


class YamlConfigLoader:
    """Loads and manages YAML style configuration from multiple sources."""

    def __init__(self) -> None:
        """Initialize the configuration loader."""
        self._yaml = YAML(typ="safe")
        self._cache: dict[str, YamlStyleConfig] = {}

    def _load_config_with_fallback(
        self, data: dict[str, t.Any], config_path: str
    ) -> YamlStyleConfig:
        """Load YAML config with fallback to defaults on error."""
        try:
            return YamlStyleConfig.from_dict(data)
        except Exception as e:
            import warnings

            warnings.warn(
                f"Invalid YAML style configuration in {config_path}: {e}. "
                "Using default YAML styling.",
                stacklevel=3,
            )
            return YamlStyleConfig()

    def _get_user_config_path(self) -> Path | None:
        """Get the path to the user configuration file."""
        # Check environment variable override
        if config_file := os.environ.get("MELTANO_CONFIG_FILE"):
            path = Path(config_file)
            return path if path.exists() else None

        # Check primary location: ~/.meltanorc
        meltanorc_path = Path.home() / ".meltanorc"
        if meltanorc_path.exists():
            return meltanorc_path

        # Check fallback XDG Base Directory spec location
        if xdg_config_home := os.environ.get("XDG_CONFIG_HOME"):
            path = Path(xdg_config_home) / "meltano" / "config.yml"
        else:
            path = Path.home() / ".config" / "meltano" / "config.yml"

        return path if path.exists() else None

    def _load_user_config_raw(self) -> dict[str, t.Any]:
        """Load raw user configuration data from file."""
        config_path = self._get_user_config_path()
        if not config_path:
            return {}

        # Check cache using file path and modification time to handle changes
        try:
            mtime = config_path.stat().st_mtime
            cache_key = f"user_raw:{config_path}:{mtime}"
            if cache_key in self._cache:
                return self._cache[cache_key]

            # Clear old cache entries for this file
            keys_to_remove = [
                k for k in self._cache if k.startswith(f"user_raw:{config_path}:")
            ]
            for key in keys_to_remove:
                del self._cache[key]
        except OSError:
            # File doesn't exist or can't be accessed
            return {}

        try:
            with config_path.open() as f:
                data = self._yaml.load(f) or {}

            self._cache[cache_key] = data
            return data
        except Exception as e:
            # Log warning but don't fail - fall back to empty dict
            import warnings

            warnings.warn(
                f"Failed to load configuration from {config_path}: {e}. "
                "Using default configuration.",
                stacklevel=2,
            )
            return {}

    def _load_user_config(self) -> YamlStyleConfig:
        """Load user YAML style configuration from file."""
        data = self._load_user_config_raw()
        yaml_config = data.get("yaml", {})
        return self._load_config_with_fallback(yaml_config, "user config")

    def get_plugin_config(self, plugin_type: str, plugin_name: str) -> dict[str, t.Any]:
        """Get plugin configuration from user config file."""
        data = self._load_user_config_raw()
        try:
            return data["plugins"][plugin_type][plugin_name]
        except (KeyError, TypeError):
            return {}

    def has_plugin_config(self, plugin_type: str, plugin_name: str) -> bool:
        """Check if plugin configuration exists in user config."""
        return bool(self.get_plugin_config(plugin_type, plugin_name))

    def _load_project_config(
        self, project_data: CommentedMap | None = None
    ) -> YamlStyleConfig:
        """Load project-level YAML style configuration."""
        if not project_data:
            return YamlStyleConfig()

        yaml_style_data = project_data.get("yaml_style", {})
        return (
            self._load_config_with_fallback(yaml_style_data, "meltano.yml")
            if yaml_style_data
            else YamlStyleConfig()
        )

    def _load_environment_config(
        self,
        project_data: CommentedMap | None = None,
        environment_name: str | None = None,
    ) -> YamlStyleConfig:
        """Load environment-specific YAML style configuration."""
        if not project_data or not environment_name:
            return YamlStyleConfig()

        for env in project_data.get("environments", []):
            if env.get("name") == environment_name:
                yaml_style_data = env.get("yaml_style", {})
                return (
                    self._load_config_with_fallback(
                        yaml_style_data, f"environment '{environment_name}'"
                    )
                    if yaml_style_data
                    else YamlStyleConfig()
                )

        return YamlStyleConfig()

    def _load_env_vars_config(self) -> YamlStyleConfig:
        """Load configuration from environment variables."""
        config_data = {}

        # Load width
        if width := os.environ.get("MELTANO_YAML_WIDTH"):
            try:
                config_data["width"] = int(width)
            except ValueError:
                import warnings

                warnings.warn(
                    f"Invalid MELTANO_YAML_WIDTH value: {width}", stacklevel=2
                )

        # Load boolean settings
        bool_values = ("true", "1", "yes")
        for env_var, key in [
            ("MELTANO_YAML_PRESERVE_QUOTES", "preserve_quotes"),
            ("MELTANO_YAML_COMPACT_SEQUENCES", "compact_sequences"),
        ]:
            if value := os.environ.get(env_var):
                config_data[key] = value.lower() in bool_values

        # Load indent settings
        indent_data = {}
        for env_suffix, key in [
            ("MAPPING", "mapping"),
            ("SEQUENCE", "sequence"),
            ("OFFSET", "offset"),
        ]:
            if value := os.environ.get(f"MELTANO_YAML_INDENT_{env_suffix}"):
                try:
                    indent_data[key] = int(value)
                except ValueError:
                    import warnings

                    warnings.warn(
                        f"Invalid MELTANO_YAML_INDENT_{env_suffix} value: {value}",
                        stacklevel=2,
                    )

        if indent_data:
            config_data["indent"] = indent_data

        if not config_data:
            return YamlStyleConfig()

        try:
            return YamlStyleConfig.from_dict(config_data)
        except Exception as e:
            import warnings

            warnings.warn(
                f"Invalid environment variable YAML configuration: {e}",
                stacklevel=2,
            )
            return YamlStyleConfig()

    def load_config(
        self,
        project_data: CommentedMap | None = None,
        environment_name: str | None = None,
    ) -> YamlStyleConfig:
        """Load complete YAML style configuration with proper precedence."""
        # Start with user configuration (lowest precedence)
        config = self._load_user_config()

        # Apply project-level configuration
        project_config = self._load_project_config(project_data)
        if project_config != YamlStyleConfig():  # Only merge if non-default
            config = config.merge(project_config)

        # Apply environment-specific configuration
        env_config = self._load_environment_config(project_data, environment_name)
        if env_config != YamlStyleConfig():  # Only merge if non-default
            config = config.merge(env_config)

        # Apply environment variables (highest precedence)
        env_vars_config = self._load_env_vars_config()
        if env_vars_config != YamlStyleConfig():  # Only merge if non-default
            config = config.merge(env_vars_config)

        return config


# Global instance for configuration loading
_config_loader = YamlConfigLoader()


def load_yaml_style_config(
    project_data: CommentedMap | None = None,
    environment_name: str | None = None,
) -> YamlStyleConfig:
    """Load YAML style configuration from all sources with proper precedence."""
    return _config_loader.load_config(project_data, environment_name)


def get_user_plugin_config(plugin_type: str, plugin_name: str) -> dict[str, t.Any]:
    """Get plugin configuration from user config file.

    Args:
        plugin_type: The plugin type (e.g., "extractors", "loaders")
        plugin_name: The plugin name (e.g., "tap-github", "target-postgres")

    Returns:
        Dictionary of plugin configuration values, or empty dict if none found.
    """
    return _config_loader.get_plugin_config(plugin_type, plugin_name)


def has_user_plugin_config(plugin_type: str, plugin_name: str) -> bool:
    """Check if plugin configuration exists in user config.

    Args:
        plugin_type: The plugin type (e.g., "extractors", "loaders")
        plugin_name: The plugin name (e.g., "tap-github", "target-postgres")

    Returns:
        True if plugin configuration exists, False otherwise.
    """
    return _config_loader.has_plugin_config(plugin_type, plugin_name)
