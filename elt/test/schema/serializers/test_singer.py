import elt.schema.serializers.singer as serializer



def test_loads():
    singer_catalog = """
{
    "streams": [
        {
            "stream": "FieldPermissions",
            "tap_stream_id": "FieldPermissions",
            "schema": {
                "type": "object",
                "additionalProperties": false,
                "properties": {
                    "Id": {
                        "type": "string"
                    },
                    "ParentId": {
                        "type": [
                            "null",
                            "string"
                        ]
                    },
                    "SobjectType": {
                        "type": [
                            "null",
                            "string"
                        ]
                    },
                    "Field": {
                        "type": [
                            "null",
                            "string"
                        ]
                    },
                    "PermissionsEdit": {
                        "type": [
                            "null",
                            "boolean"
                        ]
                    },
                    "PermissionsRead": {
                        "type": [
                            "null",
                            "boolean"
                        ]
                    },
                    "SystemModstamp": {
                        "anyOf": [
                            {
                                "type": "string",
                                "format": "date-time"
                            },
                            {
                                "type": [
                                    "string",
                                    "null"
                                ]
                            }
                        ]
                    }
                }
            },
            "metadata": [
                {
                    "breadcrumb": [
                        "properties",
                        "Id"
                    ],
                    "metadata": {
                        "inclusion": "automatic",
                        "selected-by-default": true
                    }
                },
                {
                    "breadcrumb": [
                        "properties",
                        "ParentId"
                    ],
                    "metadata": {
                        "inclusion": "available",
                        "selected-by-default": true
                    }
                },
                {
                    "breadcrumb": [
                        "properties",
                        "SobjectType"
                    ],
                    "metadata": {
                        "inclusion": "available",
                        "selected-by-default": true
                    }
                },
                {
                    "breadcrumb": [
                        "properties",
                        "Field"
                    ],
                    "metadata": {
                        "inclusion": "available",
                        "selected-by-default": true
                    }
                },
                {
                    "breadcrumb": [
                        "properties",
                        "PermissionsEdit"
                    ],
                    "metadata": {
                        "inclusion": "available",
                        "selected-by-default": true
                    }
                },
                {
                    "breadcrumb": [
                        "properties",
                        "PermissionsRead"
                    ],
                    "metadata": {
                        "inclusion": "available",
                        "selected-by-default": true
                    }
                },
                {
                    "breadcrumb": [
                        "properties",
                        "SystemModstamp"
                    ],
                    "metadata": {
                        "inclusion": "automatic",
                        "selected-by-default": true
                    }
                },
                {
                    "breadcrumb": [],
                    "metadata": {
                        "valid-replication-keys": [
                            "SystemModstamp"
                        ],
                        "table-key-properties": [
                            "Id"
                        ]
                    }
                }
            ]
        }
    ]
}
"""

    schema = serializer.loads("singer", singer_catalog)

    assert(len(schema.tables) == 1)
    import pdb; pdb.set_trace()


def test_load():
    singer_catalog_path = "/home/gitlab/git/gitlab/bizops/meltano/properties.json"

    schema = serializer.load("singer", open(singer_catalog_path))
    assert(len(schema.tables) > 20)
    assert("Usage_Ping_Data__c" in schema.tables)

    import pdb; pdb.set_trace()
