"""Project context for the Snowplow tracker."""

from __future__ import annotations

import typing as t
import uuid
from enum import Enum, auto
from functools import cached_property

from structlog.stdlib import get_logger

from meltano._vendor.snowplow_tracker import SelfDescribingJson  # noqa: WPS436
from meltano.core.tracking.schemas import ProjectContextSchema
from meltano.core.utils import hash_sha256

if t.TYPE_CHECKING:
    from meltano.core.project import Project

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
        (
            send_anonymous_usage_stats,
            send_anonymous_usage_stats_metadata,
        ) = project.settings.get_with_metadata("send_anonymous_usage_stats")

        super().__init__(
            ProjectContextSchema.url,
            {
                "context_uuid": str(uuid.uuid4()),
                "project_uuid": str(self.project_uuid),
                "project_uuid_source": self.project_uuid_source.name,
                "client_uuid": str(client_id),
                "send_anonymous_usage_stats": send_anonymous_usage_stats,
                "send_anonymous_usage_stats_source": (
                    send_anonymous_usage_stats_metadata["source"].value
                ),
            },
        )

        self.environment_name = getattr(self.project.environment, "name", None)

    @property
    def environment_name(self) -> str | None:
        """Get the name of the active environment.

        Only the hash of this value is reported to Snowplow.

        Returns:
            The name of the active environment, or `None` if there is no active
            environment.
        """
        return self._environment_name

    @environment_name.setter
    def environment_name(self, value: str | None) -> None:
        self._environment_name = value
        if value is None:
            self.data["environment_name_hash"] = None
        else:
            self.data["environment_name_hash"] = hash_sha256(value)

    @property
    def project_uuid_source(self) -> ProjectUUIDSource:
        """Obtain the source of the `project_uuid` used for telemetry.

        Returns:
            ProjectUUIDSource: The source of the `project_uuid` used for telemetry.
        """
        # Ensure the `project_uuid` has been generated
        self.project_uuid  # noqa: B018
        return self._project_uuid_source

    @cached_property
    def project_uuid(self) -> uuid.UUID:
        """Obtain the `project_id` from the project config file.

        If it is not found (e.g. first time run), generate a valid v4 UUID,
        and and store it in the project config file.

        Returns:
            The project UUID.
        """
        if project_id_str := self.project.settings.get("project_id"):
            try:
                # Project ID might already be a UUID
                project_id = uuid.UUID(project_id_str)
            except ValueError:
                # If the project ID is not a UUID, then we hash it, and use the
                # hash to make a UUID
                project_id = uuid.UUID(hash_sha256(project_id_str)[::2])
                self._project_uuid_source = ProjectUUIDSource.derived
            else:
                self._project_uuid_source = ProjectUUIDSource.explicit
        else:
            project_id = uuid.uuid4()
            self._project_uuid_source = ProjectUUIDSource.random

        return project_id
