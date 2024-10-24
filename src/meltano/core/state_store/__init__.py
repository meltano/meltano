"""State backends."""

from __future__ import annotations

import enum
import platform
import sys
import typing as t
from urllib.parse import urlparse

from meltano.core.db import project_engine
from meltano.core.state_store.azure import AZStorageStateStoreManager
from meltano.core.state_store.base import MeltanoState
from meltano.core.state_store.db import DBStateStoreManager
from meltano.core.state_store.filesystem import (
    LocalFilesystemStateStoreManager,
    WindowsFilesystemStateStoreManager,
)
from meltano.core.state_store.google import GCSStateStoreManager
from meltano.core.state_store.s3 import S3StateStoreManager

if sys.version_info < (3, 11):
    from backports.strenum import StrEnum
else:
    from enum import StrEnum

if t.TYPE_CHECKING:
    from collections.abc import Mapping

    from sqlalchemy.orm import Session

    from meltano.core.project_settings_service import ProjectSettingsService
    from meltano.core.state_store.base import StateStoreManager


__all__ = ["MeltanoState", "state_store_manager_from_project_settings"]


class StateBackend(StrEnum):
    """State backend."""

    SYSTEMDB = "systemdb"
    # These strings should match the expected scheme for URIs of
    # the given type. E.g., filesystem state backends have a
    # file://<path>/<to>/<state directory> URI
    LOCAL_FILESYSTEM = "file"
    AZURE = "azure"
    S3 = "s3"
    GCS = "gs"

    @classmethod
    def backends(cls) -> list[StateBackend]:
        """List available state backends.

        Returns:
            List of available state backends.
        """
        return list(cls)

    @property
    def _managers(
        self,
    ) -> Mapping[str, type[StateStoreManager]]:
        """Get mapping of StateBackend to associated StateStoreManager.

        Returns:
            Mapping of StateBackend to associated StateStoreManager.
        """
        return {
            self.SYSTEMDB: DBStateStoreManager,
            self.LOCAL_FILESYSTEM: LocalFilesystemStateStoreManager,
            self.S3: S3StateStoreManager,
            self.AZURE: AZStorageStateStoreManager,
            self.GCS: GCSStateStoreManager,
        }

    @property
    def manager(
        self,
    ) -> type[StateStoreManager]:
        """Get the StateStoreManager associated with this StateBackend.

        Returns:
            The StateStoreManager associated with this StateBackend.
        """
        return self._managers[self]


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
    if state_backend_uri == StateBackend.SYSTEMDB:
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
    if scheme == StateBackend.LOCAL_FILESYSTEM and "Windows" in platform.system():
        backend = WindowsFilesystemStateStoreManager
    kwargs = {name.split(".")[-1]: settings_service.get(name) for name in settings}
    return backend(**kwargs)
