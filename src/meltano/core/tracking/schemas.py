"""Meltano Iglu schemas metadata & utilities."""

from __future__ import annotations

VENDOR = "com.meltano"

SCHEMAS: dict[str, str] = {
    "cli_context": "1-0-0",
    "cli_event": "1-0-0",
    "block_event": "1-0-0",
    "environment_context": "1-0-0",
    "exit_event": "1-0-0",
    "plugins_context": "1-0-0",
    "project_context": "1-0-0",
    "telemetry_state_change_event": "1-0-0",
}


def get_schema_url(schema_name: str) -> str:
    """Construct an iglu schema URL using the provided name and the stored version.

    Parameters:
        schema_name: The name of the schema the URL should be for.

    Returns:
        The URL to the schema.
    """
    return f"iglu:{VENDOR}/{schema_name}/jsonschema/{SCHEMAS[schema_name]}"
