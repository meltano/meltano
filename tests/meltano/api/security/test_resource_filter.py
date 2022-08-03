from __future__ import annotations

import pytest
from flask import appcontext_pushed, g  # noqa: WPS347
from flask_principal import Identity, Need

from meltano.api.security.auth import ResourcePermission


@pytest.fixture
def identity(app):
    identity = Identity("test")

    def handler(sender):
        g.identity = identity

    with appcontext_pushed.connected_to(handler, app):
        yield identity


class TestResourcePermission:
    def test_allows(self, identity):
        resource_need = Need("view:design", "*")
        identity.provides.add(resource_need)

        item_need = Need("view:design", "finance")
        assert ResourcePermission(item_need).allows(identity)

    def test_allows_reject(self, identity):
        item_need = Need("view:design", "finance")
        assert not ResourcePermission(item_need).allows(identity)
