from __future__ import annotations

import importlib.resources

from meltano.core.tracking import schemas

schemas_dir = (
    importlib.resources.files("meltano.core.tracking")
    / "iglu-client-embedded"
    / "schemas"
    / "com.meltano"
)

versions_in_use = {
    x.name: x.version.split("-")
    for x in vars(schemas).values()
    if isinstance(x, schemas.IgluSchema)
}

versions_available = {
    schema_dir.name: max(
        x.name.split("-") for x in (schema_dir / "jsonschema").iterdir()
    )
    for schema_dir in schemas_dir.iterdir()
}


def test_using_latest_schemas() -> None:
    assert versions_in_use == versions_available
