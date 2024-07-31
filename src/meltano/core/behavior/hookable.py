"""Hookable class and supporting functions, classes, and decorators.

This module contains the Hookable class which allows for implementation of a
classic before/after hook pattern. Allowing you to register functions to be
called before or after given trigger.
"""

from __future__ import annotations

from collections import OrderedDict
from contextlib import asynccontextmanager

import structlog

logger = structlog.stdlib.get_logger(__name__)


class hook:  # noqa: N801
    """This decorator marks a function as a `__hook__`.

    It will be found by the `Hookable` metaclass and registered to be triggered
    accordingly.
    """

    def __init__(self, hook_name, *, can_fail=False) -> None:  # noqa: ANN001, D107
        self.name = hook_name
        self.can_fail = can_fail

    def __call__(self, func):  # noqa: ANN001, ANN204, D102
        func.__hook__ = self
        return func


class Hookable(type):
    """Metaclass that registers hook-decorated functions into `__hooks__`.

    Hooks are registered in declaration order.
    """

    def __new__(cls, name, bases, dct):  # noqa: ANN001, ANN204, D102
        new_type = type.__new__(cls, name, bases, dct)
        new_type.__hooks__ = {}

        for hook_name, hook in (
            (func.__hook__.name, func)
            for func in dct.values()
            if hasattr(func, "__hook__")
        ):
            new_type.__hooks__[hook_name] = new_type.__hooks__.get(
                hook_name,
                [],
            )
            new_type.__hooks__[hook_name].append(hook)

        return new_type

    def __prepare__(cls, bases, **kwds):  # noqa: ANN001, ANN003, ANN204, D105
        return OrderedDict()


class HookObject(metaclass=Hookable):
    """Hook base class that handles the triggering of hooks.

    Hooks are triggered in reverse MRO order, which means derived classes hooks
    are called after their base class.
    """

    @asynccontextmanager
    async def trigger_hooks(self, hook_name, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003, ANN201
        """Trigger all registered before and after functions for a given hook.

        Yields to the caller in between triggers.

        Args:
            hook_name: The hook who's registered functions that should be triggered
            args: Positional arguments to pass to the hooks being triggered.
            kwargs: Keyword arguments to pass to the hooks being triggered.

        Yields:
            `None`

        Examples:
            async with self.obj.trigger_hooks("cleanup", self):
                doStuff()
        """
        try:
            already_triggering = hook_name in self._triggering_hooks
        except AttributeError:
            self._triggering_hooks = set()
            already_triggering = False

        if not already_triggering:
            self._triggering_hooks.add(hook_name)
            await self.__class__.trigger(self, f"before_{hook_name}", *args, **kwargs)

        yield

        if not already_triggering:
            await self.__class__.trigger(self, f"after_{hook_name}", *args, **kwargs)
            self._triggering_hooks.remove(hook_name)

    @classmethod
    async def trigger(cls, target, hook_name, *args, **kwargs) -> None:  # noqa: ANN001, ANN002, ANN003
        """Trigger a registered hook function."""
        hooks = [
            hook
            for hook_cls in reversed(cls.__mro__)
            if hasattr(hook_cls, "__hooks__")
            for hook in hook_cls.__hooks__.get(hook_name, [])
        ]

        for hook_func in hooks:
            try:
                await hook_func(target, *args, **kwargs)
            except Exception as err:  # noqa: PERF203
                if hook_func.__hook__.can_fail:
                    logger.debug(str(err), exc_info=True)
                    logger.warning(
                        f"{hook_name} hook '{hook_func.__name__}' has failed: {err}",  # noqa: G004
                    )
                else:
                    raise err
