import pytest

from meltano.core.plugin import PluginType
from meltano.core.connection_service import ConnectionService


class TestConnectionService:
    @pytest.mark.parametrize(
        "loader,load_params,analyze_params",
        [
            ("target-postgres", {"schema": "tap_mock"}, {"schema": "analytics"}),
            ("target-snowflake", {"schema": "TAP_MOCK"}, {"schema": "ANALYTICS"}),
            ("target-csv", {}, {}),
            ("target-sqlite", {}, {}),
        ],
    )
    def test_params(
        self,
        project_add_service,
        elt_context_builder,
        session,
        tap,
        loader,
        load_params,
        analyze_params,
    ):
        project_add_service.add(PluginType.LOADERS, loader)

        elt_context = (
            elt_context_builder.with_extractor(tap.name)
            .with_loader(loader)
            .context(session)
        )
        subject = ConnectionService(elt_context)

        assert subject.load_params() == load_params
        assert subject.analyze_params() == analyze_params
