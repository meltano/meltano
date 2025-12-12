"""Python version compatibility utilities."""

from __future__ import annotations

import sys
import typing as t

from packaging.version import Version

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


def get_highest_python_version(versions: list[str]) -> str | None:
    """Get the highest Python version from a list.

    Args:
        versions: List of Python version strings (e.g., ['3.10', '3.11', '3.12'])

    Returns:
        Highest version string or None if list is empty
    """
    if not versions:
        return None

    try:
        # Parse as Version objects for proper semantic comparison
        version_objects = [(Version(v), v) for v in versions]
        return max(version_objects, key=lambda x: x[0])[1]
    except Exception:
        # Fallback to string sorting if parsing fails
        return sorted(versions)[-1]


def determine_plugin_python_version(
    variant: Variant,
    current_version: str | None = None,
) -> tuple[str | None, bool]:
    """Determine the Python version to use for a plugin.

    Args:
        variant: The plugin variant
        current_version: Current Python version (defaults to runtime version)

    Returns:
        Tuple of (python_version_to_use, auto_selected)
        - python_version_to_use: Version string like 'python3.11' or None
        - auto_selected: True if auto-selected due to incompatibility
    """
    try:
        supported_versions = variant.supported_python_versions
    except AttributeError:
        # Variant doesn't have supported_python_versions (old plugin)
        return None, False

    if not supported_versions:
        # No restrictions
        return None, False

    current = current_version or get_current_python_version()

    if is_python_version_supported(supported_versions, current):
        # Current version is supported
        return None, False

    # Auto-select highest supported version
    highest = get_highest_python_version(supported_versions)
    if highest:
        return f"python{highest}", True

    return None, False
