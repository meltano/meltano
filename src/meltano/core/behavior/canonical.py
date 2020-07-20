import yaml
import copy

from typing import Iterable


class Canonical(object):
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
        super(Canonical, self).__init__(*args)

        for attr, value in attrs.items():
            setattr(self, attr, value)

        self._verbatim = set()

    @classmethod
    def as_canonical(cls, target):
        if isinstance(target, Canonical):
            return {k: Canonical.as_canonical(v) for k, v in target}

        if isinstance(target, set):
            return list(map(Canonical.as_canonical, target))

        if isinstance(target, list):
            return list(map(Canonical.as_canonical, target))

        return copy.deepcopy(target)

    def canonical(self):
        return Canonical.as_canonical(self)

    @classmethod
    def parse(cls, obj) -> "Canonical":
        if obj is None:
            return None

        if isinstance(obj, Canonical):
            return obj

        return cls(**obj)

    def __getitem__(self, attr):
        return getattr(self, attr)

    def __setitem__(self, attr, value):
        return setattr(self, attr, value)

    def __iter__(self):
        for k, v in self.__dict__.items():
            if k.startswith("_"):
                continue

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

            if k == "extras":
                yield from v.items()
            else:
                yield (k, v)

    def __len__(self):
        return len(self.__dict__)

    def __contains__(self, obj):
        return obj in self.__dict__

    def update(self, other):
        other = Canonical.as_canonical(other)

        for k, v in other.items():
            setattr(self, k, v)

    @classmethod
    def yaml(cls, dumper, obj):
        return dumper.represent_mapping(
            "tag:yaml.org,2002:map", Canonical.as_canonical(obj), flow_style=False
        )


yaml.add_multi_representer(Canonical, Canonical.yaml)
