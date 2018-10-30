import contextlib


class Hookable:
    class hook():
        _hooks = {}

        def __init__(self, hook_name):
            self.hook_name = hook_name
            self.__class__._hooks[hook_name] = self.__class__._hooks.get(hook_name, [])

        def __call__(self, func):
            self.__class__._hooks[self.hook_name].append(func)
            return func

        @classmethod
        def trigger(cls, target, hook_name, *args, **kwargs):
            for hook in cls._hooks.get(hook_name, []):
                hook(target, *args, **kwargs)

    @contextlib.contextmanager
    def trigger_hooks(self, hook_name, *args, **kwargs):
        self.hook.trigger(self, f"before_{hook_name}", *args, **kwargs)
        yield
        self.hook.trigger(self, f"after_{hook_name}", *args, **kwargs)
