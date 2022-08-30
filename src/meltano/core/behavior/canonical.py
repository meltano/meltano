"""Meltano Canonical object behavior."""

from __future__ import annotations

import copy
import json
from functools import lru_cache
from os import PathLike
from typing import Any, TypeVar

import yaml
from ruamel.yaml import Representer
from ruamel.yaml.comments import CommentedMap, CommentedSeq, CommentedSet

T = TypeVar("T", bound="Canonical")  # noqa: WPS111 (name too short)


class IdHashBox:
    """Wrapper class that makes the hash of an object its Python ID."""

    def __init__(self, content: Any):
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

    def __eq__(self, other: Any) -> bool:
        """Check equality of this instance and some other object.

        Parameters:
            other: The object to check equality with.

        Returns:
            Whether this instance and `other` have the same hash.
        """
        return hash(self) == hash(other)


CANONICAL_PARSE_CACHE_SIZE = 4096


class Canonical:  # noqa: WPS214 (too many methods)
    """Defines an object that can be represented as a subset of its attributes.

    Its purpose is to be serializable as the smallest possible form.

    The attribute rules are:
      - All attributes that are Truthy
      - All attributes that are boolean (False is valid)
      - All attributes that are listed in the `_verbatim` set and non-null
      - All attributes that start with "_" are excluded
    """

    def __init__(self, *args: Any, **attrs: Any):
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
    def as_canonical(
        cls: type[T], target: Any
    ) -> dict | list | CommentedMap | CommentedSeq | Any:
        """Return a canonical representation of the given instance.

        Args:
            target: Instance to convert.

        Returns:
            Canonical representation of the given instance.
        """
        if isinstance(target, Canonical):
            result = CommentedMap([(key, cls.as_canonical(val)) for key, val in target])
            target.attrs.copy_attributes(result)
            return result

        if isinstance(target, (CommentedSet, CommentedSeq)):
            result = CommentedSeq(cls.as_canonical(val) for val in target)
            target.copy_attributes(result)
            return result

        if isinstance(target, CommentedMap):
            results = CommentedMap()
            for key, val in target.items():
                if isinstance(val, Canonical):
                    results[key] = val.canonical()
                else:
                    results[key] = cls.as_canonical(val)
            target.copy_attributes(results)
            return results

        if isinstance(target, (list, set)):
            return list(map(cls.as_canonical, target))

        if isinstance(target, dict):
            return {
                key: val.canonical()
                if isinstance(val, Canonical)
                else cls.as_canonical(val)
                for key, val in target.items()
            }

        return copy.deepcopy(target)

    def canonical(self) -> dict | list | CommentedMap | CommentedSeq | Any:
        """Return a canonical representation of the current instance.

        Returns:
            A canonical representation of the current instance.
        """
        return type(self).as_canonical(self)

    def with_attrs(self: T, *args: Any, **kwargs: Any) -> T:
        """Return a new instance with the given attributes set.

        Args:
            args: Attribute names to set.
            kwargs: Keyword arguments to set.

        Returns:
            A new instance with the given attributes set.
        """
        return type(self)(**{**self.canonical(), **kwargs})

    @classmethod
    def parse(cls: type[T], obj: Any) -> T:
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

    def is_attr_set(self, attr):
        """Return whether specified attribute has a non-default/fallback value set.

        Args:
            attr: Attribute to check.

        Returns:
            True if attribute has a non-default/fallback value set.
        """
        return self._dict.get(attr) is not None

    def __getattr__(self, attr: str) -> Any:
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
            value = self._defaults[attr](self)  # noqa: WPS529 (implicit .get())

        return value

    def __setattr__(self, attr: str, value: Any):
        """Set the given attribute to the given value.

        Args:
            attr: Attribute to set.
            value: Value to set.
        """
        if attr.startswith("_") or hasattr(type(self), attr):  # noqa: WPS421
            super().__setattr__(attr, value)
        else:
            self._dict[attr] = value

    def __getitem__(self, attr: str) -> Any:
        """Return the value of the given attribute.

        Args:
            attr: Attribute to return.

        Returns:
            Value of the given attribute.
        """
        return getattr(self, attr)

    def __setitem__(self, attr: str, value: Any) -> None:
        """Set the given attribute to the given value.

        Args:
            attr: Attribute to set.
            value: Value to set.

        Returns:
            None.
        """
        return setattr(self, attr, value)

    def __iter__(self):
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

    def __len__(self):
        """Return the number of attributes set on the current instance.

        Returns:
            Number of attributes set on the current instance.
        """
        return len(self._dict)

    def __contains__(self, obj: Any):
        """Return whether the current instance contains the given object.

        Args:
            obj: Object to check.

        Returns:
            True if the current instance contains the given object.
        """
        return obj in self._dict

    def update(self, *others: Any, **kwargs: Any) -> None:
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
    def yaml(cls, dumper: yaml.BaseDumper, obj: Any) -> yaml.MappingNode:
        """YAML serializer for Canonical objects.

        Args:
            dumper: The YAML dumper.
            obj: The Canonical object to serialize.

        Returns:
            The serialized YAML representation of the object.
        """
        return dumper.represent_mapping(
            "tag:yaml.org,2002:map", cls.as_canonical(obj), flow_style=False
        )

    @classmethod
    def to_yaml(cls, representer: Representer, obj: Any):
        """YAML serializer for Canonical objects.

        Args:
            representer: The YAML representer.
            obj: The Canonical object to serialize.

        Returns:
            The serialized YAML representation of the object.
        """
        return representer.represent_mapping(
            "tag:yaml.org,2002:map", cls.as_canonical(obj)
        )

    @classmethod
    def parse_json_file(cls: type[T], path: PathLike) -> T:
        """Parse a plugin definition from a JSON file.

        Args:
            path: The path to the JSON file.

        Returns:
            A standalone plugin definition.
        """
        with open(path) as file:
            return cls.parse(json.load(file))


yaml.add_multi_representer(Canonical, Canonical.yaml)
