from __future__ import annotations

from meltano.core.tracking import schemas
from meltano.core.utils.compat import importlib_resources

schemas_dir = (
    importlib_resources.files("meltano.core.tracking")
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
