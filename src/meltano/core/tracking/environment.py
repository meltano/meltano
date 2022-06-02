"""Snowplow Tracker."""

from __future__ import annotations

import ctypes
import ctypes.wintypes
import hashlib
import json
import os
import platform
import uuid
from collections import defaultdict
from datetime import datetime
from enum import Enum, auto
from platform import system
from typing import Any

import psutil
from backports.cached_property import cached_property
from snowplow_tracker import SelfDescribingJson
from structlog.stdlib import get_logger

import meltano
from meltano.core.project import Project
from meltano.core.settings_service import SettingsService

logger = get_logger(__name__)


class ProjectUUIDSource(Enum):
    """The source of the `project_uuid` used for telemetry."""

    explicit = auto()
    """The UUID was explicitly provided in the config as the `project_id`."""

    derived = auto()
    """The UUID was derived by hashing the `project_id` in the config."""

    random = auto()
    """The UUID was randomly generated (UUID v4) since no `project_id` was configured."""


class EnvironmentContext(SelfDescribingJson):
    def __init__(self, project: Project):
        logger.debug(
            f"Initializing '{type(self).__module__}.{type(self).__qualname__}' for {project!r}"
        )
        self.project = project
        self.settings_service = SettingsService(project)
        super().__init__(
            "iglu:com.meltano/environment_context/jsonschema/1-0-0",
            {"context_uuid": uuid.uuid4()}
            | self.project_info
            | self.system_info
            | self.process_info,
        )

    @property
    def project_uuid_source(self) -> ProjectUUIDSource:
        self.project_uuid  # Ensure the `project_uuid` has been generated
        return self._project_uuid_source

    @cached_property
    def project_uuid(self) -> uuid.UUID:
        """The `project_id` from the project config file.

        If it is not found (e.g. first time run), generate a valid v4 UUID, and and store it in the
        project config file.
        """
        project_id_str = self.settings_service.get("project_id")

        if project_id_str:
            try:
                # Project ID might already be a UUID
                project_id = uuid.UUID(project_id_str)
            except ValueError:
                # If the project ID is not a UUID, then we hash it, and use the hash to make a UUID
                project_id = uuid.UUID(
                    hashlib.sha256(project_id_str.encode()).hexdigest()[::2]
                )
                self._project_uuid_source = ProjectUUIDSource.derived
            else:
                self._project_uuid_source = ProjectUUIDSource.explicit
        else:
            project_id = uuid.uuid4()
            self._project_uuid_source = ProjectUUIDSource.random

            if self.send_anonymous_usage_stats:
                # If we are set to track anonymous usage stats, also store the generated project_id
                # back to the project config file so that it persists between meltano runs.
                self.settings_service.set("project_id", str(project_id))

        return project_id

    @cached_property
    def client_uuid(self) -> uuid.UUID:
        """The `client_id` from the non-versioned `analytics.json`.

        If it is not found (e.g. first time run), generate a valid v4 UUID, and store it in
        `analytics.json`.
        """
        analytics_json_path = self.project.meltano_dir() / "analytics.json"
        try:  # noqa: WPS229
            with open(analytics_json_path) as analytics_json_file:
                analytics_json = json.load(analytics_json_file)
        except FileNotFoundError:
            client_id = uuid.uuid4()

            if self.send_anonymous_usage_stats:
                # If we are set to track Anonymous Usage stats, also store the generated
                # `client_id` in a non-versioned `analytics.json` file so that it persists between
                # meltano runs.
                with open(analytics_json_path, "w") as analytics_json_file:
                    json.dump({"client_id": str(client_id)}, analytics_json_file)
        else:
            client_id = uuid.UUID(analytics_json["client_id"], version=4)

        return client_id

    @cached_property
    def project_info(self) -> dict[str, Any]:
        return {
            "project_uuid": self.project_uuid,
            "project_uuid_source": self.project_uuid_source.name,
            "client_uuid": self.client_uuid,
            "meltano_version": meltano.__version__,
            "python_version": platform.python_version(),
            "python_implementation": platform.python_implementation(),
            "environment_name": (
                self.project.active_environment.name
                if self.project.active_environment
                else None
            ),
        }

    @cached_property
    def system_info(self) -> dict[str, Any]:
        freedesktop_data = (
            platform.freedesktop_os_release()
            if hasattr(platform, "freedesktop_os_release")
            else defaultdict(type(None))
        )
        return {
            "system_name": platform.system() or None,
            "system_release": platform.release() or None,
            "system_version": platform.version() or None,
            "machine": platform.machine() or None,
            "node": platform.node() or None,
            "windows_edition": platform.win32_edition()
            if hasattr(platform, "win32_edition")
            else None,
            "freedesktop_id": freedesktop_data["ID"],
            "freedesktop_id_like": freedesktop_data.get("ID_LIKE", None),
            "freedesktop_version_id": freedesktop_data.get("VERSION_ID", None),
        }

    @staticmethod
    def get_process_timestamp(process: psutil.Process) -> str:
        """Obtains the creation time of a process as a ISO 8601 timestamp."""
        return datetime.utcfromtimestamp(process.create_time()).isoformat() + "Z"

    @cached_property
    def process_info(self) -> dict[str, Any]:
        process = psutil.Process()
        with process.oneshot():
            return {
                "num_cpu_cores": psutil.cpu_count(),
                "num_cpu_cores_available": self.num_available_cores,
                "process_executable_path": process.exe() or None,
                "process_arguments": process.cmdline(),
                "processe_hierarchy": [
                    {
                        "process_id": x.pid,
                        "process_name": x.name(),
                        "process_creation_timestamp": self.get_process_timestamp(x),
                    }
                    for x in (process, *process.parents())
                ],
            }

    @cached_property
    def num_available_cores(self) -> int:
        """The number of available CPU cores (obtained in a cross-platform manner)."""
        # Based off of Will Da Silva's answer at https://stackoverflow.com/a/69200821/5946921
        if hasattr(os, "sched_getaffinity"):
            return len(os.sched_getaffinity(0))
        if system() == "Windows":
            kernel32 = ctypes.WinDLL("kernel32")
            DWORD_PTR = ctypes.wintypes.WPARAM
            PDWORD_PTR = ctypes.POINTER(DWORD_PTR)
            GetCurrentProcess = kernel32.GetCurrentProcess
            GetCurrentProcess.restype = ctypes.wintypes.HANDLE
            GetProcessAffinityMask = kernel32.GetProcessAffinityMask
            GetProcessAffinityMask.argtypes = (
                ctypes.wintypes.HANDLE,
                PDWORD_PTR,
                PDWORD_PTR,
            )
            mask = DWORD_PTR()
            if GetProcessAffinityMask(
                GetCurrentProcess(), ctypes.byref(mask), ctypes.byref(DWORD_PTR())
            ):
                return bin(mask.value).count("1")
            logger.debug("Call to 'GetProcessAffinityMask' failed")
        logger.debug(
            "Unable to determine the number of available CPU cores; "
            "falling back to the total number of CPU cores"
        )
        return os.cpu_count()
