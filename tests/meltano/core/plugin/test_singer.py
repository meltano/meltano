import pytest
from unittest import mock
from pathlib import Path

from meltano.core.plugin import PluginType
from meltano.core.plugin_invoker import PluginInvoker


class TestSingerTap:
    @pytest.fixture
    def subject(self,
                project_add_service):
        return project_add_service.add(PluginType.EXTRACTORS, "tap-first")

    def config_files(self, subject, dir: Path):
        return {
            key: dir.join(file)
            for key, file in subject.config_files.items()
        }

    def test_exec_args(self, subject, tmpdir):
        base_files = self.config_files(subject, tmpdir.mkdir("base"))
        assert subject.exec_args(base_files) == ["--config", base_files["config"]]

        # when `catalog` has data
        base_files = self.config_files(subject, tmpdir.mkdir("catalog"))
        base_files["catalog"].open("w").write("...")
        assert subject.exec_args(base_files) == ["--config", base_files["config"], "--catalog", base_files["catalog"]]

        # when `state` has data
        base_files = self.config_files(subject, tmpdir.mkdir("state"))
        base_files["state"].open("w").write("...")
        assert subject.exec_args(base_files) == ["--config", base_files["config"], "--state", base_files["state"]]

    def test_run_discovery(self, project, subject):
        process_mock = mock.Mock()
        process_mock.wait.return_value = 00

        invoker = PluginInvoker(project, subject)
        invoker.prepare()
        
        with mock.patch.object(PluginInvoker, "invoke", return_value=process_mock) as invoke:
            subject.run_discovery(invoker, [])
            
            assert invoke.called_with(["--discover"])


class TestSingerTarget:
    @pytest.fixture
    def subject(self,
                project_add_service):
        return project_add_service.add(PluginType.LOADERS, "target-csv")

    def test_exec_args(self, subject):
        base_files = subject.config_files
        assert subject.exec_args(base_files) == ["--config", base_files["config"]]
