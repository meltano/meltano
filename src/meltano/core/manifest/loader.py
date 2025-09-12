"""Load and compile Meltano manifests."""

from __future__ import annotations

import json
import typing as t

import structlog

from meltano.core.manifest import Manifest

if t.TYPE_CHECKING:
    from pathlib import Path

    from meltano.core.project import Project

logger = structlog.stdlib.get_logger(__name__)


def get_manifest_path(project: Project) -> Path:
    """Get the path to the appropriate manifest file.

    Args:
        project: The Meltano project.

    Returns:
        The path to the manifest file for the current environment.
    """
    manifest_dir = project.root / ".meltano" / "manifests"

    if project.environment:
        manifest_file = (
            manifest_dir / f"meltano-manifest.{project.environment.name}.json"
        )
    else:
        manifest_file = manifest_dir / "meltano-manifest.json"

    return manifest_file


def check_manifest_staleness(project: Project, manifest_path: Path) -> bool:
    """Check if the manifest is stale compared to meltano.yml.

    Args:
        project: The Meltano project.
        manifest_path: Path to the manifest file.

    Returns:
        True if the manifest is stale (meltano.yml is newer), False otherwise.
    """
    if not manifest_path.exists():
        return False

    try:
        manifest_mtime = manifest_path.stat().st_mtime
        meltano_yml_mtime = project.meltanofile.stat().st_mtime

        return meltano_yml_mtime > manifest_mtime
    except OSError:
        # If we can't check, assume it's not stale
        return False


def compile_manifest(project: Project, manifest_path: Path) -> dict[str, t.Any]:
    """Compile a manifest for the current project and environment.

    Args:
        project: The Meltano project.
        manifest_path: Path where the manifest should be saved.

    Returns:
        The compiled manifest data.

    Raises:
        Exception: If manifest compilation fails.
    """
    logger.info(
        "Compiling manifest",
        environment=project.environment.name if project.environment else "default",
        path=str(manifest_path),
    )

    # Ensure the directory exists
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    # Create the manifest
    manifest = Manifest(
        project=project,
        path=manifest_path,
        check_schema=False,  # Don't validate during auto-compilation
        redact_secrets=True,  # Always redact secrets for safety
    )

    # Get the manifest data
    manifest_data = manifest.data

    # Write to file
    with manifest_path.open("w") as manifest_file:
        json.dump(manifest_data, manifest_file, indent=4, sort_keys=True)

    return manifest_data


def load_manifest(manifest_path: Path) -> dict[str, t.Any] | None:
    """Load a manifest from a JSON file.

    Args:
        manifest_path: Path to the manifest file.

    Returns:
        The manifest data, or None if loading fails.
    """
    try:
        with manifest_path.open("r") as manifest_file:
            return json.load(manifest_file)
    except (OSError, json.JSONDecodeError) as err:
        logger.warning(
            "Failed to load manifest",
            path=str(manifest_path),
            error=str(err),
        )
        return None


def load_or_compile_manifest(project: Project) -> dict[str, t.Any] | None:
    """Load an existing manifest or compile a new one if missing.

    This function implements the "compile if missing" strategy:
    1. If manifest exists, load and use it
    2. If manifest doesn't exist, compile it
    3. If manifest is stale, warn but still use it

    Args:
        project: The Meltano project.

    Returns:
        The manifest data, or None if both loading and compilation fail.
    """
    manifest_path = get_manifest_path(project)

    # Check if manifest exists
    if manifest_path.exists():
        # Check staleness
        if check_manifest_staleness(project, manifest_path):
            logger.warning(
                "Manifest may be out of date. Run 'meltano compile' to update it.",
                manifest_path=str(manifest_path),
            )

        # Try to load existing manifest
        manifest_data = load_manifest(manifest_path)
        if manifest_data:
            logger.debug("Using existing manifest", path=str(manifest_path))
            return manifest_data

        # If loading failed, fall through to compilation
        logger.warning(
            "Failed to load existing manifest, will recompile",
            path=str(manifest_path),
        )

    # Compile new manifest
    try:
        return compile_manifest(project, manifest_path)
    except Exception as err:
        logger.error(
            "Failed to compile manifest",
            path=str(manifest_path),
            error=str(err),
        )
        return None
