from __future__ import annotations

import json
import typing as t

import pytest

from meltano.core.plugin.singer.catalog import SelectedNode, SelectionType
from meltano.core.plugin.singer.tap import SingerTap
from meltano.core.select_service import SelectService

if t.TYPE_CHECKING:
    from sqlalchemy.orm.session import Session

    from meltano.core.project import Project


@pytest.mark.asyncio
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
    assert list_all.properties == {
        "users": {
            SelectedNode(
                key="id",
                selection=SelectionType.AUTOMATIC,
            ),
        },
    }

    # Update the catalog to include a new property
    catalog["streams"][0]["schema"]["properties"]["name"] = {"type": "string"}

    # Without refreshing the catalog, the new property should not be included
    list_all = await service.list_all(session, refresh=False)
    assert list_all.properties == {
        "users": {
            SelectedNode(
                key="id",
                selection=SelectionType.AUTOMATIC,
            ),
        },
    }

    # Refreshing the catalog should include the new property
    list_all = await service.list_all(session, refresh=True)
    assert list_all.properties == {
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
    }


@pytest.mark.usefixtures("tap")
def test_select_service_clear(project: Project) -> None:
    extractor = "tap-mock"
    service = SelectService(project, extractor)

    # Check if there are any initial select patterns (should be default "*.*")
    initial_patterns = service.current_select[:]
    assert initial_patterns == ["*.*"]

    # Add some select patterns
    service.update("users", "*", exclude=False)
    service.update("posts", "id", exclude=False)
    service.update("posts", "secret", exclude=True)

    # Verify patterns were added (should replace default)
    expected_patterns = ["users.*", "posts.id", "!posts.secret"]
    assert service.current_select == expected_patterns

    # Clear all patterns
    service.clear()

    # Verify all custom patterns were removed and we're back to default
    assert service.current_select == ["*.*"]
