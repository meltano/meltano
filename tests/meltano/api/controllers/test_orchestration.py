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
    ):
        plugin_settings_service = plugin_settings_service_factory(tap)
        plugin_settings_service.set("secure", "thisisatest", session=session)

        with mock.patch(
            "meltano.api.controllers.orchestrations.PluginDiscoveryService",
            return_value=plugin_discovery_service,
        ), app.test_request_context():
            res = api.get(
                url_for("orchestrations.get_plugin_configuration", plugin_ref=tap)
            )

            assert res.status_code == 200
            default_config = res.json["profiles"][0]["config"]

            # make sure that set `password` is still present
            # but redacted in the response
            assert plugin_settings_service.get_with_source(
                "secure", session=session
            ) == ("thisisatest", SettingValueStore.DB)
            assert default_config["secure"] == REDACTED_VALUE

            # make sure the `hidden` setting is still present
            # but hidden in the response
            assert plugin_settings_service.get_with_source(
                "hidden", session=session
            ) == (42, SettingValueStore.DEFAULT)
            assert "hidden" not in default_config

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
        plugin_settings_service.set("secure", "thisisatest", session=session)
        plugin_settings_service.set("protected", "iwontchange", session=session)

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
            ) == ("newvalue", SettingValueStore.DB)
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
