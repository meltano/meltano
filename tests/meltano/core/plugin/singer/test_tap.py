import pytest
import json
from unittest import mock

from meltano.core.plugin import PluginType
from meltano.core.plugin.error import PluginExecutionError
from meltano.core.plugin_invoker import PluginInvoker


class TestSingerTap:
    @pytest.fixture(scope="class")
    def subject(self, project_add_service):
        return project_add_service.add(PluginType.EXTRACTORS, "tap-mock")

    def test_exec_args(self, subject, session, plugin_invoker_factory, tmpdir):
        invoker = plugin_invoker_factory(subject, prepare_with_session=session)

        assert subject.exec_args(invoker) == ["--config", invoker.files["config"]]

        # when `catalog` has data
        invoker.files["catalog"].open("w").write("...")
        assert subject.exec_args(invoker) == [
            "--config",
            invoker.files["config"],
            "--catalog",
            invoker.files["catalog"],
        ]

        # when `state` has data
        invoker.files["state"].open("w").write("...")
        assert subject.exec_args(invoker) == [
            "--config",
            invoker.files["config"],
            "--catalog",
            invoker.files["catalog"],
            "--state",
            invoker.files["state"],
        ]

    def test_run_discovery(self, session, plugin_invoker_factory, subject):
        invoker = plugin_invoker_factory(subject, prepare_with_session=session)

        def mock_discovery():
            invoker.files["catalog"].open("w").write("{}")
            return ("", "")

        process_mock = mock.Mock()
        process_mock.communicate = mock_discovery
        process_mock.returncode = 0

        with mock.patch.object(
            PluginInvoker, "invoke", return_value=process_mock
        ) as invoke:
            subject.run_discovery(invoker, [])

            assert invoke.called_with(["--discover"])

    def test_run_discovery_fails(self, session, plugin_invoker_factory, subject):
        process_mock = mock.Mock()
        process_mock.communicate.return_value = ("", "")
        process_mock.returncode = 1  # something went wrong

        invoker = plugin_invoker_factory(subject, prepare_with_session=session)

        with mock.patch.object(
            PluginInvoker, "invoke", return_value=process_mock
        ) as invoke, pytest.raises(PluginExecutionError, match="returned 1"):
            subject.run_discovery(invoker, [])

            assert not invoker.files[
                "catalog"
            ].exists(), "Catalog should not be present."

    def test_apply_select(self, session, plugin_invoker_factory, subject):
        invoker = plugin_invoker_factory(subject, prepare_with_session=session)

        properties_file = invoker.files["catalog"]

        def reset_properties():
            properties_file.open("w").write('{"patterns": []}')

        def assert_patterns(*patterns):
            with properties_file.open() as catalog:
                schema = json.load(catalog)

            assert schema["patterns"] == list(patterns)

        def mock_select_executor(patterns):
            def visit(schema):
                schema["patterns"].append(patterns)

            return mock.Mock(visit=visit)

        with mock.patch(
            "meltano.core.plugin.singer.tap.SelectExecutor",
            side_effect=mock_select_executor,
        ):
            reset_properties()

            subject.apply_select(invoker)

            # When `select` isn't set in meltano.yml or discovery.yml, select all
            assert_patterns(["!*.*"], ["*.*"])

            reset_properties()

            # Pretend `select` is set in discovery.yml
            with mock.patch.object(
                invoker.plugin_def, "select", ["UniqueEntitiesName.name"]
            ):
                subject.apply_select(invoker)

                # When `select` is set in discovery.yml, use the selection
                assert_patterns(["!*.*"], ["UniqueEntitiesName.name"])

                reset_properties()

                # Pretend `select` is set in meltano.yml
                with mock.patch.object(
                    invoker.plugin, "select", ["UniqueEntitiesName.code"]
                ):
                    subject.apply_select(invoker)

                # `select` set in meltano.yml takes precedence over discovery.yml
                assert_patterns(["!*.*"], ["UniqueEntitiesName.code"])

    def test_apply_select_catalog_invalid(
        self, session, plugin_invoker_factory, subject
    ):
        invoker = plugin_invoker_factory(subject, prepare_with_session=session)

        invoker.files["catalog"].open("w").write("this is invalid json")

        with pytest.raises(PluginExecutionError, match=r"invalid"):
            subject.apply_select(invoker, [])
