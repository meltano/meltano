"""Azure state backend settings."""

from __future__ import annotations

from meltano.core.setting_definition import SettingDefinition, SettingKind

CONNECTION_STRING = SettingDefinition(
    name="state_backend.azure.connection_string",
    label="Connection String",
    description="Connection string for the Azure Blob Storage account",
    kind=SettingKind.STRING,
    sensitive=True,
    env_specific=True,
)

STORAGE_ACCOUNT_URL = SettingDefinition(
    name="state_backend.azure.storage_account_url",
    label="Storage Account URL",
    description="URL for the Azure Blob Storage account",
    kind=SettingKind.STRING,
    env_specific=True,
)
