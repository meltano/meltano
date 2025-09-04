"""S3 state backend settings."""

from __future__ import annotations

from meltano.core.setting_definition import SettingDefinition, SettingKind

AWS_ACCESS_KEY_ID = SettingDefinition(
    name="state_backend.s3.aws_access_key_id",
    label="AWS Access Key ID",
    description="AWS Access Key ID",
    kind=SettingKind.STRING,
    sensitive=True,
    env_specific=True,
)

AWS_SECRET_ACCESS_KEY = SettingDefinition(
    name="state_backend.s3.aws_secret_access_key",
    label="AWS Secret Access Key",
    description="AWS Secret Access Key",
    kind=SettingKind.STRING,
    sensitive=True,
    env_specific=True,
)

ENDPOINT_URL = SettingDefinition(
    name="state_backend.s3.endpoint_url",
    label="Endpoint URL",
    description="URL for the AWS S3 or S3-compatible storage service",
    kind=SettingKind.STRING,
    env_specific=True,
)
