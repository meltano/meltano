from __future__ import annotations

import sys
import typing as t

from fixtures.custom_addon import MyAddon
from meltano.core.behavior.addon import MeltanoAddon

if sys.version_info >= (3, 12):
    from importlib.metadata import EntryPoint, EntryPoints
else:
    from importlib_metadata import EntryPoint, EntryPoints

if t.TYPE_CHECKING:
    import pytest


def test_entry_point_group():
    """Test that the entry point group is set correctly."""
    addon = MeltanoAddon("meltano.custom_feature")

    assert addon.entry_point_group == "meltano.custom_feature"
    assert not addon.installed


def test_entry_points(monkeypatch: pytest.MonkeyPatch):
    """Test that the entry points are loaded correctly."""
    addon: MeltanoAddon[object] = MeltanoAddon("meltano.custom_feature")

    entry_points = EntryPoints(
        (
            EntryPoint(
                value="fixtures.custom_addon:MyAddon",
                name="custom",
                group="meltano.custom_feature",
            ),
        ),
    )

    with monkeypatch.context() as m:
        m.setattr(addon, "installed", entry_points)
        my_addon = addon.get("custom")
        assert my_addon is MyAddon

        addons = list(addon.get_all())
        assert addons == [MyAddon]
