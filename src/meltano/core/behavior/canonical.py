import yaml
import copy

from typing import Iterable


class Canonical(object):
    def __init__(self, *args, **attrs):
        if len(self.__class__.__mro__) > 2:
            super(Canonical, self).__init__(*args)

        for attr, value in attrs.items():
            setattr(self, attr, value)

    @classmethod
    def as_canonical(cls, target):
        if isinstance(target, Canonical):
            return {
                k: Canonical.as_canonical(v)
                for k, v in target
            }

        if isinstance(target, list):
            return list(map(Canonical.as_canonical, target))

        return copy.deepcopy(target)

    @classmethod
    def parse(cls, obj) -> 'Canonical':
        if isinstance(obj, Canonical):
            return obj

        return cls(**obj)

    def __getitem__(self, attr):
        return getattr(self, attr)

    def __setitem__(self, attr, value):
        return setattr(self, attr, value)

    def __iter__(self):
        for k, v in self.__dict__.items():
            if v is None:
                continue

            yield (k, v)

    @classmethod
    def yaml(cls, dumper, obj):
        return dumper.represent_mapping(
            "tag:yaml.org,2002:map",
            Canonical.as_canonical(obj),
            flow_style=False)


yaml.add_multi_representer(Canonical, Canonical.yaml)
