import json
from unittest import mock

import pytest
from meltano.core.plugin import PluginType


class TestSingerMapper:
    @pytest.fixture(scope="class")
    def subject(self, project_add_service):
        return project_add_service.add(PluginType.MAPPERS, "mapper-mock")

    @pytest.mark.asyncio
    async def test_exec_args(self, subject, session, plugin_invoker_factory, tmpdir):
        invoker = plugin_invoker_factory(subject)
        async with invoker.prepared(session):
            assert subject.exec_args(invoker) == ["--config", invoker.files["config"]]

    @pytest.mark.asyncio
    async def test_before_configure(
        self, subject, session, plugin_invoker_factory, tmpdir
    ):
        invoker = plugin_invoker_factory(subject)

        invoker.plugin_config_override = "config-override"
        mock_open = mock.mock_open(read_data=None)
        async with invoker.prepared(session):
            with mock.patch("builtins.open", mock_open):
                invoker.plugin_config_processed = "config-processed"
                await subject.before_configure(invoker, session)
                assert mock_open.call_args[0][0] == invoker.files["config"]
                assert mock_open.call_args[0][1] == "w"
                mock_open.return_value.write.assert_called_once_with(
                    json.dumps("config-override")
                )

        invoker.plugin_config_override = None
        mock_open = mock.mock_open(read_data=None)
        async with invoker.prepared(session):
            invoker.plugin_config_processed = "config-processed"
            with mock.patch("builtins.open", mock_open):
                await subject.before_configure(invoker, session)
                assert mock_open.call_args[0][0] == invoker.files["config"]
                assert mock_open.call_args[0][1] == "w"
                mock_open.return_value.write.assert_called_once_with(
                    json.dumps("config-processed")
                )
