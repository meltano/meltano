from __future__ import annotations

import asyncio
import json
import logging
import subprocess
import sys
from contextlib import contextmanager

import pytest
from mock import AsyncMock, mock

from meltano.core.job import Job, Payload
from meltano.core.plugin import PluginType
from meltano.core.plugin.error import PluginExecutionError
from meltano.core.plugin.singer import SingerTap
from meltano.core.plugin.singer.catalog import ListSelectedExecutor
from meltano.core.state_service import InvalidJobStateError, StateService


class TestSingerTap:
    @pytest.fixture(scope="class")
    def subject(self, project_add_service):
        return project_add_service.add(PluginType.EXTRACTORS, "tap-mock")

    @pytest.mark.order(0)
    @pytest.mark.asyncio
    async def test_exec_args(self, subject, session, plugin_invoker_factory):
        invoker = plugin_invoker_factory(subject)
        async with invoker.prepared(session):
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

    @pytest.mark.asyncio
    async def test_cleanup(self, subject, session, plugin_invoker_factory):
        invoker = plugin_invoker_factory(subject)
        async with invoker.prepared(session):
            assert invoker.files["config"].exists()

        assert not invoker.files["config"].exists()

    @pytest.mark.asyncio
    async def test_look_up_state(  # noqa: WPS213, WPS217
        self,
        subject,
        project,
        session,
        plugin_invoker_factory,
        elt_context_builder,
        monkeypatch,
    ):
        job = Job(job_name="pytest_test_runner")
        elt_context = (
            elt_context_builder.with_session(session)
            .with_extractor(subject.name)
            .with_job(job)
            .context()
        )

        invoker = plugin_invoker_factory(subject, context=elt_context)
        state_service = StateService(session=session)

        @contextmanager
        def create_job():

            new_job = Job(job_name=job.job_name)
            new_job.start()
            yield new_job
            new_job.save(session)
            if new_job.payload and not new_job.is_running():
                try:
                    state_service.add_state(
                        new_job.job_name,
                        json.dumps(new_job.payload),
                        new_job.payload_flags,
                    )
                except InvalidJobStateError:
                    pass

        async def assert_state(state):
            async with invoker.prepared(session):
                await subject.look_up_state(invoker)

            if state:
                assert invoker.files["state"].exists()
                assert json.load(invoker.files["state"].open()) == state
            else:
                assert not invoker.files["state"].exists()

        # No state by default
        await assert_state(None)

        # Running jobs with state are not considered
        with create_job() as job:
            job.payload["singer_state"] = {"success": True}
            job.payload_flags = Payload.STATE

        await assert_state(None)

        # Successful jobs without state are not considered
        with create_job() as job:
            job.success()
        await assert_state(None)

        # Successful jobs with incomplete state are considered
        with create_job() as job:
            job.payload["singer_state"] = {"incomplete_success": True}
            job.payload_flags = Payload.INCOMPLETE_STATE
            job.success()

        await assert_state({"incomplete_success": True})

        # Successful jobs with state are considered
        with create_job() as job:
            job.payload["singer_state"] = {"success": True}
            job.payload_flags = Payload.STATE
            job.success()
        await assert_state({"success": True})

        # Failed jobs without state are not considered
        with create_job() as job:
            job.fail("Whoops")

        await assert_state({"success": True})

        # Failed jobs with state are considered
        with create_job() as job:
            job.payload["singer_state"] = {"failed": True}
            job.payload_flags = Payload.STATE
            job.fail("Whoops")

        await assert_state({"failed": True})

        # Successful jobs with incomplete state are considered
        with create_job() as job:
            job.payload["singer_state"] = {"success": True}
            job.payload_flags = Payload.INCOMPLETE_STATE
            job.success()

        # Incomplete state is merged into complete state
        await assert_state({"failed": True, "success": True})

        # Failed jobs with incomplete state are considered
        with create_job() as job:
            job.payload["singer_state"] = {"failed_again": True}
            job.payload_flags = Payload.INCOMPLETE_STATE
            job.fail("Whoops")

        # Incomplete state is merged into complete state
        await assert_state({"failed": True, "success": True, "failed_again": True})

        # Custom state takes precedence
        custom_state_filename = "custom_state.json"
        custom_state_path = project.root.joinpath(custom_state_filename)
        custom_state_path.write_text('{"custom": true}')

        monkeypatch.setitem(
            invoker.settings_service.config_override, "_state", custom_state_filename
        )

        await assert_state({"custom": True})

        # With a full refresh, no state is considered
        elt_context.full_refresh = True
        await assert_state(None)

    @pytest.mark.order(1)
    @pytest.mark.asyncio
    async def test_discover_catalog(  # noqa: WPS213
        self, session, plugin_invoker_factory, subject
    ):
        invoker = plugin_invoker_factory(subject)

        catalog_path = invoker.files["catalog"]
        catalog_cache_key_path = invoker.files["catalog_cache_key"]

        def mock_discovery(*args, **kwargs):
            future = asyncio.Future()
            future.set_result(catalog_path.open("w").write('{"discovered": true}'))
            return future

        async with invoker.prepared(session):
            with mock.patch.object(
                SingerTap, "run_discovery", side_effect=mock_discovery
            ) as mocked_run_discovery:
                await subject.discover_catalog(invoker)

                assert mocked_run_discovery.called
                assert json.loads(catalog_path.read_text()) == {"discovered": True}
                assert not catalog_cache_key_path.exists()

                # If there is no cache key, discovery is invoked again
                mocked_run_discovery.reset_mock()
                await subject.discover_catalog(invoker)

                assert json.loads(catalog_path.read_text()) == {"discovered": True}
                assert not catalog_cache_key_path.exists()

                # Apply catalog rules to store the cache key
                subject.apply_catalog_rules(invoker)
                assert catalog_cache_key_path.exists()

                # If the cache key hasn't changed, discovery isn't invoked again
                mocked_run_discovery.reset_mock()
                await subject.discover_catalog(invoker)

                mocked_run_discovery.assert_not_called()
                assert json.loads(catalog_path.read_text()) == {"discovered": True}
                assert catalog_cache_key_path.exists()

                # If the cache key no longer matches, discovery is invoked again
                mocked_run_discovery.reset_mock()
                catalog_cache_key_path.write_text("bogus")
                await subject.discover_catalog(invoker)

                assert mocked_run_discovery.called
                assert json.loads(catalog_path.read_text()) == {"discovered": True}
                assert not catalog_cache_key_path.exists()

    @pytest.mark.asyncio
    async def test_discover_catalog_custom(
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

        async with invoker.prepared(session):
            await subject.discover_catalog(invoker)

        assert invoker.files["catalog"].read_text() == '{"custom": true}'

    @pytest.mark.asyncio
    async def test_apply_select(  # noqa: WPS213
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
                    catalog["rules"].append(
                        [rule.tap_stream_id, rule.breadcrumb, rule.key, rule.value]
                    )

            return mock.Mock(visit=visit)

        with mock.patch(
            "meltano.core.plugin.singer.tap.MetadataExecutor",
            side_effect=mock_metadata_executor,
        ):
            reset_catalog()

            async with invoker.prepared(session):
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
                invoker.plugin.parent._variant.extras,
                "select",
                ["UniqueEntitiesName.name"],
            )
            invoker.settings_service._setting_defs = None
            async with invoker.prepared(session):
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

            async with invoker.prepared(session):
                subject.apply_catalog_rules(invoker)

            # `select` set in meltano.yml takes precedence over discovery.yml
            assert_rules(
                ["*", [], "selected", False],
                ["*", ["properties", "*"], "selected", False],
                ["UniqueEntitiesName", [], "selected", True],
                ["UniqueEntitiesName", ["properties", "code"], "selected", True],
            )

    @pytest.mark.asyncio
    async def test_apply_catalog_rules(  # noqa: WPS213
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
            monkeypatch.setattr(invoker.plugin, "config", config)

            async with invoker.prepared(session):
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

            async with invoker.prepared(session):
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

    @pytest.mark.asyncio
    async def test_apply_catalog_rules_select_filter(  # noqa: WPS217, WPS213
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

        async def selected_properties():
            catalog_path = invoker.files["catalog"]

            with catalog_path.open("w") as catalog_file:
                json.dump(base_catalog, catalog_file)

            async with invoker.prepared(session):
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
        assert await selected_properties() == {
            "one": {"one"},
            "three": {"one", "three"},
            "five": {"one", "two", "three"},
        }

        # Simple inclusion
        monkeypatch.setitem(config_override, "_select_filter", ["three"])
        assert await selected_properties() == {"three": {"one", "three"}}

        # Simple exclusion
        monkeypatch.setitem(config_override, "_select_filter", ["!three"])
        assert await selected_properties() == {
            "one": {"one"},
            "five": {"one", "two", "three"},
        }

        # Wildcard inclusion
        monkeypatch.setitem(config_override, "_select_filter", ["t*"])
        assert await selected_properties() == {"three": {"one", "three"}}

        # Wildcard exclusion
        monkeypatch.setitem(config_override, "_select_filter", ["!t*"])
        assert await selected_properties() == {
            "one": {"one"},
            "five": {"one", "two", "three"},
        }

        # Multiple inclusion
        monkeypatch.setitem(config_override, "_select_filter", ["three", "five"])
        assert await selected_properties() == {
            "three": {"one", "three"},
            "five": {"one", "two", "three"},
        }

        # Multiple exclusion
        monkeypatch.setitem(config_override, "_select_filter", ["!three", "!five"])
        assert await selected_properties() == {"one": {"one"}}

        # Multiple wildcard inclusion
        monkeypatch.setitem(config_override, "_select_filter", ["t*", "f*"])
        assert await selected_properties() == {
            "three": {"one", "three"},
            "five": {"one", "two", "three"},
        }

        # Multiple wildcard exclusion
        monkeypatch.setitem(config_override, "_select_filter", ["!t*", "!f*"])
        assert await selected_properties() == {"one": {"one"}}

        # Mixed inclusion and exclusion
        monkeypatch.setitem(config_override, "_select_filter", ["*e", "!*ee"])
        assert await selected_properties() == {
            "one": {"one"},
            "five": {"one", "two", "three"},
        }

    @pytest.mark.asyncio
    async def test_apply_catalog_rules_invalid(
        self, session, plugin_invoker_factory, subject
    ):
        invoker = plugin_invoker_factory(subject)
        async with invoker.prepared(session):
            invoker.files["catalog"].open("w").write("this is invalid json")

            with pytest.raises(PluginExecutionError, match=r"invalid"):  # noqa: WPS360
                subject.apply_catalog_rules(invoker, [])

    @pytest.mark.asyncio
    async def test_catalog_cache_key(  # noqa: WPS217
        self, session, plugin_invoker_factory, subject, monkeypatch
    ):
        invoker = plugin_invoker_factory(subject)
        config_override = invoker.settings_service.config_override

        async def cache_key():
            async with invoker.prepared(session):
                return subject.catalog_cache_key(invoker)

        # No key if _catalog is set
        monkeypatch.setitem(config_override, "_catalog", "catalog.json")
        assert await cache_key() is None

        # Key is set if _catalog is not set
        monkeypatch.setitem(config_override, "_catalog", None)
        key = await cache_key()
        assert key is not None

        # Key doesn't change if nothing has changed
        assert await cache_key() == key

        # Key changes if config changes
        monkeypatch.setitem(config_override, "test", "foo")

        new_key = await cache_key()
        assert new_key != key
        key = new_key

        # Key changes if _schema changes
        monkeypatch.setitem(
            config_override, "_schema", {"stream": {"property": {"type": "string"}}}
        )

        new_key = await cache_key()
        assert new_key != key
        key = new_key

        # Key changes if _metadata changes
        monkeypatch.setitem(
            config_override,
            "_metadata",
            {"stream": {"property": {"is-replication-key": True}}},
        )

        new_key = await cache_key()
        assert new_key != key
        key = new_key

        # Key does not change if _select changes
        monkeypatch.setitem(config_override, "_select", ["stream"])
        assert await cache_key() == key

        # Key does not change if _select_filter changes
        monkeypatch.setitem(config_override, "_select_filter", ["stream"])
        assert await cache_key() == key

        # No key if pip_url is editable
        monkeypatch.setattr(invoker.plugin, "pip_url", "-e local")
        assert await cache_key() is None

    @pytest.mark.asyncio
    async def test_run_discovery(
        self,
        plugin_invoker_factory,
        session,
        subject,
        elt_context_builder,
        project_plugins_service,
    ):

        process_mock = mock.Mock()
        process_mock.name = subject.name
        process_mock.wait = AsyncMock(return_value=0)
        process_mock.returncode = 0
        process_mock.sterr.at_eof.side_effect = (
            True  # no output so return eof immediately
        )

        process_mock.stdout.at_eof.side_effect = (
            False,
            True,
        )  # first check needs to be false so loop starts read, after 1 line, we'll return true
        process_mock.stdout.readline = AsyncMock(return_value=b'{"discovered": true}\n')

        invoke_async = AsyncMock(return_value=process_mock)
        invoker = plugin_invoker_factory(subject)
        invoker.invoke_async = invoke_async
        catalog_path = invoker.files["catalog"]

        await subject.run_discovery(invoker, catalog_path)
        assert await invoke_async.called_with(["--discover"])

        with catalog_path.open("r") as catalog_file:
            resp = json.load(catalog_file)
            assert resp["discovered"]

    @pytest.mark.asyncio
    async def test_run_discovery_failure(
        self,
        plugin_invoker_factory,
        session,
        subject,
        elt_context_builder,
        project_plugins_service,
    ):

        process_mock = mock.Mock()
        process_mock.name = subject.name
        process_mock.wait = AsyncMock(return_value=1)
        process_mock.returncode = 1
        process_mock.stderr.at_eof.side_effect = (False, True)
        process_mock.stderr.readline = AsyncMock(return_value=b"stderr mock output")
        process_mock.stdout.at_eof.side_effect = (True, True)
        process_mock.stdout.readline = AsyncMock(return_value=b"")

        invoker = plugin_invoker_factory(subject)
        invoker.invoke_async = AsyncMock(return_value=process_mock)
        catalog_path = invoker.files["catalog"]

        with pytest.raises(PluginExecutionError, match="returned 1"):
            await subject.run_discovery(invoker, catalog_path)

        assert not catalog_path.exists(), "Catalog should not be present."

    @pytest.mark.asyncio
    async def test_run_discovery_stderr_output(
        self,
        plugin_invoker_factory,
        session,
        subject,
        elt_context_builder,
        project_plugins_service,
    ):

        process_mock = mock.Mock()
        process_mock.name = subject.name
        # we need to exit successfully to not trigger error handling
        process_mock.wait = AsyncMock(return_value=0)
        process_mock.returncode = 0
        process_mock.stderr.at_eof.side_effect = (False, True)
        process_mock.stderr.readline = AsyncMock(return_value=b"stderr mock output")
        process_mock.stdout.at_eof.side_effect = (True, True)
        process_mock.stdout.readline = AsyncMock(return_value=b"")

        invoker = plugin_invoker_factory(subject)
        invoker.invoke_async = AsyncMock(return_value=process_mock)
        catalog_path = invoker.files["catalog"]

        with mock.patch(
            "meltano.core.plugin.singer.tap.logger.isEnabledFor", return_value=False
        ), mock.patch("meltano.core.plugin.singer.tap._stream_redirect") as stream_mock:
            await subject.run_discovery(invoker, catalog_path)
            assert stream_mock.call_count == 2

        with mock.patch(
            "meltano.core.plugin.singer.tap.logger.isEnabledFor", return_value=True
        ), mock.patch(
            "meltano.core.plugin.singer.tap._stream_redirect"
        ) as stream_mock2:
            await subject.run_discovery(invoker, catalog_path)
            assert stream_mock2.call_count == 2

        # ensure stderr is redirected to devnull if we don't need it
        discovery_logger = logging.getLogger("meltano.core.plugin.singer.tap")
        original_level = discovery_logger.getEffectiveLevel()
        discovery_logger.setLevel(logging.INFO)
        with mock.patch(
            "meltano.core.plugin.singer.tap.logger.isEnabledFor", return_value=True
        ), mock.patch(
            "meltano.core.plugin.singer.tap._stream_redirect"
        ) as stream_mock3:
            await subject.run_discovery(invoker, catalog_path)

            assert stream_mock3.call_count == 2
            call_kwargs = invoker.invoke_async.call_args_list[0][1]
            assert call_kwargs.get("stderr") is subprocess.PIPE

        discovery_logger.setLevel(original_level)

    @pytest.mark.asyncio
    async def test_run_discovery_handle_io_exceptions(
        self,
        plugin_invoker_factory,
        session,
        subject,
        elt_context_builder,
        project_plugins_service,
    ):

        process_mock = mock.Mock()
        process_mock.name = subject.name
        process_mock.wait = AsyncMock(return_value=0)
        process_mock.returncode = 0
        process_mock.stderr.at_eof.side_effect = (False, True)
        process_mock.stderr.readline = AsyncMock(return_value=b"stderr mock output")
        process_mock.stdout.at_eof.side_effect = (False, True)
        process_mock.stdout.readline.side_effect = Exception("mock readline exception")

        invoker = plugin_invoker_factory(subject)
        invoker.invoke_async = AsyncMock(return_value=process_mock)
        catalog_path = invoker.files["catalog"]

        with pytest.raises(Exception, match="mock readline exception"):
            await subject.run_discovery(invoker, catalog_path)

        assert not catalog_path.exists(), "Catalog should not be present."

    @pytest.mark.asyncio
    async def test_run_discovery_utf8_output(
        self,
        plugin_invoker_factory,
        session,
        subject,
        elt_context_builder,
        project_plugins_service,
    ):

        process_mock = mock.Mock()
        process_mock.name = subject.name
        # we need to exit successfully to not trigger error handling
        process_mock.wait = AsyncMock(return_value=0)
        process_mock.returncode = 0
        process_mock.stderr.at_eof.side_effect = (False, True)
        test_string = "Hello world, Καλημέρα κόσμε, コンニチハ".encode()
        process_mock.stderr.readline = AsyncMock(return_value=test_string)
        process_mock.stdout.at_eof.side_effect = (True, True)
        process_mock.stdout.readline = AsyncMock(return_value=b"")

        invoker = plugin_invoker_factory(subject)
        invoker.invoke_async = AsyncMock(return_value=process_mock)
        catalog_path = invoker.files["catalog"]

        assert sys.getdefaultencoding() == "utf-8"

        with mock.patch(
            "meltano.core.plugin.singer.tap.logger.isEnabledFor", return_value=True
        ):
            await subject.run_discovery(invoker, catalog_path)
