from __future__ import annotations

import pytest

from meltano.core.connection_service import ConnectionService
from meltano.core.plugin import PluginType
from meltano.core.project_plugins_service import PluginAlreadyAddedException


# This is dead code that likely should have been removed
# as part of the wider m5o deprecation.
# A later issue should remove this.
@pytest.mark.skip
class TestConnectionService:
    @pytest.mark.parametrize(
        "loader,analyze_params",
        [
            # TODO: the tests that were here are broken, but are going away in 2.0
            # Properly flag in pytest etc.
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
        try:
            project_add_service.add(PluginType.LOADERS, loader)
        except PluginAlreadyAddedException:
            pass

        elt_context = (
            elt_context_builder.with_session(session)
            .with_extractor(tap.name)
            .with_loader(loader)
            .with_transform("skip")
            .context()
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
        try:
            project_add_service.add(PluginType.LOADERS, loader)
        except PluginAlreadyAddedException:
            pass

        elt_context = (
            elt_context_builder.with_session(session)
            .with_extractor(tap.name)
            .with_loader(loader)
            .with_transform("run")
            .context()
        )
        subject = ConnectionService(elt_context)

        assert subject.analyze_params() == analyze_params
