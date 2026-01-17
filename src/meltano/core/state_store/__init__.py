"""State backends."""

from __future__ import annotations

import sys
import typing as t
from urllib.parse import urlparse

from structlog.stdlib import get_logger

from meltano.core.behavior.addon import MeltanoAddon
from meltano.core.db import project_engine
from meltano.core.error import MeltanoError
from meltano.core.state_store.base import MeltanoState, StateStoreManager
from meltano.core.state_store.db import DBStateStoreManager

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from backports.strenum import StrEnum

if t.TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from meltano.core.project_settings_service import ProjectSettingsService

if sys.version_info >= (3, 12):
    from importlib.metadata import EntryPoints, entry_points
else:
    from importlib_metadata import EntryPoints, entry_points

__all__ = [
    "DBStateStoreManager",
    "MeltanoState",
    "StateBackend",
    "StateStoreManager",
    "state_store_manager_from_project_settings",
]

logger = get_logger(__name__)

SYSTEMDB = "systemdb"
SCHEME_TO_NAMESPACE = {
    "gs": "gcs",
}


class StateBackendNotFoundError(MeltanoError):
    """No state backend found for the given scheme."""

    def __init__(self, scheme: str):
        """Create a new NoStateBackendFoundError.

        Args:
            scheme: The scheme of the StateBackend.
        """
        self.scheme = scheme
        super().__init__(
            f"No state backend found for scheme '{scheme}', available backends are: "
            f"{', '.join(StateBackend.backends())}",
            instruction="Install the add-on that provides it",
        )


class StateBackend:
    """State backend."""

    addon: MeltanoAddon[type[StateStoreManager]] = MeltanoAddon(
        "meltano.state_backends",
    )

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

    @classmethod
    def get_manager_factory(cls, *, scheme: str) -> type[StateStoreManager]:
        """Get the StateStoreManager associated with this StateBackend.

        Returns:
            The StateStoreManager associated with this StateBackend.

        Raises:
            ValueError: If no state backend is found for the scheme.
        """
        try:
            manager = cls.addon.get(scheme)
        except KeyError:
            raise StateBackendNotFoundError(scheme) from None

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
    manager_factory = StateBackend.get_manager_factory(scheme=scheme)
    return manager_factory(
        **_settings_to_manager_kwargs(
            settings=settings_service,
            namespace=SCHEME_TO_NAMESPACE.get(scheme, scheme),
        )
    )


def _settings_to_manager_kwargs(
    *,
    settings: ProjectSettingsService,
    namespace: str,
) -> dict[str, t.Any]:
    """Create a dictionary of keyword arguments for a state store manager from settings.

    Args:
        settings: the settings to use.
        namespace: the setting namespace that corresponds to this manager.
    """
    kwargs = {}
    for setting_def in settings.setting_definitions:
        parts = setting_def.name.split(".")
        if parts[0] != "state_backend" or len(parts) < 2:
            continue

        # e.g. "state_backend.s3.[aws_access_key_id]"
        # or "state_backend.[lock_timeout_seconds]"
        if len(parts) == 2 or (parts[1] == namespace):
            kwargs[parts[-1]] = settings.get(setting_def.name)

    return kwargs
