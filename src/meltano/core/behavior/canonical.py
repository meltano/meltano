"""Meltano Canonical object behavior."""

import copy
import json
from os import PathLike
from typing import Any, Type, TypeVar, Union

import yaml

T = TypeVar("T", bound="Canonical")  # noqa: WPS111 (name too short)


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
        self._dict = {}

        super().__init__(*args)

        for attr, value in attrs.items():
            setattr(self, attr, value)

        self._verbatim = set()
        self._flattened = {"extras"}

        self._fallback_to = None
        self._fallbacks = set()
        self._defaults = {}

    @classmethod
    def as_canonical(cls: Type[T], target: Any) -> Union[dict, list, Any]:
        """Return a canonical representation of the given instance.

        Args:
            target: Instance to convert.

        Returns:
            Canonical representation of the given instance.
        """
        if isinstance(target, Canonical):
            return {key: Canonical.as_canonical(val) for key, val in target}

        if isinstance(target, set):
            return list(map(Canonical.as_canonical, target))

        if isinstance(target, list):
            return list(map(Canonical.as_canonical, target))

        if isinstance(target, dict):
            results = {}
            for key, val in target.items():
                if isinstance(val, Canonical):
                    results[key] = val.canonical()
                else:
                    results[key] = Canonical.as_canonical(val)
            return results

        return copy.deepcopy(target)

    def canonical(self) -> Union[dict, list, Any]:
        """Return a canonical representation of the current instance.

        Returns:
            A canonical representation of the current instance.
        """
        return Canonical.as_canonical(self)

    def with_attrs(self: T, *args: Any, **kwargs: Any) -> T:
        """Return a new instance with the given attributes set.

        Args:
            args: Attribute names to set.
            kwargs: Keyword arguments to set.

        Returns:
            A new instance with the given attributes set.
        """
        return self.__class__(**{**self.canonical(), **kwargs})

    @classmethod
    def parse(cls: Type[T], obj: Any) -> T:
        """Parse a 'Canonical' object from a dictionary or return the instance.

        Args:
            obj: Dictionary or instance to parse.

        Returns:
            Parsed instance.
        """
        if obj is None:
            return None

        if isinstance(obj, cls):
            return obj

        return cls(**obj)

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
        if attr.startswith("_") or hasattr(self.__class__, attr):  # noqa: WPS421
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
            other = Canonical.as_canonical(other)

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
            "tag:yaml.org,2002:map", Canonical.as_canonical(obj), flow_style=False
        )

    @classmethod
    def parse_json_file(cls: Type[T], path: PathLike) -> T:
        """Parse a plugin definition from a JSON file.

        Args:
            path: The path to the JSON file.

        Returns:
            A standalone plugin definition.
        """
        with open(path) as file:
            return cls.parse(json.load(file))


yaml.add_multi_representer(Canonical, Canonical.yaml)
