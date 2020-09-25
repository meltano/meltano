import pytest
import os

from meltano.core.config_service import PluginAlreadyAddedException
from meltano.core.plugin import PluginType, Variant


def assert_extractor_env(extractor, env):
    assert env["MELTANO_EXTRACTOR_NAME"] == extractor.name
    assert env["MELTANO_EXTRACTOR_NAMESPACE"] == extractor.definition.namespace
    assert env["MELTANO_EXTRACTOR_PROFILE"] == extractor.plugin.current_profile_name
    assert env["MELTANO_EXTRACTOR_VARIANT"] == extractor.definition.current_variant_name

    assert env["MELTANO_EXTRACT_TEST"] == env["TAP_MOCK_TEST"] == "mock"
    assert env["MELTANO_EXTRACT__SELECT"] == env["TAP_MOCK__SELECT"] == '["*.*"]'


def assert_loader_env(loader, env):
    assert env["MELTANO_LOADER_NAME"] == loader.name
    assert env["MELTANO_LOADER_NAMESPACE"] == loader.definition.namespace
    assert env["MELTANO_LOADER_PROFILE"] == loader.plugin.current_profile_name
    assert env["MELTANO_LOADER_VARIANT"] == loader.definition.current_variant_name

    assert (
        env["MELTANO_LOAD_HOST"]
        == env["PG_ADDRESS"]
        == os.getenv("PG_ADDRESS", "localhost")
    )
    assert (
        env["MELTANO_LOAD_SCHEMA"]
        == env["PG_SCHEMA"]
        == env["MELTANO_EXTRACT__LOAD_SCHEMA"]
        == env["MELTANO_EXTRACTOR_NAMESPACE"]
    )


def assert_transform_env(transform, env):
    assert env["MELTANO_TRANSFORM_NAME"] == transform.name
    assert env["MELTANO_TRANSFORM_NAMESPACE"] == transform.definition.namespace
    assert env["MELTANO_TRANSFORM_PROFILE"] == transform.plugin.current_profile_name
    assert env["MELTANO_TRANSFORM_VARIANT"] == Variant.ORIGINAL_NAME

    assert env["MELTANO_TRANSFORM__PACKAGE_NAME"] == "dbt_mock"


def assert_transformer_env(transformer, env):
    assert env["MELTANO_TRANSFORMER_NAME"] == transformer.name
    assert env["MELTANO_TRANSFORMER_NAMESPACE"] == transformer.definition.namespace
    assert env["MELTANO_TRANSFORMER_PROFILE"] == transformer.plugin.current_profile_name
    assert env["MELTANO_TRANSFORMER_VARIANT"] == Variant.ORIGINAL_NAME

    assert (
        env["MELTANO_TRANSFORM_TARGET"]
        == env["DBT_TARGET"]
        == env["MELTANO_LOAD__DIALECT"]
        == env["MELTANO_LOADER_NAMESPACE"]
    )
    assert (
        env["MELTANO_TRANSFORM_TARGET_SCHEMA"]
        == env["DBT_TARGET_SCHEMA"]
        == "analytics"
    )
    assert (
        env["MELTANO_TRANSFORM_SOURCE_SCHEMA"]
        == env["DBT_SOURCE_SCHEMA"]
        == env["MELTANO_LOAD__TARGET_SCHEMA"]
        == env["PG_SCHEMA"]
        == env["MELTANO_EXTRACT__LOAD_SCHEMA"]
        == env["MELTANO_EXTRACTOR_NAMESPACE"]
    )
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
        dbt,
    ):
        return (
            elt_context_builder.with_session(session)
            .with_extractor(tap.name)
            .with_loader(target_postgres.name)
            .with_transform(tap_mock_transform.name)
            .with_select_filter(["entity", "!other_entity"])
            .context()
        )

    def test_extractor(self, elt_context, session, tap):
        extractor = elt_context.extractor
        assert extractor.type == PluginType.EXTRACTORS
        assert extractor.name == tap.name

        invoker = elt_context.extractor_invoker()
        with invoker.prepared(session):
            env = invoker.env()

        assert_extractor_env(extractor, env)

    def test_loader(self, elt_context, session, target_postgres):
        loader = elt_context.loader
        assert loader.type == PluginType.LOADERS
        assert loader.name == target_postgres.name

        invoker = elt_context.loader_invoker()
        with invoker.prepared(session):
            env = invoker.env()

        assert_extractor_env(elt_context.extractor, env)
        assert_loader_env(loader, env)

    def test_transformer(
        self, elt_context, session, target_postgres, tap_mock_transform, dbt
    ):
        transformer = elt_context.transformer
        assert transformer.type == PluginType.TRANSFORMERS
        assert transformer.name == dbt.name

        transform = elt_context.transform
        assert transform.type == PluginType.TRANSFORMS
        assert transform.name == tap_mock_transform.name

        invoker = elt_context.transformer_invoker()
        with invoker.prepared(session):
            env = invoker.env()

        assert_extractor_env(elt_context.extractor, env)
        assert_loader_env(elt_context.loader, env)

        assert_transform_env(transform, env)
        assert_transformer_env(transformer, env)

    def test_select_filter(self, elt_context, session):
        assert elt_context.select_filter

        invoker = elt_context.extractor_invoker()
        invoker.prepare(session)
        assert (
            invoker.plugin_config_extras["_select_filter"] == elt_context.select_filter
        )
