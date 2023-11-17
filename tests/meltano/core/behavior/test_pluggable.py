from __future__ import annotations

import sys
import typing as t

from fixtures.custom_pluggable import MyPlugin
from meltano.core.behavior.pluggable import Pluggable

if sys.version_info >= (3, 12):
    from importlib.metadata import EntryPoint, EntryPoints
else:
    from importlib_metadata import EntryPoint, EntryPoints

if t.TYPE_CHECKING:
    import pytest


def test_entry_point_group():
    """Test that the entry point group is set correctly."""
    pluggable = Pluggable("meltano.custom_feature")

    assert pluggable.entry_point_group == "meltano.custom_feature"
    assert not pluggable.meltano_plugins


def test_entry_points(monkeypatch: pytest.MonkeyPatch):
    """Test that the entry points are loaded correctly."""
    pluggable: Pluggable[object] = Pluggable("meltano.custom_feature")

    entry_points = EntryPoints(
        (
            EntryPoint(
                value="fixtures.custom_pluggable:MyPlugin",
                name="custom",
                group="meltano.custom_feature",
            ),
        ),
    )

    with monkeypatch.context() as m:
        m.setattr(pluggable, "meltano_plugins", entry_points)
        plugin = pluggable.get_meltano_plugin("custom")
        assert plugin == MyPlugin
