"""Manager for Meltano user configuration."""

from __future__ import annotations

import threading
from configparser import ConfigParser
from pathlib import Path

import structlog

from meltano.core.error import MeltanoError
from meltano.core.utils import strtobool

logger = structlog.stdlib.get_logger(__name__)


class UserConfigReadError(MeltanoError):
    """User configuration could not be read."""

    def __init__(self, config_path: Path, original_error: Exception) -> None:
        """Create a new exception.

        Args:
            config_path: Path to the configuration file.
            original_error: The original exception that was raised.
        """
        self.config_path = config_path
        self.original_error = original_error
        reason = f"Failed to read user configuration from '{config_path}'"
        instruction = "Check file permissions and INI format syntax"
        super().__init__(reason, instruction)


class UserConfigService:
    """Meltano Service to manage user-specific configuration."""

    def __init__(self, config_path: Path | None = None) -> None:
        """Create a new UserConfigService.

        Args:
            config_path: Path to the configuration file. Defaults to ~/.meltanorc.
        """
        self.config_path = config_path or Path.home() / ".meltanorc"
        self._config: ConfigParser | None = None

    @property
    def config(self) -> ConfigParser:
        """Get the configuration parser.

        Returns:
            The configuration parser instance.

        Raises:
            UserConfigReadError: If the configuration file exists but cannot be read.
        """
        if self._config is None:
            self._config = ConfigParser()
            if self.config_path.exists():
                try:
                    with self.config_path.open() as config_file:
                        self._config.read_file(
                            config_file, source=str(self.config_path)
                        )
                except Exception as err:
                    logger.error(
                        "Failed to read user config",
                        config_path=str(self.config_path),
                        error=str(err),
                    )
                    raise UserConfigReadError(self.config_path, err) from err
        return self._config

    @property
    def yaml_indent(self) -> int:
        """Get YAML indentation level.

        Returns:
            The YAML indentation level, defaults to 2.
        """
        try:
            return self.config.getint("yaml", "indent", fallback=2)
        except ValueError:
            logger.warning(
                "Invalid yaml indent value, using default",
                config_path=str(self.config_path),
                default=2,
            )
            return 2

    def yaml_settings(self) -> dict[str, bool | int | str | None]:
        """Get all YAML formatting settings.

        Returns:
            A dictionary of YAML formatting settings.
        """
        if not self.config.has_section("yaml"):
            return {}

        known_settings = {
            "indent",
            "width",
            "block_seq_indent",
            "sequence_dash_offset",
            "preserve_quotes",
            "map_indent",
            "sequence_indent",
            "offset",
            "explicit_start",
            "explicit_end",
            "version",
            "tags",
            "canonical",
            "default_flow_style",
            "default_style",
            "allow_unicode",
            "line_break",
            "encoding",
        }

        settings: dict[str, bool | int | str | None] = {}
        for key, value in self.config.items("yaml"):
            if key not in known_settings:
                logger.warning(
                    "Unrecognized YAML setting, ignoring",
                    config_path=str(self.config_path),
                    setting=key,
                    value=value,
                )
                continue

            parsed_value = self._parse_value(value)

            if key == "indent" and isinstance(parsed_value, int) and parsed_value < 1:
                logger.warning(
                    "YAML indent must be >= 1, using default",
                    config_path=str(self.config_path),
                    invalid_value=parsed_value,
                    default=2,
                )
                parsed_value = 2
            elif key == "width" and isinstance(parsed_value, int) and parsed_value < 1:
                logger.warning(
                    "YAML width must be >= 1, using default",
                    config_path=str(self.config_path),
                    invalid_value=parsed_value,
                    default=80,
                )
                parsed_value = 80
            elif (
                key == "block_seq_indent"
                and isinstance(parsed_value, int)
                and parsed_value < 0
            ):
                logger.warning(
                    "YAML block_seq_indent must be >= 0, using default",
                    config_path=str(self.config_path),
                    invalid_value=parsed_value,
                    default=0,
                )
                parsed_value = 0

            settings[key] = parsed_value

        return settings

    def _parse_value(self, value: str) -> bool | int | str | None:
        """Parse a configuration value using Meltano utilities.

        Args:
            value: The string value to parse.

        Returns:
            The parsed value as the appropriate type.
        """
        if value.lower() in {"none", "null", ""}:
            return None

        try:
            bool_val = strtobool(value)
            return bool(bool_val)
        except ValueError:
            pass

        try:
            return int(value)
        except ValueError:
            return value


_user_config_service: UserConfigService | None = None
_user_config_service_lock = threading.Lock()


def get_user_config_service(config_path: Path | None = None) -> UserConfigService:
    """Get the global user configuration service instance.

    Args:
        config_path: Optional path to the configuration file.

    Returns:
        The UserConfigService instance.
    """
    global _user_config_service
    if _user_config_service is None or (
        config_path and config_path != _user_config_service.config_path
    ):
        with _user_config_service_lock:
            if _user_config_service is None or (
                config_path and config_path != _user_config_service.config_path
            ):
                _user_config_service = UserConfigService(config_path)
    return _user_config_service


def _reset_user_config_service() -> None:
    """Reset the global user configuration service instance.

    This function is intended for testing purposes only.
    """
    global _user_config_service
    with _user_config_service_lock:
        _user_config_service = None
