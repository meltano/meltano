"""Environment context for the Snowplow tracker."""

from __future__ import annotations

import os
import platform
import typing as t
import uuid
from collections import defaultdict
from contextlib import suppress
from datetime import datetime, timezone
from functools import cached_property
from warnings import warn

import psutil
from snowplow_tracker import SelfDescribingJson
from structlog.stdlib import get_logger

import meltano
from meltano.core.tracking.schemas import EnvironmentContextSchema
from meltano.core.utils import get_boolean_env_var, hash_sha256, safe_hasattr, strtobool
from meltano.core.utils.compat import importlib_resources

logger = get_logger(__name__)

# This file is only ever created in CI when building a release
release_marker_path = (
    importlib_resources.files("meltano.core.tracking") / ".release_marker"
)


def _get_parent_context_uuid_str() -> str | None:
    with suppress(KeyError):
        uuid_str = os.environ["MELTANO_PARENT_CONTEXT_UUID"]
        try:
            return str(uuid.UUID(uuid_str))
        except ValueError:
            warn(
                (
                    f"Invalid telemetry parent environment context UUID "
                    f"{uuid_str!r} from $MELTANO_PARENT_CONTEXT_UUID - "
                    "Meltano will continue as if $MELTANO_PARENT_CONTEXT_UUID "
                    "had not been set"
                ),
                stacklevel=2,
            )
    return None


class EnvironmentContext(SelfDescribingJson):
    """Environment context for the Snowplow tracker."""

    ci_markers: t.ClassVar[set[str]] = {
        "GITHUB_ACTIONS",
        "CI",
    }
    notable_flag_env_vars: t.ClassVar[set[str]] = {
        "CODESPACES",
        *ci_markers,
    }
    notable_hashed_env_vars: t.ClassVar[set[str]] = {
        "CODESPACE_NAME",
        "GITHUB_REPOSITORY",
        "GITHUB_USER",
    }

    @classmethod
    def _notable_hashed_env_vars(cls) -> t.Iterable[tuple[str, str]]:
        for env_var_name in cls.notable_hashed_env_vars:
            with suppress(KeyError):  # Skip unset env vars
                env_var_value = os.environ[env_var_name]
                yield env_var_name, hash_sha256(env_var_value)

    @classmethod
    def _notable_flag_env_vars(cls) -> t.Iterable[tuple[str, bool | None]]:
        for env_var_name in cls.notable_flag_env_vars:
            with suppress(KeyError):  # Skip unset env vars
                env_var_value = os.environ[env_var_name]
                try:
                    yield env_var_name, strtobool(env_var_value)
                except ValueError:
                    yield env_var_name, None

    def __init__(self) -> None:
        """Initialize the environment context."""
        super().__init__(
            EnvironmentContextSchema.url,
            {
                "context_uuid": str(uuid.uuid4()),
                "parent_context_uuid": _get_parent_context_uuid_str(),
                "meltano_version": meltano.__version__,
                "is_dev_build": not release_marker_path.is_file(),
                "is_ci_environment": any(
                    get_boolean_env_var(marker) for marker in self.ci_markers
                ),
                "notable_flag_env_vars": dict(self._notable_flag_env_vars()),
                "notable_hashed_env_vars": dict(self._notable_hashed_env_vars()),
                "python_version": platform.python_version(),
                "python_implementation": platform.python_implementation(),
                **self.system_info,
                **self.process_info,
            },
        )

    @cached_property
    def system_info(self) -> dict[str, t.Any]:
        """Get system information.

        Returns:
            A dictionary containing system information.
        """
        try:
            freedesktop_data = platform.freedesktop_os_release()
        except Exception:
            freedesktop_data = defaultdict(type(None))

        return {
            "system_name": platform.system() or None,
            "system_release": platform.release() or None,
            "system_version": platform.version() or None,
            "machine": platform.machine() or None,
            "windows_edition": platform.win32_edition()
            if safe_hasattr(platform, "win32_edition")
            else None,
            "freedesktop_id": freedesktop_data["ID"],
            "freedesktop_id_like": freedesktop_data.get("ID_LIKE", None),
            "freedesktop_version_id": freedesktop_data.get("VERSION_ID", None),
        }

    @staticmethod
    def get_process_timestamp(process: psutil.Process) -> str:
        """Obtain the creation time of a process as a ISO 8601 timestamp.

        Args:
            process: The process to obtain the creation time from.

        Returns:
            A ISO 8601 timestamp formatted string.
        """
        return f"{datetime.fromtimestamp(process.create_time(), tz=timezone.utc).isoformat()}"  # noqa: E501

    @cached_property
    def process_info(self) -> dict[str, t.Any]:
        """Obtain the process information for the current process.

        Returns:
            A dictionary containing the process information. Such as the hashed
            process name, pid, core counts, etc
        """
        process = psutil.Process()
        with process.oneshot():
            return {
                "num_cpu_cores": psutil.cpu_count(),
                "num_cpu_cores_available": self.num_available_cores,
                "process_hierarchy": [
                    {
                        "process_name_hash": hash_sha256(proc.name()),
                        "process_creation_timestamp": self.get_process_timestamp(proc),
                    }
                    for proc in (process, *process.parents())
                ],
            }

    @cached_property
    def num_available_cores(self) -> int:
        """Obtain the number of available CPU cores.

        Uses `sched_getaffinity` where available, otherwise falls back to
        `cpu_count`.

        Returns:
            The number of available CPU cores.
        """
        if safe_hasattr(os, "sched_getaffinity"):
            return len(os.sched_getaffinity(0))
        return os.cpu_count()


environment_context = EnvironmentContext()
