"""Utilities to extract information from jsonschema files."""

from __future__ import annotations

import typing as t
from contextlib import suppress

if t.TYPE_CHECKING:
    from collections.abc import Generator


def meltano_config_env_locations(
    manifest_schema: dict[str, t.Any],
    env_definition_ref: str = "#/$defs/env",
) -> set[str]:
    """Find all locations within a Meltano manifest file that can have an env field.

    Args:
        manifest_schema: The jsonschema for Meltano manifests.
        env_definition_ref: The jsonschema ref that defines what is being searched for.

    Returns:
        The locations within a Meltano manifest file that can have an env
        field, as jq filter strings.
    """
    return set(JsonschemaRefLocationParser(manifest_schema, env_definition_ref).parse())


class JsonschemaRefLocationParser:
    """Minimal jsonschema parser that finds the locations of a specified ref."""

    def __init__(self, schema: dict[str, t.Any], target_ref: str) -> None:
        """Initialize the `JsonschemaRefLocationParser`.

        Args:
            schema: The schema being parsed.
            target_ref: The ref being searched for within the given schema.
        """
        self.root_schema = schema
        self.target_ref = target_ref
        self._resolved_refs: dict[str, t.Any] = {}

    def parse(
        self,
        schema: dict[str, t.Any] | None = None,
        path: tuple[str, ...] = (),
    ) -> Generator[str, None, None]:
        """Parse the jsonschema to find the locations of the target ref.

        Args:
            schema: The jsonschema to parse. Defaults to the root schema.
            path: The path taken to arrive at the provided schema. Each element
                is a jq filter that can be applied to each previous element up
                to the root of the root schema.

        Yields:
            The path argument concatenated, which is a location of the target
            ref specified as jq filters.
        """
        if schema is None:
            schema = self.root_schema

        if "$ref" in schema:
            if schema["$ref"] == self.target_ref:
                yield "".join(path)
            else:
                yield from self.parse(self.resolve_ref(schema["$ref"], path), path)
        elif "type" in schema:
            if schema["type"] == "object":
                if "properties" in schema:
                    for name, prop in schema["properties"].items():
                        yield from self.parse(prop, (*path, f".{name}"))
                elif "allOf" in schema:
                    for shard in schema["allOf"]:
                        yield from self.parse(shard, path)
            elif schema["type"] == "array" and "items" in schema:
                yield from self.parse(schema["items"], (*path, "[]"))

    def resolve_ref(self, ref: str, path: tuple[str, ...]) -> dict[str, t.Any]:
        """Resolve a local jsonschema ref into a schema.

        Args:
            ref: The jsonschema reference to resolve.
            path: The path taken to arrive at the ref being resolved. Each
                element is a jq filter that can be applied to each previous
                element up to the root of the root schema.

        Raises:
            ValueError: Attempted to resolve a non-local reference.
            RecursionError: Attempted to resolve a recursive reference.
            KeyError: A component of the path in the ref was not found.

        Returns:
            The jsonschema the provided ref refers to.
        """
        with suppress(KeyError):
            return self._resolved_refs[ref]

        location_as_ref = self.path_to_ref(path)
        if location_as_ref.startswith(ref):
            raise RecursionError(  # noqa: TRY003
                "Cannot resolve recursive jsonschema "  # noqa: EM102
                f"ref {ref!r} at {location_as_ref!r}",
            )

        current_schema = self.root_schema
        parts = ref.split("/")

        if parts[0] != "#":
            raise ValueError("Cannot resolve non-local jsonschema ref")  # noqa: EM101, TRY003

        for key in parts[1:]:
            try:
                current_schema = current_schema[key]
            except KeyError as ex:  # noqa: PERF203
                raise KeyError(  # noqa: TRY003
                    f"Unable to resolve local jsonschema ref {ref!r} at level {key!r}",  # noqa: EM102
                ) from ex
        return current_schema

    @staticmethod
    def path_to_ref(path: tuple[str, ...]) -> str:
        """Convert a sequence of jq filters into a jsonschema ref.

        Args:
            path: The sequence of jq filters that specify the location within the json.

        Returns:
            A jsonschema ref to the same location as the provided path.
        """
        return "#" + "".join(path).replace(".", "/").replace("[]", "")
