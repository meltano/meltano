from __future__ import annotations  # noqa: D100

import typing as t


class visit_with:  # noqa: D101, N801
    def __init__(self, visit: t.Callable):  # noqa: D107
        self.visit = visit

    def __call__(self, base_cls):  # noqa: D102
        class Visitor(base_cls):
            def visit(inner_self, node, *args, **kwargs):  # noqa: N805
                return self.visit(node, inner_self, *args, **kwargs)

        return Visitor
