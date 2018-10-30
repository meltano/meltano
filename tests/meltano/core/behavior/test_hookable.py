import pytest
from unittest import mock

from meltano.core.behavior.hookable import Hookable


class Hooked(Hookable):
    _calls = []

    def call(self, hook_name):
        self._calls.append(hook_name)

    @property
    def calls(self):
        return self._calls.copy()

    @Hookable.hook("after_test")
    def after_test(self):
        self.call("after_test")

    @Hookable.hook("after_test")
    def after_test_2(self):
        self.call("after_test_2")

    @Hookable.hook("before_test")
    def before_test(self):
        self.call("before_test")

    @Hookable.hook("before_test")
    def before_test_2(self):
        self.call("before_test_2")


class TestHookable:
    @pytest.fixture
    def subject(self):
        return Hooked()

    def test_trigger_hook(self, subject):
        process = mock.MagicMock()
        with subject.trigger_hooks("test"):
            process()

        assert subject.calls == ["before_test", "before_test_2", "after_test", "after_test_2"]
        assert process.called_once
        process.reset_mock()

        # it raises exceptions correctly
        with pytest.raises(Exception), \
             subject.trigger_hooks("test"):
            raise Exception()

        assert not process.called
