"""Manager for Meltano user configuration."""

from __future__ import annotations

import threading
import typing as t
from dataclasses import KW_ONLY, dataclass, field

import platformdirs
import structlog
from ruamel.yaml import YAML

from meltano.core.error import MeltanoError

if t.TYPE_CHECKING:
    from pathlib import Path

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
        instruction = "Check file permissions and YAML format syntax"
        super().__init__(reason, instruction)


@dataclass(slots=True)
class YamlSettings:
    """YAML indentation settings."""

    _: KW_ONLY
    _indent: int = 2
    _block_seq_indent: int = 0
    _sequence_dash_offset: int | None = None

    @property
    def indent(self) -> int:
        """Get the indentation level."""
        if self._indent < 1:
            logger.warning(
                "Invalid YAML indentation level, using default",
                indent=self._indent,
            )
            return 2
        return self._indent

    @property
    def block_seq_indent(self) -> int:
        """Get the block sequence indentation level."""
        if self._block_seq_indent < 0:
            logger.warning(
                "Invalid YAML block sequence indentation level, using default",
                block_seq_indent=self._block_seq_indent,
            )
            return 0
        return self._block_seq_indent

    @property
    def sequence_dash_offset(self) -> int:
        """Get the sequence dash offset."""
        if self._sequence_dash_offset is None:
            self._sequence_dash_offset = max(0, self.indent - 2)
        return self._sequence_dash_offset

    @classmethod
    def from_dict(cls, data: dict[str, t.Any]) -> YamlSettings:
        """Create a YAML settings from a dictionary."""
        kwargs = {}
        if indent := data.get("indent"):
            kwargs["_indent"] = int(indent)

        if block_seq_indent := data.get("block_seq_indent"):
            kwargs["_block_seq_indent"] = int(block_seq_indent)

        if sequence_dash_offset := data.get("sequence_dash_offset"):
            kwargs["_sequence_dash_offset"] = int(sequence_dash_offset)

        return cls(**kwargs)


@dataclass(slots=True)
class UserConfig:
    """User configuration."""

    _: KW_ONLY
    yaml: YamlSettings = field(default_factory=YamlSettings)

    @classmethod
    def from_dict(cls, data: dict[str, t.Any]) -> UserConfig:
        """Create a UserConfig from a dictionary."""
        kwargs = {}
        if yaml := data.get("yaml"):
            kwargs["yaml"] = YamlSettings.from_dict(yaml)
        return cls(**kwargs)


class UserConfigService:
    """Meltano Service to manage user-specific configuration."""

    def __init__(self, config_path: Path | None = None) -> None:
        """Create a new UserConfigService.

        Args:
            config_path: Path to the configuration file.
                Defaults to platform-specific config directory.
        """
        self._config_path = config_path
        self._config: UserConfig | None = None

    @property
    def config_path(self) -> Path:
        """Get the path to the configuration file."""
        if self._config_path is None:
            config_dir = platformdirs.user_config_path("meltano")
            self._config_path = config_dir / "config.yml"
        return self._config_path

    @property
    def config(self) -> UserConfig:
        """Get the configuration data.

        Returns:
            The configuration data as a dictionary.

        Raises:
            UserConfigReadError: If the configuration file exists but cannot be read.
        """
        if self._config is None:
            data: dict[str, t.Any] = {}
            if self.config_path.exists():
                yaml = YAML(typ="safe")
                try:
                    with self.config_path.open() as config_file:
                        data = yaml.load(config_file) or {}
                except Exception as err:
                    logger.error(  # noqa: TRY400
                        "Failed to read user config",
                        config_path=str(self.config_path),
                        error=str(err),
                    )
                    raise UserConfigReadError(self.config_path, err) from err

            self._config = UserConfig.from_dict(data)
        return self._config

    @property
    def yaml(self) -> YamlSettings:
        """Get all YAML formatting settings.

        Returns:
            A dictionary of YAML formatting settings.
        """
        return self.config.yaml


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

    if _user_config_service is not None and (
        config_path is None or config_path == _user_config_service.config_path
    ):
        return _user_config_service

    with _user_config_service_lock:
        _user_config_service = UserConfigService(config_path)
        return _user_config_service


def _reset_user_config_service() -> None:
    """Reset the global user configuration service instance.

    This function is intended for testing purposes only.
    """
    global _user_config_service
    with _user_config_service_lock:
        _user_config_service = None
