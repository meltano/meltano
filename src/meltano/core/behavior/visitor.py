from __future__ import annotations

import typing as t


class visit_with:  # noqa: N801
    def __init__(self, visit: t.Callable):
        self.visit = visit

    def __call__(self, base_cls):  # noqa: ANN001, ANN204
        class Visitor(base_cls):
            def visit(inner_self, node, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003, ANN202, N805
                return self.visit(node, inner_self, *args, **kwargs)

        return Visitor
