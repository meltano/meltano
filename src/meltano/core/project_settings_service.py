"""Project Settings Service."""

from __future__ import annotations

import json
import sys
import typing as t

import structlog

from meltano.core.error import ProjectReadonly
from meltano.core.settings_service import SettingsService, SettingValueStore
from meltano.core.utils import nest_object

if sys.version_info >= (3, 11):
    from typing import Self  # noqa: ICN003
else:
    from typing_extensions import Self

if sys.version_info >= (3, 12):
    from typing import override  # noqa: ICN003
else:
    from typing_extensions import override

if t.TYPE_CHECKING:
    from meltano.core.project import Project
    from meltano.core.setting_definition import SettingDefinition

logger = structlog.get_logger(__name__)

PYTHON_SETTING_NAME = "python"
PYTHON_VERSION_FILENAME = ".python-version"


class ProjectSettingsService(SettingsService):
    """Project Settings Service."""

    config_override: t.ClassVar[dict[str, t.Any]] = {}  # type: ignore[misc]
    supports_environments = False

    def __init__(
        self,
        project: Project,
        *,
        show_hidden: bool = True,
        env_override: dict | None = None,
        config_override: dict | None = None,
    ):
        """Instantiate a `ProjectSettingsService` instance.

        Args:
            project: Meltano project instance.
            show_hidden: Whether to display secret setting values.
            env_override: Optional override environment values.
            config_override:  Optional override configuration values.
        """
        super().__init__(
            project=project,
            show_hidden=show_hidden,
            env_override=env_override,
            config_override=config_override,
        )

        # terminal env vars are already present from `SettingService.env`
        self.env_override = {
            # static, project-level env vars (e.g. MELTANO_ENVIRONMENT)
            **self.project.env,
            # env vars stored in the base `meltano.yml` `env:` key
            **self.project.meltano.env,
            # overrides
            **self.env_override,
        }

        self.config_override = {  # type: ignore[misc]  # ty:ignore[invalid-attribute-access]
            **self.__class__.config_override,
            **self.config_override,
        }

        try:
            self.ensure_project_id()
        except ProjectReadonly:
            logger.debug(
                "Cannot update `project_id` in `meltano.yml`: project is read-only.",
            )

    @property
    @override
    def project_settings_service(self) -> Self:
        """Settings service for this project.

        For ProjectSettingsService, just returns self.
        """
        return self

    def ensure_project_id(self) -> None:
        """Ensure `project_id` is configured properly.

        Every `meltano.yml` file should contain the `project_id`
        key-value pair. It should be present in the top-level config, rather
        than in any environment-level configs.

        If it is not present, it will be restored from `analytics.json` if possible.
        """
        try:
            project_id = self.get("project_id")
        except OSError:
            project_id = None

        if project_id is None:
            analytics_path = self.project.dirs.meltano() / "analytics.json"
            try:
                with analytics_path.open() as analytics_json_file:
                    project_id = json.load(analytics_json_file)["project_id"]
            except (OSError, KeyError, json.JSONDecodeError) as err:
                logger.debug(
                    "Unable to restore 'project_id' from 'analytics.json'",
                    err=err,
                )
            else:
                self.set("project_id", project_id, store=SettingValueStore.MELTANO_YML)
                logger.debug("Restored 'project_id' from 'analytics.json'")

    @property
    @override
    def label(self) -> str:
        """Project label."""
        return "Meltano"

    @property
    @override
    def docs_url(self) -> str:
        """URL for Meltano doc site."""
        return "https://docs.meltano.com/reference/settings"

    @property
    @override
    def db_namespace(self) -> str:
        """Namespace for setting value records in system database."""
        return "meltano"

    @property
    @override
    def setting_definitions(self) -> list[SettingDefinition]:
        """Definitions of supported settings."""
        return self.project.config_service.settings

    @property
    @override
    def meltano_yml_config(self) -> dict[str, t.Any]:
        """Current configuration in `meltano.yml`."""
        return self.project.config_service.current_config

    @override
    def update_meltano_yml_config(self, config: dict[str, t.Any]) -> None:
        """Update configuration in `meltano.yml`.

        Args:
            config: Updated config.
        """
        self.project.config_service.update_config(config)

    @override
    def process_config(self, config: dict[str, t.Any]) -> dict[str, t.Any]:
        """Process configuration dict for presentation in `meltano config meltano`.

        Args:
            config: Config to process.

        Returns:
            Processed configuration dict for presentation in `meltano config meltano`.
        """
        return nest_object(config)

    def python_version_file_value(self) -> str | None:
        """Read the project-level `.python-version` file, if present.

        Returns:
            The first non-empty, non-comment line from `.python-version`, or None.
        """
        python_version_file = self.project.root / PYTHON_VERSION_FILENAME
        try:
            contents = python_version_file.read_text(encoding="utf-8")
        except OSError:
            return None

        for line in contents.splitlines():
            value = line.strip()
            if value and not value.startswith("#"):
                return value

        return None

    @override
    def get_with_metadata(
        self,
        name: str,
        **kwargs: t.Any,
    ) -> tuple[t.Any, dict[str, t.Any]]:
        """Get a project setting with `.python-version` fallback support.

        Args:
            name: Setting name.
            kwargs: Keyword arguments forwarded to the base settings service.

        Returns:
            A tuple of setting value and metadata.
        """
        value, metadata = super().get_with_metadata(name, **kwargs)
        setting_def = kwargs.get("setting_def") or self.find_setting(name)
        setting_name = setting_def.name if setting_def else name

        if (
            setting_name == PYTHON_SETTING_NAME
            and value is None
            and metadata["source"] is SettingValueStore.DEFAULT
        ):
            python_version = self.python_version_file_value()
            if python_version:
                value = python_version
                metadata = {
                    **metadata,
                    "python_version_file": str(
                        self.project.root / PYTHON_VERSION_FILENAME,
                    ),
                }

        return value, metadata
