from __future__ import annotations

import asyncio
import json
import logging
import subprocess
import sys
import typing as t
from contextlib import contextmanager, suppress
from datetime import date, datetime, timezone
from unittest import mock
from unittest.mock import AsyncMock

import anyio
import pytest
import structlog

from meltano.core.job import Job, Payload
from meltano.core.plugin import PluginType
from meltano.core.plugin.error import PluginExecutionError
from meltano.core.plugin.singer import SingerTap
from meltano.core.plugin.singer.catalog import (
    ListSelectedExecutor,
    property_breadcrumb,
    select_metadata_rules,
)
from meltano.core.plugin_invoker import PluginInvoker
from meltano.core.state_service import InvalidJobStateError, StateService

if t.TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from sqlalchemy.orm import Session

    from meltano.core.plugin.project_plugin import ProjectPlugin
    from meltano.core.plugin.singer.catalog import CatalogDict, MetadataRule, SchemaRule
    from meltano.core.project import Project
    from meltano.core.project_add_service import ProjectAddService


class CatalogFixture:
    empty_stream: t.ClassVar[CatalogDict] = {"streams": []}
    empty_properties: t.ClassVar[CatalogDict] = {"streams": [{"tap_stream_id": "foo"}]}
    regular_stream: t.ClassVar[CatalogDict] = {
        "streams": [
            {
                "tap_stream_id": "foo",
                "schema": {
                    "properties": {
                        "bar": {"type": "string"},
                        "attribute": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                            },
                        },
                    },
                },
            },
        ],
    }


class TestSingerTap:
    @pytest.fixture(scope="class")
    def subject(self, project_add_service: ProjectAddService) -> SingerTap:
        return project_add_service.add(PluginType.EXTRACTORS, "tap-mock")

    @pytest.fixture(scope="class", autouse=True)
    def fixture_configure_structlog(self) -> None:
        structlog.stdlib.recreate_defaults(log_level=logging.INFO)

    @pytest.mark.order(0)
    @pytest.mark.asyncio
    async def test_exec_args(
        self,
        subject: SingerTap,
        session,
        plugin_invoker_factory: Callable[[ProjectPlugin], PluginInvoker],
    ) -> None:
        invoker = plugin_invoker_factory(subject)
        async with invoker.prepared(session):
            assert subject.exec_args(invoker) == ["--config", invoker.files["config"]]

            # when `catalog` has data
            invoker.files["catalog"].write_text("...")
            assert subject.exec_args(invoker) == [
                "--config",
                invoker.files["config"],
                "--catalog",
                invoker.files["catalog"],
            ]

            # when `state` has data
            invoker.files["state"].write_text("...")
            assert subject.exec_args(invoker) == [
                "--config",
                invoker.files["config"],
                "--catalog",
                invoker.files["catalog"],
                "--state",
                invoker.files["state"],
            ]

    @pytest.mark.asyncio
    async def test_cleanup(
        self,
        subject: SingerTap,
        session,
        plugin_invoker_factory,
    ) -> None:
        invoker = plugin_invoker_factory(subject)
        async with invoker.prepared(session):
            assert invoker.files["config"].exists()

        assert not invoker.files["config"].exists()

    @pytest.mark.asyncio
    async def test_look_up_state(
        self,
        subject: SingerTap,
        project,
        session,
        plugin_invoker_factory,
        elt_context_builder,
        monkeypatch,
    ) -> None:
        job = Job(job_name="pytest_test_runner")
        elt_context = (
            elt_context_builder.with_session(session)
            .with_extractor(subject.name)
            .with_job(job)
            .context()
        )

        invoker: PluginInvoker = plugin_invoker_factory(subject, context=elt_context)
        state_service = StateService(session=session)

        @contextmanager
        def create_job():
            new_job = Job(job_name=job.job_name)
            new_job.start()
            yield new_job
            new_job.save(session)
            if new_job.payload and not new_job.is_running():
                with suppress(InvalidJobStateError):
                    state_service.add_state(
                        new_job.job_name,
                        json.dumps(new_job.payload),
                        new_job.payload_flags,
                    )

        async def assert_state(state) -> None:
            async with invoker.prepared(session):
                await subject.look_up_state(invoker)

            if state:
                assert invoker.files["state"].exists()
                assert json.loads(invoker.files["state"].read_text()) == state
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
            invoker.settings_service.config_override,
            "_state",
            custom_state_filename,
        )

        await assert_state({"custom": True})

        # With a full refresh, no state is considered
        elt_context.full_refresh = True
        await assert_state(None)

    @pytest.mark.order(1)
    @pytest.mark.asyncio
    async def test_discover_catalog(
        self,
        session,
        plugin_invoker_factory: Callable[[ProjectPlugin], PluginInvoker],
        subject: SingerTap,
        monkeypatch,
    ) -> None:
        invoker = plugin_invoker_factory(subject)

        catalog_path = invoker.files["catalog"]
        catalog_cache_key_path = invoker.files["catalog_cache_key"]

        def mock_discovery(*args, **kwargs):  # noqa: ARG001
            future = asyncio.Future()
            future.set_result(catalog_path.write_text('{"discovered": true}'))
            return future

        async with invoker.prepared(session):
            with mock.patch.object(
                SingerTap,
                "run_discovery",
                side_effect=mock_discovery,
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
                await subject.apply_catalog_rules(invoker)
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

                # Apply catalog rules to store the cache key again
                await subject.apply_catalog_rules(invoker)
                assert catalog_cache_key_path.exists()

        monkeypatch.setitem(
            invoker.settings_service.config_override,
            "_use_cached_catalog",
            value=False,
        )

        async with invoker.prepared(session):
            with mock.patch.object(
                SingerTap,
                "run_discovery",
                side_effect=mock_discovery,
            ) as mocked_run_discovery:
                assert catalog_cache_key_path.exists()

                # with _use_cached_catalog = false, discovery should be invoked
                # again even with a stored cache key.
                mocked_run_discovery.reset_mock()
                await subject.discover_catalog(invoker)

                mocked_run_discovery.assert_called_once()
                assert json.loads(catalog_path.read_text()) == {"discovered": True}
                assert not catalog_cache_key_path.exists()

        def _set_invalid_catalog(*args, **kwargs):  # noqa: ARG001
            future = asyncio.Future()
            future.set_result(catalog_path.write_text('Not JSON {"discovered": true}'))
            return future

        async with invoker.prepared(session):
            with mock.patch.object(
                SingerTap,
                "run_discovery",
                side_effect=_set_invalid_catalog,
            ):
                with pytest.raises(
                    PluginExecutionError,
                    match="Invalid catalog",
                ) as exc_info:
                    await subject.discover_catalog(invoker)

                cause = exc_info.value.__cause__
                assert isinstance(cause, json.JSONDecodeError)
                assert cause.doc == 'Not JSON {"discovered": true}'
                assert cause.pos == 0

    @pytest.mark.asyncio
    async def test_discover_catalog_custom(
        self,
        project: Project,
        session,
        plugin_invoker_factory: Callable[[ProjectPlugin], PluginInvoker],
        subject: SingerTap,
        monkeypatch,
    ) -> None:
        invoker = plugin_invoker_factory(subject)

        custom_catalog_filename = "custom_catalog.json"
        custom_catalog_path = project.root.joinpath(custom_catalog_filename)
        custom_catalog_path.write_text('{"custom": true}')

        monkeypatch.setitem(
            invoker.settings_service.config_override,
            "_catalog",
            custom_catalog_filename,
        )

        # These files should be ignored if a custom catalog is provided
        invoker.files["catalog"].write_text('{"previous": true}')
        invoker.files["catalog_cache_key"].touch()

        async with invoker.prepared(session):
            with (
                mock.patch.object(
                    SingerTap,
                    "run_discovery",
                ) as mocked_run_discovery,
                mock.patch.object(
                    SingerTap,
                    "catalog_cache_key",
                ) as mocked_catalog_cache_key,
            ):
                await subject.discover_catalog(invoker)

        assert invoker.files["catalog"].read_text() == '{"custom": true}'
        assert not mocked_run_discovery.called
        assert not mocked_catalog_cache_key.called

    @pytest.mark.asyncio
    async def test_discover_catalog_custom_missing(
        self,
        project: Project,
        session: Session,
        plugin_invoker_factory: Callable[[ProjectPlugin], PluginInvoker],
        subject: SingerTap,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test using a custom catalog file that doesn't exist."""
        invoker = plugin_invoker_factory(subject)

        custom_catalog_filename = "custom_catalog.json"
        custom_catalog_path = project.root.joinpath(custom_catalog_filename)
        custom_catalog_path.unlink(missing_ok=True)

        monkeypatch.setitem(
            invoker.settings_service.config_override,
            "_catalog",
            custom_catalog_filename,
        )

        async with invoker.prepared(session):
            with pytest.raises(
                PluginExecutionError,
                match="Failed to copy catalog file",
            ) as exc_info:
                await subject.discover_catalog(invoker)

            cause = exc_info.value.__cause__
            assert isinstance(cause, OSError)
            assert cause.strerror == "No such file or directory"

    @pytest.mark.asyncio
    async def test_discover_catalog_custom_invalid(
        self,
        project: Project,
        session: Session,
        plugin_invoker_factory: Callable[[ProjectPlugin], PluginInvoker],
        subject: SingerTap,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test using a custom catalog file that is invalid JSON."""
        invoker = plugin_invoker_factory(subject)

        custom_catalog_filename = "custom_catalog.json"
        custom_catalog_path = project.root.joinpath(custom_catalog_filename)
        custom_catalog_path.write_text("Not JSON")

        monkeypatch.setitem(
            invoker.settings_service.config_override,
            "_catalog",
            custom_catalog_filename,
        )

        async with invoker.prepared(session):
            with pytest.raises(
                PluginExecutionError,
                match="Invalid catalog",
            ) as exc_info:
                await subject.discover_catalog(invoker)

            cause = exc_info.value.__cause__
            assert isinstance(cause, json.JSONDecodeError)

    @pytest.mark.asyncio
    async def test_apply_select(
        self,
        session,
        plugin_invoker_factory: Callable[[ProjectPlugin], PluginInvoker],
        subject: SingerTap,
        monkeypatch,
    ) -> None:
        invoker = plugin_invoker_factory(subject)

        catalog_path = invoker.files["catalog"]

        def reset_catalog() -> None:
            catalog_path.write_text('{"rules": []}')

        def assert_rules(*rules: Sequence) -> None:
            with catalog_path.open() as catalog_file:
                catalog = json.load(catalog_file)

            transformed_rules = [
                [
                    rule[0],
                    property_breadcrumb(rule[1]),
                    *rule[2:],
                ]
                for rule in rules
            ]

            assert catalog["rules"] == transformed_rules

        def mock_metadata_executor(rules: t.Iterable[MetadataRule]):
            def visit(catalog: dict) -> None:
                for rule in rules:
                    catalog["rules"].append(
                        [rule.tap_stream_id, rule.breadcrumb, rule.key, rule.value],
                    )

            return mock.Mock(visit=visit)

        with mock.patch(
            "meltano.core.plugin.singer.tap.MetadataExecutor",
            side_effect=mock_metadata_executor,
        ):
            reset_catalog()

            async with invoker.prepared(session):
                await subject.apply_catalog_rules(invoker)

            # When `select` isn't set in meltano.yml or the plugin def, select all
            assert_rules(
                ["*", [], "selected", False],
                ["*", ["*"], "selected", False],
                ["*", [], "selected", True],
                ["*", ["*"], "selected", True],
            )

            reset_catalog()

            # Pretend `select` is set in the plugin definition
            monkeypatch.setitem(
                invoker.plugin.parent._variant.extras,
                "select",
                ["UniqueEntitiesName.name"],
            )
            invoker.settings_service._setting_defs = None
            async with invoker.prepared(session):
                await subject.apply_catalog_rules(invoker)

            # When `select` is set in the plugin definition, use the selection
            assert_rules(
                ["*", [], "selected", False],
                ["*", ["*"], "selected", False],
                ["UniqueEntitiesName", [], "selected", True],
                ["UniqueEntitiesName", ["name"], "selected", True],
            )

            reset_catalog()

            # Pretend `select` is set in meltano.yml
            monkeypatch.setitem(
                invoker.plugin.extras,
                "select",
                ["UniqueEntitiesName.code"],
            )

            async with invoker.prepared(session):
                await subject.apply_catalog_rules(invoker)

            # `select` set in meltano.yml takes precedence over the plugin definition
            assert_rules(
                ["*", [], "selected", False],
                ["*", ["*"], "selected", False],
                ["UniqueEntitiesName", [], "selected", True],
                ["UniqueEntitiesName", ["code"], "selected", True],
            )

    @pytest.mark.asyncio
    async def test_apply_catalog_rules(
        self,
        session,
        plugin_invoker_factory: Callable[[ProjectPlugin], PluginInvoker],
        subject: SingerTap,
        monkeypatch,
    ) -> None:
        invoker = plugin_invoker_factory(subject)

        catalog_path = invoker.files["catalog"]
        catalog_cache_key_path = invoker.files["catalog_cache_key"]

        def reset_catalog() -> None:
            catalog_path.write_text('{"rules": []}')

        def assert_rules(*rules: Sequence) -> None:
            with catalog_path.open() as catalog_file:
                catalog = json.load(catalog_file)

            transformed_rules = [
                [
                    rule[0],
                    property_breadcrumb(rule[1]),
                    *rule[2:],
                ]
                for rule in rules
            ]

            assert catalog["rules"] == transformed_rules

        def mock_metadata_executor(rules: t.Iterable[MetadataRule]):
            def visit(catalog: dict) -> None:
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

        def mock_schema_executor(rules: t.Iterable[SchemaRule]):
            def visit(catalog: dict) -> None:
                for rule in rules:
                    catalog["rules"].append(
                        [rule.tap_stream_id, rule.breadcrumb, rule.payload],
                    )

            return mock.Mock(visit=visit)

        with (
            mock.patch(
                "meltano.core.plugin.singer.tap.MetadataExecutor",
                side_effect=mock_metadata_executor,
            ),
            mock.patch(
                "meltano.core.plugin.singer.tap.SchemaExecutor",
                side_effect=mock_schema_executor,
            ),
        ):
            reset_catalog()

            config = {
                "_select": ["UniqueEntitiesName.code"],
                "_metadata": {
                    "UniqueEntitiesName": {"replication-key": "created_at"},
                    "UniqueEntitiesName.created_at": {"is-replication-key": True},
                },
                "metadata.UniqueEntitiesName.payload.hash.custom-metadata": "custom-value",  # noqa: E501
                "_schema": {
                    "UniqueEntitiesName": {
                        "code": {"anyOf": [{"type": "string"}, {"type": "null"}]},
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
                await subject.apply_catalog_rules(invoker)

                cache_key = invoker.plugin.catalog_cache_key(invoker)

            # Stores the cache key
            assert catalog_cache_key_path.read_text() == cache_key

            assert_rules(
                # Schema rules
                [
                    "UniqueEntitiesName",
                    ["code"],
                    {"anyOf": [{"type": "string"}, {"type": "null"}]},
                ],
                [
                    "UniqueEntitiesName",
                    ["payload"],
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
                ["*", ["*"], "selected", False],
                # Selection metadata rules
                ["UniqueEntitiesName", [], "selected", True],
                ["UniqueEntitiesName", ["code"], "selected", True],
                # Metadata rules
                ["UniqueEntitiesName", [], "replication-key", "created_at"],
                [
                    "UniqueEntitiesName",
                    ["created_at"],
                    "is-replication-key",
                    True,
                ],
                [
                    "UniqueEntitiesName",
                    ["payload", "hash"],
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
                await subject.apply_catalog_rules(invoker)

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
    async def test_apply_catalog_rules_select_filter(
        self,
        session,
        plugin_invoker_factory: Callable[[ProjectPlugin], PluginInvoker],
        subject: SingerTap,
        monkeypatch,
    ) -> None:
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
            ],
        }

        async def selected_properties():
            catalog_path = invoker.files["catalog"]

            async with await anyio.open_file(catalog_path, "w") as catalog_file:
                await catalog_file.write(json.dumps(base_catalog))

            async with invoker.prepared(session):
                await subject.apply_catalog_rules(invoker, [])

            async with await anyio.open_file(catalog_path, "r") as catalog_file:
                catalog = json.loads(await catalog_file.read())

            lister = ListSelectedExecutor()
            lister.visit(catalog)

            return lister.selected_properties

        config_override = invoker.settings_service.config_override

        monkeypatch.setitem(
            config_override,
            "_select",
            ["one.one", "three.three", "five.*"],
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
        self,
        session,
        plugin_invoker_factory: Callable[[ProjectPlugin], PluginInvoker],
        subject: SingerTap,
    ) -> None:
        invoker = plugin_invoker_factory(subject)
        async with invoker.prepared(session):
            invoker.files["catalog"].write_text("this is invalid json")

            with pytest.raises(PluginExecutionError, match=r"invalid"):
                await subject.apply_catalog_rules(invoker, [])

    @pytest.mark.asyncio
    async def test_catalog_cache_key(
        self,
        session,
        plugin_invoker_factory,
        subject: SingerTap,
        monkeypatch,
    ) -> None:
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
            config_override,
            "_schema",
            {"stream": {"property": {"type": "string"}}},
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
    @pytest.mark.usefixtures("session", "elt_context_builder")
    async def test_run_discovery(
        self,
        plugin_invoker_factory: Callable[[ProjectPlugin], PluginInvoker],
        subject: SingerTap,
    ) -> None:
        process_mock = mock.Mock()
        process_mock.name = subject.name
        process_mock.wait = AsyncMock(return_value=0)
        process_mock.returncode = 0
        process_mock.stderr.at_eof.side_effect = (
            True,  # no output so return eof immediately
        )

        # First check needs to be false so loop starts read, after 1 line,
        # we'll return true
        process_mock.stdout.at_eof.side_effect = (False, True)
        process_mock.stdout.readline = AsyncMock(return_value=b'{"discovered": true}\n')

        invoke_async = AsyncMock(return_value=process_mock)
        invoker = plugin_invoker_factory(subject)
        invoker.invoke_async = invoke_async
        catalog_path = invoker.files["catalog"]

        await subject.run_discovery(invoker, catalog_path)
        assert invoke_async.call_args[0] == ("--discover",)

        async with await anyio.open_file(catalog_path, "r") as catalog_file:
            resp = json.loads(await catalog_file.read())
            assert resp["discovered"]

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("session", "elt_context_builder")
    async def test_run_discovery_failure(
        self,
        plugin_invoker_factory,
        subject: SingerTap,
    ) -> None:
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
    @pytest.mark.usefixtures("session", "elt_context_builder")
    async def test_run_discovery_stderr_output(
        self,
        plugin_invoker_factory,
        subject: SingerTap,
    ) -> None:
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

        with (
            mock.patch.object(
                PluginInvoker,
                "stderr_logger",
                new_callable=mock.PropertyMock,
                return_value=mock.Mock(isEnabledFor=mock.Mock(return_value=False)),
            ),
            mock.patch(
                "meltano.core.plugin.singer.tap._stream_redirect",
            ) as stream_mock,
        ):
            await subject.run_discovery(invoker, catalog_path)
            assert stream_mock.call_count == 2

        with (
            mock.patch.object(
                PluginInvoker,
                "stderr_logger",
                new_callable=mock.PropertyMock,
                return_value=mock.Mock(isEnabledFor=mock.Mock(return_value=True)),
            ),
            mock.patch(
                "meltano.core.plugin.singer.tap._stream_redirect",
            ) as stream_mock2,
        ):
            await subject.run_discovery(invoker, catalog_path)
            assert stream_mock2.call_count == 1

        # ensure stderr is redirected to devnull if we don't need it
        discovery_logger = logging.getLogger("meltano.core.plugin.singer.tap")  # noqa: TID251
        original_level = discovery_logger.getEffectiveLevel()
        discovery_logger.setLevel(logging.INFO)
        with (
            mock.patch.object(
                PluginInvoker,
                "stderr_logger",
                new_callable=mock.PropertyMock,
                return_value=mock.Mock(isEnabledFor=mock.Mock(return_value=True)),
            ),
            mock.patch(
                "meltano.core.plugin.singer.tap._stream_redirect",
            ) as stream_mock3,
            mock.patch(
                "meltano.core.plugin.singer.tap.capture_subprocess_output",
            ) as capture_subprocess_output_mock,
        ):
            await subject.run_discovery(invoker, catalog_path)

            assert stream_mock3.call_count == 1
            call_kwargs = invoker.invoke_async.call_args_list[0][1]
            assert call_kwargs.get("stderr") is subprocess.PIPE
            assert capture_subprocess_output_mock.call_count == 1

        discovery_logger.setLevel(original_level)

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("session", "elt_context_builder")
    async def test_run_discovery_handle_io_exceptions(
        self,
        plugin_invoker_factory,
        subject: SingerTap,
    ) -> None:
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
    @pytest.mark.usefixtures("session", "elt_context_builder")
    async def test_run_discovery_utf8_output(
        self,
        plugin_invoker_factory,
        subject: SingerTap,
    ) -> None:
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

        with mock.patch.object(
            PluginInvoker,
            "stderr_logger",
            new_callable=mock.PropertyMock,
            return_value=mock.Mock(isEnabledFor=mock.Mock(return_value=True)),
        ):
            await subject.run_discovery(invoker, catalog_path)

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("use_test_log_config")
    @pytest.mark.parametrize(
        ("rule_pattern", "catalog", "message"),
        (
            pytest.param(
                "bar.*",
                CatalogFixture.empty_properties,
                "Stream `bar` was not found",
                id="stream_not_found",
            ),
            pytest.param(
                "foo.*",
                CatalogFixture.empty_stream,
                "Stream `foo` was not found",
                id="no_streams_exist",
            ),
            pytest.param(
                "foo.bar",
                CatalogFixture.empty_properties,
                "Property `bar` was not found in the schema of stream `foo`",
                id="no_properties_exist",
            ),
            pytest.param(
                "foo.spam",
                CatalogFixture.regular_stream,
                "Property `spam` was not found in the schema of stream `foo`",
                id="property_not_found",
            ),
            pytest.param(
                "foo.bar",
                CatalogFixture.regular_stream,
                None,
                id="property_is_found",
            ),
            pytest.param(
                "*.bar",
                CatalogFixture.empty_stream,
                None,
                id="stream_is_wildcard",
            ),
            pytest.param(
                "zoo.*",
                CatalogFixture.empty_stream,
                "Stream `zoo` was not found",
                id="stream_not_found_property_is_wildcard",
            ),
            pytest.param(
                "foo.*",
                CatalogFixture.regular_stream,
                None,
                id="property_is_wildcard",
            ),
            pytest.param(
                "foo.attribute.name",
                CatalogFixture.regular_stream,
                None,
                id="nested_property_is_found",
            ),
            pytest.param(
                "foo.attribute.*",
                CatalogFixture.regular_stream,
                None,
                id="nested_property_is_wildcard",
            ),
            pytest.param(
                "foo.attribute.email",
                CatalogFixture.regular_stream,
                "Property `attribute.properties.email` was not "
                "found in the schema of stream `foo`",
                id="nested_property_not_found",
            ),
            pytest.param(
                "foo*.*",
                CatalogFixture.regular_stream,
                None,
                id="stream_has_wildcard",
            ),
            pytest.param(
                "foo.ATTRIBUTES.em*",
                CatalogFixture.regular_stream,
                "Property `ATTRIBUTES.properties.em*` was not "
                "found in the schema of stream `foo`",
                id="property_not_found-sub_property_has_wildcard",
            ),
        ),
    )
    async def test_warn_property_not_found(
        self,
        subject: SingerTap,
        caplog: pytest.LogCaptureFixture,
        capsys: pytest.CaptureFixture,
        rule_pattern: str,
        catalog: CatalogDict,
        message: str | None,
    ) -> None:
        """
        Warning messages should be emitted when a MetadataRule doesn't match.

        _A quirk seems to be that if this test is invoked on its own, the
        output is captured in the fixture `pytest.capsys`, however if pytest
        runs globally then the output is captured in `pytest.caplog`. Not sure
        why, hoping this message finds a developer more knowledgeable than I._

        For now, I'm adding up the output of both capsys & caplog and testing
        expected messages are captured somewhere. As in, both of these would
        work.

        ```
        uv run pytest
        uv run pytest tests/meltano/core/plugin/singer/test_tap.py::TestSingerTap::test_warn_property_not_found
        ```
        """  # noqa: D212, E501
        rules = select_metadata_rules([rule_pattern])
        subject.warn_property_not_found(rules, catalog)
        sysout, syserr = capsys.readouterr()
        # If the warning is emitted, it should be in the output
        if message is not None:
            assert message in (caplog.text + sysout + syserr)
        else:
            assert len(caplog.records) == 0
            assert syserr + sysout == ""

    @pytest.mark.asyncio
    async def test_before_configure_datetime_serialization(
        self,
        subject: SingerTap,
        session,
        plugin_invoker_factory: Callable[[ProjectPlugin], PluginInvoker],
    ) -> None:
        """Test that before_configure properly serializes datetime objects to JSON.

        This is a regression test for the bug where YAML-parsed dates (datetime.date
        objects) would fail JSON serialization with "Object of type date is not
        JSON serializable".

        The bug would occur when YAML parses "2025-01-01" as datetime.date(2025, 1, 1)
        and then json.dumps() fails when trying to serialize it.
        """
        invoker = plugin_invoker_factory(subject)

        # Create a config with datetime objects like YAML would parse them
        config_with_dates = {
            "test": "mock",
            "date_value": date(2025, 1, 1),
            "datetime_value": datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            "nested": {
                "date_in_object": date(2024, 12, 31),
            },
            "list": [
                {"name": "item1", "date": date(2025, 2, 1)},
            ],
        }

        # Directly test that before_configure can handle datetime objects
        # by temporarily setting plugin_config_processed and calling the hook
        invoker.plugin_config_processed = config_with_dates

        async with invoker.prepared(session):
            # Manually call before_configure with our datetime-containing config
            invoker.plugin_config_processed = config_with_dates
            await subject.before_configure(invoker, session)

            # Read the written config file to verify dates were serialized correctly
            config_path = invoker.files["config"]
            async with await anyio.open_file(config_path, "r") as config_file:
                written_config = json.loads(await config_file.read())

            # Verify dates were serialized to ISO format strings
            # Without the fix, json.dumps() would raise:
            # TypeError: Object of type date is not JSON serializable
            assert written_config["date_value"] == "2025-01-01"
            assert written_config["datetime_value"] == "2025-01-01T12:00:00+00:00"
            assert written_config["nested"]["date_in_object"] == "2024-12-31"
            assert written_config["list"][0]["date"] == "2025-02-01"
