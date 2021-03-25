import copy
from typing import Iterable

import yaml


class Canonical:
    """
    This class defines an object that can be reprensented as a subset of
    its attributes.

    Its purpose is to be serializable as the smallest possible form.

    The attribute rules are:
      - All attributes that are Truthy
      - All attributes that are boolean (False is valid)
      - All attributes that are listed in the `_verbatim` set and non-null
      - All attributes that start with "_" are excluded
    """

    def __init__(self, *args, **attrs):
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
    def as_canonical(cls, target):
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

    def canonical(self):
        return Canonical.as_canonical(self)

    def with_attrs(self, *args, **kwargs):
        return self.__class__(**{**self.canonical(), **kwargs})

    @classmethod
    def parse(cls, obj) -> "Canonical":
        if obj is None:
            return None

        if isinstance(obj, Canonical):
            return obj

        return cls(**obj)

    def is_attr_set(self, attr):
        """Return whether specified attribute has a non-default/fallback value set."""
        return self._dict.get(attr) is not None

    def __getattr__(self, attr):
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

    def __setattr__(self, attr, value):
        if attr.startswith("_") or hasattr(self.__class__, attr):
            super().__setattr__(attr, value)
        else:
            self._dict[attr] = value

    def __getitem__(self, attr):
        return getattr(self, attr)

    def __setitem__(self, attr, value):
        return setattr(self, attr, value)

    def __iter__(self):
        for k, v in self._dict.items():
            if not v:
                if k in self._verbatim:
                    if v is None:
                        continue
                else:
                    # bool values are valid and should be forwarded
                    if v is not False:
                        continue

            # empty canonicals should be skipped
            if isinstance(v, Canonical) and not dict(v):
                continue

            if k in self._flattened:
                if isinstance(v, Canonical):
                    yield from v
                else:
                    yield from v.items()
            else:
                yield (k, v)

    def __len__(self):
        return len(self._dict)

    def __contains__(self, obj):
        return obj in self._dict

    def update(self, *others, **kwargs):
        if kwargs:
            others = [*others, kwargs]

        for other in others:
            other = Canonical.as_canonical(other)

            for k, v in other.items():
                setattr(self, k, v)

    @classmethod
    def yaml(cls, dumper, obj):
        return dumper.represent_mapping(
            "tag:yaml.org,2002:map", Canonical.as_canonical(obj), flow_style=False
        )


yaml.add_multi_representer(Canonical, Canonical.yaml)
