"""Catalog executor classes for traversing and manipulating Singer catalog structures.

This module provides a set of classes that implement the visitor pattern for
traversing and processing Singer catalog nodes. The classes are organized into
a hierarchy, with the base `CatalogExecutor` class providing the core traversal
and dispatch functionality, and specialized executors for specific catalog
manipulation tasks (e.g., metadata, selection, schema).
"""

from __future__ import annotations

import dataclasses
import fnmatch
import re
import sys
import typing as t
from enum import Enum, auto
from functools import partial, singledispatch

import structlog

from meltano.core.behavior.visitor import visit_with

if sys.version_info >= (3, 11):
    from enum import StrEnum
    from typing import Self  # noqa: ICN003
else:
    from backports.strenum import StrEnum
    from typing_extensions import Self

if sys.version_info >= (3, 12):
    from typing import override  # noqa: ICN003
else:
    from typing_extensions import override

if t.TYPE_CHECKING:
    from collections.abc import Iterable, Sequence

logger = structlog.stdlib.get_logger(__name__)

Node: t.TypeAlias = dict[str, t.Any]


UNESCAPED_DOT = re.compile(r"(?<!\\)\.")
PROP_DELIMITER = "."
PROPERTIES_KEY = "properties"
SCHEMA_KEY = "schema"
INCLUSION_KEY = "inclusion"
SELECTED_KEY = "selected"
SELECTED_BY_DEFAULT_KEY = "selected-by-default"


class CatalogDict(t.TypedDict):
    """A catalog dictionary."""

    streams: list[dict[str, t.Any]]


class _CatalogRuleProtocol(t.Protocol):
    """A catalog rule for a stream and property."""

    tap_stream_id: str | list[str]
    breadcrumb: list[str]
    negated: bool

    @classmethod
    def matching(
        cls,
        rules: list[Self],
        tap_stream_id: str,
        breadcrumb: list[str] | None = None,
    ) -> list[Self]:
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
                PROP_DELIMITER.join(breadcrumb),
                PROP_DELIMITER.join(self.breadcrumb),
            )

        return result


@dataclasses.dataclass(slots=True)
class CatalogRule(_CatalogRuleProtocol):
    """A catalog rule for a stream and property."""

    tap_stream_id: str | list[str]
    breadcrumb: list[str] = dataclasses.field(default_factory=list)
    negated: bool = False


@dataclasses.dataclass(slots=True)
class MetadataRule(_CatalogRuleProtocol):
    """A metadata rule for a stream and property."""

    tap_stream_id: str | list[str]
    breadcrumb: list[str]
    key: str
    value: bool | str
    negated: bool = False

    @classmethod
    def select(
        cls,
        *,
        value: bool,
        stream: str | None = None,
        properties: Sequence[str] = (),
        negated: bool = False,
    ) -> MetadataRule:
        """Create a metadata rule for selecting a stream or property."""
        return cls(
            tap_stream_id=stream or [],
            breadcrumb=property_breadcrumb(properties),
            key=SELECTED_KEY,
            value=value,
            negated=negated,
        )


@dataclasses.dataclass(slots=True)
class SchemaRule(_CatalogRuleProtocol):
    """A schema rule for a stream and property."""

    tap_stream_id: str | list[str]
    breadcrumb: list[str]
    payload: dict
    negated: bool = False


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

        if UNESCAPED_DOT.search(pattern):
            stream, prop = UNESCAPED_DOT.split(pattern, maxsplit=1)
        else:
            stream = pattern
            prop = None

        return cls(
            stream_pattern=stream.replace(r"\.", PROP_DELIMITER),
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
        select = partial(MetadataRule.select, value=selected)

        rules = include_rules if selected else exclude_rules

        # Stream-only patterns should behave like stream.*
        if not prop_pattern:
            # Select the stream
            rules.append(select(stream=parsed_pattern.stream_pattern))
            # Also select all properties (like stream.*)
            rules.append(select(stream=parsed_pattern.stream_pattern, properties=["*"]))
        # Handle property patterns
        else:
            # Always select the stream for property access
            if selected or prop_pattern == "*":
                rules.append(select(stream=parsed_pattern.stream_pattern))

            props = prop_pattern.split(PROP_DELIMITER)
            rules.append(select(stream=parsed_pattern.stream_pattern, properties=props))

            # If any sub-property is selected, the parent property is selected too
            if selected:
                rules.extend(
                    select(stream=parsed_pattern.stream_pattern, properties=props[:idx])
                    for idx, prop in enumerate(props)
                    if idx > 0
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
    include_rule = MetadataRule.select(value=False, negated=True)
    # Or if it matches one of the exclusion patterns
    exclude_rule = MetadataRule.select(value=False)

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
      stream[0].properties.properties.properties.amount  → properties.amount
    """
    prop_regex = r"properties\.([^.]+)+"
    components = re.findall(prop_regex, path)
    return PROP_DELIMITER.join(components)


def property_breadcrumb(props: Iterable[str]) -> list[str]:
    """Create breadcrumb from properties path list.

    Args:
        props: List of strings representing a property breadcrumb in the JSON object.

    Returns:
        A list of strings representing a property breadcrumb in the JSON schema.

    Example:
    >>> property_breadcrumb(["payload", "content"])
    ['properties', 'payload', 'properties', 'content']
    """
    breadcrumb = []
    for prop in props:
        breadcrumb.extend([PROPERTIES_KEY, prop])

    return breadcrumb


class CatalogNode(Enum):
    """Enumeration of catalog node types encountered during traversal.

    Defines the three fundamental node types in a Singer catalog structure
    that executors can process during catalog traversal and manipulation.
    """

    STREAM = auto()
    PROPERTY = auto()
    METADATA = auto()


class SelectionType(StrEnum):
    """A valid stream or property selection type."""

    SELECTED = auto()
    EXCLUDED = auto()
    AUTOMATIC = auto()
    UNSUPPORTED = auto()

    def __bool__(self) -> bool:
        """Truth value of the selection type.

        Examples:
        >>> for selection_type in SelectionType:
        ...     if selection_type:
        ...         print(selection_type)
        selected
        automatic
        """
        return self not in {SelectionType.EXCLUDED, SelectionType.UNSUPPORTED}

    def __add__(self, other: object) -> SelectionType:
        """Combine two selection types.

        Args:
            other: Another selection type.

        Returns:
            The combined selection type.

        Examples:
        >>> SelectionType.SELECTED + SelectionType.AUTOMATIC
        <SelectionType.AUTOMATIC: 'automatic'>
        >>> SelectionType.EXCLUDED + SelectionType.UNSUPPORTED
        <SelectionType.EXCLUDED: 'excluded'>
        """
        if not isinstance(other, SelectionType):
            return NotImplemented

        if self is SelectionType.EXCLUDED or other is SelectionType.EXCLUDED:
            return SelectionType.EXCLUDED

        if self is SelectionType.AUTOMATIC or other is SelectionType.AUTOMATIC:
            return SelectionType.AUTOMATIC

        if self is SelectionType.UNSUPPORTED or other is SelectionType.UNSUPPORTED:
            return SelectionType.UNSUPPORTED

        return SelectionType.SELECTED


@singledispatch
def visit(
    node: t.Any,  # noqa: ANN401, ARG001
    executor: CatalogExecutor,  # noqa: ARG001
    path: str = "",
) -> None:
    """Visit a node in the catalog."""
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
class CatalogExecutor:
    """Base executor class for traversing and processing Singer catalog nodes.

    This class provides a visitor pattern implementation for traversing catalog
    structures and dispatching processing to specific node handlers. It serves
    as the foundation for more specialized executors that manipulate catalog
    metadata, schema properties, and selection rules.

    The executor processes three types of catalog nodes:
    - Stream nodes: Top-level catalog entries representing data streams
    - Property nodes: Schema property definitions within streams
    - Metadata nodes: Selection and inclusion metadata for streams and properties

    Subclasses should override the specific node processing methods to implement
    their custom catalog manipulation logic.
    """

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

    def __call__(self, node_type: CatalogNode, node: Node, path: str) -> None:
        """Call this instance as a function."""
        return self.execute(node_type, node, path)


class MetadataExecutor(CatalogExecutor):
    """Executor for applying metadata rules to catalog streams and properties.

    This executor processes metadata rules that control stream and property selection,
    inclusion settings, and other metadata attributes in Singer catalogs. It ensures
    proper metadata structure exists and applies rule-based transformations to
    control data extraction behavior.

    The executor automatically creates missing metadata entries with appropriate
    default inclusion settings (automatic for streams and top-level properties,
    available for nested properties).
    """

    def __init__(self, rules: list[MetadataRule]):
        """Initialize the MetadataExecutor with a list of metadata rules."""
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

    @override
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

    @override
    def property_node(
        self,
        node: Node,
        path: str,
    ) -> None:
        """Process property metadata node."""
        breadcrumb_idx = path.index(PROPERTIES_KEY)
        breadcrumb = path[breadcrumb_idx:].split(PROP_DELIMITER)

        self.ensure_metadata(breadcrumb)

    @override
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
            key == SELECTED_KEY
            and value is True
            and node.get(INCLUSION_KEY) == SelectionType.UNSUPPORTED
        ):
            return

        node[key] = value
        logger.debug("Setting '%s.%s' to '%s'", path, key, value)


class SelectExecutor(MetadataExecutor):
    """Executor for applying stream and property selection patterns to catalog metadata.

    This executor processes selection patterns (e.g., 'users', '!orders.id', 'products.*')
    and applies the corresponding metadata rules to mark streams and properties as
    selected or excluded in the catalog. It extends MetadataExecutor to handle the
    conversion of pattern-based selections into catalog metadata entries.

    Selection patterns support:
    - Stream selection: 'stream_name' selects entire streams
    - Property selection: 'stream.property' selects specific properties
    - Wildcards: 'stream.*' selects all properties in a stream
    - Exclusion: '!pattern' excludes matching streams/properties
    """  # noqa: E501

    def __init__(self, patterns: list[str]):
        """Initialize the SelectExecutor with a list of selection patterns.

        Args:
            patterns: List of selection patterns to apply to the catalog.
        """
        super().__init__(select_metadata_rules(patterns))


class SchemaExecutor(CatalogExecutor):
    """Executor for applying schema modifications to catalog property definitions.

    This executor processes schema rules that modify the JSON schema definitions
    of catalog properties. It can add, update, or replace schema properties based
    on breadcrumb patterns and payload definitions, allowing for dynamic schema
    customization during catalog processing.

    The executor ensures that property nodes exist in the catalog schema tree
    before applying modifications, creating intermediate nodes as needed. It supports
    wildcard matching in breadcrumb patterns for bulk schema operations.
    """

    def __init__(self, rules: list[SchemaRule]):
        """Initialize the SchemaExecutor with a list of schema rules.

        Args:
            rules: List of schema rules to apply to the catalog.
        """
        self._stream: Node | None = None
        self._rules = rules

    def ensure_property(self, breadcrumb: list[str]) -> None:
        """Create nodes for the breadcrumb and schema extra that matches."""
        next_node: dict[str, t.Any] = self._stream[SCHEMA_KEY]  # type: ignore[index]

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

    @override
    def stream_node(
        self,
        node: Node,
        path: str,
    ) -> None:
        """Process stream schema node."""
        self._stream = node
        tap_stream_id: str = self._stream["tap_stream_id"]
        node.setdefault(SCHEMA_KEY, {"type": "object"})

        for rule in SchemaRule.matching(self._rules, tap_stream_id):
            self.ensure_property(rule.breadcrumb)

    @override
    def property_node(self, node: Node, path: str) -> None:
        """Process property schema node."""
        tap_stream_id = self._stream["tap_stream_id"]  # type: ignore[index]

        breadcrumb_idx = path.index(PROPERTIES_KEY)
        breadcrumb = path[breadcrumb_idx:].split(PROP_DELIMITER)

        for rule in SchemaRule.matching(self._rules, tap_stream_id, breadcrumb):
            self.set_payload(node, path, rule.payload)

    def set_payload(self, node: Node, path: str, payload: dict) -> None:
        """Set node payload from a clean mapping."""
        node.clear()
        node.update(payload)
        logger.debug("Setting '%s' to %r", path, payload)


class ListExecutor(CatalogExecutor):
    """Executor for cataloging available streams and properties in a catalog.

    This executor traverses the catalog structure to build a comprehensive
    inventory of all available streams and their properties. It creates a
    mapping of stream names to sets of property paths, providing visibility
    into the complete catalog structure without regard to selection status.

    Useful for discovery operations and catalog introspection tasks.
    """

    def __init__(self) -> None:
        """Initialize the ListExecutor."""
        # properties per stream
        self.properties: dict[str, set[str]] = {}

        super().__init__()

    @override
    def stream_node(
        self,
        node: Node,
        path: str,
    ) -> None:
        """Initialize empty property set stream."""
        stream = node["tap_stream_id"]
        if stream not in self.properties:
            self.properties[stream] = set()

    @override
    def property_node(
        self,
        node: Node,
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


class ListSelectedExecutor(CatalogExecutor):
    """Executor for identifying selected streams and properties in a catalog.

    This executor analyzes catalog metadata to determine which streams and
    properties are currently selected for extraction. It processes selection
    and inclusion metadata to build collections of selected nodes, distinguishing
    between different selection types (selected, automatic, excluded, unsupported).

    The executor maintains separate collections for streams and properties,
    allowing consumers to query the current selection state and filter
    catalogs based on selection criteria.
    """

    def __init__(self) -> None:
        """Initialize the ListSelectedExecutor."""
        self.streams: set[SelectedNode] = set()
        self.properties: dict[str, set[SelectedNode]] = {}
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

        if metadata.get(INCLUSION_KEY) == SelectionType.AUTOMATIC:
            return SelectionType.AUTOMATIC
        if metadata.get(INCLUSION_KEY) == SelectionType.UNSUPPORTED:
            return SelectionType.UNSUPPORTED
        if metadata.get(SELECTED_KEY) is True or (
            metadata.get(SELECTED_KEY) is None
            and metadata.get(SELECTED_BY_DEFAULT_KEY, False)
        ):
            return SelectionType.SELECTED
        return SelectionType.EXCLUDED

    @override
    def stream_node(
        self,
        node: Node,
        path: str,
    ) -> None:
        """Initialize empty set for selected nodes in stream."""
        self._stream: str = node["tap_stream_id"]
        self.properties[self._stream] = set()

    @override
    def stream_metadata_node(
        self,
        node: Node,
        path: str,
    ) -> None:
        """Add stream selection to tap's collection."""
        selection = SelectedNode(self._stream, self.node_selection(node))
        self.streams.add(selection)

    @override
    def property_metadata_node(
        self,
        node: Node,
        path: str,
    ) -> None:
        """Add property selection to stream's collection."""
        property_path = PROP_DELIMITER.join(node["breadcrumb"])
        prop = path_property(property_path)
        selection = SelectedNode(prop, self.node_selection(node))

        self.properties[self._stream].add(selection)
