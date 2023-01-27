from __future__ import annotations

from typing import Callable


class visit_with:  # noqa: N801
    def __init__(self, visit: Callable):
        self.visit = visit

    def __call__(self, base_cls):
        class Visitor(base_cls):
            def visit(inner_self, node, *args, **kwargs):  # noqa: N805
                return self.visit(node, inner_self, *args, **kwargs)

        return Visitor
