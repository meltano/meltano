from __future__ import annotations

import json
import typing as t

import anyio
import pytest

from meltano.core.plugin import PluginType

if t.TYPE_CHECKING:
    from collections.abc import Callable

    from sqlalchemy.orm import Session

    from meltano.core.plugin.project_plugin import ProjectPlugin
    from meltano.core.plugin_invoker import PluginInvoker
    from meltano.core.project_add_service import ProjectAddService


class TestSingerMapper:
    @pytest.fixture(scope="class")
    def subject(self, project_add_service: ProjectAddService) -> ProjectPlugin:
        return project_add_service.add(
            PluginType.MAPPERS,
            "mapper-mock",
            mappings=[
                {
                    "name": "mock-mapping-0",
                    "config": {
                        "transformations": [
                            {
                                "field_id": "author_email",
                                "tap_stream_name": "commits",
                                "type": "MASK-HIDDEN",
                                "foo": "$ENV_FOO",
                            },
                        ],
                    },
                },
                {
                    "name": "mock-mapping-1",
                    "config": {
                        "transformations": [
                            {
                                "field_id": "given_name",
                                "tap_stream_name": "users",
                                "type": "lowercase",
                                "foo": "$ENV_FOO",
                            },
                        ],
                    },
                },
            ],
            config={
                "parent_mapper_setting": "parent_mapper_setting_value",
                "transformations": [
                    {
                        "field_id": "given_name",
                        "tap_stream_name": "users",
                        "type": "uppercase",
                    },
                ],
            },
            mapping_name="mock-mapping-0",
        )

    @pytest.mark.asyncio
    async def test_exec_args(
        self,
        subject: ProjectPlugin,
        session: Session,
        plugin_invoker_factory: Callable[[ProjectPlugin], PluginInvoker],
    ) -> None:
        invoker = plugin_invoker_factory(subject)
        async with invoker.prepared(session):
            assert subject.exec_args(invoker) == ["--config", invoker.files["config"]]

    @pytest.mark.asyncio
    async def test_merged_config(
        self,
        subject: ProjectPlugin,
        session: Session,
        plugin_invoker_factory: Callable[[ProjectPlugin], PluginInvoker],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        invoker = plugin_invoker_factory(subject)

        monkeypatch.setenv("ENV_FOO", "env_foo")
        async with invoker.prepared(session):
            config_path = invoker.files["config"]

            async with await anyio.open_file(config_path, "r") as config_file:
                config = json.loads(await config_file.read())

            assert config == {
                "transformations": [
                    {
                        "field_id": "author_email",
                        "tap_stream_name": "commits",
                        "type": "MASK-HIDDEN",
                        "foo": "env_foo",
                    },
                ],
                "parent_mapper_setting": "parent_mapper_setting_value",
            }
