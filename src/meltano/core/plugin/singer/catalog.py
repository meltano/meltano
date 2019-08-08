import logging
import re
from fnmatch import fnmatch
from collections import OrderedDict, namedtuple
from enum import Enum, auto
from functools import singledispatch
from typing import List

from meltano.core.behavior.visitor import visit_with


SelectPattern = namedtuple(
    "SelectPattern", ("stream_pattern", "property_pattern", "negated")
)


def parse_select_pattern(pattern: str):
    negated = False

    if pattern.startswith("!"):
        negated = True
        pattern = pattern[1:]

    stream, *_ = pattern.split(".")

    return SelectPattern(
        stream_pattern=stream, property_pattern=pattern, negated=negated
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


class CatalogNode(Enum):
    STREAM = auto()
    STREAM_METADATA = auto()
    STREAM_PROPERTY = auto()
    STREAM_PROPERTY_METADATA = auto()


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
        node_type = CatalogNode.STREAM_PROPERTY

    if re.search(r"metadata\[\d+\]$", path) and "breadcrumb" in node:
        if len(node["breadcrumb"]) == 0:
            node_type = CatalogNode.STREAM_METADATA
        else:
            node_type = CatalogNode.STREAM_PROPERTY_METADATA

    if node_type:
        logging.debug(f"Visiting {node_type} at '{path}'.")
        executor(node_type, node, path)

    for child_path, child_node in node.items():
        if node_type is CatalogNode.STREAM_PROPERTY and child_path in ["anyOf", "type"]:
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
            CatalogNode.STREAM_METADATA: self.stream_metadata_node,
            CatalogNode.STREAM_PROPERTY_METADATA: self.property_metadata_node,
            CatalogNode.STREAM_PROPERTY: self.property_node,
        }

        try:
            dispatch[node_type](node, path)
        except KeyError:
            logging.debug(f"Unknown node type '{node_type}'.")

    def stream_node(self, node, path: str):
        pass

    def property_node(self, node, path: str):
        pass

    def stream_metadata_node(self, node, path: str):
        pass

    def property_metadata_node(self, node, path: str):
        pass

    def __call__(self, node_type, node, path):
        return self.execute(node_type, node, path)


class SelectExecutor(CatalogExecutor):
    def __init__(self, patterns: List[str]):
        self._stream = None
        self._patterns = list(map(parse_select_pattern, patterns))

    @property
    def current_stream(self):
        return self._stream["tap_stream_id"]

    @classmethod
    def _match_patterns(cls, value, include=[], exclude=[]):
        included = any(fnmatch(value, pattern) for pattern in include)
        excluded = any(fnmatch(value, pattern) for pattern in exclude)

        return included and not excluded

    def update_node_selection(self, node, path: str, selected: bool):
        node["selected"] = selected
        if selected:
            logging.debug(f"{path} has been selected.")
        else:
            logging.debug(f"{path} has been deselected.")

    def stream_match_patterns(self, stream):
        return self._match_patterns(
            stream,
            include=(
                pattern.stream_pattern
                for pattern in self._patterns
                if not pattern.negated
            ),
            exclude=(
                pattern.stream_pattern
                for pattern in self._patterns
                if pattern.negated and pattern.property_pattern == "*"
            ),
        )

    def property_match_patterns(self, prop):
        return self._match_patterns(
            prop,
            include=(
                pattern.property_pattern
                for pattern in self._patterns
                if not pattern.negated
            ),
            exclude=(
                pattern.property_pattern
                for pattern in self._patterns
                if pattern.negated
            ),
        )

    def stream_node(self, node, path):
        self._stream = node
        selected = self.stream_match_patterns(self.current_stream)
        stream_metadata = {"breadcrumb": [], "metadata": {"inclusion": "automatic"}}

        try:
            metadata = next(
                metadata
                for metadata in node["metadata"]
                if len(metadata["breadcrumb"]) == 0
            )
            self.update_node_selection(metadata["metadata"], path, selected)
        except KeyError:
            node["metadata"] = [stream_metadata]
        except StopIteration:
            # This is to support legacy catalogs
            node["metadata"].insert(0, stream_metadata)

        # the node itself has a `selected` key
        self.update_node_selection(node, path, selected)

    def stream_metadata_node(self, node, path):
        metadata = node["metadata"]
        selected = self.stream_match_patterns(self.current_stream)
        self.update_node_selection(metadata, path, selected)

    def property_node(self, node, path):
        breadcrumb_idx = path.index("properties")
        breadcrumb = path[breadcrumb_idx:].split(".")

        try:
            next(
                metadata
                for metadata in self._stream["metadata"]
                if metadata["breadcrumb"] == breadcrumb
            )
        except StopIteration:
            # This is to support legacy catalogs
            self._stream["metadata"].append(
                {"breadcrumb": breadcrumb, "metadata": {"inclusion": "automatic"}}
            )

    def property_metadata_node(self, node, path):
        property_path = ".".join(node["breadcrumb"])
        prop = f"{self.current_stream}.{path_property(property_path)}"
        selected = self.property_match_patterns(prop)
        self.update_node_selection(node["metadata"], path, selected)


class ListExecutor(CatalogExecutor):
    def __init__(self, selected_only=False):
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
