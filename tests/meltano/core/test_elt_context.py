import pytest
import os

from meltano.core.plugin import PluginType


class TestELTContext:
    @pytest.fixture
    def target_postgres(self, project_add_service):
        return project_add_service.add(PluginType.LOADERS, "target-postgres")

    @pytest.fixture
    def elt_context(self, elt_context_builder, session, tap, target_postgres, dbt):
        return (
            elt_context_builder.with_extractor(tap.name)
            .with_loader(target_postgres.name)
            .with_transform("run")
            .context(session)
        )

    def test_extractor(self, elt_context, session, tap):
        extractor = elt_context.extractor
        assert extractor.type == PluginType.EXTRACTORS
        assert extractor.name == tap.name

        invoker = elt_context.extractor_invoker()
        invoker.prepare(session)
        env = invoker.env()

        assert env["TAP_MOCK_TEST"] == "mock"

    def test_loader(self, elt_context, session, target_postgres):
        loader = elt_context.loader
        assert loader.type == PluginType.LOADERS
        assert loader.name == target_postgres.name

        invoker = elt_context.loader_invoker()
        invoker.prepare(session)
        env = invoker.env()

        assert env["MELTANO_EXTRACTOR_NAME"] == elt_context.extractor.name
        assert env["MELTANO_EXTRACTOR_NAMESPACE"] == elt_context.extractor.namespace
        assert env["MELTANO_EXTRACT_TEST"] == "mock"
        assert env["TAP_MOCK_TEST"] == "mock"

        assert env["PG_ADDRESS"] == os.getenv("PG_ADDRESS", "localhost")
        assert env["PG_SCHEMA"] == env["MELTANO_EXTRACTOR_NAMESPACE"]

    def test_transformer(self, elt_context, session, dbt):
        transformer = elt_context.transformer
        assert transformer.type == PluginType.TRANSFORMERS
        assert transformer.name == dbt.name

        invoker = elt_context.transformer_invoker()
        invoker.prepare(session)
        env = invoker.env()

        assert env["MELTANO_EXTRACTOR_NAME"] == elt_context.extractor.name
        assert env["MELTANO_EXTRACTOR_NAMESPACE"] == elt_context.extractor.namespace
        assert env["MELTANO_EXTRACT_TEST"] == "mock"
        assert env["TAP_MOCK_TEST"] == "mock"

        assert env["MELTANO_LOADER_NAME"] == elt_context.loader.name
        assert env["MELTANO_LOADER_NAMESPACE"] == elt_context.loader.namespace
        assert env["MELTANO_LOAD_HOST"] == os.getenv("PG_ADDRESS", "localhost")
        assert env["MELTANO_LOAD_SCHEMA"] == env["MELTANO_EXTRACTOR_NAMESPACE"]
        assert env["PG_ADDRESS"] == os.getenv("PG_ADDRESS", "localhost")
        assert env["PG_SCHEMA"] == env["MELTANO_EXTRACTOR_NAMESPACE"]

        assert env["DBT_TARGET"] == env["MELTANO_LOADER_NAMESPACE"]
        assert env["DBT_TARGET_SCHEMA"] == "analytics"
        assert env["DBT_SOURCE_SCHEMA"] == env["MELTANO_EXTRACTOR_NAMESPACE"]
        assert env["DBT_MODELS"].startswith(env["MELTANO_EXTRACTOR_NAMESPACE"])
