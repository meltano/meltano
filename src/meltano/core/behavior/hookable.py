import contextlib
import io
import logging
from collections import OrderedDict
from typing import Iterator, Tuple


class hook:
    """
    This decorator marks a function as a __hook__.
    It will be found by the Hookable metaclass and
    registered to be triggered accordingly.
    """

    def __init__(self, hook_name, can_fail=False):
        self.name = hook_name
        self.can_fail = can_fail

    def __call__(self, func):
        func.__hook__ = self
        return func


class Hookable(type):
    """
    Metaclass that registers @hook functions into __hooks__
    Hooks are registered in declaration order.
    """

    def __new__(metacls, name, bases, dct):
        cls = type.__new__(metacls, name, bases, dct)
        cls.__hooks__ = {}

        for hook_name, hook in (
            (func.__hook__.name, func)
            for func in dct.values()
            if hasattr(func, "__hook__")
        ):
            cls.__hooks__[hook_name] = cls.__hooks__.get(hook_name, [])
            cls.__hooks__[hook_name].append(hook)

        return cls

    def __prepare__(name, bases, **kwds):
        return OrderedDict()


class HookObject(metaclass=Hookable):
    """
    Hook base class that handles the triggering of hooks.
    Hooks are triggered in reverse MRO order, which means
    derived classes hooks are called after their base class.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @contextlib.contextmanager
    def trigger_hooks(self, hook_name, *args, **kwargs):
        try:
            already_triggering = hook_name in self._triggering_hooks
        except AttributeError:
            self._triggering_hooks = set()
            already_triggering = False

        if not already_triggering:
            self._triggering_hooks.add(hook_name)
            self.__class__.trigger(self, f"before_{hook_name}", *args, **kwargs)

        yield

        if not already_triggering:
            self.__class__.trigger(self, f"after_{hook_name}", *args, **kwargs)
            self._triggering_hooks.remove(hook_name)

    @classmethod
    def trigger(cls, target, hook_name, *args, **kwargs):
        hooks = [
            hook
            for hook_cls in reversed(cls.__mro__)
            if hasattr(hook_cls, "__hooks__")
            for hook in hook_cls.__hooks__.get(hook_name, [])
        ]

        for hook_func in hooks:
            try:
                hook_func(target, *args, **kwargs)
            except Exception as err:
                logging.warning(
                    f"{hook_name} hook '{hook_func.__name__}' has failed: {err}"
                )
                if not hook_func.__hook__.can_fail:
                    raise err
