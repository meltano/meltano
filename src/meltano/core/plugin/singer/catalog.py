import logging
import re
from fnmatch import fnmatch
from collections import OrderedDict, namedtuple
from enum import Enum, auto
from functools import singledispatch
from typing import List


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


class CatalogNode(Enum):
    STREAM = auto()
    STREAM_METADATA = auto()
    STREAM_PROPERTY = auto()
    STREAM_PROPERTY_METADATA = auto()


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

    @classmethod
    def _match_patterns(cls, value, include=[], exclude=[]):
        included = any(fnmatch(value, pattern) for pattern in include)
        excluded = any(fnmatch(value, pattern) for pattern in exclude)

        return included and not excluded

    def stream_match_patterns(self, stream):
        return self._match_patterns(
            stream,
            include=(
                pattern.stream_pattern
                for pattern in self._patterns
                if not pattern.negated
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
        self._stream = node["stream"]

        if not self.stream_match_patterns(self._stream):
            logging.debug(f"{self._stream} is not selected.")
            return

        found = any(
            metadata
            for metadata in node["metadata"]
            if len(metadata["breadcrumb"]) == 0
        )

        # This is to support legacy catalogs
        if not found:
            node["metadata"].insert(
                0,
                {
                    "breadcrumb": [],
                    "metadata": {"inclusion": "available", "selected": True},
                },
            )
            logging.debug(f"{path} has been selected.")

        node.update({"selected": True})

    def stream_metadata_node(self, node, path):
        if not self.stream_match_patterns(self._stream):
            logging.debug(f"{self._stream} is not selected.")
            return

        metadata = node["metadata"]
        metadata.update({"selected": True})
        logging.debug(f"{path} has been selected.")

    def property_metadata_node(self, node, path):
        _, name = node["breadcrumb"]
        prop = f"{self._stream}.{name}"

        if not self.property_match_patterns(prop):
            logging.debug(f"{prop} is not selected.")
            return

        metadata = node["metadata"]
        if metadata.get("inclusion") == "available":
            metadata.update({"selected": True})
            logging.debug(f"{path} has been selected.")


class ListExecutor(CatalogExecutor):
    def __init__(self, selected_only=False):
        # properties per stream
        self._selected_only = selected_only
        self.properties = OrderedDict()

        super().__init__()

    def stream_node(self, node, path):
        stream = node["stream"]
        if stream not in self.properties:
            self.properties[stream] = set()

    def property_node(self, node, path):
        *_, name = path.split(".")
        # current stream
        stream = next(reversed(self.properties))
        self.properties[stream].add(name)


class ListSelectedExecutor(CatalogExecutor):
    SelectedNode = namedtuple("SelectedNode", ("key", "selected"))

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

    def is_node_selected(self, node):
        try:
            metadata = node["metadata"]
            return metadata.get("inclusion") == "automatic" or metadata.get(
                "selected", False
            )
        except KeyError:
            return False

    def stream_node(self, node, path):
        self._stream = node["stream"]
        self.properties[self._stream] = set()

    def stream_metadata_node(self, node, path):
        selection = self.SelectedNode(self._stream, self.is_node_selected(node))
        self.streams.add(selection)

    def property_metadata_node(self, node, path):
        *_, name = node["breadcrumb"]
        selection = self.SelectedNode(name, self.is_node_selected(node))

        self.properties[self._stream].add(selection)


@singledispatch
def visit(node, executor, path: str = ""):
    logging.debug(f"Skipping node at '{path}'")


@visit.register(dict)
def _(node: dict, executor, path=""):
    logging.debug(f"Visiting node at '{path}'.")
    if re.search(r"streams\[\d+\]$", path):
        executor(CatalogNode.STREAM, node, path)

    if re.search(r"schema\.properties\..*$", path):
        executor(CatalogNode.STREAM_PROPERTY, node, path)

    if re.search(r"metadata\[\d+\]$", path) and "breadcrumb" in node:
        if len(node["breadcrumb"]) == 0:
            executor(CatalogNode.STREAM_METADATA, node, path)
        else:
            executor(CatalogNode.STREAM_PROPERTY_METADATA, node, path)

    for child_path, child_node in node.items():
        visit(child_node, executor, path=f"{path}.{child_path}")


@visit.register(list)
def _(node: list, executor, path=""):
    for index, child_node in enumerate(node):
        visit(child_node, executor, path=f"{path}[{index}]")
