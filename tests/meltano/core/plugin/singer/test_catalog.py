import pytest
import json
import logging
from unittest import mock
from pathlib import Path
from copy import deepcopy

from meltano.core.config_service import PluginAlreadyAddedException
from meltano.core.plugin import PluginType
from meltano.core.plugin.error import PluginExecutionError
from meltano.core.plugin_invoker import PluginInvoker
from meltano.core.plugin.singer.catalog import (
    visit,
    SelectExecutor,
    MetadataExecutor,
    MetadataRule,
    SchemaExecutor,
    SchemaRule,
    ListExecutor,
    ListSelectedExecutor,
    path_property,
)


LEGACY_CATALOG = """
{
  "streams": [
    {
      "tap_stream_id": "UniqueEntitiesName",
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
          "unsupported": {
            "type": "null"
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
            "unsupported"
          ],
          "metadata": {
            "inclusion": "unsupported"
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
      "tap_stream_id": "UniqueEntitiesName",
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
          "unsupported": {
            "type": "null"
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
            "unsupported"
          ],
          "metadata": {
            "inclusion": "unsupported"
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
      "tap_stream_id": "UniqueEntitiesName",
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

CATALOG_PROPERTIES = {
    "id",
    "code",
    "name",
    "balance",
    "created_at",
    "active",
    "payload",
    "payload.content",
    "payload.hash",
}


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
        streams = {stream["tap_stream_id"]: stream for stream in catalog["streams"]}

        # all streams are selected
        for name, stream in streams.items():
            assert cls.stream_is_selected(stream), f"{name} is not selected."

        metadatas = [
            (stream["tap_stream_id"], metadata)
            for _, stream in streams.items()
            for metadata in stream["metadata"]
        ]

        # all fields are selected
        for stream, metadata in metadatas:
            field_metadata = metadata["metadata"]
            if field_metadata.get("inclusion") == "unsupported":
                assert not cls.metadata_is_selected(
                    field_metadata
                ), f"{stream}.{metadata['breadcrumb']} is selected"
            else:
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

        streams = {stream["tap_stream_id"]: stream for stream in catalog["streams"]}
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
            (
                "CATALOG",
                {"id", "code", "name", "code", "created_at", "payload.content"},
            ),
            ("JSON_SCHEMA", CATALOG_PROPERTIES),
        ],
        indirect=["catalog"],
    )
    def test_select(self, catalog, attrs):
        selector = SelectExecutor(
            ["UniqueEntitiesName.name", "UniqueEntitiesName.code", "*.payload.content"]
        )
        visit(catalog, selector)

        lister = ListSelectedExecutor()
        visit(catalog, lister)

        assert lister.selected_properties["UniqueEntitiesName"] == attrs

    @pytest.mark.parametrize(
        "catalog,attrs",
        [
            (
                "CATALOG",
                {"id", "balance", "created_at", "active", "payload", "payload.content"},
            ),
            ("JSON_SCHEMA", CATALOG_PROPERTIES),
        ],
        indirect=["catalog"],
    )
    def test_select_negated(self, catalog, attrs):
        selector = SelectExecutor(
            ["*.*", "!UniqueEntitiesName.code", "!UniqueEntitiesName.name", "!*.*.hash"]
        )
        visit(catalog, selector)

        lister = ListSelectedExecutor()
        visit(catalog, lister)

        assert lister.selected_properties["UniqueEntitiesName"] == attrs


class TestMetadataExecutor:
    @pytest.fixture
    def catalog(self, request):
        return json.loads(globals()[request.param])

    @pytest.mark.parametrize(
        "catalog", ["CATALOG", "JSON_SCHEMA"], indirect=["catalog"]
    )
    def test_visit(self, catalog):
        executor = MetadataExecutor(
            [
                MetadataRule("UniqueEntitiesName", [], "replication-key", "created_at"),
                MetadataRule(
                    "UniqueEntitiesName",
                    ["properties", "created_at"],
                    "is-replication-key",
                    True,
                ),
                MetadataRule(
                    "UniqueEntitiesName",
                    ["properties", "payload", "properties", "hash"],
                    "custom-metadata",
                    "custom-value",
                ),
            ]
        )
        visit(catalog, executor)

        stream_node = next(
            s for s in catalog["streams"] if s["tap_stream_id"] == "UniqueEntitiesName"
        )
        stream_metadata_node = next(
            m for m in stream_node["metadata"] if len(m["breadcrumb"]) == 0
        )
        created_at_property_metadata_node = next(
            m
            for m in stream_node["metadata"]
            if m["breadcrumb"] == ["properties", "created_at"]
        )
        hash_property_metadata_node = next(
            m
            for m in stream_node["metadata"]
            if m["breadcrumb"] == ["properties", "payload", "properties", "hash"]
        )

        assert stream_node["replication_key"] == "created_at"
        assert stream_metadata_node["metadata"]["replication-key"] == "created_at"
        assert (
            created_at_property_metadata_node["metadata"]["is-replication-key"] == True
        )
        assert (
            hash_property_metadata_node["metadata"]["custom-metadata"] == "custom-value"
        )


class TestSchemaExecutor:
    @pytest.fixture
    def catalog(self, request):
        return json.loads(globals()[request.param])

    @pytest.mark.parametrize(
        "catalog", ["CATALOG", "JSON_SCHEMA"], indirect=["catalog"]
    )
    def test_visit(self, catalog):
        executor = SchemaExecutor(
            [
                SchemaRule(
                    "UniqueEntitiesName",
                    ["properties", "code"],
                    {"anyOf": [{"type": "string"}, {"type": "null"}]},
                ),
                SchemaRule(
                    "UniqueEntitiesName",
                    ["properties", "payload"],
                    {
                        "type": "object",
                        "properties": {
                            "content": {"type": ["string", "null"]},
                            "hash": {"type": "string"},
                        },
                    },
                ),
                SchemaRule(
                    "UniqueEntitiesName",
                    ["properties", "payload", "properties", "hash"],
                    {"type": ["string", "null"]},
                ),
            ]
        )
        visit(catalog, executor)

        stream_node = next(
            s for s in catalog["streams"] if s["tap_stream_id"] == "UniqueEntitiesName"
        )
        code_property_node = stream_node["schema"]["properties"]["code"]
        hash_property_node = stream_node["schema"]["properties"]["payload"][
            "properties"
        ]["hash"]

        assert code_property_node == {"anyOf": [{"type": "string"}, {"type": "null"}]}
        assert "required" not in stream_node["schema"]["properties"]["payload"]
        assert hash_property_node == {"type": ["string", "null"]}


class TestListExecutor:
    @pytest.fixture
    def catalog(self):
        return json.loads(CATALOG)

    def test_visit(self, catalog):
        executor = ListExecutor()
        visit(catalog, executor)

        assert dict(executor.properties) == {
            "UniqueEntitiesName": {
                "code",
                "name",
                "balance",
                "created_at",
                "id",
                "active",
                "unsupported",
                "payload",
                "payload.content",
                "payload.hash",
            }
        }
