from __future__ import annotations


class NameEq:
    name: str

    def __eq__(self, other):
        return self is other or self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def __repr__(self) -> str:
        """Return a string representation of the object.

        Returns:
            A string representation of the object.
        """
        return f"{self.__class__.__name__}({self.name!r})"
