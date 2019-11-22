import pytest
from unittest import mock
from flask import url_for

from meltano.core.plugin.settings_service import (
    PluginSettingValueSource,
    REDACTED_VALUE,
    Profile,
)


class TestOrchestration:
    def test_get_configuration(self, app, api, tap, session, plugin_settings_service):
        plugin_settings_service.set(session, tap, "secure", "thisisatest")

        with mock.patch(
            "meltano.api.controllers.orchestrations.PluginSettingsService",
            return_value=plugin_settings_service,
        ), app.test_request_context():
            res = api.get(
                url_for("orchestrations.get_plugin_configuration", plugin_ref=tap)
            )

            assert res.status_code == 200

            # make sure that set `password` is still present
            # but redacted in the response
            assert plugin_settings_service.get_value(session, tap, "secure") == (
                "thisisatest",
                PluginSettingValueSource.DB,
            )

            assert res.json["profiles"][0]["config"]["secure"] == REDACTED_VALUE

    def test_save_configuration(self, app, api, tap, session, plugin_settings_service):
        plugin_settings_service.set(session, tap, "secure", "thisisatest")
        plugin_settings_service.set(session, tap, "protected", "iwontchange")

        with mock.patch(
            "meltano.api.controllers.orchestrations.PluginSettingsService",
            return_value=plugin_settings_service,
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

            # make sure that set `password` has been updated
            # but redacted in the response
            assert plugin_settings_service.get_value(session, tap, "secure") == (
                "newvalue",
                PluginSettingValueSource.DB,
            )
            assert res.json[0]["config"]["secure"] == REDACTED_VALUE

            # make sure the `readonly` field has not been updated
            assert plugin_settings_service.get_value(session, tap, "protected") == (
                "iwontchange",
                PluginSettingValueSource.DB,
            )
