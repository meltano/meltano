"""State backends."""

from __future__ import annotations

import sys
import typing as t
from urllib.parse import urlparse

from structlog.stdlib import get_logger

from meltano.core.behavior.addon import MeltanoAddon
from meltano.core.db import project_engine
from meltano.core.state_store.base import MeltanoState, StateStoreManager
from meltano.core.state_store.db import DBStateStoreManager

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from backports.strenum import StrEnum

if sys.version_info >= (3, 12):
    from importlib.metadata import EntryPoints, entry_points
else:
    from importlib_metadata import EntryPoints, entry_points

if t.TYPE_CHECKING:
    from collections.abc import Mapping

    from sqlalchemy.orm import Session

    from meltano.core.project_settings_service import ProjectSettingsService

__all__ = [
    "DBStateStoreManager",
    "MeltanoState",
    "StateBackend",
    "StateStoreManager",
    "state_store_manager_from_project_settings",
]

logger = get_logger(__name__)

SYSTEMDB = "systemdb"


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
        return [
            SYSTEMDB,
            *(ep.name for ep in cls.addon.installed),
        ]

    @property
    def manager(self) -> type[StateStoreManager]:
        """Get the StateStoreManager associated with this StateBackend.

        Returns:
            The StateStoreManager associated with this StateBackend.

        Raises:
            ValueError: If no state backend is found for the scheme.
        """
        try:
            manager = self.addon.get(self.scheme)
        except KeyError:
            msg = f"No state backend found for scheme '{self.scheme}'. "
            msg += "Available backends: " + ", ".join(self.backends())
            raise ValueError(msg) from None

        logger.info("Using %s add-on state backend", manager.__name__)
        return manager


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
    if state_backend_uri == SYSTEMDB:
        logger.info("Using systemdb state backend")
        return DBStateStoreManager(
            session=session or project_engine(settings_service.project)[1](),
        )

    scheme = urlparse(state_backend_uri).scheme
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
    kwargs = {name.split(".")[-1]: settings_service.get(name) for name in settings}
    return backend(**kwargs)
