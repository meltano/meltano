from __future__ import annotations

import json
import typing as t
from copy import deepcopy

import pytest

from meltano.core.plugin.singer.catalog import (
    SELECTED_KEY,
    CatalogRule,
    ListExecutor,
    ListSelectedExecutor,
    MetadataExecutor,
    MetadataRule,
    SchemaExecutor,
    SchemaRule,
    SelectExecutor,
    SelectionType,
    SelectPattern,
    path_property,
    select_filter_metadata_rules,
    select_metadata_rules,
    visit,
)
from meltano.core.plugin.singer.catalog import property_breadcrumb as bc

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


@pytest.fixture
def select_all_executor():
    return SelectExecutor(["*.*"])


@pytest.mark.parametrize(
    ("path", "prop"),
    (
        ("stream[0].properties.master.properties.details", "master.details"),
        ("stream[2].properties.name", "name"),
        ("stream[10].properties.list[2].properties.name", "list[2].name"),
        ("stream[0].properties.properties.properties.prop_1", "properties.prop_1"),
        (
            "stream[0].properties.I HAVE SPACES.properties.SPECIAL CHAR %",
            "I HAVE SPACES.SPECIAL CHAR %",
        ),
    ),
)
def test_path_property(path, prop) -> None:
    assert path_property(path) == prop


class TestCatalogRule:
    def test_match(self) -> None:
        rule = CatalogRule("tap_stream_id")

        # Stream ID matches
        assert rule.match("tap_stream_id")

        # Stream ID and breadcrumb match
        assert rule.match("tap_stream_id", [])

        # Breadcrumb doesn't match
        assert not rule.match("tap_stream_id", ["property"])

        # Stream ID doesn't match
        assert not rule.match("tap_stream")

    def test_match_wildcard(self) -> None:
        rule = CatalogRule("tap_stream*")

        # Stream ID pattern matches
        assert rule.match("tap_stream_id")
        assert rule.match("tap_stream_foo")
        assert rule.match("tap_stream")

        # Stream ID pattern doesn't match
        assert not rule.match("tap_strea")

    def test_match_multiple(self) -> None:
        rule = CatalogRule(["tap_stream_id", "other*"])

        # Stream ID patterns match
        assert rule.match("tap_stream_id")
        assert rule.match("other_stream")
        assert rule.match("other_foo")
        assert rule.match("other")

        # Stream ID patterns don't match
        assert not rule.match("tap_stream")
        assert not rule.match("othe")

    def test_match_negated(self) -> None:
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

    def test_match_negated_wildcard(self) -> None:
        rule = CatalogRule("tap_stream*", negated=True)

        # Stream ID pattern doesn't match, so the rule does
        assert rule.match("tap_strea")

        # Stream ID pattern matches, so the rule doesn't
        assert not rule.match("tap_stream_id")
        assert not rule.match("tap_stream_foo")
        assert not rule.match("tap_stream")

    def test_match_negated_multiple(self) -> None:
        rule = CatalogRule(["tap_stream_id", "other*"], negated=True)

        # Stream ID pattern doesn't match, so the rule does
        assert rule.match("tap_stream")
        assert rule.match("othe")

        # Stream ID pattern matches, so the rule doesn't
        assert not rule.match("tap_stream_id")
        assert not rule.match("other_stream")
        assert not rule.match("other_foo")
        assert not rule.match("other")

    def test_match_breadcrumb(self) -> None:
        rule = CatalogRule("tap_stream_id", ["property"])

        # Stream ID matches and breadcrumb is not considered
        assert rule.match("tap_stream_id")

        # Stream ID and breadcrumb match
        assert rule.match("tap_stream_id", ["property"])

        # Stream ID matches, but breadcrumb doesn't
        assert not rule.match("tap_stream_id", [])
        assert not rule.match("tap_stream_id", ["property", "nested"])

    def test_match_wildcard_breadcrumb(self) -> None:
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

    def test_match_negated_breadcrumb(self) -> None:
        rule = CatalogRule("tap_stream_id", ["property"], negated=True)

        # Stream ID doesn't match (good!) and breadcrumb is not considered
        assert rule.match("tap_stream")

        # Stream ID doesn't match (good!) and breadcrumb does
        assert rule.match("tap_stream", ["property"])

        # Stream ID doesn't match (good!), but breadcrumb doesn't match
        assert not rule.match("tap_stream", [])
        assert not rule.match("tap_stream", ["property", "nested"])


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
    def assert_catalog_is_selected(cls, catalog) -> None:
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

    def test_visit(self, catalog, select_all_executor) -> None:
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
        "catalog",
        ("CATALOG", "JSON_SCHEMA"),
        indirect=["catalog"],
    )
    def test_visit(self, catalog, select_all_executor) -> None:
        super().test_visit(catalog, select_all_executor)

    @pytest.mark.parametrize(
        "catalog",
        ("CATALOG", "JSON_SCHEMA"),
        indirect=["catalog"],
    )
    def test_select_all(self, catalog, select_all_executor) -> None:
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
                    "payload",
                    "payload.content",
                    "payload.timestamp",
                },
            ),
            ("JSON_SCHEMA", CATALOG_PROPERTIES),
        ),
        indirect=["catalog"],
    )
    def test_select(self, catalog: dict[str, t.Any], attrs: set[str]) -> None:
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
                    "payload",
                    "payload.content",
                    "payload.timestamp",
                },
            ),
            ("ESCAPED_JSON_SCHEMA", CATALOG_PROPERTIES),
        ),
        indirect=["catalog"],
    )
    def test_select_escaped(self, catalog: dict[str, t.Any], attrs: set[str]) -> None:
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
    def test_select_negated(self, catalog, attrs) -> None:
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
        ("patterns", "attrs"),
        (
            pytest.param(
                ["MyStream.*"],
                {
                    "id",
                    "name",
                    "geo",
                    "geo.city",
                    "geo.state",
                    "geo.state.name",
                    "geo.state.code",
                    "geo.country",
                    "geo.country.name",
                    "geo.country.code",
                    "geo.point",
                    "geo.point.lat",
                    "geo.point.lon",
                },
                id="stream.*",
            ),
            pytest.param(
                ["MyStream.geo.*"],
                {
                    "id",
                    "geo",
                    "geo.city",
                    "geo.state",
                    "geo.state.name",
                    "geo.state.code",
                    "geo.country",
                    "geo.country.name",
                    "geo.country.code",
                    "geo.point",
                    "geo.point.lat",
                    "geo.point.lon",
                },
                id="stream.field.*",
            ),
            pytest.param(
                ["MyStream.geo.city"],
                {"id", "geo", "geo.city"},
                id="stream.field.subfield",
            ),
            pytest.param(
                ["MyStream.geo.point.*"],
                {"id", "geo", "geo.point", "geo.point.lat", "geo.point.lon"},
                id="stream.field.subfield.*",
            ),
            pytest.param(
                ["MyStream.geo.*.*"],
                {
                    "id",
                    "geo",
                    "geo.city",
                    "geo.state",
                    "geo.state.name",
                    "geo.state.code",
                    "geo.country",
                    "geo.country.name",
                    "geo.country.code",
                    "geo.point",
                    "geo.point.lat",
                    "geo.point.lon",
                },
                id="stream.field.*.*",
            ),
            pytest.param(
                ["MyStream.geo.*", "!MyStream.geo.*.name"],
                {
                    "id",
                    "geo",
                    "geo.city",
                    "geo.state",
                    "geo.state.code",
                    "geo.country",
                    "geo.country.code",
                    "geo.point",
                    "geo.point.lat",
                    "geo.point.lon",
                },
                id="!stream.field.*.subfield",
            ),
        ),
    )
    def test_select_stream_star(self, patterns: list[str], attrs: set[str]) -> None:
        catalog = {
            "streams": [
                {
                    "tap_stream_id": "MyStream",
                    "stream": "my_stream",
                    "metadata": [
                        {
                            "breadcrumb": [],
                            "metadata": {
                                "inclusion": "available",
                                "table-key-properties": ["id"],
                            },
                        },
                        {
                            "breadcrumb": ["properties", "id"],
                            "metadata": {"inclusion": "automatic"},
                        },
                        {
                            "breadcrumb": ["properties", "name"],
                            "metadata": {"inclusion": "available"},
                        },
                        {
                            "breadcrumb": ["properties", "geo"],
                            "metadata": {"inclusion": "available"},
                        },
                        {
                            "breadcrumb": ["properties", "geo", "properties", "city"],
                            "metadata": {"inclusion": "available"},
                        },
                        {
                            "breadcrumb": ["properties", "geo", "properties", "state"],
                            "metadata": {"inclusion": "available"},
                        },
                        {
                            "breadcrumb": [
                                "properties",
                                "geo",
                                "properties",
                                "state",
                                "properties",
                                "name",
                            ],
                            "metadata": {"inclusion": "available"},
                        },
                        {
                            "breadcrumb": [
                                "properties",
                                "geo",
                                "properties",
                                "state",
                                "properties",
                                "code",
                            ],
                            "metadata": {"inclusion": "available"},
                        },
                        {
                            "breadcrumb": [
                                "properties",
                                "geo",
                                "properties",
                                "country",
                            ],
                            "metadata": {"inclusion": "available"},
                        },
                        {
                            "breadcrumb": [
                                "properties",
                                "geo",
                                "properties",
                                "country",
                                "properties",
                                "name",
                            ],
                            "metadata": {"inclusion": "available"},
                        },
                        {
                            "breadcrumb": [
                                "properties",
                                "geo",
                                "properties",
                                "country",
                                "properties",
                                "code",
                            ],
                            "metadata": {"inclusion": "available"},
                        },
                        {
                            "breadcrumb": ["properties", "geo", "properties", "point"],
                            "metadata": {"inclusion": "available"},
                        },
                        {
                            "breadcrumb": [
                                "properties",
                                "geo",
                                "properties",
                                "point",
                                "properties",
                                "lat",
                            ],
                            "metadata": {"inclusion": "available"},
                        },
                        {
                            "breadcrumb": [
                                "properties",
                                "geo",
                                "properties",
                                "point",
                                "properties",
                                "lon",
                            ],
                            "metadata": {"inclusion": "available"},
                        },
                    ],
                },
            ],
        }
        selector = SelectExecutor(patterns)
        visit(catalog, selector)

        lister = ListSelectedExecutor()
        visit(catalog, lister)

        assert lister.selected_properties["MyStream"] == attrs

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
                SelectionType.UNSUPPORTED,
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
    def test_node_selection(self, node: dict, selection_type: SelectionType) -> None:
        """Test that selection metadata produces the expected selection type member."""
        assert ListSelectedExecutor.node_selection(node) == selection_type

    def test_select_metadata_rules_stream_only_behaves_like_stream_star(self) -> None:
        """Test that stream-only patterns behave like stream.*."""
        stream_only_rules = select_metadata_rules(["users"])
        stream_star_rules = select_metadata_rules(["users.*"])

        assert len(stream_only_rules) == len(stream_star_rules) == 2

        # Both should create identical rules
        for rule1, rule2 in zip(stream_only_rules, stream_star_rules, strict=False):
            assert rule1.tap_stream_id == rule2.tap_stream_id
            assert rule1.breadcrumb == rule2.breadcrumb
            assert rule1.key == rule2.key
            assert rule1.value == rule2.value
            assert rule1.negated == rule2.negated

    def test_select_metadata_rules_stream_property_creates_both_rules(self) -> None:
        """Test that stream.property creates both stream and property rules."""
        rules = select_metadata_rules(["users.name"])

        assert len(rules) == 2

        # Find stream and property rules
        stream_rule = next(r for r in rules if r.breadcrumb == [])
        prop_rule = next(r for r in rules if r.breadcrumb != [])

        # Stream rule
        assert stream_rule.tap_stream_id == "users"
        assert stream_rule.breadcrumb == []
        assert stream_rule.key == "selected"
        assert stream_rule.value is True

        # Property rule
        assert prop_rule.tap_stream_id == "users"
        assert prop_rule.breadcrumb == ["properties", "name"]
        assert prop_rule.key == "selected"
        assert prop_rule.value is True

    def test_cli_select_exclude_integration_stream_patterns(self) -> None:
        """Test CLI --select/--exclude integration with stream-only patterns."""
        # Simulate CLI: --select users --exclude admins
        # This becomes select_filter = ["users", "!admins"]
        cli_patterns = ["users", "!admins"]
        rules = select_filter_metadata_rules(cli_patterns)

        # Should create stream-level filtering rules
        assert len(rules) == 2

        # Find include and exclude rules
        include_rule = next(r for r in rules if r.negated)
        exclude_rule = next(r for r in rules if not r.negated)

        # Include rule: streams NOT matching ["users"] get selected: false
        assert include_rule.tap_stream_id == ["users"]
        assert include_rule.breadcrumb == []
        assert include_rule.key == "selected"
        assert include_rule.value is False
        assert include_rule.negated is True

        # Exclude rule: streams matching ["admins"] get selected: false
        assert exclude_rule.tap_stream_id == ["admins"]
        assert exclude_rule.breadcrumb == []
        assert exclude_rule.key == "selected"
        assert exclude_rule.value is False
        assert exclude_rule.negated is False

    def test_select_vs_select_filter_behavior_difference(self) -> None:
        """Test that select treats stream-only patterns as stream.* while select_filter works at stream level."""  # noqa: E501
        # select with stream-only pattern creates stream + property rules
        select_rules = select_metadata_rules(["users"])
        assert len(select_rules) == 2
        stream_rule = next(r for r in select_rules if r.breadcrumb == [])
        prop_rule = next(r for r in select_rules if r.breadcrumb != [])

        assert stream_rule.tap_stream_id == "users"
        assert stream_rule.breadcrumb == []
        assert prop_rule.tap_stream_id == "users"
        assert prop_rule.breadcrumb == ["properties", "*"]

        # select_filter with stream-only pattern creates only stream-level rules
        filter_rules = select_filter_metadata_rules(["users"])
        assert len(filter_rules) == 1
        filter_rule = filter_rules[0]

        assert filter_rule.tap_stream_id == ["users"]
        assert filter_rule.breadcrumb == []
        assert filter_rule.negated is True  # This is an inclusion rule

    def test_select_filter_preserves_existing_property_selections(self) -> None:
        """Test that select_filter operates at stream level and preserves property selections made by select."""  # noqa: E501
        # This conceptual test shows the intended behavior:
        # 1. select: ["users.name", "users.email", "orders.*"] selects properties  # noqa: E501
        # 2. select_filter: ["users"] then filters to only include the users stream
        # 3. Result should be users stream with only name,email properties (select chose)  # noqa: E501

        # This is demonstrated in the existing test_apply_catalog_rules_select_filter
        # where _select: ["one.one", "three.three", "five.*"] sets property selections
        # and _select_filter: ["three"] filters to only the three stream
        # resulting in {"three": {"one", "three"}} - preserving original selection  # noqa: E501

        # The behavior is already tested in test_tap.py, this test documents the intent
        select_rules = select_metadata_rules(["users.name", "users.email"])
        filter_rules = select_filter_metadata_rules(["users"])

        # select creates specific property selections
        assert len(select_rules) == 4  # 2 stream rules + 2 property rules

        # select_filter creates stream-level filtering only
        assert len(filter_rules) == 1
        assert filter_rules[0].breadcrumb == []  # Stream level only

    def test_nested_property_selection_not_affected_by_stream_only_enhancement(
        self,
    ) -> None:
        """Test that nested property selections work correctly and aren't affected by stream-only enhancement."""  # noqa: E501
        # Test various depths of nested property selection
        patterns = [
            "users.address",  # Single-level nesting
            "users.address.city",  # Two-level nesting
            "users.address.geo.lat",  # Three-level nesting
            "orders.items.product.sku",  # Three-level nesting in different stream
        ]

        rules = select_metadata_rules(patterns)

        # Verify the correct number of rules (2 per pattern: stream + property)
        # 4 patterns x 2 rules each + 5 parent properties
        assert len(rules) == 13

        # Check that nested selections create proper breadcrumbs
        # For users.address (single-level)
        address_rules = [
            r for r in rules if r.tap_stream_id == "users" and "address" in r.breadcrumb
        ]

        # One for each nested pattern with users.address + one for each parent property
        # implicitly selected
        assert len(address_rules) == 6

        # Verify breadcrumb for users.address
        simple_address = [
            r for r in address_rules if r.breadcrumb == ["properties", "address"]
        ]

        # Selected three times:
        # - explicitly
        # - implicitly as a parent of users.address.city
        # - implicitly as a parent of users.address.geo.lat
        assert len(simple_address) == 3
        assert simple_address[0].key == "selected"
        assert simple_address[0].value is True

        # Verify breadcrumb for users.address.city (two-level)
        city_rule = [
            r
            for r in address_rules
            if r.breadcrumb == ["properties", "address", "properties", "city"]
        ]
        assert len(city_rule) == 1
        assert city_rule[0].key == "selected"
        assert city_rule[0].value is True

        # Verify breadcrumb for users.address.geo.lat (three-level)
        lat_rule = [
            r
            for r in rules
            if r.breadcrumb
            == ["properties", "address", "properties", "geo", "properties", "lat"]
        ]
        assert len(lat_rule) == 1
        assert lat_rule[0].tap_stream_id == "users"
        assert lat_rule[0].key == "selected"
        assert lat_rule[0].value is True

        # Verify orders.items.product.sku (three-level in different stream)
        sku_rule = [
            r
            for r in rules
            if r.breadcrumb
            == ["properties", "items", "properties", "product", "properties", "sku"]
        ]
        assert len(sku_rule) == 1
        assert sku_rule[0].tap_stream_id == "orders"
        assert sku_rule[0].key == "selected"
        assert sku_rule[0].value is True

        # Important: Verify that NONE of these created wildcard rules
        # (they should NOT behave like stream.* patterns)
        wildcard_rules = [r for r in rules if "*" in str(r.breadcrumb)]
        assert len(wildcard_rules) == 0, (
            "Nested property patterns should not create wildcard rules"
        )


class TestSelectionType:
    def test_selection_type_addition(self) -> None:
        st = SelectionType
        assert st.EXCLUDED + st.EXCLUDED == st.EXCLUDED
        assert st.SELECTED + st.EXCLUDED == st.EXCLUDED
        assert st.AUTOMATIC + st.EXCLUDED == st.EXCLUDED
        assert st.SELECTED + st.AUTOMATIC == st.AUTOMATIC
        assert st.SELECTED + st.SELECTED == st.SELECTED
        assert st.UNSUPPORTED + st.UNSUPPORTED == st.UNSUPPORTED

    def test_selection_type_repr(self) -> None:
        assert f"{SelectionType.EXCLUDED}" == "excluded"
        assert f"{SelectionType.AUTOMATIC}" == "automatic"
        assert f"{SelectionType.SELECTED}" == "selected"

    def test_selection_type_addition_not_implemented(self) -> None:
        with pytest.raises(TypeError, match="unsupported operand type"):
            SelectionType.SELECTED + "foo"


class TestMetadataExecutor:
    @pytest.fixture
    def catalog(self, request):
        return json.loads(globals()[request.param])

    @pytest.mark.parametrize(
        "catalog",
        ("CATALOG", "JSON_SCHEMA"),
        indirect=["catalog"],
    )
    def test_metadata_rules_order_matters(self, catalog) -> None:
        """Test that metadata rules are applied in order and last matching rule wins.

        This test documents the current behavior where metadata rules are processed
        sequentially and later rules override earlier ones when they match the same
        stream/property. This is based on the example from:
        https://docs.meltano.com/guide/integration/#setting-metadata

        In this test we verify that:
        1. A wildcard rule ("*") applies to all streams
        2. A more specific pattern ("*_full") overrides the wildcard when it matches
        3. The order of rules in the list determines the final value
        """
        # First test: wildcard rule followed by specific pattern
        # This mimics the example from the documentation where:
        # - "*": replication-method: INCREMENTAL (applies to all)
        # - "*_full": replication-method: FULL_TABLE (overrides for matching streams)
        executor_wildcard_first = MetadataExecutor(
            [
                # First rule: all streams get INCREMENTAL
                MetadataRule(
                    "*",
                    [],
                    "replication-method",
                    value="INCREMENTAL",
                ),
                # Second rule: streams ending in _full get FULL_TABLE (overrides)
                MetadataRule(
                    "*Name",  # Matches UniqueEntitiesName
                    [],
                    "replication-method",
                    value="FULL_TABLE",
                ),
            ],
        )

        catalog_copy = deepcopy(catalog)
        visit(catalog_copy, executor_wildcard_first)

        stream_node = next(
            s
            for s in catalog_copy["streams"]
            if s["tap_stream_id"] == "UniqueEntitiesName"
        )
        stream_metadata_node = next(
            m for m in stream_node["metadata"] if len(m["breadcrumb"]) == 0
        )

        # The second rule (*Name -> FULL_TABLE) should win
        assert stream_metadata_node["metadata"]["replication-method"] == "FULL_TABLE"

        # Second test: reverse the order - specific pattern followed by wildcard
        # This shows that order matters: the wildcard will override the specific pattern
        executor_wildcard_last = MetadataExecutor(
            [
                # First rule: streams ending in Name get FULL_TABLE
                MetadataRule(
                    "*Name",
                    [],
                    "replication-method",
                    value="FULL_TABLE",
                ),
                # Second rule: all streams get INCREMENTAL (overrides)
                MetadataRule(
                    "*",
                    [],
                    "replication-method",
                    value="INCREMENTAL",
                ),
            ],
        )

        catalog_copy2 = deepcopy(catalog)
        visit(catalog_copy2, executor_wildcard_last)

        stream_node2 = next(
            s
            for s in catalog_copy2["streams"]
            if s["tap_stream_id"] == "UniqueEntitiesName"
        )
        stream_metadata_node2 = next(
            m for m in stream_node2["metadata"] if len(m["breadcrumb"]) == 0
        )

        # The second rule (* -> INCREMENTAL) should win
        assert stream_metadata_node2["metadata"]["replication-method"] == "INCREMENTAL"

    @pytest.mark.parametrize(
        "catalog",
        ("CATALOG", "JSON_SCHEMA"),
        indirect=["catalog"],
    )
    def test_metadata_rules_order_matters_property_level(self, catalog) -> None:
        """Test that metadata rules order matters at the property level too.

        This test verifies that when multiple metadata rules match the same property,
        the last matching rule wins. This is important for cases where users want to
        set a default for all properties and then override specific ones.
        """
        # Apply rules: first mark all as available, then mark *_at as automatic
        executor_general_then_specific = MetadataExecutor(
            [
                # First: all properties of UniqueEntitiesName are available
                MetadataRule(
                    "UniqueEntitiesName",
                    ["properties", "*"],
                    "inclusion",
                    value="available",
                ),
                # Second: *_at properties are automatic (should override)
                MetadataRule(
                    "UniqueEntitiesName",
                    ["properties", "*_at"],
                    "inclusion",
                    value="automatic",
                ),
            ],
        )

        catalog_copy = deepcopy(catalog)
        visit(catalog_copy, executor_general_then_specific)

        stream_node = next(
            s
            for s in catalog_copy["streams"]
            if s["tap_stream_id"] == "UniqueEntitiesName"
        )

        # created_at should be automatic (second rule wins)
        created_at_metadata = next(
            m
            for m in stream_node["metadata"]
            if m["breadcrumb"] == ["properties", "created_at"]
        )
        assert created_at_metadata["metadata"]["inclusion"] == "automatic"

        # code should be available (only first rule matches)
        code_metadata = next(
            m
            for m in stream_node["metadata"]
            if m["breadcrumb"] == ["properties", "code"]
        )
        assert code_metadata["metadata"]["inclusion"] == "available"

        # Now reverse the order: specific pattern first, then general wildcard
        executor_specific_then_general = MetadataExecutor(
            [
                # First: *_at properties are automatic
                MetadataRule(
                    "UniqueEntitiesName",
                    ["properties", "*_at"],
                    "inclusion",
                    value="automatic",
                ),
                # Second: all properties are available (should override everything)
                MetadataRule(
                    "UniqueEntitiesName",
                    ["properties", "*"],
                    "inclusion",
                    value="available",
                ),
            ],
        )

        catalog_copy2 = deepcopy(catalog)
        visit(catalog_copy2, executor_specific_then_general)

        stream_node2 = next(
            s
            for s in catalog_copy2["streams"]
            if s["tap_stream_id"] == "UniqueEntitiesName"
        )

        # created_at should now be available (second rule overrides)
        created_at_metadata2 = next(
            m
            for m in stream_node2["metadata"]
            if m["breadcrumb"] == ["properties", "created_at"]
        )
        assert created_at_metadata2["metadata"]["inclusion"] == "available"

    @pytest.mark.parametrize(
        "catalog",
        ("CATALOG", "JSON_SCHEMA"),
        indirect=["catalog"],
    )
    def test_visit(self, catalog) -> None:
        executor = MetadataExecutor(
            [
                MetadataRule(
                    "UniqueEntitiesName",
                    [],
                    "replication-key",
                    value="created_at",
                ),
                MetadataRule(
                    "UniqueEntitiesName",
                    ["properties", "created_at"],
                    "is-replication-key",
                    value=True,
                ),
                MetadataRule(
                    "UniqueEntitiesName",
                    ["properties", "payload", "properties", "hash"],
                    "custom-metadata",
                    value="custom-value",
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
    @pytest.fixture
    def catalog(self, request):
        return json.loads(globals()[request.param])

    @pytest.mark.parametrize(
        "catalog",
        ("CATALOG", "JSON_SCHEMA", "EMPTY_STREAM_SCHEMA"),
        indirect=["catalog"],
    )
    def test_visit(self, catalog) -> None:
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
            assert properties_node["created_at"] == {
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
    @pytest.fixture
    def catalog(self):
        return json.loads(CATALOG)

    def test_visit(self, catalog) -> None:
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


class TestSelectPattern:
    def test_parse(self) -> None:
        parse = SelectPattern.parse
        assert parse("users") == SelectPattern(
            stream_pattern="users",
            property_pattern=None,
            negated=False,
            raw="users",
        )
        assert parse("users.id") == SelectPattern(
            stream_pattern="users",
            property_pattern="id",
            negated=False,
            raw="users.id",
        )
        assert parse("users.*") == SelectPattern(
            stream_pattern="users",
            property_pattern="*",
            negated=False,
            raw="users.*",
        )
        assert parse("!users") == SelectPattern(
            stream_pattern="users",
            property_pattern=None,
            negated=True,
            raw="!users",
        )
        assert parse("!users.*") == SelectPattern(
            stream_pattern="users",
            property_pattern="*",
            negated=True,
            raw="!users.*",
        )
        assert parse("!users.id") == SelectPattern(
            stream_pattern="users",
            property_pattern="id",
            negated=True,
            raw="!users.id",
        )


class TestMetadataRule:
    @pytest.mark.parametrize(
        ("patterns", "targets"),
        (
            pytest.param(
                ("my_stream.*",),
                [
                    ("my_stream", None),
                    ("my_stream", bc(["prop"])),
                ],
                id="select all properties of a stream",
            ),
            pytest.param(
                ("my_stream",),
                [
                    ("my_stream", None),
                    ("my_stream", bc(["prop"])),
                ],
                id="selecting a stream implies selecting all properties",
            ),
            pytest.param(
                ("my\\.stream.*",),
                [
                    ("my.stream", None),
                    ("my.stream", bc(["prop"])),
                ],
                id="escape stream with a dot",
            ),
            pytest.param(
                ("my_stream.prop.*",),
                [
                    ("my_stream", None),
                    ("my_stream", bc(["prop", "sub_prop"])),
                ],
                id="select all sub-properties of a property",
            ),
            pytest.param(
                ("my_stream.prop.sub_prop",),
                [
                    ("my_stream", None),
                    ("my_stream", bc(["prop", "sub_prop"])),
                ],
                id="select one sub-property of a property",
            ),
            pytest.param(
                ("my_stream.prop.sub_prop",),
                [
                    ("my_stream", None),
                    ("my_stream", bc(["prop"])),
                    ("my_stream", bc(["prop", "sub_prop"])),
                ],
                id="auto-select parent property when selecting one sub-property",
            ),
            pytest.param(
                ("my_stream.prop.sub_prop1",),
                [
                    ("my_stream", None),
                    ("my_stream", bc(["prop"])),
                    ("my_stream", bc(["prop", "sub_prop1"])),
                    ("my_stream", bc(["prop", "sub_prop2"])),
                ],
                id="selecting sub-properties does not imply selecting siblings",
                marks=(
                    pytest.mark.xfail(
                        reason=(
                            "Selecting sub-properties does not imply selecting siblings"
                        ),
                        strict=True,
                    ),
                ),
            ),
            pytest.param(
                ("my_stream.prop.*",),
                [
                    ("my_stream", None),
                    ("my_stream", bc(["prop"])),
                    ("my_stream", bc(["prop", "sub_prop"])),
                ],
                id="auto-select parent property when selecting sub-properties",
            ),
            pytest.param(
                ("my_stream.prop.*.*",),
                [
                    ("my_stream", None),
                    ("my_stream", bc(["prop"])),
                    ("my_stream", bc(["prop", "sub_prop"])),
                    ("my_stream", bc(["prop", "sub_prop", "sub_sub_prop"])),
                ],
                id="auto-select parent property when selecting all sub-properties",
            ),
        ),
    )
    def test_select_metadata_rules_matches(
        self,
        patterns: tuple[str],
        targets: list[tuple[str, list[str] | None]],
    ) -> None:
        rules = select_metadata_rules(patterns)
        assert all(rule.key == SELECTED_KEY and rule.value is True for rule in rules)
        assert all(
            any(rule.match(stream, breadcrumb) for rule in rules)
            for stream, breadcrumb in targets
        )

    @pytest.mark.parametrize(
        ("patterns", "matches"),
        (
            pytest.param(
                # Equivalent to excluding all streams other than `my_stream`
                ("my_stream",),
                [
                    ("my_stream", None, False),
                    ("other_stream", None, True),
                ],
                id="select one stream",
            ),
            pytest.param(
                # Equivalent to excluding all streams other than `stream_1` and
                # `stream_2`
                ("stream_1", "stream_2"),
                [
                    ("stream_1", None, False),
                    ("stream_2", None, False),
                    ("other_stream", None, True),
                ],
                id="select two stream",
            ),
            pytest.param(
                # Equivalent to excluding `my_stream`
                ("!my_stream",),
                [
                    ("my_stream", None, True),
                    ("other_stream", None, False),
                ],
                id="exclude one stream",
            ),
        ),
    )
    def test_select_filter_metadata_rules_matches(
        self,
        patterns: tuple[str],
        matches: list[tuple[str, list[str] | None, bool]],
    ) -> None:
        rules = select_filter_metadata_rules(patterns)
        assert all(rule.key == SELECTED_KEY and rule.value is False for rule in rules)
        assert all(
            rule.match(stream, breadcrumb) is match
            for rule in rules
            for stream, breadcrumb, match in matches
        )
