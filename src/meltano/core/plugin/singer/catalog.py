from __future__ import annotations  # noqa: D100

import fnmatch
import re
import sys
import typing as t
from collections import OrderedDict
from enum import Enum, auto
from functools import singledispatch

import structlog

from meltano.core.behavior.visitor import visit_with

if sys.version_info < (3, 11):
    from backports.strenum import StrEnum
else:
    from enum import StrEnum

if t.TYPE_CHECKING:
    from collections.abc import Iterable

logger = structlog.stdlib.get_logger(__name__)

Node = dict[str, t.Any]
T = t.TypeVar("T", bound="CatalogRule")


UNESCAPED_DOT = re.compile(r"(?<!\\)\.")


class CatalogDict(t.TypedDict):
    """A catalog dictionary."""

    streams: list[dict[str, t.Any]]


class CatalogRule:  # noqa: D101
    def __init__(
        self,
        tap_stream_id: str | list[str],
        breadcrumb: list[str] | None = None,
        *,
        negated: bool = False,
    ):
        """Create a catalog rule for a stream and property."""
        self.tap_stream_id = tap_stream_id
        self.breadcrumb = breadcrumb or []
        self.negated = negated

    @classmethod
    def matching(
        cls: type[T],
        rules: list[T],
        tap_stream_id: str,
        breadcrumb: list[str] | None = None,
    ) -> list[T]:
        """Filter rules that match a given breadcrumb."""
        return [rule for rule in rules if rule.match(tap_stream_id, breadcrumb)]

    def match(self, tap_stream_id: str, breadcrumb: list[str] | None = None) -> bool:
        """Evaluate if rule matches a stream or breadcrumb.

        Args:
            tap_stream_id: Singer stream identifier.
            breadcrumb: JSON property breadcrumb.

        Returns:
            Whether the stream ID or breadcrumb matches the rules.
        """
        patterns = (
            self.tap_stream_id
            if isinstance(self.tap_stream_id, list)
            else [self.tap_stream_id]
        )

        result = any(fnmatch.fnmatch(tap_stream_id, pattern) for pattern in patterns)

        # A negated rule matches a stream ID when none of the patterns match
        if self.negated:
            result = not result

        # If provided, the breadcrumb should still match, even on negated rules
        if breadcrumb is not None:
            result = result and fnmatch.fnmatch(
                ".".join(breadcrumb),
                ".".join(self.breadcrumb),
            )

        return result


class MetadataRule(CatalogRule):  # noqa: D101
    def __init__(
        self,
        tap_stream_id: str | list[str],
        breadcrumb: list[str] | None,
        key: str,
        *,
        value: bool,
        negated: bool = False,
    ):
        """Create a metadata rule for a stream and property."""
        super().__init__(tap_stream_id, breadcrumb, negated=negated)
        self.key = key
        self.value = value


class SchemaRule(CatalogRule):  # noqa: D101
    def __init__(
        self,
        tap_stream_id: str | list[str],
        breadcrumb: list[str] | None,
        payload: dict,
        *,
        negated: bool = False,
    ):
        """Create a schema rule for a stream and property."""
        super().__init__(tap_stream_id, breadcrumb, negated=negated)
        self.payload = payload


class SelectPattern(t.NamedTuple):
    """A pattern for selecting streams and properties."""

    stream_pattern: str
    property_pattern: str | None
    negated: bool
    raw: str

    @classmethod
    def parse(cls, pattern: str) -> SelectPattern:
        """Parse a SelectPattern instance from a string pattern.

        Args:
            pattern: Stream or property selection pattern.

        Returns:
            An appropriate `SelectPattern` instance.

        Example:
        >>> SelectPattern.parse("!a.b.c")
        SelectedPattern(
            stream_pattern='a',
            property_pattern='b.c',
            negated=True,
            raw='!a.b.c'
        )
        """
        raw = pattern

        negated = False
        if pattern.startswith("!"):
            negated = True
            pattern = pattern[1:]

        if re.search(UNESCAPED_DOT, pattern):
            stream, prop = re.split(UNESCAPED_DOT, pattern, maxsplit=1)
        else:
            stream = pattern
            prop = None

        return cls(
            stream_pattern=stream.replace(r"\.", "."),
            property_pattern=prop,
            negated=negated,
            raw=raw,
        )


def select_metadata_rules(patterns: Iterable[str]) -> list[MetadataRule]:
    """Create metadata rules from `select` patterns.

    Args:
        patterns: Iterable of `select` string patterns.

    Returns:
        A list of corresponding metadata rule objects.
    """
    include_rules: list[MetadataRule] = []
    exclude_rules: list[MetadataRule] = []

    for pattern in patterns:
        parsed_pattern = SelectPattern.parse(pattern)

        prop_pattern = parsed_pattern.property_pattern
        selected = not parsed_pattern.negated

        rules = include_rules if selected else exclude_rules

        if selected or not prop_pattern or prop_pattern == "*":
            rules.append(
                MetadataRule(
                    tap_stream_id=parsed_pattern.stream_pattern,
                    breadcrumb=[],
                    key="selected",
                    value=selected,
                ),
            )

        if prop_pattern:
            props = prop_pattern.split(".")

            rules.append(
                MetadataRule(
                    tap_stream_id=parsed_pattern.stream_pattern,
                    breadcrumb=property_breadcrumb(props),
                    key="selected",
                    value=selected,
                ),
            )

    return include_rules + exclude_rules


def select_filter_metadata_rules(patterns: Iterable[str]) -> list[MetadataRule]:
    """Create metadata rules from `select_filter` patterns.

    Args:
        patterns: Iterable of `select_filter` string patterns.

    Returns:
        A list of corresponding metadata rule objects.
    """
    # We set `selected: false` if the `tap_stream_id`
    # does NOT match any of the selection/inclusion patterns
    include_rule = MetadataRule(
        negated=True,
        tap_stream_id=[],
        breadcrumb=[],
        key="selected",
        value=False,
    )
    # Or if it matches one of the exclusion patterns
    exclude_rule = MetadataRule(
        tap_stream_id=[],
        breadcrumb=[],
        key="selected",
        value=False,
    )

    for pattern in patterns:
        parsed_pattern = SelectPattern.parse(pattern)

        rule = exclude_rule if parsed_pattern.negated else include_rule
        rule.tap_stream_id.append(parsed_pattern.stream_pattern)  # type: ignore[union-attr]

    rules = []
    if include_rule.tap_stream_id:
        rules.append(include_rule)
    if exclude_rule.tap_stream_id:
        rules.append(exclude_rule)

    return rules


def path_property(path: str) -> str:
    """Extract the property name from a materialized path.

    As we traverse the catalog tree, we build a materialized path
    to keep track of the parent nodes.

    Args:
        path: String representing a property path in the JSON schema.

    Returns:
        A string representing a property path in the JSON object.

    Examples:
      stream[0].properties.list_items.properties.account → list_items.account
      stream[0].properties.name                          → name
    """
    prop_regex = r"properties\.([^.]+)+"
    components = re.findall(prop_regex, path)
    return ".".join(components)


def property_breadcrumb(props: list[str]) -> list[str]:
    """Create breadcrumb from properties path list.

    Args:
        props: List of strings representing a property breadcrumb in the JSON object.

    Returns:
        A list of strings representing a property breadcrumb in the JSON schema.

    Example:
    >>> property_breadcrumb(["payload", "content"])
    ['properties', 'payload', 'properties', 'content']
    """
    if len(props) >= 2 and props[0] == "properties":
        breadcrumb = props
    else:
        breadcrumb = []
        for prop in props:
            breadcrumb.extend(["properties", prop])

    return breadcrumb


class CatalogNode(Enum):  # noqa: D101
    STREAM = auto()
    PROPERTY = auto()
    METADATA = auto()


class SelectionType(StrEnum):
    """A valid stream or property selection type."""

    SELECTED = auto()
    EXCLUDED = auto()
    AUTOMATIC = auto()
    UNSUPPORTED = auto()

    def __bool__(self) -> bool:  # noqa: D105
        return self not in {self.__class__.EXCLUDED, self.__class__.UNSUPPORTED}

    def __add__(self, other: SelectionType) -> SelectionType:  # type: ignore[override] # noqa: D105
        if self is SelectionType.EXCLUDED or other is SelectionType.EXCLUDED:
            return SelectionType.EXCLUDED

        if self is SelectionType.AUTOMATIC or other is SelectionType.AUTOMATIC:
            return SelectionType.AUTOMATIC

        if self is SelectionType.UNSUPPORTED or other is SelectionType.UNSUPPORTED:
            return SelectionType.UNSUPPORTED

        return SelectionType.SELECTED


@singledispatch
def visit(  # noqa: D103
    node,  # noqa: ANN001, ARG001
    executor,  # noqa: ANN001, ARG001
    path: str = "",
) -> None:
    logger.debug("Skipping node at '%s'", path)


@visit.register(dict)
def _(node: dict, executor, path: str = "") -> None:  # noqa: ANN001
    node_type = None

    if re.search(r"streams\[\d+\]$", path):
        node_type = CatalogNode.STREAM

    if re.search(r"schema(\.properties\.\w*)+$", path):
        node_type = CatalogNode.PROPERTY

    if re.search(r"metadata\[\d+\]$", path) and "breadcrumb" in node:
        node_type = CatalogNode.METADATA

    if node_type:
        logger.debug("Visiting %s at '%s'.", node_type, path)
        executor(node_type, node, path)

    for child_path, child_node in node.items():
        if node_type is CatalogNode.PROPERTY and child_path in {"anyOf", "type"}:
            continue

        # TODO mbergeron: refactor this to use a dynamic visitor per CatalogNode
        executor.visit(child_node, path=f"{path}.{child_path}")


@visit.register(list)
def _(node: list, executor, path: str = "") -> None:  # noqa: ANN001
    for index, child_node in enumerate(node):
        executor.visit(child_node, path=f"{path}[{index}]")


@visit_with(visit)
class CatalogExecutor:  # noqa: D101
    def execute(self, node_type: CatalogNode, node: Node, path: str) -> None:
        """Dispatch all node methods."""
        dispatch = {
            CatalogNode.STREAM: self.stream_node,
            CatalogNode.PROPERTY: self.property_node,
            CatalogNode.METADATA: self.metadata_node,
        }

        try:
            dispatch[node_type](node, path)
        except KeyError:  # pragma: no cover
            logger.debug("Unknown node type '%s'.", node_type)

    def stream_node(self, node: Node, path: str) -> None:
        """Process stream node."""

    def property_node(self, node: Node, path: str) -> None:
        """Process property node."""

    def metadata_node(self, node: Node, path: str) -> None:
        """Process metadata node."""
        if len(node["breadcrumb"]) == 0:
            self.stream_metadata_node(node, path)
        else:
            self.property_metadata_node(node, path)

    def stream_metadata_node(self, node: Node, path: str) -> None:
        """Process stream metadata node."""

    def property_metadata_node(self, node: Node, path: str) -> None:
        """Process property metadata node."""

    def __call__(self, node_type, node: Node, path: str):  # noqa: ANN001, ANN204
        """Call this instance as a function."""
        return self.execute(node_type, node, path)


class MetadataExecutor(CatalogExecutor):  # noqa: D101
    def __init__(self, rules: list[MetadataRule]):  # noqa: D107
        self._stream: Node | None = None
        self._rules = rules

    def ensure_metadata(self, breadcrumb: list[str]) -> None:
        """Handle missing metadata entries."""
        metadata_list: list[dict] = self._stream["metadata"]  # type: ignore[index]
        match = next(
            (
                metadata
                for metadata in metadata_list
                if metadata["breadcrumb"] == breadcrumb
            ),
            None,
        )

        # Missing inclusion metadata for property
        if match is None:
            # Streams and top-level properties.
            if len(breadcrumb) <= 2:
                entry = {
                    "breadcrumb": breadcrumb,
                    "metadata": {"inclusion": "automatic"},
                }
            # Exclude nested properties.
            else:
                entry = {
                    "breadcrumb": breadcrumb,
                    "metadata": {"inclusion": "available"},
                }

            metadata_list.append(entry)

    def stream_node(self, node: Node, path: str) -> None:
        """Process stream metadata node."""
        self._stream = node
        tap_stream_id = self._stream["tap_stream_id"]

        if "metadata" not in node:
            node["metadata"] = []

        self.ensure_metadata([])

        for rule in MetadataRule.matching(self._rules, tap_stream_id, []):
            # Legacy catalogs have underscorized keys on the streams themselves
            self.set_metadata(node, path, rule.key.replace("-", "_"), rule.value)

    def property_node(
        self,
        node: Node,  # noqa: ARG002
        path: str,
    ) -> None:
        """Process property metadata node."""
        breadcrumb_idx = path.index("properties")
        breadcrumb = path[breadcrumb_idx:].split(".")

        self.ensure_metadata(breadcrumb)

    def metadata_node(self, node: Node, path: str) -> None:
        """Process metadata node."""
        tap_stream_id = self._stream["tap_stream_id"]  # type: ignore[index]
        breadcrumb = node["breadcrumb"]

        logger.debug(
            "Visiting metadata node for tap_stream_id '%s', breadcrumb '%s'",
            tap_stream_id,
            breadcrumb,
        )

        for rule in MetadataRule.matching(self._rules, tap_stream_id, breadcrumb):
            self.set_metadata(
                node["metadata"],
                f"{path}.metadata",
                rule.key,
                rule.value,
            )

    def set_metadata(self, node: Node, path: str, key: str, value: t.Any) -> None:  # noqa: ANN401
        """Set selection and inclusion keys in a metadata node."""
        # Unsupported fields cannot be selected
        if (
            key == "selected"
            and value is True
            and node.get("inclusion") == "unsupported"
        ):
            return

        node[key] = value
        logger.debug("Setting '%s.%s' to '%s'", path, key, value)


class SelectExecutor(MetadataExecutor):  # noqa: D101
    def __init__(self, patterns: list[str]):  # noqa: D107
        super().__init__(select_metadata_rules(patterns))


class SchemaExecutor(CatalogExecutor):  # noqa: D101
    def __init__(self, rules: list[SchemaRule]):  # noqa: D107
        self._stream: Node | None = None
        self._rules = rules

    def ensure_property(self, breadcrumb: list[str]) -> None:
        """Create nodes for the breadcrumb and schema extra that matches."""
        next_node: dict[str, t.Any] = self._stream["schema"]  # type: ignore[index]

        for idx, key in enumerate(breadcrumb):
            # If the key contains shell-style wildcards,
            # ensure property nodes exist for matching breadcrumbs.
            if re.match(r"[*?\[\]]", key):
                node_keys = next_node.keys()
                if matching_keys := fnmatch.filter(node_keys, key):
                    matching_breadcrumb = breadcrumb.copy()
                    for key in matching_keys:
                        matching_breadcrumb[idx] = key
                        self.ensure_property(matching_breadcrumb)

                break

            # If a property node for this breadcrumb doesn't exist yet, create it.
            if key not in next_node:
                next_node[key] = {}

            next_node = next_node[key]

    def stream_node(
        self,
        node: Node,
        path,  # noqa: ANN001, ARG002
    ) -> None:
        """Process stream schema node."""
        self._stream = node
        tap_stream_id: str = self._stream["tap_stream_id"]

        if "schema" not in node:
            node["schema"] = {"type": "object"}

        for rule in SchemaRule.matching(self._rules, tap_stream_id):
            self.ensure_property(rule.breadcrumb)

    def property_node(self, node: Node, path: str) -> None:
        """Process property schema node."""
        tap_stream_id = self._stream["tap_stream_id"]  # type: ignore[index]

        breadcrumb_idx = path.index("properties")
        breadcrumb = path[breadcrumb_idx:].split(".")

        for rule in SchemaRule.matching(self._rules, tap_stream_id, breadcrumb):
            self.set_payload(node, path, rule.payload)

    def set_payload(self, node: Node, path: str, payload: dict) -> None:
        """Set node payload from a clean mapping."""
        node.clear()
        node.update(payload)
        logger.debug("Setting '%s' to %r", path, payload)


class ListExecutor(CatalogExecutor):  # noqa: D101
    def __init__(self) -> None:  # noqa: D107
        # properties per stream
        self.properties: dict[str, set[str]] = OrderedDict()

        super().__init__()

    def stream_node(
        self,
        node: Node,
        path: str,  # noqa: ARG002
    ) -> None:
        """Initialize empty property set stream."""
        stream = node["tap_stream_id"]
        if stream not in self.properties:
            self.properties[stream] = set()

    def property_node(
        self,
        node: Node,  # noqa: ARG002
        path: str,
    ) -> None:
        """Add property to stream collection."""
        prop = path_property(path)
        # current stream
        stream = next(reversed(self.properties))
        self.properties[stream].add(prop)


class SelectedNode(t.NamedTuple):
    """Selection type and key of a node."""

    key: str
    selection: SelectionType


class ListSelectedExecutor(CatalogExecutor):  # noqa: D101
    def __init__(self) -> None:  # noqa: D107
        self.streams: set[SelectedNode] = set()
        self.properties: dict[str, set[SelectedNode]] = OrderedDict()
        super().__init__()

    @property
    def selected_properties(self) -> dict[str, set[str]]:
        """Get selected streams and properties."""
        # we don't want to mutate the visitor result
        properties = self.properties.copy()

        # remove all non-selected streams
        for stream, selected in self.streams:
            if not selected:
                del properties[stream]

        # return with all non-selected properties removed
        return {
            stream: {prop for prop, selected in props if selected}
            for stream, props in properties.items()
        }

    @staticmethod
    def node_selection(node: Node) -> SelectionType:
        """Get selection type from metadata entry.

        Args:
            node: Catalog metadata dictionary.

        Returns:
            A proper `SelectionType` given the inclusion and selection metadata.
        """
        try:
            metadata: dict[str, t.Any] = node["metadata"]
        except KeyError:
            return SelectionType.EXCLUDED

        if metadata.get("inclusion") == "automatic":
            return SelectionType.AUTOMATIC
        if metadata.get("inclusion") == "unsupported":
            return SelectionType.UNSUPPORTED
        if metadata.get("selected") is True or (
            metadata.get("selected") is None
            and metadata.get("selected-by-default", False)
        ):
            return SelectionType.SELECTED
        return SelectionType.EXCLUDED

    def stream_node(
        self,
        node: Node,
        path: str,  # noqa: ARG002
    ) -> None:
        """Initialize empty set for selected nodes in stream."""
        self._stream: str = node["tap_stream_id"]
        self.properties[self._stream] = set()

    def stream_metadata_node(
        self,
        node: Node,
        path: str,  # noqa: ARG002
    ) -> None:
        """Add stream selection to tap's collection."""
        selection = SelectedNode(self._stream, self.node_selection(node))
        self.streams.add(selection)

    def property_metadata_node(
        self,
        node: Node,
        path: str,  # noqa: ARG002
    ) -> None:
        """Add property selection to stream's collection."""
        property_path = ".".join(node["breadcrumb"])
        prop = path_property(property_path)
        selection = SelectedNode(prop, self.node_selection(node))

        self.properties[self._stream].add(selection)
