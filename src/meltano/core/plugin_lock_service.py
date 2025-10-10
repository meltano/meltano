"""Plugin Lockfile Service."""

from __future__ import annotations

import json
import sys
import tempfile
import typing as t
from hashlib import sha256
from pathlib import Path as PathlibPath

from structlog.stdlib import get_logger

from meltano.core.plugin.base import StandalonePlugin
from meltano.core.venv_service import exec_async, find_uv

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

if t.TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from meltano.core.plugin.base import PluginRef
    from meltano.core.plugin.project_plugin import ProjectPlugin
    from meltano.core.project import Project

logger = get_logger(__name__)


def _convert_datetimes_to_str(obj: t.Any) -> t.Any:  # noqa: ANN401
    """Recursively convert datetime objects to ISO format strings.

    Also handles other types that can't be JSON serialized like CommentedMap.

    Args:
        obj: The object to convert (dict, list, datetime, or other).

    Returns:
        The converted object with datetimes as strings and plain Python types.
    """
    from datetime import datetime

    from ruamel.yaml.comments import CommentedMap, CommentedSeq

    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, (dict, CommentedMap)):
        return {key: _convert_datetimes_to_str(value) for key, value in obj.items()}
    if isinstance(obj, (list, CommentedSeq)):
        return [_convert_datetimes_to_str(item) for item in obj]
    return obj


async def lock_plugin_dependencies(pip_url: str) -> str | None:
    """Lock plugin dependencies using uv pip compile to pylock.toml format.

    Args:
        pip_url: The pip URL specification for the plugin.

    Returns:
        pylock.toml content as string, or None if locking fails.
    """
    if not pip_url:
        logger.debug("No pip_url provided, skipping dependency locking")
        return None

    # Create temporary requirements.in with pip_url
    requirements_in = None
    pylock_file = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".in",
            delete=False,
        ) as f:
            f.write(f"{pip_url}\n")
            requirements_in = PathlibPath(f.name)

        # Create output path for pylock.toml
        # uv requires the filename to match pylock.*.toml pattern
        temp_dir = PathlibPath(tempfile.mkdtemp())
        pylock_file = temp_dir / "pylock.toml"

        # Run uv pip compile with pylock.toml format
        # Use --quiet to minimize output and prevent pipe blocking
        # Use --no-header to avoid comments in the pylock file
        uv = find_uv()
        process = await exec_async(
            uv,
            "pip",
            "compile",
            str(requirements_in),
            "--output-file",
            str(pylock_file),
            "--format",
            "pylock.toml",
            "--quiet",
            "--no-header",
        )

        # Consume any remaining stdout
        if process.stdout:
            await process.stdout.read()

        # Return the path to the pylock.toml file instead of parsing it
        # This preserves TOML datetime format for uv to consume
        logger.debug(
            "Generated pylock.toml for %s at: %s",
            pip_url,
            pylock_file,
        )

        # Read it to get package count for logging
        with pylock_file.open("rb") as f:
            pylock_data = tomllib.load(f)

        logger.debug(
            "Locked %d packages for %s",
            len(pylock_data.get("packages", [])),
            pip_url,
        )

        # Return the file content as string (we'll save it separately)
        return pylock_file.read_text()

    except Exception as err:
        logger.warning(
            "Failed to lock dependencies for %s: %s",
            pip_url,
            err,
        )
        return None

    finally:
        # Clean up temp files
        import shutil

        if requirements_in:
            requirements_in.unlink(missing_ok=True)
        if pylock_file and pylock_file.parent.exists():
            # Remove the entire temp directory
            shutil.rmtree(pylock_file.parent, ignore_errors=True)


class LockfileAlreadyExistsError(Exception):
    """Raised when a plugin lockfile already exists."""

    def __init__(self, message: str, path: Path, plugin: PluginRef):
        """Create a new LockfileAlreadyExistsError.

        Args:
            message: The error message.
            path: The path to the existing lockfile.
            plugin: The plugin that was locked.
        """
        self.path = path
        self.plugin = plugin
        super().__init__(message)


class PluginLock:
    """Plugin lockfile."""

    def __init__(self, project: Project, plugin: ProjectPlugin) -> None:
        """Create a new PluginLock.

        Args:
            project: The project.
            plugin: The plugin to lock.
        """
        self.project = project
        self.plugin = plugin
        self.definition = plugin.definition
        self.variant = self.definition.find_variant(plugin.variant)

        self.path = self.project.plugin_lock_path(
            self.definition.type,
            self.definition.name,
            variant_name=self.variant.name,
        )

    def save_definition(self) -> None:
        """Save the plugin definition lockfile (JSON).

        This saves the .lock file containing the plugin definition.
        """
        locked_def = StandalonePlugin.from_variant(self.variant, self.definition)

        # Save the main lock file (JSON, without pylock)
        with self.path.open("w") as lockfile:
            try:
                canonical_data = locked_def.canonical()
                json.dump(canonical_data, lockfile, indent=2)
                lockfile.write("\n")
            except (TypeError, ValueError) as err:
                logger.exception(
                    "Failed to serialize lock file to JSON: %s",
                    err,
                )
                raise

    def save_dependencies(self, pip_url: str) -> None:
        """Save the locked dependencies (pylock.toml).

        This locks and saves dependencies from the given pip_url to a separate
        pylock.<plugin-name>.toml file.

        Args:
            pip_url: The pip URL to lock dependencies for.
        """
        import asyncio

        if not pip_url:
            logger.debug("No pip_url provided, skipping dependency locking")
            return

        logger.debug("Starting dependency lock for %s", pip_url)
        try:
            pylock_content = asyncio.run(lock_plugin_dependencies(pip_url))
            if pylock_content:
                # Parse to get package count for logging
                import sys

                if sys.version_info >= (3, 11):
                    import tomllib
                else:
                    import tomli as tomllib

                pylock_data = tomllib.loads(pylock_content)
                logger.info(
                    "Locked %d packages for %s",
                    len(pylock_data.get("packages", [])),
                    self.plugin.name,
                )

                # Save the pylock.toml file
                # Use pylock.<plugin-name>.toml format (uv compatible)
                # Note: plugin.name includes suffixes like --1, --2 for
                # inherited plugins
                lock_dir = self.path.parent
                pylock_filename = f"pylock.{self.plugin.name}.toml"
                pylock_path = lock_dir / pylock_filename
                pylock_path.write_text(pylock_content)
                logger.debug("Saved pylock to: %s", pylock_path)
        except Exception as err:
            logger.exception(
                "Failed to lock dependencies for %s: %s",
                self.plugin.name,
                err,
            )

    def save(self, *, lock_dependencies: bool = False) -> None:
        """Save the plugin lockfile.

        Args:
            lock_dependencies: Whether to lock dependencies using uv pip compile.
        """
        self.save_definition()

        # Lock dependencies if requested and pip_url exists
        locked_def = StandalonePlugin.from_variant(self.variant, self.definition)
        if lock_dependencies and locked_def.pip_url:
            self.save_dependencies(locked_def.pip_url)

    def load(
        self,
        *,
        create: bool = False,
        loader: Callable = lambda x: StandalonePlugin(**json.load(x)),
    ) -> StandalonePlugin:
        """Load the plugin lockfile.

        Args:
            create: Create the lockfile if it does not yet exist.
            loader: Function to process the lock file. Defaults to constructing
                a `StandalonePlugin` instance.

        Raises:
            FileNotFoundError: The lock file was not found at its expected path.

        Returns:
            The loaded plugin.
        """

        def _load():  # noqa: ANN202
            with self.path.open() as lockfile:
                return loader(lockfile)

        try:
            return _load()
        except FileNotFoundError:
            if create:
                self.save()
                return _load()
            raise

    @property
    def sha256_checksum(self) -> str:
        """Get the checksum of the lockfile.

        Returns:
            The checksum of the lockfile.
        """
        return sha256(self.path.read_bytes()).hexdigest()


class PluginLockService:
    """Plugin Lockfile Service."""

    def __init__(self, project: Project):
        """Create a new Plugin Lockfile Service.

        Args:
            project: The Meltano project.
        """
        self.project = project

    def save(
        self,
        plugin: ProjectPlugin,
        *,
        exists_ok: bool = False,
    ) -> None:
        """Save the plugin lockfile.

        Args:
            plugin: The plugin definition to save.
            exists_ok: Whether raise an exception if the lockfile already exists.

        Raises:
            LockfileAlreadyExistsError: If the lockfile already exists and is not
                flagged for overwriting.
        """
        plugin_lock = PluginLock(self.project, plugin)

        if plugin_lock.path.exists() and not exists_ok:
            raise LockfileAlreadyExistsError(
                f"Lockfile already exists: {plugin_lock.path}",  # noqa: EM102
                plugin_lock.path,
                plugin,
            )

        plugin_lock.save()

        logger.debug("Locked plugin definition", path=plugin_lock.path)
