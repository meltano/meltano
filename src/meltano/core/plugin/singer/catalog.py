import fnmatch
import logging
import re
from collections import OrderedDict, namedtuple
from enum import Enum, auto
from functools import singledispatch
from typing import List

from meltano.core.behavior.visitor import visit_with


class CatalogRule:
    def __init__(self, tap_stream_id, breadcrumb=[], negated=False):
        self.tap_stream_id = tap_stream_id
        self.breadcrumb = breadcrumb
        self.negated = negated

    @classmethod
    def matching(cls, rules, tap_stream_id, breadcrumb=None):
        return [rule for rule in rules if rule.match(tap_stream_id, breadcrumb)]

    def match(self, tap_stream_id, breadcrumb=None):
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
                ".".join(breadcrumb), ".".join(self.breadcrumb)
            )

        return result


class MetadataRule(CatalogRule):
    def __init__(self, tap_stream_id, breadcrumb, key, value, negated=False):
        super().__init__(tap_stream_id, breadcrumb, negated=negated)
        self.key = key
        self.value = value


class SchemaRule(CatalogRule):
    def __init__(self, tap_stream_id, breadcrumb, payload, negated=False):
        super().__init__(tap_stream_id, breadcrumb, negated=negated)
        self.payload = payload


SelectPattern = namedtuple(
    "SelectPattern", ("stream_pattern", "property_pattern", "negated", "raw")
)


def select_metadata_rules(patterns):
    include_rules = []
    exclude_rules = []

    for pattern in patterns:
        pattern = parse_select_pattern(pattern)

        prop_pattern = pattern.property_pattern
        selected = not pattern.negated

        rules = include_rules if selected else exclude_rules

        if selected or not prop_pattern or prop_pattern == "*":
            rules.append(
                MetadataRule(
                    tap_stream_id=pattern.stream_pattern,
                    breadcrumb=[],
                    key="selected",
                    value=selected,
                )
            )

        if prop_pattern:
            props = prop_pattern.split(".")

            rules.append(
                MetadataRule(
                    tap_stream_id=pattern.stream_pattern,
                    breadcrumb=property_breadcrumb(props),
                    key="selected",
                    value=selected,
                )
            )

    return include_rules + exclude_rules


def select_filter_metadata_rules(patterns):
    # We set `selected: false` if the `tap_stream_id`
    # does NOT match any of the selection/inclusion patterns
    include_rule = MetadataRule(
        negated=True, tap_stream_id=[], breadcrumb=[], key="selected", value=False
    )
    # Or if it matches one of the exclusion patterns
    exclude_rule = MetadataRule(
        tap_stream_id=[], breadcrumb=[], key="selected", value=False
    )

    for pattern in patterns:
        pattern = parse_select_pattern(pattern)

        rule = exclude_rule if pattern.negated else include_rule
        rule.tap_stream_id.append(pattern.stream_pattern)

    rules = []
    if include_rule.tap_stream_id:
        rules.append(include_rule)
    if exclude_rule.tap_stream_id:
        rules.append(exclude_rule)

    return rules


def parse_select_pattern(pattern: str):
    raw = pattern

    negated = False
    if pattern.startswith("!"):
        negated = True
        pattern = pattern[1:]

    if "." in pattern:
        stream, prop = pattern.split(".", maxsplit=1)
    else:
        stream = pattern
        prop = None

    return SelectPattern(
        stream_pattern=stream, property_pattern=prop, negated=negated, raw=raw
    )


def path_property(path: str):
    """
    Extract the property name from a materialized path.

    As we traverse the catalog tree, we build a materialized path
    to keep track of the parent nodes.

    Examples:

      stream[0].properties.list_items.properties.account → list_items.account
      stream[0].properties.name                          → name
    """
    prop_regex = r"properties\.([\w\[\]\d]+)+"
    components = re.findall(prop_regex, path)
    return ".".join(components)


def property_breadcrumb(props):
    if len(props) >= 2 and props[0] == "properties":
        breadcrumb = props
    else:
        breadcrumb = []
        for prop in props:
            breadcrumb.extend(["properties", prop])

    return breadcrumb


class CatalogNode(Enum):
    STREAM = auto()
    PROPERTY = auto()
    METADATA = auto()


class SelectionType(str, Enum):
    SELECTED = "selected"
    EXCLUDED = "excluded"
    AUTOMATIC = "automatic"

    def __bool__(self):
        return self is not self.__class__.EXCLUDED

    def __add__(self, other):
        if self is SelectionType.EXCLUDED or other is SelectionType.EXCLUDED:
            return SelectionType.EXCLUDED

        if self is SelectionType.AUTOMATIC or other is SelectionType.AUTOMATIC:
            return SelectionType.AUTOMATIC

        return SelectionType.SELECTED


@singledispatch
def visit(node, executor, path: str = ""):
    logging.debug(f"Skipping node at '{path}'")


@visit.register(dict)
def _(node: dict, executor, path=""):
    node_type = None

    if re.search(r"streams\[\d+\]$", path):
        node_type = CatalogNode.STREAM

    if re.search(r"schema(\.properties\.\w*)+$", path):
        node_type = CatalogNode.PROPERTY

    if re.search(r"metadata\[\d+\]$", path) and "breadcrumb" in node:
        node_type = CatalogNode.METADATA

    if node_type:
        logging.debug(f"Visiting {node_type} at '{path}'.")
        executor(node_type, node, path)

    for child_path, child_node in node.items():
        if node_type is CatalogNode.PROPERTY and child_path in ["anyOf", "type"]:
            continue

        # TODO mbergeron: refactor this to use a dynamic visitor per CatalogNode
        executor.visit(child_node, path=f"{path}.{child_path}")


@visit.register(list)
def _(node: list, executor, path=""):
    for index, child_node in enumerate(node):
        executor.visit(child_node, path=f"{path}[{index}]")


@visit_with(visit)
class CatalogExecutor:
    def execute(self, node_type: CatalogNode, node, path):
        dispatch = {
            CatalogNode.STREAM: self.stream_node,
            CatalogNode.PROPERTY: self.property_node,
            CatalogNode.METADATA: self.metadata_node,
        }

        try:
            dispatch[node_type](node, path)
        except KeyError:
            logging.debug(f"Unknown node type '{node_type}'.")

    def stream_node(self, node, path: str):
        pass

    def property_node(self, node, path: str):
        pass

    def metadata_node(self, node, path: str):
        if len(node["breadcrumb"]) == 0:
            self.stream_metadata_node(node, path)
        else:
            self.property_metadata_node(node, path)

    def stream_metadata_node(self, node, path: str):
        pass

    def property_metadata_node(self, node, path: str):
        pass

    def __call__(self, node_type, node, path):
        return self.execute(node_type, node, path)


class MetadataExecutor(CatalogExecutor):
    def __init__(self, rules: List[MetadataRule]):
        self._stream = None
        self._rules = rules

    def ensure_metadata(self, breadcrumb):
        metadata_list = self._stream["metadata"]
        try:
            next(
                metadata
                for metadata in metadata_list
                if metadata["breadcrumb"] == breadcrumb
            )
        except StopIteration:
            # This is to support legacy catalogs
            metadata_list.append(
                {"breadcrumb": breadcrumb, "metadata": {"inclusion": "automatic"}}
            )

    def stream_node(self, node, path):
        self._stream = node
        tap_stream_id = self._stream["tap_stream_id"]

        if not "metadata" in node:
            node["metadata"] = []

        self.ensure_metadata([])

        for rule in MetadataRule.matching(self._rules, tap_stream_id, []):
            # Legacy catalogs have underscorized keys on the streams themselves
            self.set_metadata(node, path, rule.key.replace("-", "_"), rule.value)

    def property_node(self, node, path):
        breadcrumb_idx = path.index("properties")
        breadcrumb = path[breadcrumb_idx:].split(".")

        self.ensure_metadata(breadcrumb)

    def metadata_node(self, node, path):
        tap_stream_id = self._stream["tap_stream_id"]
        breadcrumb = node["breadcrumb"]

        logging.debug(
            f"Visiting metadata node for tap_stream_id '{tap_stream_id}', breadcrumb '{breadcrumb}'"
        )

        for rule in MetadataRule.matching(self._rules, tap_stream_id, breadcrumb):
            self.set_metadata(
                node["metadata"], f"{path}.metadata", rule.key, rule.value
            )

    def set_metadata(self, node, path, key, value):
        # Unsupported fields cannot be selected
        if (
            key == "selected"
            and value == True
            and node.get("inclusion") == "unsupported"
        ):
            return

        node[key] = value
        logging.debug(f"Setting '{path}.{key}' to '{value}'")


class SelectExecutor(MetadataExecutor):
    def __init__(self, patterns: List[str]):
        super().__init__(select_metadata_rules(patterns))


class SchemaExecutor(CatalogExecutor):
    def __init__(self, rules: List[SchemaRule]):
        self._stream = None
        self._rules = rules

    def ensure_property(self, breadcrumb):
        next_node = self._stream["schema"]

        for idx, key in enumerate(breadcrumb):
            # If the key contains shell-style wildcards,
            # ensure property nodes exist for matching breadcrumbs.
            if re.match(r"[*?\[\]]", key):
                node_keys = next_node.keys()
                matching_keys = fnmatch.filter(node_keys, key)

                if matching_keys:
                    matching_breadcrumb = breadcrumb.copy()
                    for key in matching_keys:
                        matching_breadcrumb[idx] = key
                        self.ensure_property(matching_breadcrumb)

                break

            # If a property node for this breadcrumb doesn't exist yet, create it.
            if not key in next_node:
                next_node[key] = {}

            next_node = next_node[key]

    def stream_node(self, node, path):
        self._stream = node
        tap_stream_id = self._stream["tap_stream_id"]

        if not "schema" in node:
            node["schema"] = {"type": "object"}

        for rule in SchemaRule.matching(self._rules, tap_stream_id):
            self.ensure_property(rule.breadcrumb)

    def property_node(self, node, path):
        tap_stream_id = self._stream["tap_stream_id"]

        breadcrumb_idx = path.index("properties")
        breadcrumb = path[breadcrumb_idx:].split(".")

        for rule in SchemaRule.matching(self._rules, tap_stream_id, breadcrumb):
            self.set_payload(node, path, rule.payload)

    def set_payload(self, node, path, payload):
        node.clear()
        node.update(payload)
        logging.debug(f"Setting '{path}' to {payload!r}")


class ListExecutor(CatalogExecutor):
    def __init__(self):
        # properties per stream
        self.properties = OrderedDict()

        super().__init__()

    def stream_node(self, node, path):
        stream = node["tap_stream_id"]
        if stream not in self.properties:
            self.properties[stream] = set()

    def property_node(self, node, path):
        prop = path_property(path)
        # current stream
        stream = next(reversed(self.properties))
        self.properties[stream].add(prop)


class ListSelectedExecutor(CatalogExecutor):
    SelectedNode = namedtuple("SelectedNode", ("key", "selection"))

    def __init__(self):
        self.streams = set()
        self.properties = OrderedDict()
        super().__init__()

    @property
    def selected_properties(self):
        # we don't want to mutate the visitor result
        selected = self.properties.copy()

        # remove all non-selected streams
        for stream in (name for name, selected in self.streams if not selected):
            del selected[stream]

        # remove all non-selected properties
        for stream, props in selected.items():
            selected[stream] = {name for name, selected in props if selected}

        return selected

    def node_selection(self, node):
        try:
            metadata = node["metadata"]
            if metadata.get("inclusion") == "automatic":
                return SelectionType.AUTOMATIC

            if metadata.get("selected", False):
                return SelectionType.SELECTED

            return SelectionType.EXCLUDED
        except KeyError:
            return False

    def stream_node(self, node, path):
        self._stream = node["tap_stream_id"]
        self.properties[self._stream] = set()

    def stream_metadata_node(self, node, path):
        selection = self.SelectedNode(self._stream, self.node_selection(node))
        self.streams.add(selection)

    def property_metadata_node(self, node, path):
        property_path = ".".join(node["breadcrumb"])
        prop = path_property(property_path)
        selection = self.SelectedNode(prop, self.node_selection(node))

        self.properties[self._stream].add(selection)
