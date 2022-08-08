"""Project context for the Snowplow tracker."""

from __future__ import annotations

import uuid
from enum import Enum, auto

from cached_property import cached_property
from snowplow_tracker import SelfDescribingJson
from structlog.stdlib import get_logger

from meltano.core.project import Project
from meltano.core.project_settings_service import ProjectSettingsService
from meltano.core.tracking.schemas import ProjectContextSchema
from meltano.core.utils import hash_sha256

logger = get_logger(__name__)


class ProjectUUIDSource(Enum):
    """The source of the `project_uuid` used for telemetry."""

    # The UUID was explicitly provided in the config as the `project_id`.
    explicit = auto()

    # The UUID was derived by hashing the `project_id` in the config.
    derived = auto()

    # The UUID was randomly generated (UUID v4) since no `project_id` was configured.
    random = auto()


class ProjectContext(SelfDescribingJson):
    """Tracking context for the Meltano project."""

    def __init__(self, project: Project, client_id: uuid.UUID):
        """Initialize a meltano tracking "project" context.

        Args:
            project: The Meltano project.
            client_id: The client ID from `analytics.json`.
        """
        self.project = project
        self.settings_service = ProjectSettingsService(project)
        (
            send_anonymous_usage_stats,
            send_anonymous_usage_stats_metadata,
        ) = self.settings_service.get_with_metadata("send_anonymous_usage_stats")

        super().__init__(
            ProjectContextSchema.url,
            {
                "context_uuid": str(uuid.uuid4()),
                "project_uuid": str(self.project_uuid),
                "project_uuid_source": self.project_uuid_source.name,
                "client_uuid": str(client_id),
                "environment_name_hash": (
                    hash_sha256(self.project.active_environment.name)
                    if self.project.active_environment
                    else None
                ),
                "send_anonymous_usage_stats": send_anonymous_usage_stats,
                "send_anonymous_usage_stats_source": (
                    send_anonymous_usage_stats_metadata["source"].value
                ),
            },
        )

    @property
    def project_uuid_source(self) -> ProjectUUIDSource:
        """Obtain the source of the `project_uuid` used for telemetry.

        Returns:
            ProjectUUIDSource: The source of the `project_uuid` used for telemetry.
        """
        # Ensure the `project_uuid` has been generated
        self.project_uuid  # noqa: WPS428
        return self._project_uuid_source

    @cached_property
    def project_uuid(self) -> uuid.UUID:
        """Obtain the `project_id` from the project config file.

        If it is not found (e.g. first time run), generate a valid v4 UUID, and and store it in the
        project config file.

        Returns:
            The project UUID.
        """
        project_id_str = self.settings_service.get("project_id")

        if project_id_str:
            try:
                # Project ID might already be a UUID
                project_id = uuid.UUID(project_id_str)
            except ValueError:
                # If the project ID is not a UUID, then we hash it, and use the hash to make a UUID
                project_id = uuid.UUID(hash_sha256(project_id_str)[::2])
                self._project_uuid_source = ProjectUUIDSource.derived
            else:
                self._project_uuid_source = ProjectUUIDSource.explicit
        else:
            project_id = uuid.uuid4()
            self._project_uuid_source = ProjectUUIDSource.random

        return project_id
