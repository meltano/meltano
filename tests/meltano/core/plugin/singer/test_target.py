import pytest
from meltano.core.plugin import PluginType


class TestSingerTarget:
    @pytest.fixture
    def subject(self, project_add_service):
        try:
            return project_add_service.add(PluginType.LOADERS, "target-mock")
        except PluginAlreadyAddedException as err:
            return err.plugin

    def test_exec_args(self, subject, session, plugin_invoker_factory):
        invoker = plugin_invoker_factory(subject)
        with invoker.prepared(session):
            assert subject.exec_args(invoker) == ["--config", invoker.files["config"]]
