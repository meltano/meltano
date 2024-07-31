"""State backends."""

from __future__ import annotations

import platform
import sys
import typing as t
from enum import Enum
from urllib.parse import urlparse

from structlog.stdlib import get_logger

from meltano.core.behavior.addon import MeltanoAddon
from meltano.core.db import project_engine
from meltano.core.state_store.azure import AZStorageStateStoreManager
from meltano.core.state_store.base import StateStoreManager
from meltano.core.state_store.db import DBStateStoreManager
from meltano.core.state_store.filesystem import (
    LocalFilesystemStateStoreManager,
    WindowsFilesystemStateStoreManager,
)
from meltano.core.state_store.google import GCSStateStoreManager
from meltano.core.state_store.s3 import S3StateStoreManager

if t.TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from meltano.core.project_settings_service import ProjectSettingsService

if sys.version_info >= (3, 12):
    from importlib.metadata import EntryPoints, entry_points
else:
    from importlib_metadata import EntryPoints, entry_points

__all__ = [
    "AZStorageStateStoreManager",
    "BuiltinStateBackendEnum",
    "DBStateStoreManager",
    "GCSStateStoreManager",
    "LocalFilesystemStateStoreManager",
    "S3StateStoreManager",
    "StateBackend",
    "StateStoreManager",
    "state_store_manager_from_project_settings",
]

logger = get_logger(__name__)


class BuiltinStateBackendEnum(str, Enum):
    """State backend."""

    SYSTEMDB = "systemdb"
    # These strings should match the expected scheme for URIs of
    # the given type. E.g., filesystem state backends have a
    # file://<path>/<to>/<state directory> URI
    LOCAL_FILESYSTEM = "file"
    AZURE = "azure"
    S3 = "s3"
    GCS = "gs"


class StateBackend:
    """State backend."""

    addon: MeltanoAddon[type[StateStoreManager]] = MeltanoAddon(
        "meltano.state_backends",
    )

    def __init__(self, scheme: str) -> None:
        """Create a new StateBackend.

        Args:
            scheme: The scheme of the StateBackend.
        """
        self.scheme = scheme

    @classmethod
    def backends(cls) -> list[str]:
        """List available state backends.

        Returns:
            List of available state backends.
        """
        return list(BuiltinStateBackendEnum) + [ep.name for ep in cls.addon.installed]

    @property
    def _builtin_managers(
        self,
    ) -> t.Mapping[str, type[StateStoreManager]]:
        """Get mapping of StateBackend to associated StateStoreManager.

        Returns:
            Mapping of StateBackend to associated StateStoreManager.
        """
        return {
            BuiltinStateBackendEnum.SYSTEMDB: DBStateStoreManager,
            BuiltinStateBackendEnum.LOCAL_FILESYSTEM: LocalFilesystemStateStoreManager,
            BuiltinStateBackendEnum.S3: S3StateStoreManager,
            BuiltinStateBackendEnum.AZURE: AZStorageStateStoreManager,
            BuiltinStateBackendEnum.GCS: GCSStateStoreManager,
        }

    @property
    def manager(
        self,
    ) -> type[StateStoreManager]:
        """Get the StateStoreManager associated with this StateBackend.

        Returns:
            The StateStoreManager associated with this StateBackend.

        Raises:
            ValueError: If no state backend is found for the scheme.
        """
        try:
            return self._builtin_managers[self.scheme]
        except KeyError:
            logger.info(
                "No builtin state backend found for scheme '%s'",
                self.scheme,
            )

        try:
            return self.addon.get(self.scheme)
        except KeyError:
            logger.info(
                "No state backend plugin found for scheme '%s'",
                self.scheme,
            )

        # TODO: This should be a Meltano exception
        msg = f"No state backend found for scheme '{self.scheme}'"
        raise ValueError(msg)


def state_store_manager_from_project_settings(
    settings_service: ProjectSettingsService,
    session: Session | None = None,
) -> StateStoreManager:
    """Return a StateStoreManager based on the project's settings.

    Args:
        settings_service: the settings service to use
        session: the session to use if using default systemdb state backend

    Returns:
        The relevant StateStoreManager instance.
    """
    state_backend_uri: str = settings_service.get("state_backend.uri")
    parsed = urlparse(state_backend_uri)
    if state_backend_uri == BuiltinStateBackendEnum.SYSTEMDB:
        return DBStateStoreManager(
            session=session or project_engine(settings_service.project)[1](),
        )
    scheme = parsed.scheme
    # Get backend-specific settings
    # AND top-level state_backend settings
    setting_defs = filter(
        lambda setting_def: setting_def.name.startswith(
            f"state_backend.{'gcs' if scheme == 'gs' else scheme}",
        )
        or (
            setting_def.name.startswith("state_backend")
            and len(setting_def.name.split(".")) == 2
        ),
        settings_service.setting_definitions,
    )
    settings = (setting_def.name for setting_def in setting_defs)
    backend = StateBackend(scheme).manager
    if (
        scheme == BuiltinStateBackendEnum.LOCAL_FILESYSTEM
        and "Windows" in platform.system()
    ):
        backend = WindowsFilesystemStateStoreManager
    kwargs = {name.split(".")[-1]: settings_service.get(name) for name in settings}
    return backend(**kwargs)
