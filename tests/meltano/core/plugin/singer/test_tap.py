import pytest
import json
from unittest import mock

from meltano.core.plugin import PluginType
from meltano.core.plugin.error import PluginExecutionError
from meltano.core.plugin_invoker import PluginInvoker
from meltano.core.plugin.singer.catalog import ListSelectedExecutor


class TestSingerTap:
    @pytest.fixture(scope="class")
    def subject(self, project_add_service):
        return project_add_service.add(PluginType.EXTRACTORS, "tap-mock")

    def test_exec_args(self, subject, session, plugin_invoker_factory, tmpdir):
        invoker = plugin_invoker_factory(subject)
        with invoker.prepared(session):
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

    def test_cleanup(self, subject, session, plugin_invoker_factory):
        invoker = plugin_invoker_factory(subject)
        with invoker.prepared(session):
            assert invoker.files["config"].exists()

        assert not invoker.files["config"].exists()

    def test_discover_catalog(self, session, plugin_invoker_factory, subject):
        invoker = plugin_invoker_factory(subject)

        catalog_path = invoker.files["catalog"]

        def mock_discovery():
            catalog_path.open("w").write('{"discovered": true}')
            return ("", "")

        process_mock = mock.Mock()
        process_mock.communicate = mock_discovery
        process_mock.returncode = 0

        with invoker.prepared(session), mock.patch.object(
            PluginInvoker, "invoke", return_value=process_mock
        ) as invoke:
            subject.discover_catalog(invoker, [])

            assert invoke.called_with(["--discover"])

            assert catalog_path.read_text() == '{"discovered": true}'

    def test_discover_catalog_custom(
        self, project, session, plugin_invoker_factory, subject, monkeypatch
    ):
        invoker = plugin_invoker_factory(subject)

        custom_catalog_filename = "custom_catalog.json"
        custom_catalog_path = project.root.joinpath(custom_catalog_filename)
        custom_catalog_path.write_text('{"custom": true}')

        monkeypatch.setitem(
            invoker.settings_service.config_override,
            "_catalog",
            custom_catalog_filename,
        )

        with invoker.prepared(session):
            subject.discover_catalog(invoker, [])

        assert invoker.files["catalog"].read_text() == '{"custom": true}'

    def test_discover_catalog_fails(self, session, plugin_invoker_factory, subject):
        process_mock = mock.Mock()
        process_mock.communicate.return_value = ("", "")
        process_mock.returncode = 1  # something went wrong

        invoker = plugin_invoker_factory(subject)
        with invoker.prepared(session):
            with mock.patch.object(
                PluginInvoker, "invoke", return_value=process_mock
            ) as invoke, pytest.raises(PluginExecutionError, match="returned 1"):
                subject.discover_catalog(invoker, [])

                assert not invoker.files[
                    "catalog"
                ].exists(), "Catalog should not be present."

    def test_apply_select(self, session, plugin_invoker_factory, subject, monkeypatch):
        invoker = plugin_invoker_factory(subject)

        catalog_path = invoker.files["catalog"]

        def reset_catalog():
            catalog_path.open("w").write('{"rules": []}')

        def assert_rules(*rules):
            with catalog_path.open() as catalog_file:
                catalog = json.load(catalog_file)

            assert catalog["rules"] == list(rules)

        def mock_metadata_executor(rules):
            def visit(catalog):
                for rule in rules:
                    catalog["rules"].append(
                        [rule.tap_stream_id, rule.breadcrumb, rule.key, rule.value]
                    )

            return mock.Mock(visit=visit)

        with mock.patch(
            "meltano.core.plugin.singer.tap.MetadataExecutor",
            side_effect=mock_metadata_executor,
        ):
            reset_catalog()

            with invoker.prepared(session):
                subject.apply_catalog_rules(invoker)

            # When `select` isn't set in meltano.yml or discovery.yml, select all
            assert_rules(
                ["*", [], "selected", False],
                ["*", ["properties", "*"], "selected", False],
                ["*", [], "selected", True],
                ["*", ["properties", "*"], "selected", True],
            )

            reset_catalog()

            # Pretend `select` is set in discovery.yml
            monkeypatch.setitem(
                invoker.plugin_def.extras, "select", ["UniqueEntitiesName.name"]
            )
            invoker.settings_service._setting_defs = None
            with invoker.prepared(session):
                subject.apply_catalog_rules(invoker)

            # When `select` is set in discovery.yml, use the selection
            assert_rules(
                ["*", [], "selected", False],
                ["*", ["properties", "*"], "selected", False],
                ["UniqueEntitiesName", [], "selected", True],
                ["UniqueEntitiesName", ["properties", "name"], "selected", True],
            )

            reset_catalog()

            # Pretend `select` is set in meltano.yml
            monkeypatch.setitem(
                invoker.plugin.extras, "select", ["UniqueEntitiesName.code"]
            )

            with invoker.prepared(session):
                subject.apply_catalog_rules(invoker)

            # `select` set in meltano.yml takes precedence over discovery.yml
            assert_rules(
                ["*", [], "selected", False],
                ["*", ["properties", "*"], "selected", False],
                ["UniqueEntitiesName", [], "selected", True],
                ["UniqueEntitiesName", ["properties", "code"], "selected", True],
            )

    def test_apply_catalog_rules(
        self, session, plugin_invoker_factory, subject, monkeypatch
    ):
        invoker = plugin_invoker_factory(subject)

        catalog_path = invoker.files["catalog"]

        def reset_catalog():
            catalog_path.open("w").write('{"rules": []}')

        def assert_rules(*rules):
            with catalog_path.open() as catalog_file:
                catalog = json.load(catalog_file)

            assert catalog["rules"] == list(rules)

        def mock_metadata_executor(rules):
            def visit(catalog):
                for rule in rules:
                    rule_list = [
                        rule.tap_stream_id,
                        rule.breadcrumb,
                        rule.key,
                        rule.value,
                    ]
                    if rule.negated:
                        rule_list.append({"negated": True})
                    catalog["rules"].append(rule_list)

            return mock.Mock(visit=visit)

        def mock_schema_executor(rules):
            def visit(catalog):
                for rule in rules:
                    catalog["rules"].append(
                        [rule.tap_stream_id, rule.breadcrumb, rule.payload]
                    )

            return mock.Mock(visit=visit)

        with mock.patch(
            "meltano.core.plugin.singer.tap.MetadataExecutor",
            side_effect=mock_metadata_executor,
        ), mock.patch(
            "meltano.core.plugin.singer.tap.SchemaExecutor",
            side_effect=mock_schema_executor,
        ):
            reset_catalog()

            config = {
                "_select": ["UniqueEntitiesName.code"],
                "_metadata": {
                    "UniqueEntitiesName": {"replication-key": "created_at"},
                    "UniqueEntitiesName.created_at": {"is-replication-key": True},
                },
                "metadata.UniqueEntitiesName.properties.payload.properties.hash.custom-metadata": "custom-value",
                "_schema": {
                    "UniqueEntitiesName": {
                        "code": {"anyOf": [{"type": "string"}, {"type": "null"}]}
                    },
                    "UniqueEntitiesName.payload.type": "object",
                    "UniqueEntitiesName.payload.properties": {
                        "content": {"type": ["string", "null"]},
                        "hash": {"type": "string"},
                    },
                },
                "_select_filter": [
                    "UniqueEntitiesName",
                    "!OtherEntitiesName",
                    "SelectAnother",
                    "!ExcludeAnother",
                ],
            }

            # Pretend `config` is set in meltano.yml
            with mock.patch.object(invoker.plugin, "config", config):
                with invoker.prepared(session):
                    subject.apply_catalog_rules(invoker)

            assert_rules(
                # Schema rules
                [
                    "UniqueEntitiesName",
                    ["properties", "code"],
                    {"anyOf": [{"type": "string"}, {"type": "null"}]},
                ],
                [
                    "UniqueEntitiesName",
                    ["properties", "payload"],
                    {
                        "type": "object",
                        "properties": {
                            "content": {"type": ["string", "null"]},
                            "hash": {"type": "string"},
                        },
                    },
                ],
                # Clean slate selection metadata rules
                ["*", [], "selected", False],
                ["*", ["properties", "*"], "selected", False],
                # Selection metadata rules
                ["UniqueEntitiesName", [], "selected", True],
                ["UniqueEntitiesName", ["properties", "code"], "selected", True],
                # Metadata rules
                ["UniqueEntitiesName", [], "replication-key", "created_at"],
                [
                    "UniqueEntitiesName",
                    ["properties", "created_at"],
                    "is-replication-key",
                    True,
                ],
                [
                    "UniqueEntitiesName",
                    ["properties", "payload", "properties", "hash"],
                    "custom-metadata",
                    "custom-value",
                ],
                # Selection filter metadata rules
                [
                    ["UniqueEntitiesName", "SelectAnother"],
                    [],
                    "selected",
                    False,
                    {"negated": True},
                ],
                [["OtherEntitiesName", "ExcludeAnother"], [], "selected", False],
            )

            reset_catalog()

            # If a custom catalog is provided, only selection filters are applied
            config_override = invoker.settings_service.config_override
            monkeypatch.setitem(config_override, "_catalog", "custom_catalog.json")

            # Pretend `config` is set in meltano.yml
            with mock.patch.object(invoker.plugin, "config", config):
                with invoker.prepared(session):
                    subject.apply_catalog_rules(invoker)

            assert_rules(
                # Selection filter metadata rules
                [
                    ["UniqueEntitiesName", "SelectAnother"],
                    [],
                    "selected",
                    False,
                    {"negated": True},
                ],
                [["OtherEntitiesName", "ExcludeAnother"], [], "selected", False],
            )

    def test_apply_catalog_rules_select_filter(
        self, session, plugin_invoker_factory, subject, monkeypatch
    ):
        invoker = plugin_invoker_factory(subject)

        stream_metadata = {
            "metadata": [{"breadcrumb": [], "metadata": {"inclusion": "available"}}]
        }

        base_catalog = {
            "streams": [
                {"tap_stream_id": "one", **stream_metadata},
                {"tap_stream_id": "two", **stream_metadata},
                {"tap_stream_id": "three", **stream_metadata},
                {"tap_stream_id": "four", **stream_metadata},
                {"tap_stream_id": "five", **stream_metadata},
            ]
        }

        def selected_entities():
            catalog_path = invoker.files["catalog"]

            with catalog_path.open("w") as catalog_file:
                json.dump(base_catalog, catalog_file)

            with invoker.prepared(session):
                subject.apply_catalog_rules(invoker, [])

            with catalog_path.open() as catalog_file:
                catalog = json.load(catalog_file)

            lister = ListSelectedExecutor()
            lister.visit(catalog)

            return list(lister.selected_properties.keys())

        config_override = invoker.settings_service.config_override

        monkeypatch.setitem(config_override, "_select", ["one.*", "three.*", "five.*"])
        assert selected_entities() == ["one", "three", "five"]

        # Simple inclusion
        monkeypatch.setitem(config_override, "_select_filter", ["three"])
        assert selected_entities() == ["three"]

        # Simple exclusion
        monkeypatch.setitem(config_override, "_select_filter", ["!three"])
        assert selected_entities() == ["one", "five"]

        # Wildcard inclusion
        monkeypatch.setitem(config_override, "_select_filter", ["t*"])
        assert selected_entities() == ["three"]

        # Wildcard exclusion
        monkeypatch.setitem(config_override, "_select_filter", ["!t*"])
        assert selected_entities() == ["one", "five"]

        # Multiple inclusion
        monkeypatch.setitem(config_override, "_select_filter", ["three", "five"])
        assert selected_entities() == ["three", "five"]

        # Multiple exclusion
        monkeypatch.setitem(config_override, "_select_filter", ["!three", "!five"])
        assert selected_entities() == ["one"]

        # Multiple wildcard inclusion
        monkeypatch.setitem(config_override, "_select_filter", ["t*", "f*"])
        assert selected_entities() == ["three", "five"]

        # Multiple wildcard exclusion
        monkeypatch.setitem(config_override, "_select_filter", ["!t*", "!f*"])
        assert selected_entities() == ["one"]

        # Mixed inclusion and exclusion
        monkeypatch.setitem(config_override, "_select_filter", ["*e", "!*ee"])
        assert selected_entities() == ["one", "five"]

    def test_apply_catalog_rules_invalid(
        self, session, plugin_invoker_factory, subject
    ):
        invoker = plugin_invoker_factory(subject)
        with invoker.prepared(session):
            invoker.files["catalog"].open("w").write("this is invalid json")

            with pytest.raises(PluginExecutionError, match=r"invalid"):
                subject.apply_catalog_rules(invoker, [])
