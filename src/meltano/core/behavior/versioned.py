from __future__ import annotations  # noqa: D100

from abc import ABC, abstractmethod


class IncompatibleVersionError(Exception):
    """A component is incompatible with its representation."""

    def __init__(self, message, file_version: int, version: int):  # noqa: ANN001, D107
        super().__init__(message)

        self.file_version = file_version
        self.version = version


class Versioned(ABC):
    """Mixin to represent something that must be compatible with a certain version."""

    @property
    @abstractmethod
    def file_version(self) -> int:  # noqa: D102
        pass

    def is_compatible(self, version: int | None = None) -> bool | None:  # noqa: D102
        try:
            self.ensure_compatible(version=version)
            return True
        except IncompatibleVersionError:
            return False

    def ensure_compatible(self, version: int | None = None) -> None:  # noqa: D102
        version = self.__class__.__version__ if version is None else version
        file_version = self.file_version

        if file_version != version:
            raise IncompatibleVersionError(
                f"Version {version} required, currently at {self.file_version}",  # noqa: EM102
                file_version,
                version,
            )
