"""Google Cloud Storage state backend settings."""

from __future__ import annotations

from meltano.core.setting_definition import SettingDefinition, SettingKind

APPLICATION_CREDENTIALS = SettingDefinition(
    name="state_backend.gcs.application_credentials",
    label="Application Credentials",
    description=(
        "Path to the credential file to use in authenticating to Google Cloud Storage"
    ),
    kind=SettingKind.STRING,
    sensitive=True,
    env_specific=True,
)

APPLICATION_CREDENTIALS_PATH = SettingDefinition(
    name="state_backend.gcs.application_credentials_path",
    label="Application Credentials Path",
    description=(
        "Path to the credential file to use in authenticating to Google Cloud Storage"
    ),
    kind=SettingKind.STRING,
    sensitive=True,
    env_specific=True,
)

APPLICATION_CREDENTIALS_JSON = SettingDefinition(
    name="state_backend.gcs.application_credentials_json",
    label="Application Credentials JSON",
    description=(
        "JSON object containing the service account credentials for "
        "Google Cloud Storage"
    ),
    kind=SettingKind.STRING,
    sensitive=True,
    env_specific=True,
)
