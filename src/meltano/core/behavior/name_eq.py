from __future__ import annotations


class NameEq:
    def __eq__(self, other):  # noqa: ANN001, ANN204
        return self is other or self.name == other.name

    def __hash__(self):  # noqa: ANN204
        return hash(self.name)
