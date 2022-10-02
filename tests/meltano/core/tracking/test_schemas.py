from __future__ import annotations

from pathlib import Path

from meltano.core.tracking import schemas

schemas_dir = (
    Path(__file__).parents[4]
    / "src"
    / "meltano"
    / "core"
    / "tracking"
    / "iglu-client-embedded"
    / "schemas"
    / "com.meltano"
)

versions_in_use = {
    x.name: x.version.split("-")
    for x in vars(schemas).values()  # noqa: WPS421
    if isinstance(x, schemas.IgluSchema)
}

versions_available = {
    schema_dir.stem: max(
        x.stem.split("-") for x in (schema_dir / "jsonschema").iterdir()
    )
    for schema_dir in schemas_dir.iterdir()
}


def test_using_latest_schemas():
    assert versions_in_use == versions_available
