"""Python version compatibility utilities."""

from __future__ import annotations

import sys
import typing as t

if t.TYPE_CHECKING:
    from meltano.core.plugin.base import Variant


def get_current_python_version() -> str:
    """Get the current Python version as a string (e.g., '3.11').

    Returns:
        Python version in format 'major.minor'
    """
    return f"{sys.version_info.major}.{sys.version_info.minor}"


def is_python_version_supported(
    supported_versions: list[str] | None,
    current_version: str | None = None,
) -> bool:
    """Check if current Python version is in the supported list.

    Args:
        supported_versions: List of supported Python versions (e.g., ['3.10', '3.11'])
        current_version: Python version to check (defaults to current runtime)

    Returns:
        True if current version is supported or no restrictions exist, False otherwise
    """
    if not supported_versions:
        # No restrictions means all versions supported
        return True

    version = current_version or get_current_python_version()
    return version in supported_versions


def _parse_python_version(version: str) -> tuple[int, int]:
    major, minor = version.split(".", maxsplit=1)
    return int(major), int(minor)


def determine_plugin_python_version(
    variant: Variant,
    *,
    current_version: str | None = None,
) -> str | None:
    """Determine the Python version to use for a plugin.

    Args:
        variant: The plugin variant
        current_version: Current Python version (defaults to runtime version)

    Returns:
        Version string like 'python3.11' or None
    """
    supported_versions = variant.supported_python_versions

    if not supported_versions:
        # No restrictions
        return None

    current = current_version or get_current_python_version()

    if is_python_version_supported(supported_versions, current):
        # Current version is supported
        return None

    # Auto-select highest supported version
    return f"python{max(supported_versions, key=lambda x: _parse_python_version(x))}"
