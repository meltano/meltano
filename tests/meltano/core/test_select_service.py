from __future__ import annotations

import json
import typing as t
from collections import OrderedDict

import pytest

from meltano.core.plugin.singer.catalog import SelectedNode, SelectionType
from meltano.core.plugin.singer.tap import SingerTap
from meltano.core.select_service import SelectService

if t.TYPE_CHECKING:
    from sqlalchemy.orm.session import Session

    from meltano.core.project import Project


@pytest.mark.asyncio()
@pytest.mark.usefixtures("tap")
async def test_select_service_list_all(
    project: Project,
    session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    catalog = {
        "streams": [
            {
                "stream": "users",
                "tap_stream_id": "users",
                "metadata": [
                    {"breadcrumb": [], "metadata": {"selected": True}},
                ],
                "schema": {
                    "properties": {
                        "id": {"type": "integer"},
                    },
                },
            },
        ],
    }
    extractor = "tap-mock"
    service = SelectService(project, extractor)

    async def mock_run_discovery(tap, plugin_invoker, catalog_path) -> None:  # noqa: ARG001
        with catalog_path.open("w") as catalog_file:
            json.dump(catalog, catalog_file)

    # Mock tap's run_discovery method
    monkeypatch.setattr(
        SingerTap,
        "run_discovery",
        mock_run_discovery,
    )

    list_all = await service.list_all(session, refresh=False)
    assert list_all.streams == {
        SelectedNode(
            key="users",
            selection=SelectionType.SELECTED,
        ),
    }
    assert list_all.properties == OrderedDict(
        {
            "users": {
                SelectedNode(
                    key="id",
                    selection=SelectionType.AUTOMATIC,
                ),
            },
        },
    )

    # Update the catalog to include a new property
    catalog["streams"][0]["schema"]["properties"]["name"] = {"type": "string"}

    # Without refreshing the catalog, the new property should not be included
    list_all = await service.list_all(session, refresh=False)
    assert list_all.properties == OrderedDict(
        {
            "users": {
                SelectedNode(
                    key="id",
                    selection=SelectionType.AUTOMATIC,
                ),
            },
        },
    )

    # Refreshing the catalog should include the new property
    list_all = await service.list_all(session, refresh=True)
    assert list_all.properties == OrderedDict(
        {
            "users": {
                SelectedNode(
                    key="id",
                    selection=SelectionType.AUTOMATIC,
                ),
                SelectedNode(
                    key="name",
                    selection=SelectionType.AUTOMATIC,
                ),
            },
        },
    )
