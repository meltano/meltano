from __future__ import annotations

import os

import pytest

from meltano.core.plugin import PluginType, Variant
from meltano.core.project_plugins_service import PluginAlreadyAddedException


def assert_extractor_env(extractor, env) -> None:
    assert env["MELTANO_EXTRACTOR_NAME"] == extractor.name
    assert env["MELTANO_EXTRACTOR_NAMESPACE"] == extractor.namespace
    assert env["MELTANO_EXTRACTOR_VARIANT"] == extractor.variant

    assert env["MELTANO_EXTRACT_TEST"] == env["TAP_MOCK_TEST"] == "mock"
    assert env["MELTANO_EXTRACT__SELECT"] == env["TAP_MOCK__SELECT"] == '["*.*"]'


def assert_loader_env(loader, env) -> None:
    assert env["MELTANO_LOADER_NAME"] == loader.name
    assert env["MELTANO_LOADER_NAMESPACE"] == loader.namespace
    assert env["MELTANO_LOADER_VARIANT"] == loader.variant

    assert env["MELTANO_LOAD_HOST"] == os.getenv("TARGET_POSTGRES_HOST", "localhost")

    assert (
        env["MELTANO_LOAD_DEFAULT_TARGET_SCHEMA"]
        == env["MELTANO_EXTRACT__LOAD_SCHEMA"]
        == env["MELTANO_EXTRACTOR_NAMESPACE"]
    )


def assert_transform_env(transform, env) -> None:
    assert env["MELTANO_TRANSFORM_NAME"] == transform.name
    assert env["MELTANO_TRANSFORM_NAMESPACE"] == transform.namespace
    assert env["MELTANO_TRANSFORM_VARIANT"] == Variant.ORIGINAL_NAME


def assert_transformer_env(transformer, env) -> None:
    assert env["MELTANO_TRANSFORMER_NAME"] == transformer.name
    assert env["MELTANO_TRANSFORMER_NAMESPACE"] == transformer.namespace
    assert env["MELTANO_TRANSFORMER_VARIANT"] == "dbt-labs"

    assert (
        env["MELTANO_TRANSFORM_TARGET"]
        == env["DBT_TARGET"]
        == env["MELTANO_LOAD__DIALECT"]
    )
    assert (
        env["MELTANO_TRANSFORM_TARGET_SCHEMA"]
        == env["DBT_TARGET_SCHEMA"]
        == "analytics"
    )
    assert env["MELTANO_EXTRACT__LOAD_SCHEMA"] == env["MELTANO_EXTRACTOR_NAMESPACE"]
    assert env["MELTANO_TRANSFORM_MODELS"] == env["DBT_MODELS"]

    assert env["MELTANO_TRANSFORM__PACKAGE_NAME"] in env["DBT_MODELS"]
    assert env["MELTANO_EXTRACTOR_NAMESPACE"] in env["DBT_MODELS"]
    assert "my_meltano_project" in env["DBT_MODELS"]


class TestELTContext:
    @pytest.fixture
    def target_postgres(self, project_add_service):
        try:
            return project_add_service.add(PluginType.LOADERS, "target-postgres")
        except PluginAlreadyAddedException as err:
            return err.plugin

    @pytest.fixture
    def tap_mock_transform(self, project_add_service):
        try:
            return project_add_service.add(PluginType.TRANSFORMS, "tap-mock-transform")
        except PluginAlreadyAddedException as err:
            return err.plugin

    @pytest.fixture
    def elt_context(
        self,
        elt_context_builder,
        session,
        tap,
        target_postgres,
        tap_mock_transform,
        dbt,  # noqa: ARG002
    ):
        return (
            elt_context_builder.with_session(session)
            .with_extractor(tap.name)
            .with_loader(target_postgres.name)
            .with_transform(tap_mock_transform.name)
            .with_select_filter(["entity", "!other_entity"])
            .context()
        )

    @pytest.mark.asyncio
    async def test_extractor(self, elt_context, session, tap) -> None:
        extractor = elt_context.extractor
        assert extractor.type == PluginType.EXTRACTORS
        assert extractor.name == tap.name

        invoker = elt_context.extractor_invoker()
        async with invoker.prepared(session):
            env = invoker.env()

        assert_extractor_env(extractor, env)

    @pytest.mark.asyncio
    async def test_loader(self, elt_context, session, target_postgres) -> None:
        loader = elt_context.loader
        assert loader.type == PluginType.LOADERS
        assert loader.name == target_postgres.name

        invoker = elt_context.loader_invoker()
        async with invoker.prepared(session):
            env = invoker.env()

        assert_extractor_env(elt_context.extractor, env)
        assert_loader_env(loader, env)

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("target_postgres")
    async def test_transformer(
        self,
        elt_context,
        session,
        tap_mock_transform,
        dbt,
    ) -> None:
        transformer = elt_context.transformer
        assert transformer.type == PluginType.TRANSFORMERS
        assert transformer.name == dbt.name

        transform = elt_context.transform
        assert transform.type == PluginType.TRANSFORMS
        assert transform.name == tap_mock_transform.name

        invoker = elt_context.transformer_invoker()
        async with invoker.prepared(session):
            env = invoker.env()

        assert_extractor_env(elt_context.extractor, env)
        assert_loader_env(elt_context.loader, env)

        assert_transform_env(transform, env)
        assert_transformer_env(transformer, env)

    @pytest.mark.asyncio
    async def test_select_filter(self, elt_context, session) -> None:
        assert elt_context.select_filter

        invoker = elt_context.extractor_invoker()
        await invoker.prepare(session)
        assert (
            invoker.plugin_config_extras["_select_filter"] == elt_context.select_filter
        )
