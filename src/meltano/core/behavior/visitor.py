from typing import Callable
from functools import wraps


class visit_with:
    def __init__(self, visit: Callable):
        self.visit = visit

    def __call__(self, cls):
        # keep a reference to the proper visitor
        __visit__ = self.visit

        class Visitor(cls):
            def visit(self, node, *args, **kwargs):
                return __visit__(node, self, *args, **kwargs)

        return Visitor
