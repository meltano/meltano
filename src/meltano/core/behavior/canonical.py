"""Meltano Canonical object behavior."""

from __future__ import annotations

import copy
import json
import typing as t
from functools import lru_cache

import yaml
from ruamel.yaml.comments import CommentedMap, CommentedSeq, CommentedSet

if t.TYPE_CHECKING:
    from os import PathLike

    from ruamel.yaml import Representer

T = t.TypeVar("T", bound="Canonical")  # (name too short)


class IdHashBox:
    """Wrapper class that makes the hash of an object its Python ID."""

    def __init__(self, content: t.Any):  # noqa: ANN401
        """Initialize the `IdHashBox`.

        Parameters:
            content: The object that will be stored within the `IdHashBox`.
                Its Python ID will be used to hash the `IdHashBox` instance.
        """
        self.content = content

    def __hash__(self) -> int:
        """Hash the `IdHashBox` according to the Python ID of its content.

        Returns:
            The Python ID of the content of the `IdHashBox` instance.
        """
        return id(self.content)

    def __eq__(self, other: t.Any) -> bool:  # noqa: ANN401
        """Check equality of this instance and some other object.

        Parameters:
            other: The object to check equality with.

        Returns:
            Whether this instance and `other` have the same hash.
        """
        return hash(self) == hash(other)


CANONICAL_PARSE_CACHE_SIZE = 4096


class Annotations(t.NamedTuple):
    """Tuple storing the data of an annotation, and its index."""

    index: int
    data: CommentedMap


class AnnotationsMeta(type):
    """Metaclass to intercept and store annotations before calling `__init__`."""

    def __call__(cls, *args: t.Any, **kwargs: t.Any) -> t.Any:  # noqa: ANN401
        """Create and return an instance of the class this metaclass is applied to.

        Args:
            *args: Positional arguments for the instance.
            **kwargs: Keyword arguments for the instance.

        Returns:
            The newly created instance of the class this metaclass is applied to.
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
        instance = super().__call__(*args, **kwargs)
        # Store the annotations for later re-insertion during serialization
        instance._annotations = extracted_annotations
        return instance


class Canonical(metaclass=AnnotationsMeta):  # (too many methods)
    """Defines an object that can be represented as a subset of its attributes.

    Its purpose is to be serializable as the smallest possible form.

    The attribute rules are:
      - All attributes that are Truthy
      - All attributes that are boolean (False is valid)
      - All attributes that are listed in the `_verbatim` set and non-null
      - All attributes that start with "_" are excluded
    """

    def __init__(self, *args: t.Any, **attrs: t.Any):
        """Initialize the current instance with the given attributes.

        Args:
            args: Arguments to initialize with.
            attrs: Keyword arguments to initialize with.
        """
        self._dict = CommentedMap()

        super().__init__(*args)

        for attr, value in attrs.items():
            setattr(self, attr, value)

        self._verbatim = set()
        self._flattened = {"extras"}

        self._fallback_to = None
        self._fallbacks = set()
        self._defaults = {}

    @classmethod
    def _canonize(cls, val: t.Any) -> t.Any:  # noqa: ANN401
        """Call `as_canonical` on `val`, respecting `Canonical` subclasses.

        Args:
            val: An object on which `as_canonical` should be called. If `val`
                has an `as_canonical` attribute it will be called. Otherwise
                the `as_caonical` attribute of this class will be used.

        Returns:
            The value obtained from calling `as_canonical`.
        """
        return getattr(type(val), "as_canonical", cls.as_canonical)(val)

    @classmethod
    def as_canonical(
        cls: type[T],
        target: t.Any,  # noqa: ANN401
    ) -> dict | list | CommentedMap | CommentedSeq | t.Any:  # noqa: ANN401
        """Return a canonical representation of the given instance.

        Args:
            target: An instance to convert.

        Returns:
            A canonical representation of the given instance.
        """
        if isinstance(target, Canonical):
            result = CommentedMap((key, cls._canonize(val)) for key, val in target)
            if target._annotations is not None:
                result.insert(
                    target._annotations.index,
                    "annotations",
                    target._annotations.data,
                )
            target.attrs.copy_attributes(result)
            return result

        if isinstance(target, dict):
            as_dict = {key: cls._canonize(val) for key, val in target.items()}
            if isinstance(target, CommentedMap):
                as_commented_map = CommentedMap(as_dict)
                target.copy_attributes(as_commented_map)
                return as_commented_map
            return as_dict

        if isinstance(target, (list, set, CommentedSet)):
            as_list = [cls._canonize(val) for val in target]
            if isinstance(target, (CommentedSet, CommentedSeq)):
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

    def with_attrs(self: T, *args: t.Any, **kwargs: t.Any) -> T:
        """Return a new instance with the given attributes set.

        Args:
            args: Attribute names to set.
            kwargs: Keyword arguments to set.

        Returns:
            A new instance with the given attributes set.
        """
        return type(self)(*args, **{**self.canonical(), **kwargs})

    @classmethod
    def parse(cls: type[T], obj: t.Any) -> T:  # noqa: ANN401
        """Parse a 'Canonical' object from a dictionary or return the instance.

        Args:
            obj: Dictionary or instance to parse.

        Returns:
            Parsed instance.
        """
        return cls._parse(IdHashBox(obj))

    @classmethod
    @lru_cache(maxsize=CANONICAL_PARSE_CACHE_SIZE)
    def _parse(cls: type[T], boxed_obj: IdHashBox) -> T:
        """Parse a `Canonical` object from a dictionary or return the instance.

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

        instance = cls(**obj)

        if isinstance(obj, CommentedMap):
            obj.copy_attributes(instance.attrs)

        return instance

    @property
    def attrs(self) -> CommentedMap:
        """Return the attributes of the current instance.

        Returns:
            Attributes of the current instance.
        """
        return self._dict

    def is_attr_set(self, attr):  # noqa: ANN001, ANN201
        """Return whether specified attribute has a non-default/fallback value set.

        Args:
            attr: Attribute to check.

        Returns:
            True if attribute has a non-default/fallback value set.
        """
        return self._dict.get(attr) is not None

    def __getattr__(self, attr: str) -> t.Any:  # noqa: ANN401
        """Return the value of the given attribute.

        Args:
            attr: Attribute to return.

        Returns:
            Value of the given attribute.

        Raises:
            AttributeError: If the attribute is not set.
        """
        try:
            value = self._dict[attr]
        except KeyError as err:
            if self._fallback_to and not attr.startswith("_"):
                return getattr(self._fallback_to, attr)

            raise AttributeError(attr) from err

        if value is not None:
            return value

        if attr in self._fallbacks and self._fallback_to:
            value = getattr(self._fallback_to, attr)

        if value is not None:
            return value

        if attr in self._defaults:
            value = self._defaults[attr](self)

        return value

    def __setattr__(self, attr: str, value: t.Any) -> None:  # noqa: ANN401
        """Set the given attribute to the given value.

        Args:
            attr: Attribute to set.
            value: Value to set.
        """
        if attr.startswith("_") or hasattr(type(self), attr):
            super().__setattr__(attr, value)
        else:
            self._dict[attr] = value

    def __getitem__(self, attr: str) -> t.Any:  # noqa: ANN401
        """Return the value of the given attribute.

        Args:
            attr: Attribute to return.

        Returns:
            Value of the given attribute.
        """
        return getattr(self, attr)

    def __setitem__(self, attr: str, value: t.Any) -> None:  # noqa: ANN401
        """Set the given attribute to the given value.

        Args:
            attr: Attribute to set.
            value: Value to set.

        Returns:
            None.
        """
        return setattr(self, attr, value)

    def __iter__(self):  # noqa: ANN204
        """Return an iterator over the attributes set on the current instance.

        Yields:
            An iterator over the attributes set on the current instance.
        """
        for key, val in self._dict.items():
            if not val:
                if key in self._verbatim:
                    if val is None:
                        continue
                else:
                    # bool values are valid and should be forwarded
                    if val is not False:
                        continue

            # empty canonicals should be skipped
            if isinstance(val, Canonical) and not dict(val):
                continue

            if key in self._flattened:
                if isinstance(val, Canonical):
                    yield from val
                else:
                    yield from val.items()
            else:
                yield (key, val)

    def __len__(self) -> int:
        """Return the number of attributes set on the current instance.

        Returns:
            Number of attributes set on the current instance.
        """
        return len(self._dict)

    def __contains__(self, obj: t.Any) -> bool:  # noqa: ANN401
        """Return whether the current instance contains the given object.

        Args:
            obj: Object to check.

        Returns:
            True if the current instance contains the given object.
        """
        return obj in self._dict

    def update(self, *others: t.Any, **kwargs: t.Any) -> None:
        """Update the current instance with the given others.

        Args:
            others: Other instances to update with.
            kwargs: Keyword arguments to update with.
        """
        if kwargs:
            others = [*others, kwargs]

        for other in others:
            other = type(self).as_canonical(other)

            for key, val in other.items():
                setattr(self, key, val)

    @classmethod
    def yaml(cls, dumper: yaml.BaseDumper, obj: t.Any) -> yaml.MappingNode:  # noqa: ANN401
        """YAML serializer for Canonical objects.

        Args:
            dumper: The YAML dumper.
            obj: The Canonical object to serialize.

        Returns:
            The serialized YAML representation of the object.
        """
        return dumper.represent_mapping(
            "tag:yaml.org,2002:map",
            cls.as_canonical(obj),
            flow_style=False,
        )

    @classmethod
    def to_yaml(cls, representer: Representer, obj: t.Any):  # noqa: ANN206, ANN401
        """YAML serializer for Canonical objects.

        Args:
            representer: The YAML representer.
            obj: The Canonical object to serialize.

        Returns:
            The serialized YAML representation of the object.
        """
        return representer.represent_mapping(
            "tag:yaml.org,2002:map",
            cls.as_canonical(obj),
        )

    @classmethod
    def parse_json_file(cls: type[T], path: PathLike) -> T:
        """Parse a plugin definition from a JSON file.

        Args:
            path: The path to the JSON file.

        Returns:
            A standalone plugin definition.
        """
        with open(path) as file:  # noqa: PTH123
            return cls.parse(json.load(file))


yaml.add_multi_representer(Canonical, Canonical.yaml)
