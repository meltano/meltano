import pytest
import json
from unittest import mock
from contextlib import contextmanager

from meltano.core.plugin import PluginType
from meltano.core.plugin.error import PluginExecutionError
from meltano.core.plugin_invoker import PluginInvoker
from meltano.core.plugin.singer.catalog import ListSelectedExecutor
from meltano.core.job import Job, Payload


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

    @pytest.mark.asyncio
    async def test_look_up_state(
        self,
        subject,
        project,
        session,
        plugin_invoker_factory,
        elt_context_builder,
        monkeypatch,
    ):
        job = Job(job_id="pytest_test_runner")
        elt_context = (
            elt_context_builder.with_session(session)
            .with_extractor(subject.name)
            .with_job(job)
            .context()
        )

        invoker = plugin_invoker_factory(subject, context=elt_context)

        @contextmanager
        def create_job():
            new_job = Job(job_id=job.job_id)
            new_job.start()
            yield new_job
            new_job.save(session)

        def assert_state(state):
            with invoker.prepared(session):
                subject.look_up_state(invoker, [])

            if state:
                assert invoker.files["state"].exists()
                assert json.load(invoker.files["state"].open()) == state
            else:
                assert not invoker.files["state"].exists()

        # No state by default
        assert_state(None)

        # Running jobs with state are not considered
        with create_job() as job:
            job.payload["singer_state"] = {"success": True}
            job.payload_flags = Payload.STATE

        assert_state(None)

        # Successful jobs without state are not considered
        with create_job() as job:
            job.success()

        assert_state(None)

        # Successful jobs with incomplete state are considered
        with create_job() as job:
            job.payload["singer_state"] = {"incomplete_success": True}
            job.payload_flags = Payload.INCOMPLETE_STATE
            job.success()

        assert_state({"incomplete_success": True})

        # Successful jobs with state are considered
        with create_job() as job:
            job.payload["singer_state"] = {"success": True}
            job.payload_flags = Payload.STATE
            job.success()

        assert_state({"success": True})

        # Running jobs with state are not considered
        with create_job() as job:
            job.payload["singer_state"] = {"success": True}
            job.payload_flags = Payload.STATE

        assert_state({"success": True})

        # Failed jobs without state are not considered
        with create_job() as job:
            job.fail("Whoops")

        assert_state({"success": True})

        # Failed jobs with state are considered
        with create_job() as job:
            job.payload["singer_state"] = {"failed": True}
            job.payload_flags = Payload.STATE
            job.fail("Whoops")

        assert_state({"failed": True})

        # Successful jobs with incomplete state are considered
        with create_job() as job:
            job.payload["singer_state"] = {"success": True}
            job.payload_flags = Payload.INCOMPLETE_STATE
            job.success()

        # Incomplete state is merged into complete state
        assert_state({"failed": True, "success": True})

        # Failed jobs with incomplete state are considered
        with create_job() as job:
            job.payload["singer_state"] = {"failed_again": True}
            job.payload_flags = Payload.INCOMPLETE_STATE
            job.fail("Whoops")

        # Incomplete state is merged into complete state
        assert_state({"failed": True, "success": True, "failed_again": True})

        # Custom state takes precedence
        custom_state_filename = "custom_state.json"
        custom_state_path = project.root.joinpath(custom_state_filename)
        custom_state_path.write_text('{"custom": true}')

        monkeypatch.setitem(
            invoker.settings_service.config_override, "_state", custom_state_filename
        )

        assert_state({"custom": True})

        # With a full refresh, no state is considered
        elt_context.full_refresh = True
        assert_state(None)

    def test_discover_catalog(self, session, plugin_invoker_factory, subject):
        invoker = plugin_invoker_factory(subject)

        catalog_path = invoker.files["catalog"]
        catalog_cache_key_path = invoker.files["catalog_cache_key"]

        def mock_discovery():
            catalog_path.open("w").write('{"discovered": true}')
            return ("", "")

        process_mock = mock.Mock()
        process_mock.communicate = mock_discovery
        process_mock.returncode = 0

        with invoker.prepared(session):
            with mock.patch.object(
                PluginInvoker, "invoke", return_value=process_mock
            ) as invoke:
                subject.discover_catalog(invoker, [])

                assert invoke.called_with(["--discover"])

            assert json.loads(catalog_path.read_text()) == {"discovered": True}
            assert not catalog_cache_key_path.exists()

            # If there is no cache key, discovery is invoked again
            with mock.patch.object(
                PluginInvoker, "invoke", return_value=process_mock
            ) as invoke:
                subject.discover_catalog(invoker, [])

                assert invoke.called_with(["--discover"])

            assert json.loads(catalog_path.read_text()) == {"discovered": True}
            assert not catalog_cache_key_path.exists()

            # Apply catalog rules to store the cache key
            subject.apply_catalog_rules(invoker, [])
            assert catalog_cache_key_path.exists()

            # If the cache key hasn't changed, discovery isn't invoked again
            with mock.patch.object(
                PluginInvoker, "invoke", return_value=process_mock
            ) as invoke:
                subject.discover_catalog(invoker, [])

                invoke.assert_not_called()

            assert json.loads(catalog_path.read_text()) == {"discovered": True}
            assert catalog_cache_key_path.exists()

            # If the cache key no longer matches, discovery is invoked again
            catalog_cache_key_path.write_text("bogus")

            with mock.patch.object(
                PluginInvoker, "invoke", return_value=process_mock
            ) as invoke:
                subject.discover_catalog(invoker, [])

                assert invoke.called_with(["--discover"])

            assert json.loads(catalog_path.read_text()) == {"discovered": True}
            assert not catalog_cache_key_path.exists()

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
        catalog_cache_key_path = invoker.files["catalog_cache_key"]

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

                    cache_key = invoker.plugin.catalog_cache_key(invoker)

            # Stores the cache key
            assert catalog_cache_key_path.read_text() == cache_key

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

                    cache_key = invoker.plugin.catalog_cache_key(invoker)

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

            # Doesn't store a cache key when a custom catalog is provided
            assert not catalog_cache_key_path.exists()
            assert cache_key is None

    def test_apply_catalog_rules_select_filter(
        self, session, plugin_invoker_factory, subject, monkeypatch
    ):
        invoker = plugin_invoker_factory(subject)

        stream_data = {
            "schema": {
                "type": "object",
                "properties": {
                    "one": {"type": "string"},
                    "two": {"type": "string"},
                    "three": {"type": "string"},
                },
            },
            "metadata": [
                {"breadcrumb": [], "metadata": {"inclusion": "available"}},
                {
                    "breadcrumb": ["properties", "one"],
                    "metadata": {"inclusion": "automatic"},
                },
                {
                    "breadcrumb": ["properties", "two"],
                    "metadata": {"inclusion": "available"},
                },
                {
                    "breadcrumb": ["properties", "three"],
                    "metadata": {"inclusion": "available"},
                },
            ],
        }

        base_catalog = {
            "streams": [
                {"tap_stream_id": "one", **stream_data},
                {"tap_stream_id": "two", **stream_data},
                {"tap_stream_id": "three", **stream_data},
                {"tap_stream_id": "four", **stream_data},
                {"tap_stream_id": "five", **stream_data},
            ]
        }

        def selected_properties():
            catalog_path = invoker.files["catalog"]

            with catalog_path.open("w") as catalog_file:
                json.dump(base_catalog, catalog_file)

            with invoker.prepared(session):
                subject.apply_catalog_rules(invoker, [])

            with catalog_path.open() as catalog_file:
                catalog = json.load(catalog_file)

            lister = ListSelectedExecutor()
            lister.visit(catalog)

            return lister.selected_properties

        config_override = invoker.settings_service.config_override

        monkeypatch.setitem(
            config_override, "_select", ["one.one", "three.three", "five.*"]
        )

        # `one` is always included because it has `inclusion: automatic`
        assert selected_properties() == {
            "one": {"one"},
            "three": {"one", "three"},
            "five": {"one", "two", "three"},
        }

        # Simple inclusion
        monkeypatch.setitem(config_override, "_select_filter", ["three"])
        assert selected_properties() == {"three": {"one", "three"}}

        # Simple exclusion
        monkeypatch.setitem(config_override, "_select_filter", ["!three"])
        assert selected_properties() == {
            "one": {"one"},
            "five": {"one", "two", "three"},
        }

        # Wildcard inclusion
        monkeypatch.setitem(config_override, "_select_filter", ["t*"])
        assert selected_properties() == {"three": {"one", "three"}}

        # Wildcard exclusion
        monkeypatch.setitem(config_override, "_select_filter", ["!t*"])
        assert selected_properties() == {
            "one": {"one"},
            "five": {"one", "two", "three"},
        }

        # Multiple inclusion
        monkeypatch.setitem(config_override, "_select_filter", ["three", "five"])
        assert selected_properties() == {
            "three": {"one", "three"},
            "five": {"one", "two", "three"},
        }

        # Multiple exclusion
        monkeypatch.setitem(config_override, "_select_filter", ["!three", "!five"])
        assert selected_properties() == {"one": {"one"}}

        # Multiple wildcard inclusion
        monkeypatch.setitem(config_override, "_select_filter", ["t*", "f*"])
        assert selected_properties() == {
            "three": {"one", "three"},
            "five": {"one", "two", "three"},
        }

        # Multiple wildcard exclusion
        monkeypatch.setitem(config_override, "_select_filter", ["!t*", "!f*"])
        assert selected_properties() == {"one": {"one"}}

        # Mixed inclusion and exclusion
        monkeypatch.setitem(config_override, "_select_filter", ["*e", "!*ee"])
        assert selected_properties() == {
            "one": {"one"},
            "five": {"one", "two", "three"},
        }

    def test_apply_catalog_rules_invalid(
        self, session, plugin_invoker_factory, subject
    ):
        invoker = plugin_invoker_factory(subject)
        with invoker.prepared(session):
            invoker.files["catalog"].open("w").write("this is invalid json")

            with pytest.raises(PluginExecutionError, match=r"invalid"):
                subject.apply_catalog_rules(invoker, [])

    def test_catalog_cache_key(
        self, session, plugin_invoker_factory, subject, monkeypatch
    ):
        invoker = plugin_invoker_factory(subject)
        config_override = invoker.settings_service.config_override

        def cache_key():
            with invoker.prepared(session):
                return subject.catalog_cache_key(invoker)

        # No key if _catalog is set
        monkeypatch.setitem(config_override, "_catalog", "catalog.json")
        assert cache_key() is None

        # Key is set if _catalog is not set
        monkeypatch.setitem(config_override, "_catalog", None)
        key = cache_key()
        assert key is not None

        # Key doesn't change if nothing has changed
        assert cache_key() == key

        # Key changes if config changes
        monkeypatch.setitem(config_override, "test", "foo")

        new_key = cache_key()
        assert new_key != key
        key = new_key

        # Key changes if _schema changes
        monkeypatch.setitem(
            config_override, "_schema", {"stream": {"property": {"type": "string"}}}
        )

        new_key = cache_key()
        assert new_key != key
        key = new_key

        # Key changes if _metadata changes
        monkeypatch.setitem(
            config_override,
            "_metadata",
            {"stream": {"property": {"is-replication-key": True}}},
        )

        new_key = cache_key()
        assert new_key != key
        key = new_key

        # Key does not change if _select changes
        monkeypatch.setitem(config_override, "_select", ["stream"])
        assert cache_key() == key

        # Key does not change if _select_filter changes
        monkeypatch.setitem(config_override, "_select_filter", ["stream"])
        assert cache_key() == key

        # No key if pip_url is editable
        monkeypatch.setattr(invoker.plugin_def, "pip_url", "-e local")
        assert cache_key() is None
