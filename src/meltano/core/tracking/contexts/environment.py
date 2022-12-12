"""Environment context for the Snowplow tracker."""

from __future__ import annotations

import os
import platform
import uuid
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

import psutil
from cached_property import cached_property
from snowplow_tracker import SelfDescribingJson
from structlog.stdlib import get_logger

import meltano
from meltano.core.tracking.schemas import EnvironmentContextSchema
from meltano.core.utils import hash_sha256, safe_hasattr

logger = get_logger(__name__)

# This file is only ever created in CI when building a release
release_marker_path = Path(__file__).parent / ".release_marker"


class EnvironmentContext(SelfDescribingJson):
    """Environment context for the Snowplow tracker."""

    def __init__(self):
        """Initialize the environment context."""
        ci_markers = ("GITHUB_ACTIONS", "CI")
        super().__init__(
            EnvironmentContextSchema.url,
            {
                "context_uuid": str(uuid.uuid4()),
                "meltano_version": meltano.__version__,
                "is_dev_build": not release_marker_path.exists(),
                "is_ci_environment": any(
                    # True if 'true', 'TRUE', 'True', or '1'
                    os.environ.get(marker, "").lower()[:1] in {"1", "t"}
                    for marker in ci_markers
                ),
                "python_version": platform.python_version(),
                "python_implementation": platform.python_implementation(),
                **self.system_info,
                **self.process_info,
            },
        )

    @cached_property
    def system_info(self) -> dict[str, Any]:
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
        return f"{datetime.utcfromtimestamp(process.create_time()).isoformat()}Z"

    @cached_property
    def process_info(self) -> dict[str, Any]:
        """Obtain the process information for the current process.

        Returns:
            A dictionary containing the process information. Such as the hashed process name, pid, core counts, etc
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

        Uses sched_getaffinity where available, otherwise falls back to cpu_count().

        Returns:
            int: The number of available CPU cores.
        """
        if safe_hasattr(os, "sched_getaffinity"):
            return len(os.sched_getaffinity(0))
        return os.cpu_count()


environment_context = EnvironmentContext()
