"""Version check service for Meltano CLI."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
import sys
import typing as t
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import platformdirs
import requests
import structlog.stdlib
from packaging.version import parse

from meltano.core._packaging import editable_installation

if t.TYPE_CHECKING:
    from pathlib import Path

    from meltano.core.project import Project

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


def _get_cache_dir() -> Path:
    """Get the cache directory for the version check.

    This should be unique per Meltano executable, so
    we hash the Python executable path and use that as the subdirectory.
    """
    unique_id = hashlib.sha256(sys.executable.encode()).hexdigest()
    return platformdirs.user_cache_path("meltano") / "version_check" / unique_id


class VersionCheckService:
    """Service for checking if Meltano is up to date."""

    def __init__(
        self,
        project: Project | None = None,
        *,
        cache_dir: Path | None = None,
    ):
        """Initialize the version check service."""
        self.project = project
        cache_dir = cache_dir or _get_cache_dir()
        self._cache_file = cache_dir / "version_check_cache.json"

    def should_check_version(self) -> bool:
        """Determine if version check should be performed."""
        # Check environment variable first
        if editable_installation() is not None:
            return False

        if os.environ.get("MELTANO_CLI_DISABLE_VERSION_CHECK", "").lower() in (
            "1",
            "true",
            "yes",
        ):
            return False

        # Check project setting if available
        if self.project is not None:
            return not self.project.settings.get("cli.disable_version_check")

        return True

    def _is_development_version(self, version_str: str) -> bool:
        """Check if this is a development version."""
        return "dev" in version_str or version_str == "0.0.0"

    def _load_cache(self) -> dict[str, t.Any] | None:
        """Load cached version check data."""
        if not self._cache_file.exists():
            return None

        with self._cache_file.open(encoding="utf-8") as f:
            cache_data = json.load(f)

        # Check if cache is still valid
        check_time = datetime.fromisoformat(cache_data["check_timestamp"])
        if datetime.now(timezone.utc) - check_time < CACHE_DURATION:
            return cache_data

        return None

    def _save_cache(self, latest_version: str) -> None:
        """Save version check data to cache."""
        cache_data = {
            "latest_version": latest_version,
            "check_timestamp": datetime.now(timezone.utc).isoformat(),
        }

        self._cache_file.parent.mkdir(parents=True, exist_ok=True)
        with self._cache_file.open("w", encoding="utf-8") as f:
            json.dump(cache_data, f)

    def _fetch_latest_version(self) -> str | None:
        """Fetch the latest version from PyPI."""
        try:
            response = requests.get(PYPI_URL, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            return data["info"]["version"]
        except Exception:  # noqa: BLE001
            logger.debug("Failed to fetch latest version from PyPI", exc_info=True)
            return None

    def _check_version(self) -> VersionCheckResult | None:
        """Check if a newer version of Meltano is available."""
        if not self.should_check_version():
            return None

        current_version = importlib.metadata.version("meltano")

        # Skip check for development versions
        if self._is_development_version(current_version):
            return None

        # Try to get latest version from cache first
        if cache_data := self._load_cache():
            latest_version = cache_data["latest_version"]
        else:
            # Fetch from PyPI
            latest_version = self._fetch_latest_version()
            if not latest_version:
                return None

            # Save to cache
            self._save_cache(latest_version)

        # Compare versions
        current = parse(current_version)
        latest = parse(latest_version)

        # TODO: get upgrade command in a reliable and cross-platform way
        # Maybe check out https://github.com/aj-white/piplexed for inspiration
        # and consider using `uv tool dir` and `pipx environment`.
        upgrade_command = None

        return VersionCheckResult(
            current_version=current_version,
            latest_version=latest_version,
            is_outdated=current < latest,
            upgrade_command=upgrade_command,
        )

    def format_update_message(self, result: VersionCheckResult) -> str:
        """Format the update message for display."""
        if not result.is_outdated:
            return ""

        message = (
            f"A new version of Meltano is available (v{result.latest_version}) "
            f"and you are currently running v{result.current_version}. "
        )

        if result.upgrade_command:
            message += f"To upgrade: `{result.upgrade_command}`. "

        message += "For more information, visit: https://docs.meltano.com/getting-started/installation."

        return message

    def check_version(self) -> VersionCheckResult | None:
        """Check if a newer version of Meltano is available."""
        try:
            return self._check_version()
        except Exception:  # noqa: BLE001
            logger.debug("Failed to check version", exc_info=True)
            return None
