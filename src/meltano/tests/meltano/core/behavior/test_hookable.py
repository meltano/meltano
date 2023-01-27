from __future__ import annotations

import mock
import pytest

from meltano.core.behavior.hookable import HookObject, hook


class Hooked(HookObject):
    def __init__(self):
        self._calls = []

    def call(self, hook_name):
        self._calls.append(hook_name)

    @property
    def calls(self):
        return self._calls.copy()

    @hook("after_test")
    async def after_test(self):
        self.call("after_test")

    @hook("after_test")
    async def after_test2(self):
        self.call("after_test_2")

    @hook("before_test")
    async def before_test(self):
        self.call("before_test")

    @hook("before_test")
    async def before_test2(self):
        self.call("before_test_2")


class DerivedHooked(Hooked):
    @hook("before_test")
    async def derived_before_test(self):
        super().call("derived_before_test")  # noqa: WPS613


class Hooked2(HookObject):
    @hook("before_test")
    async def another_class(self):
        raise Exception()


class TestHookable:
    @pytest.mark.asyncio
    async def test_trigger_hook(self):
        subject = Hooked()
        process = mock.MagicMock()
        async with subject.trigger_hooks("test"):
            process()

        assert subject.calls == [
            "before_test",
            "before_test_2",
            "after_test",
            "after_test_2",
        ]
        assert process.called_once

    @pytest.mark.asyncio
    async def test_trigger_hook_raise(self):
        subject = Hooked()
        with pytest.raises(Exception):
            async with subject.trigger_hooks("test"):
                raise Exception()

        assert subject.calls == ["before_test", "before_test_2"]

    @pytest.mark.asyncio
    async def test_trigger_derived_hook(self):
        subject = DerivedHooked()

        process = mock.MagicMock()
        async with subject.trigger_hooks("test"):
            process()

        assert subject.calls == [
            "before_test",
            "before_test_2",
            "derived_before_test",
            "after_test",
            "after_test_2",
        ]
        assert process.called_once
