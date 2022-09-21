"""Meltano Iglu schemas metadata & utilities."""

from __future__ import annotations

from dataclasses import dataclass

DEFAULT_VENDOR = "com.meltano"


@dataclass
class IgluSchema:
    """Dataclass to store the name, version, vendor, and URL for an Iglu schema."""

    name: str
    version: str
    vendor: str = DEFAULT_VENDOR

    @property
    def url(self) -> str:
        """Construct an iglu schema URL.

        Returns:
            The URL to the schema.
        """
        return f"iglu:{self.vendor}/{self.name}/jsonschema/{self.version}"


CliContextSchema = IgluSchema("cli_context", "1-1-0")
CliEventSchema = IgluSchema("cli_event", "1-0-1")
BlockEventSchema = IgluSchema("block_event", "1-0-0")
EnvironmentContextSchema = IgluSchema("environment_context", "1-0-0")
ExceptionContextSchema = IgluSchema("exception_context", "1-0-0")
ExitEventSchema = IgluSchema("exit_event", "1-0-1")
PluginsContextSchema = IgluSchema("plugins_context", "1-0-0")
ProjectContextSchema = IgluSchema("project_context", "1-1-0")
TelemetryStateChangeEventSchema = IgluSchema("telemetry_state_change_event", "1-0-0")
