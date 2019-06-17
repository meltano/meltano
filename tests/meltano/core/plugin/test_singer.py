import pytest
import json
import logging
from unittest import mock
from pathlib import Path
from copy import deepcopy

from meltano.core.plugin import PluginType
from meltano.core.plugin.error import PluginExecutionError
from meltano.core.plugin_invoker import PluginInvoker
from meltano.core.plugin.singer.catalog import (
    visit,
    SelectExecutor,
    ListExecutor,
    ListSelectedExecutor,
    path_property,
)


LEGACY_CATALOG = """
{
  "streams": [
    {
      "tap_stream_id": "Entity",
      "stream": "entities",
      "key_properties": [
        "id"
      ],
      "schema": {
        "type": "object",
        "additionalProperties": false,
        "properties": {
          "id": {
            "type": "number"
          },
          "code": {
            "type": [
              "string",
              "null"
            ]
          },
          "name": {
            "type": [
              "string",
              "null"
            ]
          },
          "created_at": {
            "type": [
              "string",
              "null"
            ],
            "format": "date-time"
          },
          "active": {
            "type": [
              "boolean",
              "null"
            ]
          },
          "balance": {
            "type": [
              "number",
              "null"
            ]
          },
          "payload": {
            "type": "object",
            "properties": {
              "content": {"type": ["string", "null"]},
              "hash": {"type": "string"}
            },
            "required": ["hash"]
          }
        }
      },
      "metadata": [
        {
          "breadcrumb": [
            "properties",
            "id"
          ],
          "metadata": {
              "inclusion": "automatic"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "code"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "name"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "created_at"
          ],
          "metadata": {
            "inclusion": "automatic"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "active"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "balance"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "payload"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "payload",
            "properties",
            "content"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "payload",
            "properties",
            "hash"
          ],
          "metadata": {
            "inclusion": "available"
          }
        }
      ],
      "replication_key": "created_at",
      "replication_method": "INCREMENTAL"
    }
  ]
}
"""

CATALOG = """
{
  "streams": [
    {
      "tap_stream_id": "Entity",
      "stream": "entities",
      "schema": {
        "type": "object",
        "additionalProperties": false,
        "properties": {
          "id": {
            "type": "number"
          },
          "code": {
            "type": [
              "string",
              "null"
            ]
          },
          "name": {
            "type": [
              "string",
              "null"
            ]
          },
          "created_at": {
            "type": [
              "string",
              "null"
            ],
            "format": "date-time"
          },
          "active": {
            "type": [
              "boolean",
              "null"
            ]
          },
          "balance": {
            "type": [
              "number",
              "null"
            ]
          },
          "payload": {
            "type": "object",
            "properties": {
              "content": {"type": ["string", "null"]},
              "hash": {"type": "string"}
            },
            "required": ["hash"]
          }
        }
      },
      "metadata": [
        {
          "breadcrumb": [
            "properties",
            "id"
          ],
          "metadata": {
            "inclusion": "automatic"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "code"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "name"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "created_at"
          ],
          "metadata": {
            "inclusion": "automatic"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "active"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "balance"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "payload"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "payload",
            "properties",
            "content"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [
            "properties",
            "payload",
            "properties",
            "hash"
          ],
          "metadata": {
            "inclusion": "available"
          }
        },
        {
          "breadcrumb": [],
          "metadata": {
            "table-key-properties": ["id"],
            "valid-replication-keys": ["created_at"],
            "forced-replication-method": "INCREMENTAL"
          }
        }
      ]
    }
  ]
}
"""

JSON_SCHEMA = """
{
  "streams": [
    {
      "tap_stream_id": "Entity",
      "stream": "entities",
      "schema": {
        "type": "object",
        "additionalProperties": false,
        "properties": {
          "id": {
            "type": "number"
          },
          "code": {
            "type": [
              "string",
              "null"
            ]
          },
          "name": {
            "type": [
              "string",
              "null"
            ]
          },
          "created_at": {
            "anyOf": [
              {"type": "string", "format": "date-time"},
              {"type": ["string", "null"]}
            ]
          },
          "active": {
            "type": [
              "boolean",
              "null"
            ]
          },
          "balance": {
            "type": [
              "number",
              "null"
            ]
          },
          "payload": {
            "type": "object",
            "properties": {
              "content": {"type": ["string", "null"]},
              "hash": {"type": "string"}
            },
            "required": ["hash"]
          }
        }
      }
    }
  ]
}
"""


@pytest.fixture
def select_all_executor():
    return SelectExecutor(["*.*"])


@pytest.mark.parametrize(
    "path,prop",
    [
        ("stream[0].properties.master.properties.details", "master.details"),
        ("stream[2].properties.name", "name"),
        ("stream[10].properties.list[2].properties.name", "list[2].name"),
    ],
)
def test_path_property(path, prop):
    assert path_property(path) == prop


class TestSingerTap:
    @pytest.fixture(scope="class")
    def subject(self, project_add_service):
        return project_add_service.add(PluginType.EXTRACTORS, "tap-mock")

    def config_files(self, subject, dir: Path):
        return {key: dir.join(file) for key, file in subject.config_files.items()}

    def test_exec_args(self, subject, tmpdir):
        base_files = self.config_files(subject, tmpdir.mkdir("base"))
        assert subject.exec_args(base_files) == ["--config", base_files["config"]]

        # when `catalog` has data
        base_files = self.config_files(subject, tmpdir.mkdir("catalog"))
        base_files["catalog"].open("w").write("...")
        assert subject.exec_args(base_files) == [
            "--config",
            base_files["config"],
            "--catalog",
            base_files["catalog"],
        ]

        # when `state` has data
        base_files = self.config_files(subject, tmpdir.mkdir("state"))
        base_files["state"].open("w").write("...")
        assert subject.exec_args(base_files) == [
            "--config",
            base_files["config"],
            "--state",
            base_files["state"],
        ]

    def test_run_discovery(self, session, plugin_invoker_factory, subject):
        invoker = plugin_invoker_factory(session, subject)
        invoker.prepare()

        def mock_discovery():
            invoker.files["catalog"].open("w").write(CATALOG)
            return 0

        process_mock = mock.Mock()
        process_mock.wait = mock_discovery

        with mock.patch.object(
            PluginInvoker, "invoke", return_value=process_mock
        ) as invoke:
            subject.run_discovery(invoker, [])

            assert invoke.called_with(["--discover"])

    def test_run_discovery_fails(self, session, plugin_invoker_factory, subject):
        process_mock = mock.Mock()
        process_mock.wait.return_value = 1  # something went wrong

        invoker = plugin_invoker_factory(session, subject)
        invoker.prepare()

        with mock.patch.object(
            PluginInvoker, "invoke", return_value=process_mock
        ) as invoke, pytest.raises(PluginExecutionError):
            subject.run_discovery(invoker, [])

            assert not invoker.files[
                "catalog"
            ].exists(), "Catalog should not be present."

    def test_apply_select_catalog_invalid(
        self, session, plugin_invoker_factory, subject
    ):
        process_mock = mock.Mock()
        process_mock.wait.return_value = 0

        invoker = plugin_invoker_factory(session, subject)
        invoker.prepare()

        def corrupt_catalog(*_, **__):
            invoker.files["catalog"].open("w").write("this is invalid json")

            return process_mock

        with mock.patch.object(
            PluginInvoker, "invoke", side_effect=corrupt_catalog
        ) as invoke:
            subject.apply_select(invoker, [])

            assert not invoker.files[
                "catalog"
            ].exists(), "Catalog should not be present."


class TestLegacyCatalogSelectVisitor:
    @pytest.fixture
    def catalog(self):
        return json.loads(LEGACY_CATALOG)

    @classmethod
    def stream_is_selected(cls, stream):
        return stream.get("selected", False)

    @classmethod
    def metadata_is_selected(cls, metadata):
        inclusion = metadata.get("inclusion")
        if inclusion == "automatic":
            return True

        return metadata.get("selected", False)

    @classmethod
    def assert_catalog_is_selected(cls, catalog):
        streams = {stream["stream"]: stream for stream in catalog["streams"]}

        metadatas = {
            stream["stream"]: metadata
            for _, stream in streams.items()
            for metadata in stream["metadata"]
        }

        # all streams are selected
        for name, stream in streams.items():
            assert cls.stream_is_selected(stream), f"{name} is not selected."

        # all fields are selected
        for stream, metadata in metadatas.items():
            field_metadata = metadata["metadata"]
            assert cls.metadata_is_selected(
                field_metadata
            ), f"{stream}.{metadata['breadcrumb']} is not selected"

    def test_visit(self, catalog, select_all_executor):
        visit(catalog, select_all_executor)

        self.assert_catalog_is_selected(catalog)


class TestCatalogSelectVisitor(TestLegacyCatalogSelectVisitor):
    @pytest.fixture
    def catalog(self, request):
        return json.loads(globals()[request.param])

    @classmethod
    def stream_is_selected(cls, stream):
        try:
            stream_metadata = next(
                metadata
                for metadata in stream["metadata"]
                if len(metadata["breadcrumb"]) == 0
            )

            return cls.metadata_is_selected(stream_metadata["metadata"])
        except (KeyError, IndexError):
            return False

    @pytest.mark.parametrize(
        "catalog", ["CATALOG", "JSON_SCHEMA"], indirect=["catalog"]
    )
    def test_visit(self, catalog, select_all_executor):
        super().test_visit(catalog, select_all_executor)

    @pytest.mark.parametrize(
        "catalog", ["CATALOG", "JSON_SCHEMA"], indirect=["catalog"]
    )
    def test_select_all(self, catalog, select_all_executor):
        visit(catalog, select_all_executor)
        self.assert_catalog_is_selected(catalog)

        streams = {stream["stream"]: stream for stream in catalog["streams"]}
        stream_metadata = len(
            [
                metadata
                for stream in streams.values()
                for metadata in stream["metadata"]
                if len(metadata["breadcrumb"]) == 0
            ]
        )

        assert stream_metadata == 1, "Extraneous stream metadata"

    @pytest.mark.parametrize(
        "catalog,attrs",
        [
            ("CATALOG", {"id", "code", "name", "code", "created_at"}),
            (
                "JSON_SCHEMA",
                {
                    "id",
                    "code",
                    "name",
                    "balance",
                    "created_at",
                    "active",
                    "payload",
                    "payload.content",
                    "payload.hash",
                },
            ),
        ],
        indirect=["catalog"],
    )
    def test_select(self, catalog, attrs):
        selector = SelectExecutor(["entities.name", "entities.code"])
        visit(catalog, selector)

        lister = ListSelectedExecutor()
        visit(catalog, lister)

        assert lister.selected_properties["entities"] == attrs

    @pytest.mark.parametrize(
        "catalog,attrs",
        [
            (
                "CATALOG",
                {
                    "id",
                    "balance",
                    "created_at",
                    "active",
                    "payload",
                    "payload.content",
                    "payload.hash",
                },
            ),
            (
                "JSON_SCHEMA",
                {
                    "id",
                    "code",
                    "name",
                    "balance",
                    "created_at",
                    "active",
                    "payload",
                    "payload.content",
                    "payload.hash",
                },
            ),
        ],
        indirect=["catalog"],
    )
    def test_select_negated(self, catalog, attrs):
        selector = SelectExecutor(["*.*", "!entities.code", "!entities.name"])
        visit(catalog, selector)

        lister = ListSelectedExecutor()
        visit(catalog, lister)

        assert lister.selected_properties["entities"] == attrs


class TestListExecutor:
    @pytest.fixture
    def catalog(self):
        return json.loads(CATALOG)

    def test_visit(self, catalog):
        executor = ListExecutor()
        visit(catalog, executor)

        assert dict(executor.properties) == {
            "entities": {
                "code",
                "name",
                "balance",
                "created_at",
                "id",
                "active",
                "payload",
                "payload.content",
                "payload.hash",
            }
        }


class TestSingerTarget:
    @pytest.fixture
    def subject(self, project_add_service):
        return project_add_service.add(PluginType.LOADERS, "target-mock")

    def test_exec_args(self, subject):
        base_files = subject.config_files
        assert subject.exec_args(base_files) == ["--config", base_files["config"]]
