from __future__ import annotations

import mock

from asserts import assert_cli_runner
from meltano.cli import cli
from meltano.core.project_settings_service import (
    ProjectSettingsService,
    SettingValueStore,
)


class TestCliUi:
    def test_ui(self, project, cli_runner):
        with mock.patch(
            "meltano.cli.ui.APIWorker.start"
        ) as start_api_worker, mock.patch(
            "meltano.cli.ui.UIAvailableWorker.start"
        ) as start_ui_available_worker:
            result = cli_runner.invoke(cli, "ui")
            assert_cli_runner(result)

            assert start_api_worker.called
            assert start_ui_available_worker.called

    def test_ui_setup(self, project, cli_runner, monkeypatch):
        monkeypatch.setenv("MELTANO_UI_SECRET_KEY", "existing_secret_key")

        with mock.patch("meltano.cli.ui.secrets.token_hex", return_value="fake_secret"):
            result = cli_runner.invoke(cli, ["ui", "setup", "meltano.example.com"])

        assert_cli_runner(result)

        assert (
            "Setting 'ui.secret_key' has already been set in the environment"
            in result.stdout
        )

        settings_service = ProjectSettingsService(project)

        assert settings_service.get_with_source("ui.server_name") == (
            "meltano.example.com",
            SettingValueStore.DOTENV,
        )
        assert settings_service.get_with_source("ui.secret_key") == (
            "existing_secret_key",
            SettingValueStore.ENV,
        )
        assert settings_service.get_with_source("ui.password_salt") == (
            "fake_secret",
            SettingValueStore.DOTENV,
        )
