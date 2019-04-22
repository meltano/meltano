import pytest
from unittest import mock

from meltano.core.behavior.hookable import HookObject, hook, TriggerError


class Hooked(HookObject):
    def __init__(self):
        self._calls = []

    def call(self, hook_name):
        self._calls.append(hook_name)

    @property
    def calls(self):
        return self._calls.copy()

    @hook("after_test")
    def after_test(self):
        self.call("after_test")

    @hook("after_test")
    def after_test_2(self):
        self.call("after_test_2")

    @hook("before_test")
    def before_test(self):
        self.call("before_test")

    @hook("before_test")
    def before_test_2(self):
        self.call("before_test_2")


class DerivedHooked(Hooked):
    @hook("before_test")
    def derived_before_test(self):
        super().call("derived_before_test")


class Hooked2(HookObject):
    @hook("before_test")
    def another_class(self):
        raise Exception()


class HookedException(Hooked):
    def __init__(self):
        self.before_ex = Exception("before")
        self.after_ex = Exception("after")

        super().__init__()

    @hook("before_test")
    def hook_raises_before(self):
        self.call("hook_raises_before")
        raise self.before_ex

    @hook("after_test")
    def hook_raises_after(self):
        self.call("hook_raises_after")
        raise self.after_ex


class TestHookable:
    def test_trigger_hook(self):
        subject = Hooked()
        process = mock.MagicMock()
        with subject.trigger_hooks("test"):
            process()

        assert subject.calls == [
            "before_test",
            "before_test_2",
            "after_test",
            "after_test_2",
        ]
        assert process.called_once

    def test_trigger_hook_raise(self):
        subject = Hooked()
        process = mock.MagicMock()

        # it raises exceptions correctly
        with pytest.raises(Exception), subject.trigger_hooks("test"):
            raise Exception()

        assert subject.calls == ["before_test", "before_test_2"]

    def test_trigger_derived_hook(self):
        subject = DerivedHooked()

        process = mock.MagicMock()
        with subject.trigger_hooks("test"):
            process()

        assert subject.calls == [
            "before_test",
            "before_test_2",
            "derived_before_test",
            "after_test",
            "after_test_2",
        ]
        assert process.called_once

    def test_trigger_hook_raises(self):
        subject = HookedException()
        process = mock.MagicMock()

        with pytest.raises(TriggerError) as ex, subject.trigger_hooks("test"):
            process()

        assert subject.before_ex is ex.value.before_hooks["before_test"]
        assert subject.after_ex is ex.value.after_hooks["after_test"]

        # assert not process.called
        assert subject.calls == [
            "before_test",
            "before_test_2",
            "hook_raises_before",
            "after_test",
            "after_test_2",
            "hook_raises_after",
        ]
