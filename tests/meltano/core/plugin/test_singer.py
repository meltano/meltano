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


@pytest.fixture
def select_all_executor():
    return SelectExecutor(["*.*"])


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

    def test_run_discovery(self, project, subject):
        invoker = PluginInvoker(project, subject)
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

    def test_run_discovery_fails(self, project, subject):
        process_mock = mock.Mock()
        process_mock.wait.return_value = 1  # something went wrong

        invoker = PluginInvoker(project, subject)
        invoker.prepare()

        with mock.patch.object(
            PluginInvoker, "invoke", return_value=process_mock
        ) as invoke, pytest.raises(PluginExecutionError):
            subject.run_discovery(invoker, [])

            assert not invoker.files[
                "catalog"
            ].exists(), "Catalog should not be present."

    def test_apply_select_catalog_invalid(self, project, subject):
        process_mock = mock.Mock()
        process_mock.wait.return_value = 0

        invoker = PluginInvoker(project, subject)
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
    def catalog(self):
        return json.loads(CATALOG)

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

    def test_select(self, catalog):
        selector = SelectExecutor(["entities.name", "entities.code"])
        visit(catalog, selector)

        lister = ListSelectedExecutor()
        visit(catalog, lister)

        assert lister.selected_properties == {
            "entities": {
                "id",  # automatic
                "created_at",  # automatic
                "name",  # selected
                "code",  # selected
            }
        }

    def test_select_negated(self, catalog):
        selector = SelectExecutor(["*.*", "!entities.code", "!entities.name"])
        visit(catalog, selector)

        lister = ListSelectedExecutor()
        visit(catalog, lister)

        assert lister.selected_properties == {
            "entities": {"balance", "created_at", "id", "active"}
        }


class TestListExecutor:
    @pytest.fixture
    def catalog(self):
        return json.loads(CATALOG)

    def test_visit(self, catalog):
        executor = ListExecutor()
        visit(catalog, executor)

        assert dict(executor.properties) == {
            "entities": {"code", "name", "balance", "created_at", "id", "active"}
        }


class TestSingerTarget:
    @pytest.fixture
    def subject(self, project_add_service):
        return project_add_service.add(PluginType.LOADERS, "target-mock")

    def test_exec_args(self, subject):
        base_files = subject.config_files
        assert subject.exec_args(base_files) == ["--config", base_files["config"]]
