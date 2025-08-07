from __future__ import annotations  # noqa: D100

import typing as t

if t.TYPE_CHECKING:
    from collections.abc import Callable


class visit_with:  # noqa: D101, N801
    def __init__(self, visit: Callable):  # noqa: D107
        self.visit = visit

    def __call__(self, base_cls):  # noqa: ANN001, ANN204, D102
        class Visitor(base_cls):
            def visit(inner_self, node, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003, ANN202, N805
                return self.visit(node, inner_self, *args, **kwargs)

        return Visitor
