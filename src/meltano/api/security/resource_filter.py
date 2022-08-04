from __future__ import annotations

from copy import copy
from typing import Callable

from flask_principal import Need

from .auth import ResourcePermission


class ResourceFilter:
    """Filters API responses for a certain set of permissions."""

    def __init__(self):
        self._needs = []

    def filter_all(self, permission_type, resources):
        return list(self.filter(permission_type, resources))

    def filter(self, permission_type, resources):
        for r in resources:
            needs = [need(permission_type, r) for need in self._needs]
            perm = ResourcePermission(*needs)

            if perm.can():
                yield self.scope(permission_type, copy(r))

    def needs(self, need: Callable):
        self._needs.append(need)

        return self

    def scope(self, permission_type, resource):
        return resource


class NameFilterMixin:
    def __init__(self, *args):
        super().__init__(*args)

        self.needs(self.name_need)

    def name_need(self, permission_type, resource):
        return Need(permission_type, resource["name"])


class TopicFilter(NameFilterMixin, ResourceFilter):
    def __init__(self, *args, design_filter=None):
        super().__init__(*args)

        self._design_filter = design_filter or DesignFilter()

    def scope(self, permission_type, topic):
        topic["designs"] = list(
            self._design_filter.filter("view:design", topic["designs"])
        )

        return topic


class DesignFilter(NameFilterMixin, ResourceFilter):
    pass  # noqa: WPS604
