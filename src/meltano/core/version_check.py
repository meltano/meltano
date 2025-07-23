"""Version check service for Meltano CLI."""

from __future__ import annotations

import json
import os
import sys
import typing as t
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
import structlog.stdlib
from packaging.version import InvalidVersion, parse

from meltano import __version__
from meltano.core.utils import get_no_color_flag

if t.TYPE_CHECKING:
    from meltano.core.project_settings_service import ProjectSettingsService

logger = structlog.stdlib.get_logger(__name__)

PYPI_URL = "https://pypi.org/pypi/meltano/json"
CACHE_DURATION = timedelta(hours=24)
REQUEST_TIMEOUT = 5  # seconds


@dataclass
class VersionCheckResult:
    """Result of a version check."""

    current_version: str
    latest_version: str
    is_outdated: bool
    upgrade_command: str | None = None


class VersionCheckService:
    """Service for checking if Meltano is up to date."""

    def __init__(
        self,
        project_settings_service: ProjectSettingsService | None = None,
        cache_dir: Path | None = None,
    ):
        """Initialize the version check service."""
        self.settings_service = project_settings_service
        self.cache_dir = cache_dir
        self._cache_file = None
        if cache_dir:
            self._cache_file = cache_dir / "version_check_cache.json"

    def should_check_version(self) -> bool:
        """Determine if version check should be performed."""
        # Check environment variable first
        if os.environ.get("MELTANO_CLI_DISABLE_VERSION_CHECK", "").lower() in (
            "1",
            "true",
            "yes",
        ):
            return False

        # Check project setting if available
        if self.settings_service:
            try:
                return not self.settings_service.get("cli.disable_version_check")
            except Exception:
                # If setting doesn't exist or error, default to checking
                logger.debug("Failed to get version check setting", exc_info=True)

        return True

    def _is_development_version(self, version_str: str) -> bool:
        """Check if this is a development version."""
        return "dev" in version_str or version_str == "0.0.0"

    def _load_cache(self) -> dict[str, t.Any] | None:
        """Load cached version check data."""
        if not self._cache_file or not self._cache_file.exists():
            return None

        try:
            with self._cache_file.open(encoding="utf-8") as f:
                cache_data = json.load(f)

            # Check if cache is still valid
            check_time = datetime.fromisoformat(cache_data["check_timestamp"])
            if datetime.now(timezone.utc) - check_time < CACHE_DURATION:
                return cache_data

        except Exception:
            logger.debug("Failed to load version cache", exc_info=True)

        return None

    def _save_cache(self, latest_version: str) -> None:
        """Save version check data to cache."""
        if not self._cache_file:
            return

        cache_data = {
            "latest_version": latest_version,
            "check_timestamp": datetime.now(timezone.utc).isoformat(),
        }

        try:
            self._cache_file.parent.mkdir(parents=True, exist_ok=True)
            with self._cache_file.open("w", encoding="utf-8") as f:
                json.dump(cache_data, f)
        except Exception:
            logger.debug("Failed to save version cache", exc_info=True)

    def _fetch_latest_version(self) -> str | None:
        """Fetch the latest version from PyPI."""
        try:
            response = requests.get(PYPI_URL, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            return data["info"]["version"]
        except Exception:
            logger.debug("Failed to fetch latest version from PyPI", exc_info=True)
            return None

    def _get_upgrade_command(self) -> str:
        """Get the appropriate upgrade command based on installation method."""
        # Check if running in a virtual environment
        in_venv = sys.prefix != sys.base_prefix

        # Try to detect installation method
        # Check for uv
        if Path(sys.executable).parent.joinpath("uv").exists():
            return "uv pip install --upgrade meltano"

        # Check for pipx
        pipx_home = os.environ.get("PIPX_HOME", str(Path.home() / ".local/pipx"))
        if Path(pipx_home).exists() and "pipx" in sys.executable:
            return "pipx upgrade meltano"

        # Default to pip
        if in_venv:
            return "pip install --upgrade meltano"
        return "pip install --user --upgrade meltano"

    def check_version(self) -> VersionCheckResult | None:
        """Check if a newer version of Meltano is available."""
        if not self.should_check_version():
            return None

        current_version = __version__

        # Skip check for development versions
        if self._is_development_version(current_version):
            return None

        # Try to get latest version from cache first
        cache_data = self._load_cache()
        if cache_data:
            latest_version = cache_data["latest_version"]
        else:
            # Fetch from PyPI
            latest_version = self._fetch_latest_version()
            if not latest_version:
                return None

            # Save to cache
            self._save_cache(latest_version)

        # Compare versions
        try:
            current = parse(current_version)
            latest = parse(latest_version)
            is_outdated = current < latest
        except InvalidVersion:
            logger.debug(
                "Invalid version comparison: %s vs %s",
                current_version,
                latest_version,
            )
            return None

        upgrade_command = self._get_upgrade_command() if is_outdated else None

        return VersionCheckResult(
            current_version=current_version,
            latest_version=latest_version,
            is_outdated=is_outdated,
            upgrade_command=upgrade_command,
        )

    def format_update_message(self, result: VersionCheckResult) -> str:
        """Format the update message for display."""
        if not result.is_outdated:
            return ""

        # Use plain text format if no color is requested
        no_color = get_no_color_flag()

        lines = [
            f"A new version of Meltano is available (v{result.latest_version})!",
            f"You are currently running v{result.current_version}.",
            "",
            "To upgrade:",
            f"  {result.upgrade_command}",
            "",
            "For more information, visit: https://docs.meltano.com/guide/installation",
        ]

        message = "\n".join(lines)

        if not no_color:
            # Add some color formatting for terminals that support it
            message = f"\033[94m{message}\033[0m"  # Blue text

        return message
