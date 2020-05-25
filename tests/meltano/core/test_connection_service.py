import pytest

from meltano.core.plugin import PluginType
from meltano.core.connection_service import ConnectionService


class TestConnectionService:
    @pytest.mark.parametrize(
        "loader,analyze_params",
        [
            ("target-postgres", {"schema": "tap_mock"}),
            ("target-snowflake", {"schema": "tap_mock"}),
            ("target-csv", {}),
            ("target-sqlite", {}),
        ],
    )
    def test_params(
        self,
        project_add_service,
        elt_context_builder,
        session,
        tap,
        dbt,
        loader,
        analyze_params,
    ):
        project_add_service.add(PluginType.LOADERS, loader)

        elt_context = (
            elt_context_builder.with_extractor(tap.name)
            .with_loader(loader)
            .with_transform("skip")
            .context(session)
        )
        subject = ConnectionService(elt_context)

        assert subject.analyze_params() == analyze_params

    @pytest.mark.parametrize(
        "loader,analyze_params",
        [
            ("target-postgres", {"schema": "analytics"}),
            ("target-snowflake", {"schema": "analytics"}),
            ("target-csv", {}),
            ("target-sqlite", {}),
        ],
    )
    def test_params_with_transform(
        self,
        project_add_service,
        elt_context_builder,
        session,
        tap,
        dbt,
        loader,
        analyze_params,
    ):
        project_add_service.add(PluginType.LOADERS, loader)

        elt_context = (
            elt_context_builder.with_extractor(tap.name)
            .with_loader(loader)
            .with_transform("run")
            .context(session)
        )
        subject = ConnectionService(elt_context)

        assert subject.analyze_params() == analyze_params
