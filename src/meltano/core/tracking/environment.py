"""Environment context for the Snowplow tracker."""

from __future__ import annotations

import ctypes
import ctypes.wintypes
import os
import platform
import uuid
from collections import defaultdict
from datetime import datetime
from platform import system
from typing import Any

import psutil
from backports.cached_property import cached_property
from snowplow_tracker import SelfDescribingJson
from structlog.stdlib import get_logger

import meltano

logger = get_logger(__name__)


class EnvironmentContext(SelfDescribingJson):
    def __init__(self):
        logger.debug(
            f"Initializing '{type(self).__module__}.{type(self).__qualname__}'"
        )
        super().__init__(
            "iglu:com.meltano/environment_context/jsonschema/1-0-0",
            {
                "context_uuid": uuid.uuid4(),
                "meltano_version": meltano.__version__,
                "python_version": platform.python_version(),
                "python_implementation": platform.python_implementation(),
            }
            | self.system_info
            | self.process_info,
        )

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


environment_context = EnvironmentContext()
