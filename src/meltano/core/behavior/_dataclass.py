"""Dataclass mixin that preserves YAML comments and provides Canonical-like behavior."""

from __future__ import annotations

import copy
import sys
import typing as t
from dataclasses import fields, is_dataclass
from functools import lru_cache

from ruamel.yaml.comments import CommentedMap, CommentedSeq, CommentedSet

if sys.version_info >= (3, 11):
    from typing import Self  # noqa: ICN003
else:
    from typing_extensions import Self

if t.TYPE_CHECKING:
    import ruamel.yaml.dumper
    import ruamel.yaml.nodes
    import ruamel.yaml.representer

from meltano.core.behavior.canonical import (
    CANONICAL_PARSE_CACHE_SIZE,
    Annotations,
    AnnotationsMeta,
    IdHashBox,
)


class CanonicalDataclassMeta(AnnotationsMeta):
    """Metaclass that combines dataclass with annotation handling."""

    def __call__(cls, *args: t.Any, **kwargs: t.Any) -> t.Any:  # noqa: ANN401, N805
        """Create and return an instance, handling annotations before __init__.

        Args:
            *args: Positional arguments for the instance.
            **kwargs: Keyword arguments for the instance.

        Returns:
            The newly created instance with annotations stored separately.
        """
        # Remove the annotations from the arguments that would be used for `__init__`.
        extracted_annotations = (
            Annotations(
                index=list(kwargs.keys()).index("annotations"),
                data=kwargs.pop("annotations"),
            )
            if "annotations" in kwargs
            else None
        )

        # For dataclasses, filter out extra kwargs that aren't fields
        if is_dataclass(cls):
            field_names = {f.name for f in fields(cls)}  # type: ignore[unreachable]
            extra_kwargs = {k: v for k, v in kwargs.items() if k not in field_names}
            filtered_kwargs = {k: v for k, v in kwargs.items() if k in field_names}

            # Create instance with only valid field kwargs
            instance = super(AnnotationsMeta, cls).__call__(*args, **filtered_kwargs)

            # Store extra kwargs for later access
            if extra_kwargs and hasattr(instance, "_dict"):
                for key, value in extra_kwargs.items():
                    instance._dict[key] = value
            if extra_kwargs and hasattr(instance, "_extra_attrs"):
                instance._extra_attrs.update(extra_kwargs)
        else:
            instance = super(AnnotationsMeta, cls).__call__(*args, **kwargs)

        # Store the annotations for later re-insertion during serialization
        instance._annotations = extracted_annotations
        return instance


class CanonicalDataclassMixin:
    """Mixin for dataclasses that provides Canonical-like YAML serialization.

    This mixin provides:
    - YAML comment preservation via CommentedMap storage
    - Filtering of None/empty values (except False)
    - parse() and canonical() methods for serialization
    - Annotations support
    - Support for extra kwargs not defined in dataclass fields
    """

    def __post_init__(self, **extra_kwargs: t.Any) -> None:
        """Initialize the YAML comment storage after dataclass __init__.

        Args:
            **extra_kwargs: Extra keyword arguments not defined in dataclass fields.
        """
        # Store YAML comments and metadata
        self._dict = CommentedMap()
        self._annotations: Annotations | None = None
        self._extra_attrs: dict[str, t.Any] = {}

        # Copy field values to _dict for YAML comment preservation
        if is_dataclass(self):
            for field in fields(self):  # type: ignore[unreachable]
                value = getattr(self, field.name)
                if value is not None:
                    self._dict[field.name] = value

        # Store any extra kwargs that weren't part of the dataclass
        self._extra_attrs = extra_kwargs
        for key, value in extra_kwargs.items():
            self._dict[key] = value

    @classmethod
    def _canonize(cls, val: t.Any) -> t.Any:  # noqa: ANN401
        """Call `as_canonical` on `val`, respecting dataclass types.

        Args:
            val: An object on which `as_canonical` should be called.

        Returns:
            The value obtained from calling `as_canonical`.
        """
        return getattr(type(val), "as_canonical", cls.as_canonical)(val)

    @classmethod
    def as_canonical(
        cls,
        target: t.Any,  # noqa: ANN401
    ) -> dict | list | CommentedMap | CommentedSeq | t.Any:  # noqa: ANN401
        """Return a canonical representation of the given instance.

        Args:
            target: An instance to convert.

        Returns:
            A canonical representation of the given instance.
        """
        if isinstance(target, CanonicalDataclassMixin):
            # Build the canonical dict from dataclass fields
            result = CommentedMap()
            if is_dataclass(target):
                for field in fields(target):  # type: ignore[unreachable]
                    val = getattr(target, field.name)
                    # Skip None values and empty values (except False)
                    if val is None or (not val and val is not False):
                        continue
                    # Skip empty dataclass instances
                    if isinstance(val, CanonicalDataclassMixin) and not dict(
                        cls.as_canonical(val),
                    ):
                        continue
                    result[field.name] = cls._canonize(val)

            # Re-insert annotations if they exist
            if hasattr(target, "_annotations") and target._annotations is not None:
                result.insert(
                    target._annotations.index,
                    "annotations",
                    target._annotations.data,
                )

            # Copy YAML attributes (comments, etc.) if they exist
            if hasattr(target, "_dict"):
                target._dict.copy_attributes(result)

            return result

        if isinstance(target, dict):
            as_dict = {key: cls._canonize(val) for key, val in target.items()}
            if isinstance(target, CommentedMap):
                as_commented_map = CommentedMap(as_dict)
                target.copy_attributes(as_commented_map)
                return as_commented_map
            return as_dict

        if isinstance(target, list | set | CommentedSet):
            as_list = [cls._canonize(val) for val in target]
            if isinstance(target, CommentedSet | CommentedSeq):
                as_commented_seq = CommentedSeq(as_list)
                target.copy_attributes(as_commented_seq)
                return as_commented_seq
            return as_list

        return copy.deepcopy(target)

    def canonical(self) -> dict | list | CommentedMap | CommentedSeq | t.Any:  # noqa: ANN401
        """Return a canonical representation of the current instance.

        Returns:
            A canonical representation of the current instance.
        """
        return type(self).as_canonical(self)

    @classmethod
    def parse(cls, obj: t.Any) -> Self | None:  # noqa: ANN401
        """Parse a dataclass object from a dictionary or return the instance.

        Args:
            obj: Dictionary or instance to parse.

        Returns:
            Parsed instance.
        """
        return cls._parse(IdHashBox(obj))

    @classmethod
    @lru_cache(maxsize=CANONICAL_PARSE_CACHE_SIZE)
    def _parse(cls, boxed_obj: IdHashBox) -> Self | None:
        """Parse a dataclass object from a dictionary or return the instance.

        Args:
            boxed_obj: Dictionary or instance to parse wrapped in an `IdHashBox`.

        Returns:
            Parsed instance.
        """
        obj = boxed_obj.content

        if obj is None:
            return None

        if isinstance(obj, cls):
            return obj

        # Filter kwargs to only include fields defined on the dataclass
        if is_dataclass(cls):
            field_names = {f.name for f in fields(cls)}  # type: ignore[unreachable]
            filtered_kwargs = {k: v for k, v in obj.items() if k in field_names}
        else:
            filtered_kwargs = dict(obj)

        instance = cls(**filtered_kwargs)

        # Copy YAML attributes if the source is a CommentedMap
        if isinstance(obj, CommentedMap) and hasattr(instance, "_dict"):
            obj.copy_attributes(instance._dict)

        return instance

    @property
    def attrs(self) -> CommentedMap:
        """Return the attributes storage (for YAML comments).

        Returns:
            Attributes storage.
        """
        return self._dict

    def __getitem__(self, key: str) -> t.Any:  # noqa: ANN401
        """Support subscript access to fields.

        Args:
            key: The field name to access.

        Returns:
            The field value.
        """
        return getattr(self, key)

    def __setitem__(self, key: str, value: t.Any) -> None:  # noqa: ANN401
        """Support subscript assignment to fields.

        Args:
            key: The field name to set.
            value: The value to set.
        """
        setattr(self, key, value)

    @classmethod
    def yaml(
        cls,
        dumper: ruamel.yaml.dumper.BaseDumper,
        obj: t.Any,  # noqa: ANN401
    ) -> ruamel.yaml.nodes.MappingNode:
        """YAML serializer for dataclass objects.

        Args:
            dumper: The YAML dumper.
            obj: The dataclass object to serialize.

        Returns:
            The serialized YAML representation of the object.
        """
        return dumper.represent_mapping(
            "tag:yaml.org,2002:map",
            cls.as_canonical(obj),
            flow_style=False,
        )

    @classmethod
    def to_yaml(
        cls,
        representer: ruamel.yaml.representer.Representer,
        obj: t.Any,  # noqa: ANN401
    ) -> ruamel.yaml.nodes.MappingNode:
        """YAML serializer for dataclass objects.

        Args:
            representer: The YAML representer.
            obj: The dataclass object to serialize.

        Returns:
            The serialized YAML representation of the object.
        """
        return representer.represent_mapping(
            "tag:yaml.org,2002:map",
            cls.as_canonical(obj),
        )
