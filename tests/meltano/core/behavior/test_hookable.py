import pytest
from unittest import mock

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
        process.reset_mock()

        # it raises exceptions correctly
        with pytest.raises(Exception), subject.trigger_hooks("test"):
            raise Exception()

        assert not process.called

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
