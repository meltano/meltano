from __future__ import annotations  # noqa: D100


class NameEq:  # noqa: D101
    def __eq__(self, other):  # noqa: ANN001, ANN204, D105
        return self is other or self.name == other.name

    def __hash__(self):  # noqa: ANN204, D105
        return hash(self.name)
