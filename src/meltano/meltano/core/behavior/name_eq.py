from __future__ import annotations


class NameEq:
    def __eq__(self, other):
        return self is other or self.name == other.name

    def __hash__(self):
        return hash(self.name)
