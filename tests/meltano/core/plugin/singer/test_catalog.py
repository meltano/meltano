from __future__ import annotations

import json

import pytest

from meltano.core.plugin.singer.catalog import (  # noqa: WPS235
    CatalogRule,
    ListExecutor,
    ListSelectedExecutor,
    MetadataExecutor,
    MetadataRule,
    SchemaExecutor,
    SchemaRule,
    SelectExecutor,
    SelectionType,
    path_property,
    visit,
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
              "hash": {"type": "string"},
              "timestamp": {"type": "string", "format": "date-time"}
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
          "breadcrumb": [
            "properties",
            "payload",
            "properties",
            "timestamp"
          ],
          "metadata": {
            "inclusion": "available",
            "selected-by-default": true
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

# Duplicate CATALOG, but change the stream ID to Unique.Entities.Name
# to test that it is properly escaped
ESCAPED_CATALOG = """
{
  "streams": [
    {
      "tap_stream_id": "Unique.Entities.Name",
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
              "hash": {"type": "string"},
              "timestamp": {"type": "string", "format": "date-time"}
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
          "breadcrumb": [
            "properties",
            "payload",
            "properties",
            "timestamp"
          ],
          "metadata": {
            "inclusion": "available",
            "selected-by-default": true
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

ESCAPED_JSON_SCHEMA = """
{
  "streams": [
    {
      "tap_stream_id": "Unique.Entities.Name",
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


EMPTY_STREAM_SCHEMA = """
{
  "streams": [
    {
      "tap_stream_id": "UniqueEntitiesName",
      "stream": "entities",
      "schema": {
        "type": "object"
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
}


@pytest.fixture()
def select_all_executor():
    return SelectExecutor(["*.*"])


@pytest.mark.parametrize(
    ("path", "prop"),
    (
        ("stream[0].properties.master.properties.details", "master.details"),
        ("stream[2].properties.name", "name"),
        ("stream[10].properties.list[2].properties.name", "list[2].name"),
    ),
)
def test_path_property(path, prop):
    assert path_property(path) == prop


class TestCatalogRule:
    def test_match(self):
        rule = CatalogRule("tap_stream_id")

        # Stream ID matches
        assert rule.match("tap_stream_id")

        # Stream ID and breadcrumb match
        assert rule.match("tap_stream_id", [])

        # Breadcrumb doesn't match
        assert not rule.match("tap_stream_id", ["property"])

        # Stream ID doesn't match
        assert not rule.match("tap_stream")

    def test_match_wildcard(self):
        rule = CatalogRule("tap_stream*")

        # Stream ID pattern matches
        assert rule.match("tap_stream_id")
        assert rule.match("tap_stream_foo")
        assert rule.match("tap_stream")

        # Stream ID pattern doesn't match
        assert not rule.match("tap_strea")

    def test_match_multiple(self):
        rule = CatalogRule(["tap_stream_id", "other*"])

        # Stream ID patterns match
        assert rule.match("tap_stream_id")
        assert rule.match("other_stream")
        assert rule.match("other_foo")
        assert rule.match("other")

        # Stream ID patterns don't match
        assert not rule.match("tap_stream")
        assert not rule.match("othe")

    def test_match_negated(self):
        rule = CatalogRule("tap_stream_id", negated=True)

        # Stream ID doesn't match, so the rule does
        assert rule.match("tap_stream")

        # Stream ID doesn't match (good!) and breadcrumb does
        assert rule.match("tap_stream", [])

        # Stream ID matches, so the rule doesn't
        assert not rule.match("tap_stream_id")
        assert not rule.match("tap_stream_id", [])
        assert not rule.match("tap_stream_id", ["property"])

        # Stream ID doesn't match (good!), but breadcrumb doesn't match
        assert not rule.match("tap_stream", ["property"])

    def test_match_negated_wildcard(self):
        rule = CatalogRule("tap_stream*", negated=True)

        # Stream ID pattern doesn't match, so the rule does
        assert rule.match("tap_strea")

        # Stream ID pattern matches, so the rule doesn't
        assert not rule.match("tap_stream_id")
        assert not rule.match("tap_stream_foo")
        assert not rule.match("tap_stream")

    def test_match_negated_multiple(self):
        rule = CatalogRule(["tap_stream_id", "other*"], negated=True)

        # Stream ID pattern doesn't match, so the rule does
        assert rule.match("tap_stream")
        assert rule.match("othe")

        # Stream ID pattern matches, so the rule doesn't
        assert not rule.match("tap_stream_id")
        assert not rule.match("other_stream")
        assert not rule.match("other_foo")
        assert not rule.match("other")

    def test_match_breadcrumb(self):
        rule = CatalogRule("tap_stream_id", ["property"])

        # Stream ID matches and breadcrumb is not considered
        assert rule.match("tap_stream_id")

        # Stream ID and breadcrumb match
        assert rule.match("tap_stream_id", ["property"])

        # Stream ID matches, but breadcrumb doesn't
        assert not rule.match("tap_stream_id", [])
        assert not rule.match("tap_stream_id", ["property", "nested"])

    def test_match_wildcard_breadcrumb(self):
        rule = CatalogRule("tap_stream_id", ["proper*"])

        # Stream ID and breadcrumb pattern match
        assert rule.match("tap_stream_id")
        assert rule.match("tap_stream_id", ["property"])
        assert rule.match("tap_stream_id", ["proper_foo"])
        assert rule.match("tap_stream_id", ["proper"])
        assert rule.match("tap_stream_id", ["property", "bar"])

        # Breadcrumb pattern doesn't match
        assert not rule.match("tap_stream_id", [])
        assert not rule.match("tap_stream_id", ["other"])

    def test_match_negated_breadcrumb(self):
        rule = CatalogRule("tap_stream_id", ["property"], negated=True)

        # Stream ID doesn't match (good!) and breadcrumb is not considered
        assert rule.match("tap_stream")

        # Stream ID doesn't match (good!) and breadcrumb does
        assert rule.match("tap_stream", ["property"])

        # Stream ID doesn't match (good!), but breadcrumb doesn't match
        assert not rule.match("tap_stream", [])
        assert not rule.match("tap_stream", ["property", "nested"])


class TestLegacyCatalogSelectVisitor:
    @pytest.fixture()
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
                    field_metadata,
                ), f"{stream}.{metadata['breadcrumb']} is selected"
            else:
                assert cls.metadata_is_selected(
                    field_metadata,
                ), f"{stream}.{metadata['breadcrumb']} is not selected"

    def test_visit(self, catalog, select_all_executor):
        visit(catalog, select_all_executor)

        self.assert_catalog_is_selected(catalog)


class TestCatalogSelectVisitor(TestLegacyCatalogSelectVisitor):
    @pytest.fixture()
    def catalog(self, request):
        return json.loads(globals()[request.param])  # noqa: WPS421

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
        "catalog",
        ("CATALOG", "JSON_SCHEMA"),
        indirect=["catalog"],
    )
    def test_visit(self, catalog, select_all_executor):
        super().test_visit(catalog, select_all_executor)

    @pytest.mark.parametrize(
        "catalog",
        ("CATALOG", "JSON_SCHEMA"),
        indirect=["catalog"],
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
            ],
        )

        assert stream_metadata == 1, "Extraneous stream metadata"

    @pytest.mark.parametrize(
        ("catalog", "attrs"),
        (
            (
                "CATALOG",
                {
                    "id",
                    "code",
                    "name",
                    "created_at",
                    "payload.content",
                    "payload.timestamp",
                },
            ),
            ("JSON_SCHEMA", CATALOG_PROPERTIES),
        ),
        indirect=["catalog"],
    )
    def test_select(self, catalog, attrs):
        selector = SelectExecutor(
            [
                "UniqueEntitiesName.code",
                "UniqueEntitiesName.name",
                "*.payload.content",
            ],
        )
        visit(catalog, selector)

        lister = ListSelectedExecutor()
        visit(catalog, lister)

        assert lister.selected_properties["UniqueEntitiesName"] == attrs

    @pytest.mark.parametrize(
        ("catalog", "attrs"),
        (
            (
                "ESCAPED_CATALOG",
                {
                    "id",
                    "code",
                    "name",
                    "created_at",
                    "payload.content",
                    "payload.timestamp",
                },
            ),
            ("ESCAPED_JSON_SCHEMA", CATALOG_PROPERTIES),
        ),
        indirect=["catalog"],
    )
    def test_select_escaped(self, catalog, attrs):
        selector = SelectExecutor(
            [
                "Unique\\.Entities\\.Name.code",
                "Unique\\.Entities\\.Name.name",
                "*.payload.content",
            ],
        )
        visit(catalog, selector)

        lister = ListSelectedExecutor()
        visit(catalog, lister)

        assert lister.selected_properties["Unique.Entities.Name"] == attrs

    @pytest.mark.parametrize(
        ("catalog", "attrs"),
        (
            (
                "CATALOG",
                {"id", "balance", "created_at", "active", "payload", "payload.content"},
            ),
            ("JSON_SCHEMA", CATALOG_PROPERTIES),
        ),
        indirect=["catalog"],
    )
    def test_select_negated(self, catalog, attrs):
        selector = SelectExecutor(
            [
                "*.*",
                "!UniqueEntitiesName.code",
                "!UniqueEntitiesName.name",
                "!*.*.hash",
                "!*.*.timestamp",
            ],
        )
        visit(catalog, selector)

        lister = ListSelectedExecutor()
        visit(catalog, lister)

        assert lister.selected_properties["UniqueEntitiesName"] == attrs

    @pytest.mark.parametrize(
        ("node", "selection_type"),
        (
            (
                {"breadcrumb": ["properties", "a"], "metadata": {"selected": True}},
                SelectionType.SELECTED,
            ),
            (
                {"breadcrumb": ["properties", "a"], "metadata": {"selected": False}},
                SelectionType.EXCLUDED,
            ),
            (
                {
                    "breadcrumb": ["properties", "a"],
                    "metadata": {"inclusion": "automatic"},
                },
                SelectionType.AUTOMATIC,
            ),
            (
                {
                    "breadcrumb": ["properties", "a"],
                    "metadata": {"inclusion": "unsupported"},
                },
                SelectionType.EXCLUDED,
            ),
            (
                {
                    "breadcrumb": ["properties", "a"],
                    "metadata": {"inclusion": "available"},
                },
                SelectionType.EXCLUDED,
            ),
            (
                {
                    "breadcrumb": ["properties", "a"],
                    "metadata": {"selected": True, "inclusion": "available"},
                },
                SelectionType.SELECTED,
            ),
            (
                {
                    "breadcrumb": ["properties", "a"],
                    "metadata": {"selected": False, "selected-by-default": True},
                },
                SelectionType.EXCLUDED,
            ),
            (
                {
                    "breadcrumb": ["properties", "a"],
                    "metadata": {"selected-by-default": True},
                },
                SelectionType.SELECTED,
            ),
            (
                {"breadcrumb": ["properties", "a"]},
                SelectionType.EXCLUDED,
            ),
        ),
        ids=[
            "selected: true",
            "selected: false",
            "inclusion: available",
            "selected: true, inclusion: available",
            "inclusion: automatic",
            "inclusion: unsupported",
            "selected: false, selected-by-default: true",
            "selected-by-default: true",
            "no metadata",
        ],
    )
    def test_node_selection(self, node: dict, selection_type: SelectionType):
        """Test that selection metadata produces the expected selection type member."""
        assert ListSelectedExecutor.node_selection(node) == selection_type


class TestMetadataExecutor:
    @pytest.fixture()
    def catalog(self, request):
        return json.loads(globals()[request.param])  # noqa: WPS421

    @pytest.mark.parametrize(
        "catalog",
        ("CATALOG", "JSON_SCHEMA"),
        indirect=["catalog"],
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
            ],
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
            created_at_property_metadata_node["metadata"]["is-replication-key"] is True
        )
        assert (
            hash_property_metadata_node["metadata"]["custom-metadata"] == "custom-value"
        )


class TestSchemaExecutor:
    @pytest.fixture()
    def catalog(self, request):
        return json.loads(globals()[request.param])  # noqa: WPS421

    @pytest.mark.parametrize(
        "catalog",
        ("CATALOG", "JSON_SCHEMA", "EMPTY_STREAM_SCHEMA"),
        indirect=["catalog"],
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
                    ["properties", "*_at"],
                    {"type": "string", "format": "date"},
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
                    ["properties", "*load", "properties", "hash"],
                    {"type": ["string", "null"]},
                ),
            ],
        )
        visit(catalog, executor)

        stream_node = next(
            s for s in catalog["streams"] if s["tap_stream_id"] == "UniqueEntitiesName"
        )
        properties_node = stream_node["schema"]["properties"]

        assert properties_node["code"] == {
            "anyOf": [{"type": "string"}, {"type": "null"}],
        }

        if "created_at" in properties_node:
            assert properties_node["created_at"] == {  # noqa: WPS52
                "type": "string",
                "format": "date",
            }
        else:
            # If no matching properties were found for a glob-like pattern,
            # no new property is created
            assert "*_at" not in properties_node

        assert properties_node["payload"] == {
            "type": "object",
            "properties": {
                "content": {"type": ["string", "null"]},
                "hash": {"type": ["string", "null"]},
            },
        }


class TestListExecutor:
    @pytest.fixture()
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
                "payload.timestamp",
            },
        }
