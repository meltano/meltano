from __future__ import annotations

import json

from flask import Flask, url_for
from flask.testing import FlaskClient
from flask.wrappers import Response
from mock import AsyncMock, mock

from meltano.core.settings_service import REDACTED_VALUE, SettingValueStore


class TestOrchestration:
    def test_get_configuration(
        self,
        app,
        api,
        tap,
        session,
        plugin_settings_service_factory,
        project_plugins_service,
        monkeypatch,
    ):
        plugin_settings_service = plugin_settings_service_factory(tap)
        plugin_settings_service.set(
            "secure", "thisisatest", store=SettingValueStore.DOTENV, session=session
        )

        monkeypatch.setenv("TAP_MOCK_BOOLEAN", "false")

        with mock.patch(
            "meltano.api.controllers.orchestrations.ProjectPluginsService",
            return_value=project_plugins_service,
        ), app.test_request_context():
            res = api.get(
                url_for("orchestrations.get_plugin_configuration", plugin_ref=tap)
            )

            assert res.status_code == 200
            config = res.json["config"]
            config_metadata = res.json["config_metadata"]

            # make sure that set `password` is still present
            # but redacted in the response
            assert plugin_settings_service.get_with_source(
                "secure", session=session
            ) == ("thisisatest", SettingValueStore.DOTENV)
            assert config["secure"] == REDACTED_VALUE
            assert config_metadata["secure"]["redacted"] is True
            assert config_metadata["secure"]["source"] == "dotenv"
            assert config_metadata["secure"]["auto_store"] == "dotenv"
            assert config_metadata["secure"]["overwritable"] is True

            # make sure the `hidden` setting is still present
            # but hidden in the response
            assert plugin_settings_service.get_with_source(
                "hidden", session=session
            ) == (42, SettingValueStore.DEFAULT)
            assert "hidden" not in config

            # Extras are excluded
            assert "_select" not in config
            assert "_metadata" not in config
            assert "_schema" not in config

            setting_names = [s["name"] for s in res.json["settings"]]
            assert "_select" not in setting_names
            assert "_metadata" not in setting_names
            assert "_schema" not in setting_names

    def test_save_configuration(
        self,
        app,
        api,
        tap,
        session,
        plugin_settings_service_factory,
        project_plugins_service,
    ):
        plugin_settings_service = plugin_settings_service_factory(tap)
        plugin_settings_service.set(
            "secure", "thisisatest", store=SettingValueStore.DOTENV, session=session
        )
        plugin_settings_service.set(
            "protected", "iwontchange", store=SettingValueStore.DB, session=session
        )

        with mock.patch(
            "meltano.api.controllers.orchestrations.ProjectPluginsService",
            return_value=project_plugins_service,
        ), app.test_request_context():
            res = api.put(
                url_for("orchestrations.save_plugin_configuration", plugin_ref=tap),
                json={"config": {"protected": "N33DC0FF33", "secure": "newvalue"}},
            )

            assert res.status_code == 200
            config = res.json["config"]

            # make sure that set `password` has been updated
            # but redacted in the response
            assert plugin_settings_service.get_with_source(
                "secure", session=session
            ) == ("newvalue", SettingValueStore.DOTENV)
            assert config["secure"] == REDACTED_VALUE

            # make sure the `readonly` field has not been updated
            assert plugin_settings_service.get_with_source(
                "protected", session=session
            ) == ("iwontchange", SettingValueStore.DB)

            # make sure the `hidden` setting is still present
            # but hidden in the response
            assert plugin_settings_service.get_with_source(
                "hidden", session=session
            ) == (42, SettingValueStore.DEFAULT)
            assert "hidden" not in config

    @mock.patch("meltano.core.plugin_test_service.PluginInvoker.invoke_async")
    @mock.patch("meltano.api.controllers.orchestrations.ProjectPluginsService")
    def test_test_plugin_configuration_success(
        self,
        mock_project_plugins_service,
        mock_invoke_async,
        app: Flask,
        api: FlaskClient,
        tap,
        project_plugins_service,
    ):

        mock_project_plugins_service.return_value = project_plugins_service

        mock_invoke = mock.Mock()
        mock_invoke.sterr.at_eof.side_effect = True
        mock_invoke.stdout.at_eof.side_effect = (False, True)
        mock_invoke.wait = AsyncMock(return_value=-1)
        mock_invoke.returncode = -1
        payload = json.dumps({"type": "RECORD"}).encode()
        mock_invoke.stdout.readline = AsyncMock(return_value=b"%b" % payload)

        mock_invoke_async.return_value = mock_invoke

        with app.test_request_context():
            url = url_for("orchestrations.test_plugin_configuration", plugin_ref=tap)
            res: Response = api.post(url, json={})

        assert res.status_code == 200
        assert res.json["is_success"]

    @mock.patch("meltano.core.plugin_test_service.PluginInvoker.invoke_async")
    @mock.patch("meltano.api.controllers.orchestrations.ProjectPluginsService")
    def test_test_plugin_configuration_failure(
        self,
        mock_project_plugins_service,
        mock_invoke_async,
        app: Flask,
        api: FlaskClient,
        tap,
        project_plugins_service,
    ):

        mock_project_plugins_service.return_value = project_plugins_service

        mock_invoke = mock.Mock()
        mock_invoke.sterr.at_eof.side_effect = True
        mock_invoke.stdout.at_eof.side_effect = (False, True)
        mock_invoke.wait = AsyncMock(return_value=0)
        mock_invoke.returncode = 0
        payload = b"test"
        mock_invoke.stdout.readline = AsyncMock(return_value=b"%b" % payload)

        mock_invoke_async.return_value = mock_invoke

        with app.test_request_context():
            url = url_for("orchestrations.test_plugin_configuration", plugin_ref=tap)
            res: Response = api.post(url, json={})

        assert res.status_code == 200
        assert not res.json["is_success"]
