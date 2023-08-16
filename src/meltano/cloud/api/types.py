"""Static types for the Meltano Cloud client."""

from __future__ import annotations

import typing as t


class CloudExecution(t.TypedDict):
    """Meltano Cloud execution details."""

    execution_id: str
    start_time: str
    end_time: str | None
    status: str
    exit_code: int

    deployment_name: str
    schedule_name: str
    job_name: str


class CloudProjectSchedule(t.TypedDict):
    """Meltano Cloud project schedule details."""

    deployment_name: str
    schedule_name: str
    interval: str
    enabled: bool


class CloudProject(t.TypedDict):
    """Meltano Cloud project details."""

    # Tenant resource key and project ID are included to enable
    # `meltano cloud project use`, which sets the default project ID
    # to use in internal API requests:
    tenant_resource_key: str
    project_id: str

    # Public attributes:
    project_name: str
    git_repository: str
    project_root_path: str

    # Added client-side:
    default: bool


class CloudDeployment(t.TypedDict):
    """Meltano Cloud deployment details."""

    deployment_name: str
    environment_name: str
    git_rev: str
    git_rev_hash: str
    last_deployed_timestamp: str

    # Added client-side:
    default: bool


class CloudConfigProject(t.TypedDict):
    """Meltano cloud config project settings for default deployments."""

    default_deployment_name: str | None


class CloudConfigOrg(t.TypedDict):
    """Meltano cloud config org for storing default projects and deployments."""

    default_project_id: str | None
    projects_defaults: dict[str, CloudConfigProject]


class CloudNotification(t.TypedDict):
    """Meltano Cloud notification details."""

    type: str
    status: str
    recipient: str
    filters: list[dict[str, t.Any]]
