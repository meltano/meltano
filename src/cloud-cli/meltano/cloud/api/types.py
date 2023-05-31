"""Static types for the Meltano Cloud client."""

from __future__ import annotations

import sys

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict


class CloudExecution(TypedDict):
    """Meltano Cloud execution details."""

    execution_id: str
    start_time: str
    end_time: str | None
    status: str
    exit_code: int

    environment_name: str
    schedule_name: str
    job_name: str


class CloudProjectSchedule(TypedDict):
    """Meltano Cloud project schedule details."""

    deployment_name: str
    schedule_name: str
    interval: str
    enabled: bool


class CloudProject(TypedDict):
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


class CloudDeployment(TypedDict):
    """Meltano Cloud deployment details."""

    deployment_name: str
    environment_name: str
    git_rev: str
    git_rev_hash: str
    last_deployed_timestamp: str

    # Added client-side:
    default: bool
