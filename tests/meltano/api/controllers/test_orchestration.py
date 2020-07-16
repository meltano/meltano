import pytest
from unittest import mock
from flask import url_for

from meltano.core.plugin.settings_service import (
    SettingValueStore,
    REDACTED_VALUE,
    Profile,
)


class TestOrchestration:
    def test_get_configuration(
        self,
        app,
        api,
        tap,
        session,
        plugin_settings_service_factory,
        plugin_discovery_service,
        monkeypatch,
    ):
        plugin_settings_service = plugin_settings_service_factory(tap)
        plugin_settings_service.set(
            "secure", "thisisatest", store=SettingValueStore.DOTENV, session=session
        )

        monkeypatch.setenv("TAP_MOCK_BOOLEAN", "false")

        with mock.patch(
            "meltano.api.controllers.orchestrations.PluginDiscoveryService",
            return_value=plugin_discovery_service,
        ), app.test_request_context():
            res = api.get(
                url_for("orchestrations.get_plugin_configuration", plugin_ref=tap)
            )

            assert res.status_code == 200
            default_profile = res.json["profiles"][0]
            config = default_profile["config"]
            config_metadata = default_profile["config_metadata"]

            # make sure that set `password` is still present
            # but redacted in the response
            assert plugin_settings_service.get_with_source(
                "secure", session=session
            ) == ("thisisatest", SettingValueStore.DOTENV)
            assert config["secure"] == REDACTED_VALUE
            assert config_metadata["secure"]["redacted"] == True
            assert config_metadata["secure"]["source"] == "dotenv"
            assert config_metadata["secure"]["auto_store"] == "dotenv"
            assert config_metadata["secure"]["overwritable"] == True

            # make sure that `boolean` cannot be overwritten
            assert plugin_settings_service.get_with_source(
                "boolean", session=session
            ) == (False, SettingValueStore.ENV)
            assert config["boolean"] == False
            assert config_metadata["boolean"]["source"] == "env"
            assert config_metadata["boolean"]["auto_store"] == "dotenv"
            assert config_metadata["boolean"]["overwritable"] == False

            # make sure the `hidden` setting is still present
            # but hidden in the response
            assert plugin_settings_service.get_with_source(
                "hidden", session=session
            ) == (42, SettingValueStore.DEFAULT)
            assert "hidden" not in config

    def test_save_configuration(
        self,
        app,
        api,
        tap,
        session,
        plugin_settings_service_factory,
        plugin_discovery_service,
    ):
        plugin_settings_service = plugin_settings_service_factory(tap)
        plugin_settings_service.set(
            "secure", "thisisatest", store=SettingValueStore.DOTENV, session=session
        )
        plugin_settings_service.set(
            "protected", "iwontchange", store=SettingValueStore.DB, session=session
        )

        with mock.patch(
            "meltano.core.plugin.settings_service.PluginDiscoveryService",
            return_value=plugin_discovery_service,
        ), app.test_request_context():
            res = api.put(
                url_for("orchestrations.save_plugin_configuration", plugin_ref=tap),
                json=[
                    {
                        "name": Profile.DEFAULT.name,
                        "config": {"protected": "N33DC0FF33", "secure": "newvalue"},
                    }
                ],
            )

            assert res.status_code == 200
            config = res.json[0]["config"]

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
